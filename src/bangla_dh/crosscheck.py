"""Out-of-domain check of the Phase 3 results on two news corpora.

Phase 3 searched and evaluated on Bangla Wikipedia only (D4). This module
asks whether its conclusions survive on news text the search never saw:

``crosscheck-build``     data/corpus/crosscheck-v1/*.jsonl.gz (normalized,
                         deduplicated, split as corpus-v1) + frequency and
                         keystroke tables in results/phase3-crosscheck/
``crosscheck-optimize``  the Phase 3 search on newspaper/train (fewer seeds):
                         how much a news-trained layout gains
``evaluate-crosscheck``  scores, checks, REPORT.md, crosscheck.json,
                         run-manifest.json

The source files (collected by the project owner, outside the repository)
are read in place and never modified; their SHA-256 goes to the manifest.
"""
from __future__ import annotations

import datetime as _dt
import gzip
import hashlib
import itertools
import json
import multiprocessing as mp
import platform
import re
import statistics
import time
from pathlib import Path

from . import __version__
from .bangla.grammar import Escape, UnitSet
from .bangla.inventory import INVENTORY_FILE, load_inventory
from .bangla.normalize import describe as describe_normalization
from .bangla.normalize import normalize_text
from .bangla.styles import NO_KEY, STYLES, THIRD_LAYER, load_styles
from .corpus import frequency as freq
from .corpus.build import _Writer, split_of
from .paths import repo_state, DATA, PROJECT_ROOT, RESULTS_ROOT, hash_outputs, relative_to_project, write_json, write_text
from .phase2 import frequency_record as phase2_record
from .phase2_report import _f, _pct, _show
from .phase3 import (FIRST_SEED, HELDOUT, SEARCH_SETTINGS, TRAIN, actions_of, best_layout, problem_fixed,
                     style_frequencies as phase3_style_frequencies, style_round_trips)
from .phase3 import corpus_file as phase3_corpus_file
from .phase3_report import _label, layout_tables
from .reference import sha256_file
from .scoring import baselines
from .scoring.j0 import score_tokens, score_units
from .scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from .scoring.verify import verify_style
from .search import keystrokes
from .search.anneal import Instance, run as run_search
from .search.problem import PROBLEM_FILE, load_problem, parse_slot, slot_name, slots

CONFIG_FILE = DATA / "crosscheck-v1.json"
RESULTS = RESULTS_ROOT / "phase3-crosscheck"
FREQUENCIES = RESULTS / "frequencies"
SEARCH = RESULTS / "search"
SPLITS = ("train", "heldout")
WIKI = (TRAIN, HELDOUT)


def load_config() -> dict:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def dataset_names(config: dict | None = None) -> list[str]:
    return [d["name"] for d in (config or load_config())["datasets"]]


def news_corpora(config: dict | None = None) -> list[str]:
    return [f"{name}/{split}" for name in dataset_names(config) for split in SPLITS]


def corpus_path(name: str, config: dict | None = None) -> Path:
    config = config or load_config()
    return PROJECT_ROOT / config["output_directory"] / f"{name.replace('/', '-')}.jsonl.gz"


def source_files(dataset: dict, config: dict) -> list[Path]:
    return [PROJECT_ROOT / config["source_root"] / f for f in dataset["files"]]


# --- build: corpus ---------------------------------------------------------------

