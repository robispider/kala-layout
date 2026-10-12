"""Phase 2 driver: inventory, frequencies, scorer checks, baselines, report.

Steps (each a CLI command, see ``cli.py``):

``build-inventory``   data/bangla-symbols-v1.json + results/phase2/inventory-validation.json
``build-corpus``      data/corpus/bangla-corpus-v1/*.jsonl.gz + results/phase2/corpus-manifest.json
``compute-frequency`` token tables + results/phase2/frequencies/*.json
``evaluate-phase2``   checks, baselines, REPORT.md, phase2.json, run-manifest.json
"""
from __future__ import annotations

import datetime as _dt
import json
import platform
import random
import time
from collections import Counter
from pathlib import Path

from . import __version__
from .bangla.grammar import Action, KeyMap, UnitSet, nfc, segment, single_action_keymap
from .bangla.inventory import (HASANT, INVENTORY_FILE, build_inventory, is_consonant_unit, load_inventory,
                               segment_consonants)
from .colemak.keyboard import load_layout
from .colemak.frequency import load_frequency_file
from .colemak.analysis import perform_analysis
from .corpus import build as corpus_build
from .corpus import frequency as freq
from .paths import (repo_state, CORPUS_DATA, PROJECT_ROOT, RESULTS_ROOT, hash_outputs, kala_path,
                    relative_to_project, write_json, write_text)
from .reference import load_published, resource, sha256_file
from .scoring.j0 import score_tokens, score_units
from .scoring.layouts import (bijoy_matches_unijoy, english_model_and_assignment, load_english_frequencies,
                              unijoy_keymap, UNIJOY, BIJOY)
from .scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, MAIN_BLOCK, KeyModel
from .scoring.verify import verify_j0

RESULTS = RESULTS_ROOT / "phase2"
FREQUENCIES = RESULTS / "frequencies"
OPTIMIZATION_FREQUENCIES = FREQUENCIES / "optimization-frequencies.json"
LAYERS = ("base", "shift", "altgr")
REFERENCE_SEED = 20261010
WORD_LISTS = ["tools/kala-eval/datasets/top20k.tsv", "tools/kala-eval/datasets/err_frequent_gold.tsv",
              "tools/kala-eval/datasets/err_inflected.tsv", "tools/kala-eval/datasets/err_rare_gold.tsv",
              "tools/kala-eval/datasets/err_usage_dev.tsv", "tools/kala-eval/datasets/err_usage_test.tsv"]


# --- step 1: inventory --------------------------------------------------------

def run_inventory() -> list[Path]:
    inventory, report = build_inventory()
    return [write_json(INVENTORY_FILE, inventory), write_json(RESULTS / "inventory-validation.json", report)]


# --- step 2: corpus ------------------------------------------------------------

def run_corpus() -> list[Path]:
    manifest = corpus_build.build(corpus_build.load_config())
    return [write_json(RESULTS / "corpus-manifest.json", manifest)]


def corpus_files() -> dict[str, Path]:
    """'<domain>/<split>' → corpus file, from the corpus manifest."""
    manifest = json.loads((RESULTS / "corpus-manifest.json").read_text(encoding="utf-8"))
    return {f"{d}/{s}": PROJECT_ROOT / info["path"]
            for d, domain in manifest["domains"].items() for s, info in domain["splits"].items()}


# --- step 3: frequencies ---------------------------------------------------------

def run_frequency() -> list[Path]:
    inventory = load_inventory()
    units = UnitSet.from_inventory(inventory)
    written, records = [], {}
    for name, path in corpus_files().items():
        record, table = freq.compute(path, units, inventory["symbol_list_sha256"])
        records[name] = record
        written.append(write_json(FREQUENCIES / f"{name.replace('/', '-')}.json", record, indent=1))
        print(f"{name}: N={record['N']} tokens={record['tokens']} types={record['token_types']}")
    weights = {k: v for k, v in corpus_build.load_config()["frequency_weights"].items() if k != "description"}
    u, v = freq.mixture(records, weights)
    sources = {name: {"file": relative_to_project(FREQUENCIES / f"{name.replace('/', '-')}.json"), "N": records[name]["N"]}
               for name in weights}
    written.append(freq.write_mixture(OPTIMIZATION_FREQUENCIES, u, v, weights, sources))
    return written


def frequency_record(name: str) -> dict:
    return freq.load_table(FREQUENCIES / f"{name.replace('/', '-')}.json")


# --- step 4: evaluation ------------------------------------------------------------

def reference_slots() -> list[tuple[str, str]]:
    """The 90 v1 candidate slots: 30 main-block keys × base/Shift/AltGr."""
    return [(key, layer) for layer in LAYERS for key in MAIN_BLOCK]


