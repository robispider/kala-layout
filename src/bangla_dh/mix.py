"""Mixed-corpus search: the Phase 3 search on a weighted mix of training texts.

Owner request of 10 October 2026: search styles A and D (the two styles going
to typing tests) on Wikipedia and news text together, instead of Wikipedia
only (D4).

Every keystroke table gives frequencies per unit of its own text
(``u = label_counts / N``, ``v = pair_counts / N``), so the mixed frequencies
``u = Σ_c w_c u_c`` and ``v = Σ_c w_c v_c`` (weights summing to one) give

    J_mix(L) = Σ_c w_c J_c(L)

exactly: the mix weights each text by its weight, not by its size
(bnwiki/train has 390 M units, newspaper/train 718 M). Only training splits
can be mixed; the held-out splits stay unseen and score the result.

Search per style, all on the mixed objective:

* ``seeds`` runs of the Phase 3 search (annealing, descent, iterated local
  search), the first from the greedy layout, the others random;
* ``polish``: iterated local search from every earlier best layout of the
  style (Phase 3 and the news cross-check) at three perturbation strengths;
* ``confirmation``: the same from the best of all of the above.

Output ``results/mix-search/``: ``search/<style>.json`` (every run with its
layout), ``mix-search.json`` (held-out scores of the mixed, Wikipedia and news
layouts, checks) and ``run-manifest.json``. Every layout is "best found".
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
from .crosscheck import RESULTS as CROSSCHECK, WIKI, news_best_layout, news_corpora, score_style, style_record
from .paths import repo_state, RESULTS_ROOT, hash_outputs, relative_to_project, write_json
from .phase3 import RESULTS as PHASE3, SEARCH_SETTINGS, best_layout, problem_fixed
from .reference import sha256_file
from .scoring.model import ANSI_GRID, KeyModel
from .search.anneal import Instance, State, iterated_local_search, run as run_search
from .search.problem import PROBLEM_FILE, load_problem, slots

RESULTS = RESULTS_ROOT / "mix-search"
SEARCH = RESULTS / "search"
FIRST_SEED = 20261101
DEFAULT_STYLES = ("A", "D")
DEFAULT_WEIGHTS = {"bnwiki/train": 0.5, "newspaper/train": 0.5}
HELDOUT = ("bnwiki/heldout", "newspaper/heldout", "bard-novel/heldout")
POLISH_STRENGTHS = [[2, 6], [4, 10], [8, 16]]  # polish and confirmation: 5 x the run's ILS iterations each


def parse_weights(items: list[str] | None) -> dict[str, float]:
    """``["bnwiki/train=1", "newspaper/train=1"]`` → weights summing to one."""
    if not items:
        return dict(DEFAULT_WEIGHTS)
    known = {name for name in (*WIKI, *news_corpora()) if name.endswith("/train")}
    raw = {}
    for item in items:
        name, _, value = item.partition("=")
        if name not in known:
            raise ValueError(f"{name}: not a training split (choose from {', '.join(sorted(known))})")
        raw[name] = float(value or 1)
        if raw[name] <= 0:
            raise ValueError(f"{name}: weight must be positive")
    total = sum(raw.values())
    return {name: w / total for name, w in raw.items()}


def mixed_frequencies(style: str, weights: dict[str, float]) -> tuple[dict, dict]:
    u: dict[str, float] = {}
    v: dict[tuple[str, str], float] = {}
    for name, w in weights.items():
        _, uc, vc = style_record(style, name)
        for label, f in uc.items():
            u[label] = u.get(label, 0.0) + w * f
        for pair, f in vc.items():
            v[pair] = v.get(pair, 0.0) + w * f
    return u, v


def mix_instance(style: str, weights: dict[str, float], model: KeyModel, problem: dict) -> Instance:
    u, v = mixed_frequencies(style, weights)
    return Instance(problem["styles"][style]["searched_symbols"], slots(), problem_fixed(problem), u, v, model, "J1")


def earlier_layouts(style: str) -> dict[str, dict[str, tuple[str, str]]]:
    """Best layouts of the earlier searches, the starts of the polish runs."""
    found = {}
    for name, load in (("phase3 (bnwiki)", best_layout), ("crosscheck (newspaper)", news_best_layout)):
        try:
            found[name] = load(style)
        except FileNotFoundError:
            pass
    return found


_instances: dict[str, Instance] = {}


def _init(styles: list[str], weights: dict[str, float]) -> None:
    model = KeyModel.from_grid(ANSI_GRID)
    problem = load_problem()
    for style in styles:
        _instances[style] = mix_instance(style, weights, model, problem)


def _layout(inst: Instance, perm: list[int]) -> list[str]:
    return [inst.labels[perm.index(k)] for k in range(inst.n)]


def _search_job(job) -> tuple[str, str, dict]:
    style, seed, start, s = job
    inst = _instances[style]
    result = run_search(inst, seed, start, s["sa_steps"], s["t_ratio"], s["ils_iterations"], tuple(s["ils_strength"]))
    result["layout"] = _layout(inst, result.pop("perm"))
    return style, "search", result


def _ils_job(job) -> tuple[str, str, dict]:
    kind, style, seed, origin, perm, strength, iterations = job
    inst = _instances[style]
    started = time.time()
    state = State(inst, perm)
    start = state.score
    iterated_local_search(state, random.Random(seed), iterations, tuple(strength))
    final = inst.score(state.perm)
    return style, kind, {"seed": seed, "origin": origin, "strength": strength, "iterations": iterations,
                         "start": start, "final": final, "improved": final < start - 1e-12,
                         "seconds": round(time.time() - started, 2), "layout": _layout(inst, state.perm)}


def _ils_jobs(kind: str, style: str, origin: str, perm: list[int], first_seed: int, iterations: int) -> list[tuple]:
    return [(kind, style, first_seed + k, origin, perm, strength, iterations)
            for k, strength in enumerate(POLISH_STRENGTHS)]


def _score_of(r: dict) -> float:
    return r["best_score"] if "best_score" in r else r["final"]


def run_optimize(styles=DEFAULT_STYLES, weights: dict[str, float] | None = None, seeds: int = 256,
                 sa_steps: int | None = None, ils_iterations: int | None = None,
                 workers: int | None = None, out: Path | None = None, first_seed: int = FIRST_SEED,
                 use_earlier: bool = True) -> list[Path]:
    """``out`` (inside the project) receives the results instead of ``results/mix-search``;
    ``first_seed`` shifts every seed; ``use_earlier=False`` leaves out the polish runs that start from the
    Phase 3 and news layouts, so the result comes from the seeded searches alone."""
    out = Path(out) if out else RESULTS
    search_dir = out / "search"
    weights = weights or dict(DEFAULT_WEIGHTS)
    styles = list(styles)
    settings = {k: v for k, v in SEARCH_SETTINGS.items() if k not in ("confirmation", "frequencies")}
    settings["seeds"], settings["frequencies"] = seeds, weights
    for name, value in (("sa_steps", sa_steps), ("ils_iterations", ils_iterations)):
        if value is not None:
            settings[name] = value
    polish = {"ils_iterations": 5 * settings["ils_iterations"], "strengths": POLISH_STRENGTHS}
    settings["polish"] = settings["confirmation"] = polish
    problem = load_problem()
    model = KeyModel.from_grid(ANSI_GRID)
    local = {style: mix_instance(style, weights, model, problem) for style in styles}
    jobs = [(style, first_seed + k, "greedy" if k == 0 else "random", settings)
            for style in styles for k in range(seeds)]
    polish_jobs = []
    for style in styles:
        for n, (origin, layout) in enumerate(earlier_layouts(style).items() if use_earlier else ()):
            polish_jobs += _ils_jobs("polish", style, origin, local[style].perm_of(layout), first_seed + 5000 + 10 * n,
                                   polish["ils_iterations"])
    runs = {style: {"search": [], "polish": [], "confirmation": []} for style in styles}
    total = len(jobs) + len(polish_jobs)
    started = time.time()
    print(f"mixed objective {weights}; {len(jobs)} search runs + {len(polish_jobs)} polish runs", flush=True)
    with mp.Pool(workers or max(1, min(24, mp.cpu_count() - 4)), initializer=_init,
                 initargs=(styles, weights)) as pool:
        stream = [pool.imap_unordered(_search_job, jobs), pool.imap_unordered(_ils_job, polish_jobs)]
        done = 0
        for results in stream:
            for style, kind, result in results:
                runs[style][kind].append(result)
                done += 1
                if done % 16 == 0 or done == total:
                    print(f"{done}/{total} runs, {time.time() - started:.0f} s", flush=True)
        confirm_jobs = []
        for style in styles:
            best = min(runs[style]["search"] + runs[style]["polish"], key=lambda r: (_score_of(r), r["seed"]))
            perm = local[style].perm_of(dict(zip(best["layout"], local[style].slots)))
            confirm_jobs += _ils_jobs("confirmation", style, f"best (seed {best['seed']})", perm, first_seed + 9000,
                                     polish["ils_iterations"])
        for style, kind, result in pool.imap_unordered(_ils_job, confirm_jobs):
            runs[style][kind].append(result)
    print(f"search done, {time.time() - started:.0f} s", flush=True)
    written = []
    for style in styles:
        record = search_record(style, weights, settings, runs[style], problem)
        written.append(write_json(search_dir / f"{style}.json", record, indent=1))
        st = record["statistics"]
        print(f"style {style}: best mixed J1 {record['best']['J1']:.6f} ({record['best']['found_by']}), "
              f"{st['runs_reaching_best']}/{st['runs']} search runs reach it, {st['distinct_best_layouts']} distinct",
              flush=True)
    evaluation = evaluate(styles, weights, problem, search_dir)
    written.append(write_json(out / "mix-search.json", evaluation, indent=1))
    written.append(write_json(out / "run-manifest.json", manifest(written, styles, weights, settings, first_seed)))
    for name, passed in evaluation["checks"].items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    return written


def search_record(style: str, weights: dict, settings: dict, runs: dict, problem: dict) -> dict:
    search = sorted(runs["search"], key=lambda r: r["seed"])
    polish = sorted(runs["polish"], key=lambda r: r["seed"])
    confirmation = sorted(runs["confirmation"], key=lambda r: r["seed"])
    best = min(search + polish + confirmation, key=lambda r: (_score_of(r), r["seed"]))
    found_by = ("search" if best in search else "polish" if best in polish else "confirmation")
    scores = [r["best_score"] for r in search]
    top = min(scores)
    return {
        "style": style, "description": problem["styles"][style]["description"], "settings": settings,
        "frequencies": {relative_to_project(_keystroke_path(style, name)): w for name, w in weights.items()},
        "problem_sha256": problem["problem_sha256"], "effort_grid": relative_to_project(ANSI_GRID),
        "slots": problem["slots"],
        "best": {"seed": best["seed"], "found_by": found_by + (f" from {best['origin']}" if "origin" in best else ""),
                 "J1": _score_of(best), "layout": dict(zip(best["layout"], problem["slots"]))},
        "statistics": {"runs": len(scores), "best": top, "median": statistics.median(scores), "worst": max(scores),
                       "runs_reaching_best": sum(s <= top + 1e-9 for s in scores),
                       "distinct_best_layouts": len({tuple(r["layout"]) for r in search if r["best_score"] <= top + 1e-9}),
                       "seconds_total": round(sum(r["seconds"] for r in search), 1),
                       "polish_or_confirmation_improved_search": _score_of(best) < top - 1e-12},
        "polish": polish, "confirmation": confirmation, "runs": search,
    }


def _keystroke_path(style: str, name: str) -> Path:
    from .crosscheck import keystroke_file
    from .phase3 import frequency_file

    return frequency_file(style, name) if name in WIKI else keystroke_file(style, name)


def mixed_best_layout(style: str, search_dir: Path = SEARCH) -> dict[str, tuple[str, str]]:
    from .search.problem import parse_slot

    record = json.loads((search_dir / f"{style}.json").read_text(encoding="utf-8"))
    return {label: parse_slot(slot) for label, slot in record["best"]["layout"].items()}


def evaluate(styles: list[str], weights: dict[str, float], problem: dict, search_dir: Path = SEARCH) -> dict:
    """Held-out scores of the mixed layout and the earlier layouts of each
    style, and a check that the search objective equals the weighted table
    scores on the training splits."""
    model = KeyModel.from_grid(ANSI_GRID)
    fixed = problem_fixed(problem)
    out = {"weights": weights, "heldout": list(HELDOUT), "styles": {}, "checks": {}}
    objective_ok = True
    for style in styles:
        layouts = {"mixed": mixed_best_layout(style, search_dir), **earlier_layouts(style)}
        inst = mix_instance(style, weights, model, problem)
        rows = {}
        for name, layout in layouts.items():
            scores = {corpus: score_style(style, layout, corpus, model, fixed) for corpus in (*weights, *HELDOUT)}
            mixed_train = sum(w * scores[c]["J1"] for c, w in weights.items())
            search_value = inst.score(inst.perm_of(layout))
            objective_ok &= abs(mixed_train - search_value) < 1e-9
            rows[name] = {"mixed_train_J1": mixed_train, "search_objective": search_value,
                          "scores": {c: {k: s[k] for k in ("J1", "J0", "E1", "E2", "M") if k in s}
                                     for c, s in scores.items()}}
        out["styles"][style] = rows
    out["checks"]["search objective equals the weighted table scorer on the training splits"] = objective_ok
    return out


def manifest(outputs: list[Path], styles: list[str], weights: dict, settings: dict, first_seed: int = FIRST_SEED) -> dict:
    head, clean = repo_state()
    inputs = {relative_to_project(p): sha256_file(p) for p in (PROBLEM_FILE, ANSI_GRID)}
    for style in styles:
        for name in (*weights, *HELDOUT):
            path = _keystroke_path(style, name)
            inputs[relative_to_project(path)] = sha256_file(path)
        for path in (PHASE3 / "search" / f"{style}.json", CROSSCHECK / "search" / f"{style}.json"):
            if path.exists():
                inputs[relative_to_project(path)] = sha256_file(path)
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "repo_commit": head, "working_tree_clean": clean,
            "parameters": {"objective": "J1 as Phase 3, on the weighted mix of training splits", "weights": weights,
                           "styles": styles, "effort_grid": relative_to_project(ANSI_GRID),
                           "fingering": "model-optimal (D3 default)", "middle_index_benefit": "kept (D6 default)",
                           "search": settings, "seed_range": [first_seed, first_seed + settings["seeds"] - 1]},
            "inputs": inputs, "outputs": hash_outputs(outputs)}
