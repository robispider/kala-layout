"""Phase 3 driver: problem file, per-style keystroke tables, seeded search,
evaluation.

Steps (each a CLI command, see ``cli.py``):

``build-problem``     data/problem-v1.json (task 1)
``style-frequency``   results/phase3/frequencies/<style>-<corpus>.json (task 2)
``optimize``          results/phase3/search/<style>.json (task 4)
``evaluate-phase3``   checks, J1 baselines, held-out comparison, REPORT.md,
                      phase3.json, run-manifest.json (tasks 2, 3, 5)

Corpus: Bangla Wikipedia only (D4, 10 October 2026): the search uses
bnwiki/train, the comparison adds bnwiki/heldout. BanLemma is not used.
"""
from __future__ import annotations

import datetime as _dt
import json
import multiprocessing as mp
import platform
import random
import statistics
import time
from pathlib import Path

from . import __version__
from .bangla.grammar import Action, UnitSet, nfc
from .bangla.inventory import INVENTORY_FILE, load_inventory
from .bangla.styles import NO_KEY, STYLES, THIRD_LAYER, Style, load_styles
from .paths import repo_state, PROJECT_ROOT, RESULTS_ROOT, hash_outputs, kala_path, relative_to_project, write_json
from .phase2 import WORD_LISTS, frequency_record, heldout_sample, score_record, word_list_texts
from .reference import sha256_file
from .scoring.j0 import score_units
from .scoring.layouts import UNIJOY, unijoy_keymap
from .scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from .scoring.verify import verify_style
from .search import keystrokes
from .search.anneal import Instance, State, iterated_local_search, run as run_search
from .search.problem import (PROBLEM_FILE, build_problem, check_problem, load_problem, parse_slot, slot_name, slots)

RESULTS = RESULTS_ROOT / "phase3"
FREQUENCIES = RESULTS / "frequencies"
SEARCH = RESULTS / "search"
CORPORA = ("bnwiki/train", "bnwiki/heldout")
TRAIN = "bnwiki/train"
HELDOUT = "bnwiki/heldout"
FIRST_SEED = 20261011
SEARCH_SETTINGS = {"seeds": 64, "sa_steps": 1_000_000, "t_ratio": 1e-3, "ils_iterations": 1000,
                   "ils_strength": [2, 6], "objective": "J1", "frequencies": TRAIN,
                   "confirmation": {"seeds": 6, "ils_iterations": 5000, "strengths": [[2, 6], [4, 10], [8, 16]]},
                   "starts": "the first seed starts from the frequency-sorted greedy layout, the others from "
                             "random permutations"}


# --- task 1: problem ------------------------------------------------------------

def run_problem() -> list[Path]:
    problem = build_problem()
    problems = check_problem(problem)
    if problems:
        raise ValueError("; ".join(problems))
    return [write_json(PROBLEM_FILE, problem)]


def problem_fixed(problem: dict) -> dict[str, tuple[str, str]]:
    return {label: parse_slot(slot) for label, slot in problem["fixed"].items()}


# --- task 2: per-style keystroke tables -------------------------------------------

def frequency_file(style: str, corpus: str) -> Path:
    return FREQUENCIES / f"{style}-{corpus.replace('/', '-')}.json"


def run_style_frequency(workers: int | None = None) -> list[Path]:
    written = []
    for corpus in CORPORA:
        record = frequency_record(corpus)
        for style in STYLES:
            table = keystrokes.compute(style, record, PROJECT_ROOT, workers)
            table["corpus"] = corpus
            written.append(write_json(frequency_file(style, corpus), table, indent=1))
            non_space = table["N"] - table["space_units"]
            print(f"{style} {corpus}: {table['keystrokes_excluding_space'] / non_space:.4f} keystrokes per "
                  f"non-space unit, {table['escaped_unit_count']} escaped units")
    return written


def style_frequencies(style: str, corpus: str) -> tuple[dict, dict, dict]:
    record = json.loads(frequency_file(style, corpus).read_text(encoding="utf-8"))
    u, v = keystrokes.frequencies(record)
    return record, u, v


# --- task 4: search -----------------------------------------------------------------

def instance(style: str, model: KeyModel, corpus: str = TRAIN, objective: str = "J1",
             problem: dict | None = None) -> Instance:
    problem = problem or load_problem()
    _, u, v = style_frequencies(style, corpus)
    return Instance(problem["styles"][style]["searched_symbols"], slots(), problem_fixed(problem), u, v, model,
                    objective)