def _lines(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield line


# A sentence mark directly followed by a Bangla letter: the scrape dropped the
# line break between two sentences (``শ্রমিকেরা।সফিপুর``). The repair types a space there.
GLUED = re.compile("([।?!])(?=[\u0980-\u09FF])")
SENTENCE_END = re.compile(r"(?<=[।?!])")
MIN_SENTENCE = 20  # characters; shorter pieces (datelines, captions) are too generic to show shared text


def sentence_digests(paragraphs: list[str]) -> list[bytes]:
    return [hashlib.blake2b(x.encode("utf-8"), digest_size=8).digest()
            for p in paragraphs for x in (y.strip() for y in SENTENCE_END.split(p)) if len(x) >= MIN_SENTENCE]


def _clean(job: tuple[str, bool]) -> tuple[str, str | None, list[str], int, list[bytes]]:
    line, repair = job
    document = json.loads(line)
    paragraphs, repairs = [], 0
    for paragraph in document.get("paragraphs") or []:
        for text in normalize_text(paragraph):
            if repair:
                text, n = GLUED.subn(r"\1 ", text)
                repairs += n
            paragraphs.append(text)
    return str(document["id"]), document.get("title"), paragraphs, repairs, sentence_digests(paragraphs)


def build_corpus(config: dict, workers: int | None = None, log=print) -> dict:
    """One gzip JSON-lines file per dataset and split. A dataset with
    ``exclude_documents_sharing_sentences_with`` drops every document that
    shares a sentence (at least MIN_SENTENCE characters) with that earlier
    dataset, so it holds only text the earlier one does not."""
    directory = PROJECT_ROOT / config["output_directory"]
    sentences: dict[str, set[bytes]] = {}
    datasets = {}
    with mp.Pool(workers or max(1, min(16, mp.cpu_count() - 2))) as pool:
        for dataset in config["datasets"]:
            started = time.time()
            name = dataset["name"]
            repair = dataset.get("repair_glued_sentences", False)
            exclude = dataset.get("exclude_documents_sharing_sentences_with")
            files = source_files(dataset, config)
            sources = []
            for path in files:
                log(f"  hashing {path}")
                sources.append({"file": path.as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
            own: set[bytes] = set()
            writer = _Writer(directory, name, list(SPLITS), set())
            documents = paragraphs_in = repairs = sentence_count = shared_sentences = excluded = 0
            try:
                for path in files:
                    lines = _lines(path)
                    while batch := list(itertools.islice(lines, 8192)):
                        for document_id, title, paragraphs, fixed, digests in pool.imap(
                                _clean, [(line, repair) for line in batch], chunksize=64):
                            documents += 1
                            paragraphs_in += len(paragraphs)
                            repairs += fixed
                            sentence_count += len(digests)
                            own.update(digests)
                            if exclude:
                                shared = sum(d in sentences[exclude] for d in digests)
                                shared_sentences += shared
                                if shared:
                                    excluded += 1
                                    continue
                            writer.add(split_of(f"{name}:{document_id}", config["split"]), document_id, title, paragraphs)
                        if documents % 65536 < 8192:
                            log(f"  {name}: {documents} documents, {time.time() - started:.0f} s")
            finally:
                writer.close()
            sentences[name] = own
            datasets[name] = {
                "label": dataset["label"], "sources": sources, "documents_read": documents,
                "paragraphs_read": paragraphs_in, "sentences_read": sentence_count,
                "glued_sentence_repairs": repairs if repair else None,
                "exclusion": {"dataset": exclude, "sentences_shared": shared_sentences,
                              "documents_excluded": excluded} if exclude else None,
                "duplicate_paragraphs_removed": writer.duplicates,
                "documents_without_new_paragraphs": writer.empty_documents,
                "splits": {s: {**writer.counts[s], "path": relative_to_project(p), "sha256": sha256_file(p)}
                           for s, p in writer.paths.items()},
                "seconds": round(time.time() - started, 1)}
            log(f"{name}: {json.dumps({k: v for k, v in datasets[name].items() if k != 'sources'}, ensure_ascii=False)}")
    return {"version": config["version"], "config": relative_to_project(CONFIG_FILE),
            "config_sha256": sha256_file(CONFIG_FILE), "normalization": describe_normalization(),
            "glued_sentence_repair": {"pattern": GLUED.pattern, "replacement": "the mark followed by one space"},
            "shared_sentence_rule": {"split_after": "। ? !", "min_characters": MIN_SENTENCE,
                                     "digest": "blake2b-64 of the stripped sentence"},
            "split": config["split"], "datasets": datasets}


# --- build: frequency and keystroke tables -----------------------------------------

def frequency_file(name: str) -> Path:
    return FREQUENCIES / f"{name.replace('/', '-')}.json"


def keystroke_file(style: str, name: str) -> Path:
    return FREQUENCIES / f"{style}-{name.replace('/', '-')}.json"


def run_build(workers: int | None = None, skip_corpus: bool = False) -> list[Path]:
    config = load_config()
    written = []
    if not skip_corpus:
        written.append(write_json(RESULTS / "corpus-manifest.json", build_corpus(config, workers)))
    inventory = load_inventory()
    units = UnitSet.from_inventory(inventory)
    for name in news_corpora(config):
        started = time.time()
        record, _ = freq.compute(corpus_path(name, config), units, inventory["symbol_list_sha256"])
        record["corpus"] = name
        written.append(write_json(frequency_file(name), record, indent=1))
        print(f"{name}: N={record['N']} tokens={record['tokens']} types={record['token_types']}, "
              f"{time.time() - started:.0f} s", flush=True)
        for style in STYLES:
            table = keystrokes.compute(style, record, PROJECT_ROOT, workers)
            table["corpus"] = name
            written.append(write_json(keystroke_file(style, name), table, indent=1))
            non_space = table["N"] - table["space_units"]
            print(f"  {style}: {table['keystrokes_excluding_space'] / non_space:.4f} keystrokes per non-space unit, "
                  f"{table['escaped_unit_count']} escaped units", flush=True)
    return written


def unit_record(name: str) -> dict:
    """Phase 2 style frequency record (units and bigrams) of any corpus."""
    return phase2_record(name) if name in WIKI else freq.load_table(frequency_file(name))


def style_record(style: str, name: str) -> tuple[dict, dict, dict]:
    if name in WIKI:
        return phase3_style_frequencies(style, name)
    record = json.loads(keystroke_file(style, name).read_text(encoding="utf-8"))
    u, v = keystrokes.frequencies(record)
    return record, u, v


# --- optimize on news ---------------------------------------------------------------

_instances: dict[str, Instance] = {}


def news_instance(style: str, model: KeyModel, name: str, problem: dict | None = None) -> Instance:
    problem = problem or load_problem()
    _, u, v = style_record(style, name)
    return Instance(problem["styles"][style]["searched_symbols"], slots(), problem_fixed(problem), u, v, model, "J1")


def _search_init(name: str) -> None:
    model = KeyModel.from_grid(ANSI_GRID)
    problem = load_problem()
    for style in STYLES:
        _instances[style] = news_instance(style, model, name, problem)


def _search_job(job) -> tuple[str, dict]:
    style, seed, start, s = job
    result = run_search(_instances[style], seed, start, s["sa_steps"], s["t_ratio"], s["ils_iterations"],
                        tuple(s["ils_strength"]))
    result["layout"] = [_instances[style].labels[result["perm"].index(k)] for k in range(_instances[style].n)]
    del result["perm"]
    return style, result


def run_optimize(seeds: int | None = None, workers: int | None = None) -> list[Path]:
    config = load_config()
    name = config["search"]["frequencies"]
    settings = {k: v for k, v in SEARCH_SETTINGS.items() if k not in ("confirmation", "frequencies")}
    settings.update({"seeds": seeds or config["search"]["seeds"], "frequencies": name})
    jobs = [(style, FIRST_SEED + k, "greedy" if k == 0 else "random", settings)
            for style in STYLES for k in range(settings["seeds"])]
    runs: dict[str, list[dict]] = {style: [] for style in STYLES}
    started = time.time()
    with mp.Pool(workers or max(1, min(24, mp.cpu_count() - 4)), initializer=_search_init, initargs=(name,)) as pool:
        for done, (style, result) in enumerate(pool.imap_unordered(_search_job, jobs), 1):
            runs[style].append(result)
            if done % 16 == 0 or done == len(jobs):
                print(f"{done}/{len(jobs)} runs, {time.time() - started:.0f} s", flush=True)
    problem = load_problem()
    written = []
    for style in STYLES:
        style_runs = sorted(runs[style], key=lambda r: r["seed"])
        scores = [r["best_score"] for r in style_runs]
        best = min(style_runs, key=lambda r: (r["best_score"], r["seed"]))
        record = {
            "style": style, "settings": settings, "frequencies": relative_to_project(keystroke_file(style, name)),
            "frequencies_sha256": sha256_file(keystroke_file(style, name)),
            "problem_sha256": problem["problem_sha256"], "effort_grid": relative_to_project(ANSI_GRID),
            "best": {"seed": best["seed"], "J1": best["best_score"],
                     "layout": {label: slot for label, slot in zip(best["layout"], problem["slots"])}},
            "statistics": {"runs": len(scores), "best": min(scores), "median": statistics.median(scores),
                           "worst": max(scores), "runs_reaching_best": sum(s <= min(scores) + 1e-9 for s in scores),
                           "seconds_total": round(sum(r["seconds"] for r in style_runs), 1)},
            "runs": [{k: r[k] for k in ("seed", "start", "start_score", "after_annealing", "after_descent",
                                        "best_score", "seconds")} | {"layout": r["layout"]} for r in style_runs],
        }
        written.append(write_json(SEARCH / f"{style}.json", record, indent=1))
        print(f"style {style}: best J1 on {name} {min(scores):.6f} (seed {best['seed']}), "
              f"{record['statistics']['runs_reaching_best']}/{len(scores)} runs reach it", flush=True)
    return written


def news_best_layout(style: str) -> dict[str, tuple[str, str]]:
    record = json.loads((SEARCH / f"{style}.json").read_text(encoding="utf-8"))
    return {label: parse_slot(slot) for label, slot in record["best"]["layout"].items()}


# --- evaluation ------------------------------------------------------------------------

GRIDS = {"unrounded": (ANSI_GRID, None), "one_decimal": (ANSI_GRID, 1), "traditional_unrounded": (ANSI_TRADITIONAL_GRID, None)}
# Metrics compared between layouts (lower is better for each).
METRICS = (("J1", "J1"), ("J0", "J0"), ("E1", "E1 (key effort)"), ("E2", "E2 (bigram penalties)"),
           ("E2_same_finger", "same finger"), ("M", "M (Shift)"), ("keystrokes_per_non_space_unit", "keystrokes per unit"))


def grid_model(grid: str) -> KeyModel:
    path, decimals = GRIDS[grid]
    return KeyModel.from_grid(path, decimals=decimals)


def score_style(style: str, layout: dict, name: str, model: KeyModel, fixed: dict) -> dict:
    record, u, v = style_record(style, name)
    result = score_units(actions_of({**layout, **fixed}), u, v, model)
    result["keystrokes_per_non_space_unit"] = record["keystrokes_excluding_space"] / (record["N"] - record["space_units"])
    result["escaped_units"] = record["escaped_unit_count"]
    result["escaped_share"] = record["escaped_unit_count"] / record["N"]
    return result


class _CountingKeyMap:
    """Passes ``encode`` through and counts escaped units, weighted by the
    count of the token being scored (``score_tokens`` encodes each token once,
    right after reading it)."""

    def __init__(self, keymap, units: UnitSet):
        self.keymap, self.units, self.weight, self.escaped = keymap, units, 0, {}

    def encode(self, token: str):
        steps = self.keymap.encode(token)
        for step in steps:
            if isinstance(step, Escape) and self.units.is_unit(step.char):
                self.escaped[step.char] = self.escaped.get(step.char, 0) + self.weight
        return steps


def score_baseline(entry: dict, name: str, model: KeyModel, units: UnitSet) -> dict:
    record = unit_record(name)
    km = _CountingKeyMap(baselines.keymap(entry, model), units)

    def tokens():
        for token, count in freq.read_token_table(PROJECT_ROOT / record["token_table"]):
            km.weight = count
            yield token, count

    result = score_tokens(km, tokens(), record["N"], model)
    result.pop("top_penalty_pairs", None)
    result["keystrokes_per_non_space_unit"] = result["keystrokes_excluding_space"] / (record["N"] - record["space_units"])
    result["escaped_units"] = sum(km.escaped.values())
    result["escaped_share"] = result["escaped_units"] / record["N"]
    result["escaped_unit_top"] = sorted(km.escaped.items(), key=lambda kv: -kv[1])[:8]
    return result


def _baseline_job(job) -> tuple[str, str, str, dict]:
    entry, name, grid = job
    return entry["name"], name, grid, score_baseline(entry, name, grid_model(grid), UnitSet.from_inventory())


def _verify_job(job) -> tuple[str, str, dict]:
    style, name, path, layout = job
    return style, name, verify_style([Path(path)], style, layout, INVENTORY_FILE, ANSI_GRID)


def total_variation(a: dict, b: dict) -> float:
    return 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b))


def distribution_shift(reference: str, others: list[str]) -> dict:
    ru, rv = freq.frequencies(unit_record(reference))
    out = {}
    for name in others:
        u, v = freq.frequencies(unit_record(name))
        changes = sorted(set(ru) | set(u), key=lambda k: -abs(u.get(k, 0.0) - ru.get(k, 0.0)))[:12]
        out[name] = {"units_TV": total_variation(ru, u), "bigrams_TV": total_variation(rv, v),
                     "largest_unit_changes": [[k, ru.get(k, 0.0), u.get(k, 0.0)] for k in changes]}
    return out


def baseline_best(scores_by_grid: dict, metric: str) -> tuple[float | None, str | None]:
    """A baseline's lowest value of ``metric`` over the three grids, and that grid."""
    values = [(s[metric], g) for g, s in scores_by_grid.items() if s.get(metric) is not None]
    return min(values) if values else (None, None)


def comparisons(scores: dict, base: dict, corpora: list[str]) -> dict:
    """Every Phase 3 layout against every baseline at its best grid, metric by metric."""
    out = {}
    for s in STYLES:
        for b, record in base.items():
            for c in corpora:
                ours = scores["wiki"][s][c]["unrounded"]
                rows = {}
                for metric, _ in METRICS:
                    theirs, grid = baseline_best(record["scores"][c], metric)
                    rows[metric] = {"ours": ours[metric], "baseline": theirs, "baseline_grid": grid,
                                    "better": None if theirs is None else ours[metric] < theirs}
                out[f"{s} vs {b} on {c}"] = {
                    "style": s, "baseline": b, "corpus": c, "metrics": rows,
                    "better_in_every_metric": all(r["better"] for r in rows.values()),
                    "escaped_share": {"ours": ours["escaped_share"],
                                      "baseline": record["scores"][c]["unrounded"]["escaped_share"]}}
    return out


def run_evaluation() -> dict:
    started = time.time()
    config = load_config()
    inventory = load_inventory()
    units = UnitSet.from_inventory(inventory)
    problem = load_problem()
    styles = load_styles(inventory)
    fixed = problem_fixed(problem)
    models = {"unrounded": KeyModel.from_grid(ANSI_GRID), "one_decimal": KeyModel.from_grid(ANSI_GRID, decimals=1)}
    model = models["unrounded"]
    news = news_corpora(config)
    news_heldouts = [c for c in news if c.endswith("/heldout")]
    heldouts = [HELDOUT] + news_heldouts
    every = [TRAIN, HELDOUT] + news
    result: dict = {"config": config, "corpus": json.loads((RESULTS / "corpus-manifest.json").read_text(encoding="utf-8"))}

    print("Corpus statistics ...", flush=True)
    corpora = {}
    for name in every:
        r = unit_record(name)
        corpora[name] = {k: r[k] for k in ("documents", "paragraphs", "tokens", "token_types", "N", "space_units",
                                           "out_of_inventory_characters")}
        corpora[name]["out_of_inventory_top"] = list(r["out_of_inventory_counts"].items())[:10]
    result["corpora"] = corpora
    result["shift"] = distribution_shift(TRAIN, [HELDOUT] + news)

    print("Keystroke tables ...", flush=True)
    tables = {}
    for style in STYLES:
        for name in every:
            record, _, _ = style_record(style, name)
            non_space = record["N"] - record["space_units"]
            tables[f"{style} {name}"] = {
                "N": record["N"], "keystrokes_per_non_space_unit": record["keystrokes_excluding_space"] / non_space,
                "escaped_units": record["escaped_unit_count"], "escaped_share": record["escaped_unit_count"] / record["N"],
                "rule_escapes": sum(c for unit, c in record["escaped_units"].items()
                                    if unit not in THIRD_LAYER and unit not in NO_KEY),
                "escaped_top": list(record["escaped_units"].items())[:8]}
    result["keystroke_tables"] = tables

    print("Round trips ...", flush=True)
    texts = {}
    for name in news_heldouts:
        table = PROJECT_ROOT / unit_record(name)["token_table"]
        texts[f"{name} token types (top 200000)"] = [t for _, (t, _c) in zip(range(200_000), freq.read_token_table(table))]
    result["round_trip"] = style_round_trips(styles, texts)

    print("Layout scores ...", flush=True)
    layouts = {"wiki": {s: best_layout(s) for s in STYLES}, "news": {s: news_best_layout(s) for s in STYLES}}
    result["layouts"] = {kind: {s: {label: slot_name(slot) for label, slot in layout.items()}
                                for s, layout in by_style.items()} for kind, by_style in layouts.items()}
    scores = {kind: {s: {name: {grid: score_style(s, layouts[kind][s], name, m, fixed) for grid, m in models.items()}
                         for name in every} for s in STYLES} for kind in layouts}
    result["scores"] = scores
    result["layout_differences"] = {s: sorted(label for label in layouts["wiki"][s]
                                              if layouts["wiki"][s][label] != layouts["news"][s][label])
                                    for s in STYLES}

    print("Baselines ...", flush=True)
    registry, skipped = baselines.load_registry(with_skipped=True)
    result["baselines_skipped"] = skipped
    base = {e["name"]: {"entry": baselines.describe(e), "scores": {},
                        "placed_units_not_producible": sorted(
                            set(units.placed) - set(baselines.keymap(e, model).producible()))}
            for e in registry}
    jobs = [(e, name, grid) for e in registry for name in heldouts for grid in GRIDS]
    jobs += [(e, TRAIN, grid) for e in registry if e["name"] == "UniJoy" for grid in GRIDS]
    with mp.Pool(min(len(jobs), max(1, mp.cpu_count() - 8))) as pool:
        for b, name, grid, scored in pool.imap_unordered(_baseline_job, jobs):
            base[b]["scores"].setdefault(name, {})[grid] = scored
    for e in registry:
        km = baselines.keymap(e, model)
        per = {}
        for source, items in texts.items():
            sample = items[:20_000]
            results = [km.round_trip(t) for t in sample]
            per[source.replace("200000", "20000")] = {
                "texts": len(sample), "round_trip_ok": sum(ok for ok, _ in results),
                "failures": sum(not ok for ok, _ in results), "texts_with_escapes": sum(n > 0 for _, n in results),
                "failure_examples": [t for t, (ok, _) in zip(sample, results) if not ok][:10]}
        base[e["name"]]["round_trip"] = per
    result["baselines"] = base
    result["comparisons"] = comparisons(scores, base, heldouts)

    print("Checks ...", flush=True)
    phase3 = json.loads((RESULTS_ROOT / "phase3" / "phase3.json").read_text(encoding="utf-8"))
    checks: dict = {"phase3_reproduced": {}, "search": {}, "verifier": {}}
    for name in WIKI:
        for s in STYLES:
            ours = scores["wiki"][s][name]["unrounded"]["J1"]
            theirs = phase3["scores"][s][name]["unrounded"]["J1"]
            checks["phase3_reproduced"][f"{s} {name}"] = {"J1": ours, "phase3_J1": theirs, "pass": ours == theirs}
        ours = base["UniJoy"]["scores"][name]["unrounded"]["J1"]
        theirs = phase3["unijoy"]["scores"][name]["unrounded"]["J1"]
        checks["phase3_reproduced"][f"UniJoy {name}"] = {"J1": ours, "phase3_J1": theirs,
                                                         "pass": abs(ours - theirs) < 1e-12}
    for s in STYLES:
        record = json.loads((SEARCH / f"{s}.json").read_text(encoding="utf-8"))
        inst = news_instance(s, model, config["search"]["frequencies"], problem)
        search_j1 = inst.score(inst.perm_of(layouts["news"][s]))
        table_j1 = scores["news"][s][config["search"]["frequencies"]]["unrounded"]["J1"]
        checks["search"][s] = {"search_record_J1": record["best"]["J1"], "instance_J1": search_j1, "table_J1": table_j1,
                               "pass": abs(search_j1 - table_j1) < 1e-9 and abs(record["best"]["J1"] - table_j1) < 1e-9}
    vjobs = [(s, name, str(corpus_path(name, config)), {**result["layouts"]["wiki"][s], **problem["fixed"]})
             for s in STYLES for name in news_heldouts]
    with mp.Pool(len(vjobs)) as pool:
        verified = pool.map(_verify_job, vjobs)
    for s, name, v in verified:
        table = scores["wiki"][s][name]["unrounded"]
        record, _, _ = style_record(s, name)
        difference = max(abs(v["J1"] - table["J1"]), abs(v["J0"] - table["J0"])) / table["J1"]
        checks["verifier"][f"{s} {name}"] = {
            "verifier": v, "table_J1": table["J1"], "max_relative_difference": difference,
            "pass": difference < 1e-9 and v["N"] == record["N"] and v["escaped_units"] == record["escaped_unit_count"]
            and v["keystrokes_excluding_space"] == record["keystrokes_excluding_space"]}
    result["checks"] = checks
    result["search"] = {s: {k: v for k, v in json.loads((SEARCH / f"{s}.json").read_text(encoding="utf-8")).items()
                            if k in ("settings", "statistics", "best", "frequencies_sha256")} for s in STYLES}
    result["models"] = {g: grid_model(g).describe() for g in GRIDS}
    result["seconds"] = round(time.time() - started, 1)
    return result


def acceptance(ev: dict) -> dict[str, bool]:
    c = ev["checks"]
    return {
        "Phase 3 scores reproduced exactly on bnwiki (layouts and UniJoy)": all(
            x["pass"] for x in c["phase3_reproduced"].values()),
        "NFC round trip of every style on the news held-out tokens": all(
            s["failures"] == 0 for style in ev["round_trip"].values() for s in style.values()),
        "every baseline round-trips the most frequent news held-out token types": all(
            r["failures"] == 0 for b in ev["baselines"].values() for r in b["round_trip"].values()),
        "news search objective equals the table scorer": all(x["pass"] for x in c["search"].values()),
        "independent verifier equals the table scorer on the news held-out splits": all(
            x["pass"] for x in c["verifier"].values()),
    }


# --- report ----------------------------------------------------------------------------

def _rank(values: dict[str, float]) -> str:
    return " < ".join(sorted(values, key=values.get))


def _change(new: float, old: float) -> str:
    return f"{new - old:+.4f} ({100 * (new / old - 1):+.1f} %)"


def _metric(value: float | None, metric: str) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}"