def unigram_greedy_assignment(u: dict[str, float], placed: set[str], model: KeyModel) -> dict[str, tuple[str, str]]:
    """Most frequent symbol on the cheapest slot: the minimum of E1 alone
    (rearrangement inequality). With free layers it stacks three symbols on
    each of the cheapest keys, so it is a bound ingredient, not a candidate."""
    symbols = sorted(placed, key=lambda s: (-u.get(s, 0.0), s))
    slots = sorted(reference_slots(), key=lambda kl: (model.effort(kl[0]), LAYERS.index(kl[1]), kl[0]))
    return dict(zip(symbols, slots))


def base_first_greedy_assignment(u: dict[str, float], placed: set[str], model: KeyModel) -> dict[str, tuple[str, str]]:
    """Frequency-sorted symbols on the base layer first (cheapest key first),
    then Shift, then AltGr: the naive 'frequent letters on home keys' layout."""
    symbols = sorted(placed, key=lambda s: (-u.get(s, 0.0), s))
    slots = sorted(reference_slots(), key=lambda kl: (LAYERS.index(kl[1]), model.effort(kl[0]), kl[0]))
    return dict(zip(symbols, slots))


def random_assignment(placed: set[str], seed: int) -> dict[str, tuple[str, str]]:
    rng = random.Random(seed)
    slots = reference_slots()
    rng.shuffle(slots)
    return dict(zip(sorted(placed), slots))


def lower_bound_0(u: dict[str, float], v: dict[tuple[str, str], float], placed: set[str], model: KeyModel) -> dict:
    """LB_0 of RESEARCH_SPEC 8.3 for the 90-slot scope."""
    greedy = unigram_greedy_assignment(u, placed, model)
    e1_min = sum(u.get(s, 0.0) * model.effort(key) for s, (key, _) in greedy.items())
    min_b = min(min(model.same_finger), min(min(r) for r in model.neighbour), 0.0)
    pair_mass = sum(f for (a, b), f in v.items() if a != b and a in placed and b in placed)
    return {"scope": "85 placed symbols on 90 main-block slots (30 keys × base/Shift/AltGr), J0 with free layers",
            "E1_min": e1_min, "min_B": min_b, "placed_pair_mass": pair_mass, "LB0": e1_min + min_b * pair_mass}


def actions_of(assignment: dict[str, tuple[str, str]]) -> dict[str, Action]:
    return {unit: Action(key, layer, unit) for unit, (key, layer) in assignment.items()}


def english_cross_check() -> dict:
    rows, worst = [], 0.0
    for row in load_published()["comparison_table"]["rows"]:
        layout = load_layout(resource(f"layout_full/{row['layout']}.keyb"), resource("config/" + row["config"]))
        char_freqs, bigram_freqs = load_frequency_file(layout.alphabet(), resource("freq/en_books.freq"))
        port = perform_analysis(layout, char_freqs, bigram_freqs).effort_totals()
        model, assignment = english_model_and_assignment(layout)
        u, v = load_english_frequencies(resource("freq/en_books.freq"), layout.alphabet())
        mine = score_units(assignment, u, v, model)
        diff = max(abs(port["total"] - mine["J0"]), abs(port["base"] - mine["E1"]), abs(port["bigram"] - mine["E2"]))
        worst = max(worst, diff)
        rows.append({"label": row["label"], "config": row["config"], "port_total": port["total"],
                     "scorer_J0": mine["J0"], "max_abs_difference": diff})
    return {"frequency": "freq/en_books.freq", "rows": rows, "max_abs_difference": worst,
            "tolerance": 1e-6, "pass": worst <= 1e-6}


def word_list_texts() -> dict[str, list[str]]:
    out = {}
    for relative in WORD_LISTS:
        words = []
        for line in kala_path(relative).read_text(encoding="utf-8").splitlines():
            fields = line.split("\t")
            if not fields or not fields[0]:
                continue
            words.append(fields[1] if relative.split("/")[-1].startswith("err_") and len(fields) > 1 else fields[0])
        out[relative] = words
    return out


def round_trip_check(keymaps: list[KeyMap], texts: dict[str, list[str]], units: UnitSet) -> dict:
    """NFC(decode(encode(T))) == NFC(T) for every text, per key map. Texts
    with characters a map cannot produce are counted separately (their
    covered parts still have to round-trip)."""
    out = {}
    for keymap in keymaps:
        per_source = {}
        for source, items in texts.items():
            ok = fail = escaped = 0
            failures = []
            for text in items:
                good, escapes = keymap.round_trip(text)
                escaped += escapes > 0
                if good:
                    ok += 1
                else:
                    fail += 1
                    if len(failures) < 10:
                        failures.append(text)
            per_source[source] = {"texts": len(items), "round_trip_ok": ok, "failures": fail,
                                  "texts_with_unproducible_characters": escaped, "failure_examples": failures}
        out[keymap.name] = per_source
    return out