_instances: dict[str, Instance] = {}


def _search_init() -> None:
    model = KeyModel.from_grid(ANSI_GRID)
    problem = load_problem()
    for style in STYLES:
        _instances[style] = instance(style, model, problem=problem)


def _search_job(job: tuple[str, int, str, dict]) -> tuple[str, dict]:
    style, seed, start, s = job
    result = run_search(_instances[style], seed, start, s["sa_steps"], s["t_ratio"], s["ils_iterations"],
                        tuple(s["ils_strength"]))
    result["layout"] = [_instances[style].labels[result["perm"].index(k)] for k in range(_instances[style].n)]
    del result["perm"]
    return style, result


def _confirm_job(job: tuple[str, int, list[int], list[int], int]) -> tuple[str, dict]:
    """Iterated local search from a style's best layout with stronger
    perturbations: a check that the best found is not easily improved."""
    style, seed, layout_perm, strength, iterations = job
    inst = _instances[style]
    state = State(inst, layout_perm)
    start = state.score
    iterated_local_search(state, random.Random(seed), iterations, tuple(strength))
    final = inst.score(state.perm)
    return style, {"seed": seed, "strength": strength, "iterations": iterations, "start": start, "final": final,
                   "improved": final < start - 1e-12,
                   "layout": [inst.labels[state.perm.index(k)] for k in range(inst.n)]}


def run_optimize(styles=STYLES, seeds: int | None = None, sa_steps: int | None = None,
                 ils_iterations: int | None = None, workers: int | None = None) -> list[Path]:
    settings = dict(SEARCH_SETTINGS)
    for name, value in (("seeds", seeds), ("sa_steps", sa_steps), ("ils_iterations", ils_iterations)):
        if value is not None:
            settings[name] = value
    if ils_iterations is not None:
        settings["confirmation"] = {**settings["confirmation"], "ils_iterations": 5 * ils_iterations}
    jobs = [(style, FIRST_SEED + k, "greedy" if k == 0 else "random", settings)
            for style in styles for k in range(settings["seeds"])]
    runs: dict[str, list[dict]] = {style: [] for style in styles}
    started = time.time()
    with mp.Pool(workers or max(1, min(24, mp.cpu_count() - 4)), initializer=_search_init) as pool:
        for done, (style, result) in enumerate(pool.imap_unordered(_search_job, jobs), 1):
            runs[style].append(result)
            if done % 16 == 0 or done == len(jobs):
                print(f"{done}/{len(jobs)} runs, {time.time() - started:.0f} s", flush=True)
        confirm = settings["confirmation"]
        confirm_jobs = []
        for style in styles:
            inst = instance(style, KeyModel.from_grid(ANSI_GRID))
            best = min(runs[style], key=lambda r: (r["best_score"], r["seed"]))
            perm = inst.perm_of({label: slot for label, slot in zip(best["layout"], inst.slots)})
            for k in range(confirm["seeds"]):
                strength = confirm["strengths"][k % len(confirm["strengths"])]
                confirm_jobs.append((style, FIRST_SEED + 1000 + k, perm, strength, confirm["ils_iterations"]))
        confirmations: dict[str, list[dict]] = {style: [] for style in styles}
        for style, result in pool.imap_unordered(_confirm_job, confirm_jobs):
            confirmations[style].append(result)
        print(f"confirmation done, {time.time() - started:.0f} s", flush=True)
    problem = load_problem()
    written = []
    for style in styles:
        style_runs = sorted(runs[style], key=lambda r: r["seed"])
        confirmed = sorted(confirmations[style], key=lambda r: r["seed"])
        best = min(style_runs + confirmed, key=lambda r: (r.get("best_score", r.get("final")), r["seed"]))
        best = {"seed": best["seed"], "best_score": best.get("best_score", best.get("final")), "layout": best["layout"]}
        scores = [r["best_score"] for r in style_runs]
        record = {
            "style": style, "description": problem["styles"][style]["description"], "settings": settings,
            "frequencies": relative_to_project(frequency_file(style, TRAIN)),
            "frequencies_sha256": sha256_file(frequency_file(style, TRAIN)),
            "problem_sha256": problem["problem_sha256"], "effort_grid": relative_to_project(ANSI_GRID),
            "slots": problem["slots"],
            "best": {"seed": best["seed"], "J1": best["best_score"],
                     "layout": {label: slot for label, slot in zip(best["layout"], problem["slots"])}},
            "statistics": {"runs": len(scores), "best": min(scores), "median": statistics.median(scores),
                           "worst": max(scores),
                           "runs_reaching_best": sum(s <= min(scores) + 1e-9 for s in scores),
                           "distinct_best_layouts": len({tuple(r["layout"]) for r in style_runs
                                                         if r["best_score"] <= min(scores) + 1e-9}),
                           "seconds_total": round(sum(r["seconds"] for r in style_runs), 1)},
            "confirmation": [{k: r[k] for k in ("seed", "strength", "iterations", "start", "final", "improved")}
                             for r in confirmed],
            "runs": style_runs,
        }
        written.append(write_json(SEARCH / f"{style}.json", record, indent=1))
        print(f"style {style}: best J1 {min(scores):.6f} (seed {best['seed']}), "
              f"{record['statistics']['runs_reaching_best']}/{len(scores)} runs reach it; confirmation improved it: "
              f"{any(r['improved'] for r in confirmed)}", flush=True)
    return written


