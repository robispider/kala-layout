"""e4: seeded search for strictly lower J1 and cross-space same-finger movement.

No existing layouts are overwritten. Resume is explicit, hash-checked, and
requires identical search settings/inputs; worker count may change.
"""
from __future__ import annotations

import argparse
import datetime
from fractions import Fraction
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import random
import time

from .. import challenge
from ..paths import PROJECT_ROOT, hash_outputs, output_path, repo_state, write_json, write_text
from ..reference import sha256_file
from ..scoring.model import KeyModel
from ..search.problem import PROBLEM_FILE, slot_name
from .actions import diagnostics, from_style, j_reference
from .continuous import evaluate_cache
from .continuous_counts import DEFAULT, load_verified
from .evaluate import MODELS
from .inputs import HELDOUT, TRAIN, frequency_path, unit_path, load_candidates, read_json, validate_layout
from .joint_engine import Archive, search
from .joint_problem import DIRECTIONS, JointProblem, WEIGHTS, endpoint_counts
from .mechanics import audit, evaluator, SOURCE
from .mechanics_counts import map_triples, triples_from_json
from .report import csv_text
from .safety import new_run_directory, protected_hashes
from .artifact_storage import write_json_compressed

VERSION = "joint-j1-movement-v1"
FIRST_SEED = 2026101300
_problems, _starts = {}, {}


def preserved():
    result = protected_hashes()
    for season in ("evaluator-e1", "evaluator-e2", "evaluator-e3"):
        result.update(hash_outputs([p for p in (PROJECT_ROOT / "results" / season).rglob("*") if p.is_file()]))
    return result


def atomic_json(path, value):
    target = output_path(path)
    temporary = output_path(target.with_name(target.name + ".tmp"))
    write_json(temporary, value)
    os.replace(temporary, target)
    return target


def run_identity(style, seed):
    return f"{style}-{seed}"


def initialize(styles, counts_root):
    global _problems, _starts
    candidates, _ = load_candidates(True)
    _problems, _starts = {}, {}
    for style in styles:
        rows = [c for c in candidates if c.style == style]
        reference = next(c for c in rows if any(n.startswith("Kala ") for n in c.names))
        problem = JointProblem(style, reference.layout, counts_root)
        _problems[style] = problem
        _starts[style] = [problem.j1.perm_of(c.layout) for c in rows]


def search_job(job):
    style, seed, ordinal, settings = job
    problem = _problems[style]
    rng = random.Random(seed)
    kind = ordinal % 5
    if kind == 0:
        start, name = problem.reference_perm, "published-reference"
    elif kind == 1:
        index = rng.randrange(len(_starts[style]))
        start, name = _starts[style][index], f"retained-map-{index}"
    elif kind == 2:
        start, name = list(problem.reference_perm), "perturbed-reference"
        for _ in range(8):
            i, k = rng.sample(range(problem.j1.n), 2)
            start[i], start[k] = start[k], start[i]
    elif kind == 3:
        start, name = list(range(problem.j1.n)), "random"
        rng.shuffle(start)
    else:
        start, name = problem.j1.greedy(), "greedy-J1"
    direction = DIRECTIONS[ordinal % len(DIRECTIONS)]
    result = search(problem, seed, direction, start, settings["steps"], settings["ils_iterations"],
                    settings["archive_limit"], settings["t_ratio"])
    result.update(style=style, start=name, start_perm=list(start), id=run_identity(style, seed),
                  version=VERSION, settings_sha256=settings_digest(settings))
    return result