def heldout_sample(record_name: str, limit: int) -> list[str]:
    table = PROJECT_ROOT / frequency_record(record_name)["token_table"]
    return [token for _, (token, _count) in zip(range(limit), freq.read_token_table(table))]


def cluster_statistics(record_name: str) -> dict:
    """Consonant clusters (C্C…) in running text vs Kala's conjunct list."""
    table = PROJECT_ROOT / frequency_record(record_name)["token_table"]
    clusters = Counter()
    for token, count in freq.read_token_table(table):
        pieces = segment(token)
        i = 0
        while i < len(pieces):
            if is_consonant_unit(pieces[i]) and i + 2 < len(pieces) and pieces[i + 1] == HASANT \
                    and is_consonant_unit(pieces[i + 2]):
                j = i
                while j + 2 < len(pieces) and pieces[j + 1] == HASANT and is_consonant_unit(pieces[j + 2]):
                    j += 2
                clusters["".join(pieces[i:j + 1])] += count
                i = j + 1
            else:
                i += 1
    kala = {nfc(e) for e in json.loads(kala_path("data/bn/Alphabet.json").read_text(encoding="utf-8"))["conjuncts"]}
    kala_valid = {e for e in kala if segment_consonants(e)}
    total = sum(clusters.values())
    in_kala = sum(c for k, c in clusters.items() if k in kala_valid)
    return {"corpus": record_name, "cluster_tokens": total, "distinct_clusters": len(clusters),
            "share_of_cluster_occurrences_in_kala_list": in_kala / total if total else None,
            "kala_valid_clusters_never_seen": len(kala_valid - set(clusters)),
            "top": [[k, c] for k, c in clusters.most_common(40)],
            "frequent_missing_from_kala": [[k, c] for k, c in clusters.most_common(400) if k not in kala_valid][:25]}


def score_record(keymap: KeyMap, record_name: str, model: KeyModel) -> dict:
    record = frequency_record(record_name)
    table = PROJECT_ROOT / record["token_table"]
    result = score_tokens(keymap, freq.read_token_table(table), record["N"], model)
    non_space = record["N"] - record["space_units"]
    result["keystrokes_per_non_space_unit"] = result["keystrokes_excluding_space"] / non_space
    result["J0_per_non_space_unit"] = result["J0"] * record["N"] / non_space
    return result