def best_layout(style: str) -> dict[str, tuple[str, str]]:
    record = json.loads((SEARCH / f"{style}.json").read_text(encoding="utf-8"))
    return {label: parse_slot(slot) for label, slot in record["best"]["layout"].items()}


# --- evaluation -----------------------------------------------------------------------

def actions_of(layout: dict[str, tuple[str, str]]) -> dict[str, Action]:
    return {label: Action(key, layer, label) for label, (key, layer) in layout.items()}


def score_layout(style: str, layout: dict[str, tuple[str, str]], corpus: str, model: KeyModel,
                 fixed: dict[str, tuple[str, str]]) -> dict:
    record, u, v = style_frequencies(style, corpus)
    result = score_units(actions_of({**layout, **fixed}), u, v, model)
    non_space = record["N"] - record["space_units"]
    result["keystrokes_per_non_space_unit"] = record["keystrokes_excluding_space"] / non_space
    result["escaped_units"] = record["escaped_unit_count"]
    return result


def style_round_trips(styles: dict[str, Style], texts: dict[str, list[str]]) -> dict:
    out = {}
    for name, style in styles.items():
        per_source = {}
        for source, items in texts.items():
            ok = escaped = 0
            failures = []
            for text in items:
                good, escapes = style.round_trip(text)
                ok += good
                escaped += escapes > 0
                if not good and len(failures) < 10:
                    failures.append(text)
            per_source[source] = {"texts": len(items), "round_trip_ok": ok, "failures": len(items) - ok,
                                  "texts_with_escapes": escaped, "failure_examples": failures}
        out[name] = per_source
    return out


def style_examples(styles: dict[str, Style]) -> dict:
    words = ["আমি", "বই", "দই", "বউ", "কাজ", "এই", "ক্ষমতা", "উৎসর্গ", "তিনিই", "প্রতিষ্ঠান"]
    return {name: {w: [s if isinstance(s, str) else f"escape {s.char}" for s in style.encode(nfc(w))]
                   for w in words} for name, style in styles.items()}


def lower_bound_0(inst: Instance) -> dict:
    """Elementary bound (RESEARCH_SPEC 8.3) for one style's 52-slot J1
    problem: the fixed labels' constant, the rearrangement minimum of
    Σ u_i C(slot), and every remaining pair at the smallest penalty."""
    e1_min = sum(a * b for a, b in zip(sorted(inst.u, reverse=True), sorted(inst.C)))
    min_b = min(min(row) for row in inst.B)
    pair_mass = sum(sum(row) for row in inst.W) / 2
    fixed_pair_terms = sum(min(inst.U[i][s] - inst.u[i] * inst.C[s] for s in range(inst.n)) for i in range(inst.n))
    return {"scope": "52 searched labels on the 52 v1 slots, fixed keys as in the problem file, J1, "
                     "training frequencies", "E1_min": e1_min, "min_B": min_b, "searched_pair_mass": pair_mass,
            "fixed_constant": inst.const, "fixed_pair_terms_min": fixed_pair_terms,
            "LB0": inst.const + e1_min + min(0.0, min_b) * pair_mass + fixed_pair_terms}