def input_files(styles, counts_root):
    _, files = load_candidates(True)
    files += [PROBLEM_FILE, *MODELS.values(), challenge.SCRIPT, PROJECT_ROOT / "challenge/challenge-data.json",
              Path(counts_root) / "run-manifest.json", SOURCE / "source-lock.json"]
    for entry in read_json(SOURCE / "source-lock.json")["files"]:
        files.append(SOURCE / entry["file"])
    for style in styles:
        for corpus in (*TRAIN, *HELDOUT):
            # Verify identity/version/hash before starting or resuming.
            cache, path = load_verified(Path(counts_root), "style", style, corpus)
            endpoint_counts(cache)
            if cache["corpus_sha256"] != read_json(unit_path(corpus))["corpus_sha256"]:
                raise ValueError("e3 cache corpus provenance changed")
            files += [path, frequency_path(style, corpus), unit_path(corpus)]
    files += [p for p in (PROJECT_ROOT / "src/bangla_dh").rglob("*.py")]
    return sorted(set(files))


def settings_digest(settings):
    return hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()


def prepare(out, settings, inputs, resume=False):
    before = preserved()
    state = {"version": VERSION, "settings": settings, "input_sha256": inputs,
             "python": platform.python_version(), "platform": platform.platform(), "protected_sha256": before}
    target = Path(out).resolve()
    if not any(target.is_relative_to((PROJECT_ROOT / p).resolve()) and target != (PROJECT_ROOT / p).resolve()
               for p in ("work/evaluator-experiments", "results/evaluator-e4")):
        raise ValueError("joint search output must stay inside work/evaluator-experiments or results/evaluator-e4")
    if not resume:
        target = new_run_directory(target)
        write_json(target / "search-plan.json", state)
        atomic_json(target / "progress.json", {"completed": {}})
    else:
        if read_json(target / "search-plan.json") != state:
            raise ValueError("resume refused: inputs, code, settings, environment or protected files changed")
        if (target / "run-manifest.json").exists():
            raise ValueError("run already complete; choose a new output directory")
    progress = read_json(target / "progress.json")
    for name, digest in progress["completed"].items():
        if name != Path(name).name or len(name.split("-")) != 2 or name.split("-")[0] not in ("A", "D") or not name.split("-")[1].isdigit():
            raise ValueError("invalid checkpoint run identity")
        if sha256_file(target / "runs" / (name + ".json")) != digest:
            raise ValueError("checkpoint run hash mismatch: " + name)
    return target, before, progress


def evaluate_layout(style, layout, counts_root, models):
    rows = []
    from ..phase3 import problem_fixed
    from ..search.problem import load_problem
    assignment = {**layout, **problem_fixed(load_problem())}
    for corpus in (*TRAIN, *HELDOUT):
        cache, _ = load_verified(Path(counts_root), "style", style, corpus)
        tables = from_style(read_json(frequency_path(style, corpus)), assignment)
        triples = map_triples(triples_from_json(cache["triples"]), assignment)
        for scenario, model in models.items():
            rows.append({"corpus": corpus, "scenario": scenario, "reference": j_reference(tables, model),
                         "diagnostics": diagnostics(tables, model), "continuous": evaluate_cache(cache, model, assignment),
                         "mechanics": evaluator(scenario).score(tables),
                         "engram_order": evaluator(scenario).score_triples(triples)})
    return rows


def classify_exact(j, s, reference_j, reference_s):
    return {"lower_J1": j < reference_j, "lower_movement": s < reference_s,
            "joint_training_improvement": j < reference_j and s < reference_s}


def recover_checkpoint(target, settings, progress, expected_ids):
    """Recover complete atomic writes, never incomplete temporary files."""
    for path in sorted((target / "runs").glob("*.json")):
        name = path.stem
        if name in progress["completed"]:
            continue
        orphan = read_json(path)
        if (name not in expected_ids or orphan.get("id") != name or orphan.get("version") != VERSION
                or orphan.get("settings_sha256") != settings_digest(settings) or not orphan.get("verified")):
            raise ValueError("untracked checkpoint cannot be recovered: " + str(path))
        progress["completed"][name] = sha256_file(path)
    atomic_json(target / "progress.json", progress)