def run_evaluation() -> dict:
    started = time.time()
    inventory = load_inventory()
    units = UnitSet.from_inventory(inventory)
    placed = set(units.placed)
    models = {"unrounded": KeyModel.from_grid(ANSI_GRID), "one_decimal": KeyModel.from_grid(ANSI_GRID, decimals=1)}
    model = models["unrounded"]
    # Typists learn UniJoy with traditional fingering (decision D3), so baselines also get that grid.
    baseline_models = {**models, "traditional_unrounded": KeyModel.from_grid(ANSI_TRADITIONAL_GRID)}
    names = list(corpus_files())
    records = {name: frequency_record(name) for name in names}
    opt = json.loads(OPTIMIZATION_FREQUENCIES.read_text(encoding="utf-8"))
    u = opt["u"]
    v = {(a, b): f for a, b, f in opt["v"]}

    unijoy = {grid: unijoy_keymap(m) for grid, m in baseline_models.items()}
    references = {"unigram-greedy (E1 minimum)": unigram_greedy_assignment(u, placed, model),
                  "base-layer-first frequency greedy": base_first_greedy_assignment(u, placed, model),
                  f"random (seed {REFERENCE_SEED})": random_assignment(placed, REFERENCE_SEED)}

    result: dict = {"inventory": {"file": relative_to_project(INVENTORY_FILE), "counts": inventory["counts"],
                                  "symbol_list_sha256": inventory["symbol_list_sha256"]}}
    print("English cross-check ...")
    result["english_cross_check"] = english_cross_check()

    print("Round trips ...")
    texts = word_list_texts()
    heldout_name = next(n for n in names if n.endswith("/heldout") and n.startswith("bnwiki"))
    texts[f"{heldout_name} token types (top 200000)"] = heldout_sample(heldout_name, 200_000)
    reference_map = single_action_keymap("Bangla-DH reference (base-layer-first greedy)",
                                         references["base-layer-first frequency greedy"], effort=model.effort)
    result["round_trip"] = round_trip_check([unijoy["unrounded"], reference_map], texts, units)

    print("Baselines ...")
    baselines = {}
    for name in names:
        baselines[name] = {grid: score_record(unijoy[grid], name, baseline_models[grid]) for grid in baseline_models}
        print(f"  UniJoy {name}: J0 {baselines[name]['unrounded']['J0']:.4f}")
    result["unijoy"] = {"source": UNIJOY, "sha256": sha256_file(kala_path(UNIJOY)),
                        "bijoy_file_identical_to_unijoy": bijoy_matches_unijoy(),
                        "producible_units": sorted(placed & _producible_units(unijoy["unrounded"])),
                        "placed_units_not_producible": sorted(placed - _producible_units(unijoy["unrounded"])),
                        "scores": baselines}

    print("Reference layouts and consistency ...")
    refs = {}
    for label, assignment in references.items():
        actions = actions_of(assignment)
        entry = {"assignment": {s: f"{k}/{layer}" for s, (k, layer) in sorted(assignment.items(), key=lambda kv: (LAYERS.index(kv[1][1]), MAIN_BLOCK.index(kv[1][0])))}}
        entry["optimization_frequencies"] = {g: score_units(actions, u, v, m) for g, m in models.items()}
        per_corpus = {}
        for name in names:
            ru, rv = freq.frequencies(records[name])
            per_corpus[name] = score_units(actions, ru, rv, model)
        entry["by_corpus"] = per_corpus
        refs[label] = entry
    result["reference_layouts"] = refs

    # Three routes on the held-out split must agree for single-action layouts.
    label = "base-layer-first frequency greedy"
    assignment = references[label]
    by_tables = refs[label]["by_corpus"][heldout_name]["J0"]
    by_tokens = score_record(single_action_keymap(label, assignment, effort=model.effort), heldout_name, model)["J0"]
    # The verifier maps units to keys; layers do not change J0, and two units
    # sharing a key are different actions on that key in both scorers.
    by_verifier = verify_j0([corpus_files()[heldout_name]], {s: k for s, (k, _) in assignment.items()},
                            INVENTORY_FILE, ANSI_GRID)
    difference = max(abs(by_tokens - by_tables), abs(by_verifier["J0"] - by_tables)) / by_tables
    result["scorer_consistency"] = {
        "corpus": heldout_name, "layout": label, "J0_unit_tables": by_tables, "J0_token_table": by_tokens,
        "J0_independent_verifier": by_verifier["J0"], "verifier_N": by_verifier["N"],
        "table_N": records[heldout_name]["N"], "max_relative_difference": difference,
        "pass": difference < 1e-9 and by_verifier["N"] == records[heldout_name]["N"]}
    result["lower_bound_0"] = lower_bound_0(u, v, placed, model)
    result["clusters"] = cluster_statistics(names[0])
    result["models"] = {g: m.describe() for g, m in baseline_models.items()}
    result["seconds"] = round(time.time() - started, 1)
    return result


def _producible_units(keymap: KeyMap) -> set[str]:
    """Placed units the map can type (directly or through a sequence)."""
    out = set()
    for output in keymap.producible():
        out.update(segment(output))
    return out


def manifest(outputs: list[Path], evaluation: dict | None) -> dict:
    head, clean = repo_state()
    inputs = {relative_to_project(p): sha256_file(p)
              for p in (INVENTORY_FILE, corpus_build.CORPUS_CONFIG, ANSI_GRID, ANSI_TRADITIONAL_GRID)}
    inputs.update({f"kala:{p}": sha256_file(kala_path(p)) for p in
                   ["data/bn/Alphabet.json", "kala/layout/bn/Alphabet.json", "kala/layout/bn/conjuncts.json",
                    UNIJOY, BIJOY] + WORD_LISTS})
    corpus = json.loads((RESULTS / "corpus-manifest.json").read_text(encoding="utf-8"))
    for name, domain in corpus["domains"].items():
        inputs[f"{domain['source']['path']}@{domain['source']['commit'][:12]}"] = domain["source"]["sha256"]
        for split, info in domain["splits"].items():
            inputs[info["path"]] = info["sha256"]
    for path in sorted(FREQUENCIES.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if "token_table" in record:
            inputs[record["token_table"]] = record["token_table_sha256"]
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "repo_commit": head, "working_tree_clean": clean,
            "parameters": {"reference_seed": REFERENCE_SEED, "effort_grid": relative_to_project(ANSI_GRID),
                           "grids": ["unrounded", "one decimal (half-up)"], "objective": "J0 (M, Q off: D2 default)",
                           "middle_index_benefit": "kept (D6 default)"},
            "inputs": inputs, "outputs": hash_outputs(outputs)}