def _verify_job(job) -> tuple[str, dict]:
    style, corpus_files, layout = job
    return style, verify_style([Path(p) for p in corpus_files], style, layout, INVENTORY_FILE, ANSI_GRID)


def corpus_file(name: str) -> Path:
    manifest = json.loads((RESULTS_ROOT / "phase2" / "corpus-manifest.json").read_text(encoding="utf-8"))
    domain, split = name.split("/")
    return PROJECT_ROOT / manifest["domains"][domain]["splits"][split]["path"]


def run_evaluation() -> dict:
    started = time.time()
    inventory = load_inventory()
    problem = load_problem()
    styles = load_styles(inventory)
    fixed = problem_fixed(problem)
    models = {"unrounded": KeyModel.from_grid(ANSI_GRID), "one_decimal": KeyModel.from_grid(ANSI_GRID, decimals=1)}
    model = models["unrounded"]
    result: dict = {"problem": {"file": relative_to_project(PROBLEM_FILE), "sha256": sha256_file(PROBLEM_FILE),
                                "problem_sha256": problem["problem_sha256"],
                                "matches_build": problem == build_problem(inventory),
                                "consistency_problems": check_problem(problem, inventory)}}

    print("Round trips ...")
    texts = word_list_texts()
    texts[f"{HELDOUT} token types (top 200000)"] = heldout_sample(HELDOUT, 200_000)
    result["round_trip"] = style_round_trips(styles, texts)
    result["examples"] = style_examples(styles)

    print("Keystroke tables ...")
    tables = {}
    for style in STYLES:
        for corpus in CORPORA:
            record, _, _ = style_frequencies(style, corpus)
            non_space = record["N"] - record["space_units"]
            tables[f"{style} {corpus}"] = {
                "N": record["N"], "keystrokes_per_non_space_unit": record["keystrokes_excluding_space"] / non_space,
                "escaped_units": record["escaped_unit_count"], "escaped_share": record["escaped_unit_count"] / record["N"],
                "escaped_top": list(record["escaped_units"].items())[:15],
                "rule_escapes": sum(c for unit, c in record["escaped_units"].items()
                                    if unit not in THIRD_LAYER and unit not in NO_KEY),
                "token_table_sha256": record["token_table_sha256"]}
    result["keystroke_tables"] = tables

    print("UniJoy under J1 ...")
    unijoy_models = {**models, "traditional_unrounded": KeyModel.from_grid(ANSI_TRADITIONAL_GRID)}
    phase2 = json.loads((RESULTS_ROOT / "phase2" / "phase2.json").read_text(encoding="utf-8"))
    unijoy = {}
    for corpus in CORPORA:
        unijoy[corpus] = {}
        for grid, m in unijoy_models.items():
            scored = score_record(unijoy_keymap(m), corpus, m)
            scored.pop("top_penalty_pairs", None)
            scored.pop("escaped_top", None)
            scored["phase2_J0"] = phase2["unijoy"]["scores"][corpus][grid]["J0"]
            unijoy[corpus][grid] = scored
    result["unijoy"] = {"source": UNIJOY, "sha256": sha256_file(kala_path(UNIJOY)), "scores": unijoy,
                        "J0_matches_phase2": all(abs(s["J0"] - s["phase2_J0"]) < 1e-12
                                                 for c in unijoy.values() for s in c.values())}

    print("Search results and scorer checks ...")
    searches, layouts, scores, checks, bounds = {}, {}, {}, {}, {}
    for style in STYLES:
        record = json.loads((SEARCH / f"{style}.json").read_text(encoding="utf-8"))
        searches[style] = {k: record[k] for k in ("settings", "statistics", "frequencies_sha256", "problem_sha256")}
        searches[style]["best"] = {"seed": record["best"]["seed"], "J1": record["best"]["J1"]}
        searches[style]["confirmation"] = record["confirmation"]
        searches[style]["runs"] = [{k: r[k] for k in ("seed", "start", "start_score", "after_annealing",
                                                      "after_descent", "best_score", "seconds")}
                                   for r in record["runs"]]
        layout = best_layout(style)
        layouts[style] = {label: slot_name(slot) for label, slot in layout.items()}
        scores[style] = {corpus: {grid: score_layout(style, layout, corpus, m, fixed) for grid, m in models.items()}
                         for corpus in CORPORA}
        inst = instance(style, model, problem=problem)
        inst_j0 = instance(style, model, objective="J0", problem=problem)
        perm = inst.perm_of(layout)
        checks[style] = {"instance_J1": inst.score(perm), "table_J1": scores[style][TRAIN]["unrounded"]["J1"],
                         "instance_J0": inst_j0.score(perm), "table_J0": scores[style][TRAIN]["unrounded"]["J0"],
                         "search_record_J1": record["best"]["J1"]}
        bounds[style] = lower_bound_0(inst)
        bounds[style]["max_slot_cost"] = max(inst.C)
    result["search"] = searches
    result["best_layouts"] = layouts
    result["scores"] = scores
    result["lower_bound_0"] = bounds

    print("Independent verifier on the held-out split ...")
    jobs = [(style, [str(corpus_file(HELDOUT))], {**layouts[style], **problem["fixed"]}) for style in STYLES]
    with mp.Pool(len(jobs)) as pool:
        verified = dict(pool.map(_verify_job, jobs))
    for style in STYLES:
        table = scores[style][HELDOUT]["unrounded"]
        record, _, _ = style_frequencies(style, HELDOUT)
        v = verified[style]
        difference = max(abs(v["J1"] - table["J1"]), abs(v["J0"] - table["J0"])) / table["J1"]
        checks[style].update({"verifier": v, "verifier_vs_tables_max_relative_difference": difference,
                              "verifier_pass": difference < 1e-9 and v["N"] == record["N"]
                              and v["escaped_units"] == record["escaped_unit_count"]
                              and v["keystrokes_excluding_space"] == record["keystrokes_excluding_space"]})
        c = checks[style]
        c["instance_pass"] = (abs(c["instance_J1"] - c["table_J1"]) < 1e-9 and abs(c["instance_J0"] - c["table_J0"]) < 1e-9
                              and abs(c["search_record_J1"] - c["table_J1"]) < 1e-9)
    result["checks"] = checks
    result["models"] = {g: m.describe() for g, m in unijoy_models.items()}
    result["seconds"] = round(time.time() - started, 1)
    return result