def build_report(ev: dict) -> str:
    config = ev["config"]
    names = dataset_names(config)
    news_ho = [f"{n}/heldout" for n in names]
    heldouts = [HELDOUT] + news_ho
    scores, base = ev["scores"], ev["baselines"]
    search_corpus = config["search"]["frequencies"]
    ok = acceptance(ev)
    wiki = {s: {c: scores["wiki"][s][c]["unrounded"] for c in scores["wiki"][s]} for s in STYLES}
    uj = base["UniJoy"]["scores"]
    comps = ev["comparisons"]
    L: list[str] = []
    w = L.append

    w("# Phase 3 cross-check on two news corpora")
    w("")
    w("Generated by `bangla-dh evaluate-crosscheck`. Machine-readable record: [crosscheck.json](crosscheck.json); "
      "news search records: [search/](search/); hashes of every input and output: [run-manifest.json](run-manifest.json). "
      "The Phase 3 report ([../phase3/REPORT.md](../phase3/REPORT.md)) is unchanged; **previous** below means its "
      "Wikipedia results, **current** the news results.")
    w("")
    w("Phase 3 searched on Bangla Wikipedia only (D4) and checked its best layouts on held-out Wikipedia text, the same "
      "domain. Here the same layouts, unchanged, are scored on news text the search never saw, against every baseline "
      "in [`data/baselines/registry.json`](../../data/baselines/registry.json), and the Phase 3 search is re-run on news "
      "text to measure how much a news-trained layout would gain. Model, grids, styles and problem are those of "
      "Phase 3 (D3 and D6 at their defaults). All Bangla-DH layouts are **best found**.")
    w("")

    # summary
    w("## Summary")
    w("")
    w("| Layout | J1 previous (bnwiki held-out) | " + " | ".join(f"J1 current ({c})" for c in news_ho) + " |")
    w("| --- | --- | " + " --- |" * len(news_ho))
    for s in STYLES:
        w(f"| Bangla-DH {s} | {_f(wiki[s][HELDOUT]['J1'])} | " +
          " | ".join(f"{_f(wiki[s][c]['J1'])} ({_change(wiki[s][c]['J1'], wiki[s][HELDOUT]['J1'])})" for c in news_ho) + " |")
    for b, record in base.items():
        sc = record["scores"]
        w(f"| {b} | {_metric(sc[HELDOUT]['unrounded']['J1'], 'J1')} | " +
          " | ".join(_metric(sc[c]["unrounded"]["J1"], "J1") for c in news_ho) + " |")
    w("")
    for c in heldouts:
        w(f"* Style order on {c} (J1, lower is better): {_rank({s: wiki[s][c]['J1'] for s in STYLES})}.")
    best_style = min(STYLES, key=lambda st: wiki[st][HELDOUT]["J1"])
    w(f"* Style {best_style} (lowest J1) against each fixed layout on all three held-out sets, metric by metric "
      f"(each baseline at its best grid; section 3):")
    w("")
    w(f"| Baseline | J1 ({best_style} / baseline, {news_ho[0]}) | Better in | Worse in |")
    w("| --- | --- | --- | --- |")
    for b in base:
        rows = [comps[f"{best_style} vs {b} on {c}"] for c in heldouts]
        better = [label for metric, label in METRICS if all(r["metrics"][metric]["better"] for r in rows)]
        worse = []
        for metric, label in METRICS:
            if not all(r["metrics"][metric]["better"] for r in rows):
                pairs = ", ".join(f"{r['metrics'][metric]['ours']:.4f} / {_metric(r['metrics'][metric]['baseline'], metric)}"
                                  for r in rows)
                worse.append(f"{label} ({pairs})")
        news_row = comps[f"{best_style} vs {b} on {news_ho[0]}"]["metrics"]["J1"]
        w(f"| {b} | {news_row['ours']:.4f} / {_metric(news_row['baseline'], 'J1')} | "
          f"{', '.join(better) or 'none'} | {'; '.join(worse) or '**none: better in every metric**'} |")
    w("")
    high_escape = [b for b, r in base.items() if max(r["scores"][c]["unrounded"]["escaped_share"] for c in heldouts) > 0.005]
    w("* Keystrokes per unit fall below one only through keys that type two units at once (`্র`, `র্`, `্য`, "
      f"conjuncts) or through escaped text; every Bangla-DH key types one unit, so {best_style} cannot beat such layouts "
      "on keystroke count, only on effort. "
      + (f"{', '.join(high_escape)} cannot type part of the text on base/Shift (escaped, cost-free: "
         + ", ".join(f"{b} {_pct(max(base[b]['scores'][c]['unrounded']['escaped_share'] for c in heldouts), 1)}" for b in high_escape)
         + "), which flatters its J and keystroke count." if high_escape else ""))
    order = {c: _rank({st: wiki[st][c]["J1"] for st in STYLES}) for c in heldouts}
    if len(set(order.values())) > 1:
        w("* The style order changes between corpora: " + "; ".join(f"{c}: {o}" for c, o in order.items()) +
          ". The pairs that swap differ by less than " +
          f"{max(abs(wiki['A'][c]['J1'] - wiki['B'][c]['J1']) for c in news_ho):.4f} J1 on news text (A and B).")
    regrets = {s: {c: wiki[s][c]["J1"] / scores["news"][s][c]["unrounded"]["J1"] - 1 for c in news_ho} for s in STYLES}
    worst = max(r for by_c in regrets.values() for r in by_c.values())
    w(f"* A layout re-optimized on {search_corpus} beats the Phase 3 layout on news held-out text by at most "
      f"{_pct(worst)} of J1 (section 5).")
    w("* Checks: " + "; ".join(f"{name}: {'PASS' if passed else 'FAIL'}" for name, passed in ok.items()) + ".")
    w("")

    # 1 data
    w("## 1. Data")
    w("")
    w(f"Config: [`data/crosscheck-v1.json`](../../data/crosscheck-v1.json). Sources are read in place (SHA-256 in "
      f"[corpus-manifest.json](corpus-manifest.json)), normalized with `bangla-dh-text-v1`, deduplicated by paragraph "
      f"within each dataset and split by document with the corpus-v1 rule (10 % held-out). Titles are not used. "
      f"The `wikidata` folder of the same collection is the Phase 2 Wikipedia corpus (identical token tables), so it "
      f"adds nothing new.")
    w("")
    w("| Dataset | Source | Documents read | Sentence marks repaired | Documents kept | Characters kept |")
    w("| --- | --- | --- | --- | --- | --- |")
    for n in names:
        d = ev["corpus"]["datasets"][n]
        kept = sum(x["documents"] for x in d["splits"].values())
        chars = sum(x["characters"] for x in d["splits"].values())
        w(f"| {n} | {d['label']} | {d['documents_read']:,} | {d['glued_sentence_repairs'] or 0:,} | {kept:,} | {chars:,} |")
    w("")
    for n in names:
        d = ev["corpus"]["datasets"][n]
        if d["exclusion"]:
            x = d["exclusion"]
            w(f"* **{n}:** {x['sentences_shared']:,} of {d['sentences_read']:,} sentences "
              f"({_pct(x['sentences_shared'] / d['sentences_read'], 1)}) also occur in {x['dataset']}, so BARD as "
              f"delivered is mostly the same newspaper text. {x['documents_excluded']:,} of {d['documents_read']:,} "
              f"documents share at least one sentence with {x['dataset']} and are dropped; the rest is text the news "
              f"search never saw.")
    w("* **Glued sentences:** both scrapes dropped the line break between sentences (`শ্রমিকেরা।সফিপুর`); a sentence "
      "mark directly followed by a Bangla character gets one space. Without it the danda would be scored as followed "
      "by a letter instead of the thumb.")
    w("")
    w("| Corpus | Documents | Tokens | Token types | N (units incl. space) | Characters outside the inventory |")
    w("| --- | --- | --- | --- | --- | --- |")
    for c, r in ev["corpora"].items():
        oov = r["out_of_inventory_characters"]
        w(f"| {c} | {r['documents']:,} | {r['tokens']:,} | {r['token_types']:,} | {r['N']:,} | "
          f"{oov:,} ({_pct(oov / (r['N'] + oov), 1)}) |")
    w("")
    w("Distance of each corpus's unit and bigram frequencies from bnwiki/train (total variation: 0 identical, 1 disjoint):")
    w("")
    w("| Corpus | Units | Bigrams | Largest unit changes (bnwiki/train → corpus) |")
    w("| --- | --- | --- | --- |")
    for c, d in ev["shift"].items():
        changes = ", ".join(f"{_label(k)} {_pct(a)}→{_pct(b)}" for k, a, b in d["largest_unit_changes"][:6])
        w(f"| {c} | {d['units_TV']:.4f} | {d['bigrams_TV']:.4f} | {changes} |")
    w("")

    # 2 previous vs current
    w("## 2. Previous (Wikipedia) and current (news) results")
    w("")
    w("Phase 3 layouts, model-optimal grid, unrounded. J1 = E1 + E2 + M per unit of text (space included).")
    w("")
    w("| Layout | Corpus | J1 | E1 | E2 | same finger | M | keystrokes per unit | J1 change vs bnwiki held-out |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for s in STYLES:
        for c in heldouts:
            r = wiki[s][c]
            change = "(previous)" if c == HELDOUT else _change(r["J1"], wiki[s][HELDOUT]["J1"])
            w(f"| Bangla-DH {s} | {c} | {_f(r['J1'])} | {_f(r['E1'])} | {_f(r['E2'])} | {_f(r['E2_same_finger'])} | "
              f"{_f(r['M'])} | {r['keystrokes_per_non_space_unit']:.4f} | {change} |")
    for b, record in base.items():
        for c in heldouts:
            r = record["scores"][c]["unrounded"]
            prev = record["scores"][HELDOUT]["unrounded"]["J1"]
            change = "(previous)" if c == HELDOUT else (_change(r["J1"], prev) if r["J1"] and prev else "n/a")
            w(f"| {b} | {c} | {_metric(r['J1'], 'J1')} | {_f(r['E1'])} | {_f(r['E2'])} | {_f(r['E2_same_finger'])} | "
              f"{_metric(r['M'], 'M')} | {r['keystrokes_per_non_space_unit']:.4f} | {change} |")
    w("")
    w("Advantage over UniJoy (J1, UniJoy at its own best grid):")
    w("")
    w("| Style | " + " | ".join(heldouts) + " |")
    w("| --- |" + " --- |" * len(heldouts))
    for s in STYLES:
        cells = []
        for c in heldouts:
            theirs, grid = baseline_best(uj[c], "J1")
            cells.append(f"{_pct(wiki[s][c]['J1'] / theirs - 1, 1)}")
        w(f"| {s} | " + " | ".join(cells) + " |")
    w("")
    w("Train → held-out change of J1 inside each news dataset (both splits unseen by the Phase 3 search): " +
      "; ".join(f"{n}: " + ", ".join(f"{s} {wiki[s][f'{n}/heldout']['J1'] - wiki[s][f'{n}/train']['J1']:+.4f}"
                                      for s in STYLES) for n in names) + ".")
    w("")
    w("Grid sensitivity on the news held-out splits (J1): one-decimal grid "
      + "; ".join(f"{c}: " + ", ".join(f"{s} {_f(scores['wiki'][s][c]['one_decimal']['J1'])}" for s in STYLES)
                  for c in news_ho) + ".")
    w("")

    # 3 baselines
    w("## 3. Bangla-DH against every baseline, metric by metric")
    w("")
    w("Registry: [`data/baselines/registry.json`](../../data/baselines/registry.json); how to add a layout: "
      "[`data/baselines/README.md`](../../data/baselines/README.md). Each Bangla-DH layout is scored on the "
      "model-optimal grid it was designed for. Each baseline gets, **per metric**, its lowest value over the "
      "model-optimal (unrounded, one decimal) and traditional-fingering grids, so a win does not depend on the "
      "fingering assumption (D3). ✓ = Bangla-DH lower (better).")
    w("")
    for b, record in base.items():
        e = record["entry"]
        missing = record["placed_units_not_producible"]
        w(f"### {b}")
        w("")
        rt = "; ".join(f"{src}: {r['round_trip_ok']:,}/{r['texts']:,} round trips" for src, r in record["round_trip"].items())
        w(f"Source `{e['file']}` (SHA-256 `{e['sha256'][:16]}…`), {e['kind']}, typists' fingering: {e['fingering']}. "
          f"{e['provenance']} Placed units it cannot type on base/Shift: "
          f"{', '.join(_label(u) for u in missing) or 'none'}. {rt}.")
        w("")
        w("| Style | Corpus | " + " | ".join(label for _, label in METRICS) + " | Every metric | Escaped share (ours / theirs) |")
        w("| --- | --- |" + " --- |" * len(METRICS) + " --- | --- |")
        for s in STYLES:
            for c in heldouts:
                x = comps[f"{s} vs {b} on {c}"]
                cells = []
                for metric, _ in METRICS:
                    r = x["metrics"][metric]
                    mark = "n/a" if r["better"] is None else ("✓" if r["better"] else "✗")
                    cells.append(f"{r['ours']:.4f} / {_metric(r['baseline'], metric)} {mark}")
                esc = x["escaped_share"]
                w(f"| {s} | {c} | " + " | ".join(cells) +
                  f" | {'yes' if x['better_in_every_metric'] else 'no'} | {_pct(esc['ours'], 3)} / {_pct(esc['baseline'], 3)} |")
        w("")
    if ev.get("baselines_skipped"):
        w("Not compared (phonetic or not a fixed layout): " + ", ".join(
            f"`{Path(x['file']).parent.name}` ({x['type']})" for x in ev["baselines_skipped"]) + ".")
        w("")
    w("Escaped units cost nothing in J, so a layout with a larger escaped share is flattered by it. These metrics are "
      "the model's effort terms; they are not typing speed, learnability or error rate, which need the planned "
      "typing study.")
    w("")

    # 4 styles on news
    w("## 4. Vowel-entry styles on news text")
    w("")
    w("| Style | Corpus | Keystrokes per non-space unit | Escaped units | Share of N | Rule escapes | Most escaped |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    for s in STYLES:
        for c in heldouts:
            t = ev["keystroke_tables"][f"{s} {c}"]
            top = ", ".join(f"{_show(u)} {k:,}" for u, k in t["escaped_top"][:5])
            w(f"| {s} | {c} | {t['keystrokes_per_non_space_unit']:.4f} | {t['escaped_units']:,} | "
              f"{_pct(t['escaped_share'], 3)} | {t['rule_escapes']:,} | {top} |")
    w("")
    w("NFC round trip `NFC(decode(encode(T))) = NFC(T)` on the most frequent news token types:")
    w("")
    w("| Style | Text set | Texts | Round trip OK | Failures | With escapes |")
    w("| --- | --- | --- | --- | --- | --- |")
    for s, per in ev["round_trip"].items():
        for source, r in per.items():
            w(f"| {s} | {source} | {r['texts']:,} | {r['round_trip_ok']:,} | {r['failures']} | {r['texts_with_escapes']:,} |")
    w("")

    # 5 search and regret
    w(f"## 5. Search on {search_corpus} and domain regret")
    w("")
    st = ev["search"][STYLES[0]]["settings"]
    w(f"The Phase 3 search (simulated annealing {st['sa_steps']:,} steps, steepest descent, {st['ils_iterations']:,} "
      f"iterations of iterated local search), {st['seeds']} seeds per style (Phase 3: 64), objective J1, frequencies "
      f"{search_corpus}, no confirmation runs.")
    w("")
    w("| Style | Runs | Best J1 (train) | Median | Worst | Runs reaching the best | Labels on another slot than in Phase 3 |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    for s in STYLES:
        x = ev["search"][s]["statistics"]
        w(f"| {s} | {x['runs']} | {x['best']:.6f} | {x['median']:.6f} | {x['worst']:.6f} | {x['runs_reaching_best']} | "
          f"{len(ev['layout_differences'][s])} of 52 |")
    w("")
    worse_found = [st for st in STYLES
                   if scores["wiki"][st][search_corpus]["unrounded"]["J1"] < scores["news"][st][search_corpus]["unrounded"]["J1"]]
    if worse_found:
        w("For " + ", ".join(worse_found) + " the Phase 3 layout scores better on " + search_corpus + " itself (" +
          "; ".join(f"{st}: {scores['wiki'][st][search_corpus]['unrounded']['J1']:.6f} against "
                    f"{scores['news'][st][search_corpus]['unrounded']['J1']:.6f}" for st in worse_found) +
          ") than the best layout the news search found: the shorter news search did not reach it, and the "
          "Wikipedia-trained layout is at least as good on news text as anything that search visited.")
        w("")
    w("J1 of the Phase 3 (bnwiki-trained) layout against the news-trained layout. Regret is what the Phase 3 layout "
      "costs on that text relative to the news-trained one; on bnwiki it is negative (the news layout costs there).")
    w("")
    w("| Style | Corpus | bnwiki-trained | news-trained | Regret of the bnwiki layout |")
    w("| --- | --- | --- | --- | --- |")
    for s in STYLES:
        for c in heldouts:
            a = scores["wiki"][s][c]["unrounded"]["J1"]
            b = scores["news"][s][c]["unrounded"]["J1"]
            w(f"| {s} | {c} | {_f(a)} | {_f(b)} | {_pct(a / b - 1)} |")
    w("")
    for s in STYLES:
        w(f"### Style {s}: news-trained layout")
        w("")
        w(f"Labels moved relative to Phase 3: {' '.join(_show(x) for x in ev['layout_differences'][s]) or 'none'}.")
        w("")
        L.extend(layout_tables(ev["layouts"]["news"][s]))

    # 6 checks
    w("## 6. Checks")
    w("")
    w("| Check | Item | Value | Reference | Pass |")
    w("| --- | --- | --- | --- | --- |")
    for item, x in ev["checks"]["phase3_reproduced"].items():
        w(f"| Phase 3 reproduced | {item} | {x['J1']:.12f} | {x['phase3_J1']:.12f} | {'PASS' if x['pass'] else 'FAIL'} |")
    for item, x in ev["checks"]["search"].items():
        w(f"| news search = table scorer | {item} | {x['instance_J1']:.12f} | {x['table_J1']:.12f} | "
          f"{'PASS' if x['pass'] else 'FAIL'} |")
    for item, x in ev["checks"]["verifier"].items():
        w(f"| verifier = tables | {item} | {x['verifier']['J1']:.12f} | {x['table_J1']:.12f} "
          f"(rel. {x['max_relative_difference']:.1e}) | {'PASS' if x['pass'] else 'FAIL'} |")
    w("")
    for name, passed in ok.items():
        w(f"* {'PASS' if passed else 'FAIL'}: {name}")
    w("")

    w("## 7. Reproduce")
    w("")
    w("```bash")
    w("bangla-dh crosscheck-build      # corpora, frequencies and keystroke tables (about 25 minutes)")
    w("bangla-dh crosscheck-optimize   # 4 styles x 32 seeds on newspaper/train")
    w("bangla-dh evaluate-crosscheck   # scores every registered baseline too")
    w("```")
    w("")
    return "\n".join(L)


def manifest(outputs: list[Path], ev: dict) -> dict:
    head, clean = repo_state()
    inputs = {relative_to_project(p): sha256_file(p) for p in (CONFIG_FILE, baselines.REGISTRY, INVENTORY_FILE,
                                                              PROBLEM_FILE, ANSI_GRID, ANSI_TRADITIONAL_GRID)}
    for record in ev["baselines"].values():
        e = record["entry"]
        inputs[("kala:" if e["kind"] == "kala" else "") + e["file"]] = e["sha256"]
    for d in ev["corpus"]["datasets"].values():
        for source in d["sources"]:
            inputs[f"external:{source['file']}"] = source["sha256"]
        for split in d["splits"].values():
            inputs[split["path"]] = split["sha256"]
    for name in WIKI:
        inputs[relative_to_project(phase3_corpus_file(name))] = sha256_file(phase3_corpus_file(name))
    phase3 = RESULTS_ROOT / "phase3"
    for p in [phase3 / "phase3.json"] + sorted(phase3.glob("search/*.json")) + sorted(phase3.glob("frequencies/*.json")):
        inputs[relative_to_project(p)] = sha256_file(p)
    settings = ev["search"][STYLES[0]]["settings"]
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "repo_commit": head, "working_tree_clean": clean,
            "parameters": {"objective": "J1 as Phase 3", "effort_grid": relative_to_project(ANSI_GRID),
                           "fingering": "model-optimal (D3 default); baselines also on traditional fingering",
                           "middle_index_benefit": "kept (D6 default)", "search": settings,
                           "seed_range_per_style": [FIRST_SEED, FIRST_SEED + settings["seeds"] - 1]},
            "inputs": inputs, "outputs": hash_outputs(outputs)}


def run_and_write(report_only: bool = False) -> int:
    """``report_only`` rewrites REPORT.md and the manifest from crosscheck.json without re-scoring."""
    if report_only:
        evaluation = json.loads((RESULTS / "crosscheck.json").read_text(encoding="utf-8"))
    else:
        evaluation = run_evaluation()
    outputs = [write_json(RESULTS / "crosscheck.json", evaluation, indent=1),
               write_text(RESULTS / "REPORT.md", build_report(evaluation))]
    produced = [RESULTS / "corpus-manifest.json"] + sorted(FREQUENCIES.glob("*.json")) + sorted(SEARCH.glob("*.json"))
    outputs.append(write_json(RESULTS / "run-manifest.json", manifest(produced + outputs, evaluation)))
    for path in outputs:
        print(path)
    checks = acceptance(evaluation)
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    return 0 if all(checks.values()) else 1