def finish(target, settings, progress, counts_root, before, fidelity, inputs, workers):
    candidates, _ = load_candidates(True)
    problems, refs, reference_evaluation = {}, {}, {}
    models = {s: KeyModel.from_grid(path) for s, path in MODELS.items()}
    merged = {}
    for style in settings["styles"]:
        reference = next(c for c in candidates if c.style == style and any(n.startswith("Kala ") for n in c.names))
        refs[style] = reference
        problems[style] = JointProblem(style, reference.layout, counts_root)
        merged[style] = Archive(settings["frontier_limit"], (problems[style].ref_j, problems[style].ref_s))
        reference_evaluation[style] = evaluate_layout(style, reference.layout, counts_root, models)
        merged[style].offer(problems[style].ref_j, problems[style].ref_s, problems[style].reference_perm)
    runs = []
    for name in sorted(progress["completed"]):
        result = read_json(target / "runs" / (name + ".json"))
        runs.append({k: v for k, v in result.items() if k != "archive"})
        for row in result["archive"]:
            merged[result["style"]].offer(row["j"], row["s"], row["perm"])
    # Full secondary diagnostics for selected training-only frontier points.
    # Each run's complete bounded archive remains available in runs/*.json.
    scored, written, csv_rows = [], [], []
    public = challenge.load_scorer(challenge.SCRIPT)
    data, data_hash = public.load_data()
    public_model = public.Model(data)
    for style in settings["styles"]:
        problem = problems[style]
        for point in merged[style].retained():
            layout = problem.assignment(point["perm"])
            validate_layout(style, layout)
            j, s = problem.verify(point["perm"])
            identity = hashlib.sha256(json.dumps([style, sorted(layout.items())], ensure_ascii=False).encode()).hexdigest()[:16]
            cid = f"{style}-{identity}"
            file = target / "layouts" / (cid + ".json")
            submission = {"name": f"Experimental joint search {cid}", "style": style, "layout": challenge._key_layout(layout)}
            # Official parser/scorer must agree exactly, not just approximately.
            official = public.evaluate(submission, data, data_hash, public_model)
            if not official["valid"] or Fraction(official["J1_exact"]) != j:
                raise ValueError("candidate differs from exact official challenge J1")
            expected_bytes = (json.dumps(submission, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            if file.exists():
                if file.read_bytes() != expected_bytes:
                    raise FileExistsError("existing candidate layout differs; refusing overwrite: " + str(file))
                written.append(file)
            else:
                written.append(write_json(file, submission))
            rows = evaluate_layout(style, layout, counts_root, models)
            ref_rows = {(r["corpus"], r["scenario"]): r for r in reference_evaluation[style]}
            for row in rows:
                ref = ref_rows[row["corpus"], row["scenario"]]
                row["changes"] = {"J1_percent": 100 * (row["reference"]["J1"] / ref["reference"]["J1"] - 1),
                    "movement_percentage_points": 100 * (row["continuous"]["bounds"]["same_finger_different_key"]["lower"]
                         - ref["continuous"]["bounds"]["same_finger_different_key"]["lower"]),
                    "shift_share_percentage_points": 100 * (row["diagnostics"]["shift_share_of_non_space_presses"]
                         - ref["diagnostics"]["shift_share_of_non_space_presses"]),
                    "repeat_rate_percentage_points": 100 * (row["continuous"]["bounds"]["same_key"]["lower"]
                         - ref["continuous"]["bounds"]["same_key"]["lower"]),
                    "engram_pair_lower": row["mechanics"]["bounds"]["engram_avg4"]["lower"]
                         - ref["mechanics"]["bounds"]["engram_avg4"]["lower"],
                    "engram_order_lower": row["engram_order"]["bounds"]["lower"] - ref["engram_order"]["bounds"]["lower"]}
            flags = classify_exact(j, s, problem.reference_j, problem.reference_s)
            entry = {"id": cid, "style": style, "layout_file": file.relative_to(PROJECT_ROOT).as_posix(),
                "training_J1_exact": str(j), "training_movement_exact": str(s),
                "training_J1": float(j), "training_movement": float(s), **flags,
                "training_J1_change_percent": 100 * (float(j / problem.reference_j) - 1),
                "training_movement_change_percent": 100 * (float(s / problem.reference_s) - 1),
                "heldout_all_primary_improve": all(r["changes"]["J1_percent"] < 0 and r["changes"]["movement_percentage_points"] < 0
                    for r in rows if r["corpus"] in HELDOUT and r["scenario"] == "model-optimal"),
                "layout": {k: slot_name(v) for k, v in sorted(layout.items())}, "scores": rows}
            scored.append(entry)
            csv_rows.append({k: entry[k] for k in ("id", "style", "training_J1", "training_movement",
                "training_J1_change_percent", "training_movement_change_percent", "lower_J1", "lower_movement",
                "joint_training_improvement", "heldout_all_primary_improve", "layout_file")})
            print(f"Verified {cid}: J1 {entry['training_J1_change_percent']:+.6f}%, movement "
                  f"{entry['training_movement_change_percent']:+.4f}%; joint improvement {flags['joint_training_improvement']}", flush=True)
    if preserved() != before:
        raise ValueError("an existing scientific/layout file changed")
    result = {"season": "e4", "version": VERSION, "objective": "strictly lower J1 and cross-space same-finger different-key rate",
        "settings": settings, "official_layouts_replaced": False, "search_run_count": len(runs), "runs": runs,
        "references": {s: {"name": "Kala Goti" if s == "A" else "Kala Jhor", "J1_exact": str(p.reference_j),
                           "movement_exact": str(p.reference_s), "scores": reference_evaluation[s]} for s, p in problems.items()},
        "candidates": scored, "joint_improvement_count": sum(r["joint_training_improvement"] for r in scored),
        "source_fidelity": fidelity, "checks": {"exact_J1_and_endpoint_counts": True,
            "official_scorer_agrees_exactly": True, "original_files_preserved": True, "heldout_not_used_for_selection": True}}
    written += [write_json_compressed(target / "results.json", result), write_text(target / "candidates.csv", csv_text(csv_rows, list(csv_rows[0]))),
                write_text(target / "REPORT.md", render(result)), write_json(target / "source-fidelity.json", fidelity)]
    written += [target / "search-plan.json", target / "progress.json"]
    written += [target / "runs" / (name + ".json") for name in sorted(progress["completed"])]
    revision, clean = repo_state()
    write_json(target / "run-manifest.json", {"season": "e4", "version": VERSION,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "git_revision": revision,
        "working_tree_clean": clean, "python": platform.python_version(), "platform": platform.platform(),
        "parameters": settings, "workers_at_final_invocation": workers,
        "seeds": {s: [settings["first_seed"] + i*settings["seeds"],
                            settings["first_seed"] + (i+1)*settings["seeds"] - 1] for i, s in enumerate(settings["styles"])},
        "exploration_energy": "relative Chebyshev directions; direction zero searches J1 alone; not a comfort total",
        "acceptance": "both exact training fractions strictly below the same-style published reference",
        "archive_pruning": "bounded evenly spaced J1-order indices; endpoints, best joint goal and run-direction endpoint protected; not exhaustive",
        "published_season_changed": False, "input_sha256": inputs, "output_sha256": hash_outputs(written),
        "protected_original_sha256": before, "checks": result["checks"]})
    print(f"Finished: {len(runs)} runs; {result['joint_improvement_count']} verified joint improvements. {target / 'REPORT.md'}", flush=True)
    return result


def render(result):
    lines = ["# Joint J1/movement search: experimental season e4", "",
        "A success requires strictly lower exact training J1 AND strictly fewer same-finger different-key "
        "endpoint moves across a space than the published map of the same vowel style. Higher-J1 movement "
        "trade-offs are reported separately and never labeled a success. All existing layouts/results are preserved.", "",
        f"Completed {result['search_run_count']} deterministic runs. Verified joint improvements: **{result['joint_improvement_count']}**.", "",
        "## Training comparison", "",
        "| Candidate | Style | J1 change | Movement change | Joint improvement | All held-out primary scores improve |",
        "| --- | --- | --- | --- | --- | --- |"]
    for r in result["candidates"]:
        lines.append(f"| {r['id']} | {r['style']} | {r['training_J1_change_percent']:+.6f}% | "
                     f"{r['training_movement_change_percent']:+.4f}% | {r['joint_training_improvement']} | {r['heldout_all_primary_improve']} |")
    lines += ["", "References: style A is Kala Goti; style D is Kala Jhor. Both objectives use the original 50/50 "
        "Wikipedia/newspaper training mix, each source normalized independently. Primary fingering is the frozen "
        "model-optimal grid. J1 retains Shift and extra-action effort; movement excludes separate modifier presses "
        "and keeps same-key repeats separate. Exact J1 uses the existing integer/challenge model; exact movement "
        "uses rational endpoint counts. No ergonomic weights or Colemak constants are changed.", "",
        "## Corpus and fingering changes", "",
        "| Candidate | Corpus | Fingering | J1 change | SF movement change (percentage points) | Shift change (percentage points) | Repeat change (percentage points) | Engram pair lower change | Engram order lower change |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in result["candidates"]:
        for row in r["scores"]:
            c = row["changes"]
            lines.append(f"| {r['id']} | {row['corpus']} | {row['scenario']} | {c['J1_percent']:+.6f}% | "
                f"{c['movement_percentage_points']:+.6f} | {c['shift_share_percentage_points']:+.6f} | "
                f"{c['repeat_rate_percentage_points']:+.6f} | {c['engram_pair_lower']:+.6f} | {c['engram_order_lower']:+.6f} |")
    lines += ["", "The full JSON retains coverage bounds, individual pair components, repeated-key and distance "
        "diagnostics, both fingerings, and every corpus separately. Secondary movement scores are checks for "
        "regressions, not additional success gates or a combined comfort ranking. Held-out scores never guide "
        "search or selection; these already-examined benchmarks are exploratory, not fresh human validation.", "",
        "## What the search explored", "",
        "Each seed cycles among the reference, retained J1 maps, a perturbed reference, a random permutation and "
        "the greedy J1 map. Seeds cycle through the recorded relative Chebyshev directions, including J1-only "
        "exploration. Negative energy for nonzero directions means both relative objectives improve, but final "
        "success is verified using exact fractions. These directions diversify search; they are not ergonomic weights.", "",
        "Each run keeps a bounded non-dominated training archive, and the final report selects a bounded training "
        "archive from their union. Best observed joint-goal candidates and each run's attained-direction endpoint "
        "are additionally protected from crowding. Per-run archives, seeds and starts are saved in runs/. Pruning is explicit; "
        "the frontier is not exhaustive. Annealing and iterated local search use separately cached O(1) swap "
        "deltas for each symmetric pair objective; no corpus text is read in the search loop.", "",
        "Candidates are best found for the stated search, never proven optimal. A result of zero joint improvements "
        "does not prove none exist. Existing optimality certificates do not transfer. The original J1 challenge "
        "DATA_VERSION, layout files, reproduction lock and website scores are unchanged. Layout JSON files in "
        "layouts/ are compatible with the challenge scorer and remain separate from published layouts.", "",
        "## Reproduction and interruption", "",
        "search-plan.json pins settings, code and data before dispatch. Each completed run is saved atomically and "
        "hashed in progress.json. Use the same command with --resume after interruption; worker count may change. "
        "Resume refuses changed code/data/settings and refuses an already completed run. A fresh output directory "
        "is required for another experiment. run-manifest.json records all output hashes and preservation checks.", ""]
    return "\n".join(lines)


def run(out, styles=("A", "D"), seeds=512, steps=1_000_000, ils_iterations=1000, workers=None,
        first_seed=FIRST_SEED, archive_limit=64, frontier_limit=32, t_ratio=1e-3, resume=False, counts_from=DEFAULT):
    if workers is None:
        workers = max(1, min(28, (os.cpu_count() or 1) - 4))
    if not 1 <= workers <= 64 or seeds < 1 or steps < 1 or ils_iterations < 0 or first_seed < 0:
        raise ValueError("invalid workers/seeds/steps/ILS/first seed")
    if not 0 < t_ratio < 1 or not 2 <= archive_limit <= 1024 or not 2 <= frontier_limit <= 1024:
        raise ValueError("invalid temperature/archive limits")
    styles = list(styles)
    if not styles or len(set(styles)) != len(styles) or any(s not in ("A", "D") for s in styles):
        raise ValueError("choose distinct styles A and/or D")
    settings = {"styles": styles, "seeds": seeds, "steps": steps, "ils_iterations": ils_iterations,
        "first_seed": first_seed, "archive_limit": archive_limit, "frontier_limit": frontier_limit,
        "t_ratio": t_ratio, "directions": list(DIRECTIONS), "training_weights": {c: str(w) for c, w in WEIGHTS.items()},
        "counts_from": Path(counts_from).resolve().relative_to(PROJECT_ROOT).as_posix()}
    inputs = hash_outputs(input_files(styles, Path(counts_from)))
    target, before, progress = prepare(out, settings, inputs, resume)
    fidelity = audit()
    all_jobs = [(s, first_seed + i*seeds + k, k, settings) for i, s in enumerate(styles) for k in range(seeds)]
    expected_ids = {run_identity(j[0], j[1]) for j in all_jobs}
    if not set(progress["completed"]).issubset(expected_ids):
        raise ValueError("checkpoint contains unexpected runs")
    # Recover the crash window after a complete atomic run write but before its
    # progress hash was saved. Incomplete *.tmp writes are never treated as runs.
    recover_checkpoint(target, settings, progress, expected_ids)
    jobs = [j for j in all_jobs if run_identity(j[0], j[1]) not in progress["completed"]]
    print(f"e4: {len(all_jobs)} runs ({seeds} per style); {len(progress['completed'])} completed; {workers} workers", flush=True)
    started = time.perf_counter()
    if jobs:
        # Pool's context manager terminates queued/in-flight work on interruption;
        # only the parent writes artifacts, so completed checkpoints stay intact.
        with mp.get_context("spawn").Pool(workers, initializer=initialize, initargs=(styles, Path(counts_from))) as pool:
            for result in pool.imap_unordered(search_job, jobs):
                path = target / "runs" / (result["id"] + ".json")
                if path.exists():
                    raise FileExistsError("untracked run file exists; refusing overwrite: " + str(path))
                atomic_json(path, result)
                progress["completed"][result["id"]] = sha256_file(path)
                atomic_json(target / "progress.json", progress)
                print(f"{len(progress['completed'])}/{len(all_jobs)} saved: {result['id']}; direction {result['direction']}; "
                      f"{len(result['archive'])} archived; {time.perf_counter()-started:.1f}s elapsed", flush=True)
    if preserved() != before:
        raise ValueError("an existing scientific/layout file changed during search")
    return finish(target, settings, progress, Path(counts_from), before, fidelity, inputs, workers)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new folder under results/evaluator-e4 or work/evaluator-experiments")
    parser.add_argument("--styles", nargs="+", choices=("A", "D"), default=["A", "D"])
    parser.add_argument("--seeds", type=int, default=512, help="runs per style, distributed across exploration directions")
    parser.add_argument("--steps", type=int, default=1_000_000)
    parser.add_argument("--ils-iterations", type=int, default=1000)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--first-seed", type=int, default=FIRST_SEED)
    parser.add_argument("--archive-limit", type=int, default=64)
    parser.add_argument("--frontier-limit", type=int, default=32)
    parser.add_argument("--t-ratio", type=float, default=1e-3)
    parser.add_argument("--counts-from", type=Path, default=DEFAULT)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        run(args.out, args.styles, args.seeds, args.steps, args.ils_iterations, args.workers,
            args.first_seed, args.archive_limit, args.frontier_limit, args.t_ratio, args.resume, args.counts_from)
    except KeyboardInterrupt:
        parser.exit(130, "Interrupted. Completed runs are checkpointed; rerun the same command with --resume.\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Joint search failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