def acceptance(ev: dict) -> dict[str, bool]:
    return {
        "problem file matches the inventory and the style definitions": ev["problem"]["matches_build"]
        and not ev["problem"]["consistency_problems"],
        "NFC round trip of every style on the word lists and held-out tokens": all(
            s["failures"] == 0 for style in ev["round_trip"].values() for s in style.values()),
        "UniJoy J0 unchanged from Phase 2": ev["unijoy"]["J0_matches_phase2"],
        "search objective equals the table scorer (J0 and J1)": all(c["instance_pass"] for c in ev["checks"].values()),
        "independent verifier equals the table scorer on the held-out split": all(
            c["verifier_pass"] for c in ev["checks"].values()),
    }


def manifest(outputs: list[Path]) -> dict:
    head, clean = repo_state()
    inputs = {relative_to_project(p): sha256_file(p) for p in (INVENTORY_FILE, PROBLEM_FILE, ANSI_GRID, ANSI_TRADITIONAL_GRID)}
    inputs.update({f"kala:{p}": sha256_file(kala_path(p)) for p in [UNIJOY] + WORD_LISTS})
    for corpus in CORPORA:
        record = frequency_record(corpus)
        inputs[record["token_table"]] = record["token_table_sha256"]
        inputs[relative_to_project(corpus_file(corpus))] = sha256_file(corpus_file(corpus))
    inputs["results/phase2/phase2.json"] = sha256_file(RESULTS_ROOT / "phase2" / "phase2.json")
    seeds = {style: [FIRST_SEED, FIRST_SEED + SEARCH_SETTINGS["seeds"] - 1] for style in STYLES}
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "repo_commit": head, "working_tree_clean": clean,
            "parameters": {"objective": "J1 (M = other hand's Shift key from the model grid, lambda_m = 1, Q = 0; D2)",
                           "effort_grid": relative_to_project(ANSI_GRID), "fingering": "model-optimal (D3 default)",
                           "middle_index_benefit": "kept (D6 default)", "corpus": "Bangla Wikipedia only (D4)",
                           "search": SEARCH_SETTINGS, "seed_range_per_style": seeds},
            "inputs": inputs, "outputs": hash_outputs(outputs)}
