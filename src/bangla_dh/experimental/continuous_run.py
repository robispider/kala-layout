"""Season e3: continuous-text action coverage and cross-space diagnostics."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import json
from pathlib import Path
import platform

from ..paths import PROJECT_ROOT, gzip_text_writer, hash_outputs, repo_state, write_json, write_text
from ..scoring import baselines
from ..scoring.model import KeyModel
from .actions import ActionTables, from_style, j_reference
from .continuous import EVENTS, evaluate_cache
from .continuous_counts import DEFAULT, E2, VERSION, CATEGORIES, build_job, cache_name, load_verified, verified_result
from .evaluate import MODELS
from .inputs import HELDOUT, TRAIN, frequency_path, unit_path, read_json, load_candidates
from .mechanics import audit
from .report import csv_text
from .safety import new_run_directory, protected_hashes


def average(rows, weights):
    if not rows or {r["corpus"] for r in rows} != set(weights):
        raise ValueError("summary needs exactly the specified corpora")
    if len(rows) != len(weights) or abs(sum(weights.values()) - 1) > 1e-12:
        raise ValueError("invalid averaging weights/duplicate corpus")
    result = {"J1": sum(weights[r["corpus"]] * r["reference"]["J1"] for r in rows)}
    for key in ("within_word_share", "space_touching_share", "coverage"):
        result[key] = (sum(weights[r["corpus"]] * r["continuous"][key] for r in rows)
                       if all(r["continuous"][key] is not None for r in rows) else None)
    result["bounds"] = {event: {side: sum(weights[r["corpus"]] * r["continuous"]["bounds"][event][side]
                    for r in rows) for side in ("lower", "upper")}
                    if all(event in r["continuous"]["bounds"] for r in rows) else None for event in EVENTS}
    return result


def comparisons(summary):
    """Descriptive interval-separated orders; no composite or candidate selection."""
    rows = []
    for i, a in enumerate(sorted(summary)):
        for b in sorted(summary)[i+1:]:
            row = {"a": a, "b": b, "lower_J1": a if summary[a]["J1"] < summary[b]["J1"]
                   else b if summary[b]["J1"] < summary[a]["J1"] else None}
            for event in EVENTS:
                x, y = summary[a]["bounds"][event], summary[b]["bounds"][event]
                if x is None or y is None:
                    row[event] = {"lower_rate": None, "a_minus_b": None}
                    continue
                row[event] = {"lower_rate": a if x["upper"] < y["lower"] else b if y["upper"] < x["lower"] else None,
                              "a_minus_b": [x["lower"] - y["upper"], x["upper"] - y["lower"]]}
            rows.append(row)
    return rows


def render(result):
    lines = ["# Continuous-text mechanics: evaluation season e3", "",
        "Exact consecutive action windows, including spaces, for all eight public fixed layouts and the retained A/D maps. "
        "These are movement frequencies, not measured speed, comfort, a new search objective or an optimality claim.", "",
        "## Counting rules", "",
        "Words use their own layout encoder and the frozen e2 canonical policy. Space is an explicit action. "
        "Escapes, paragraph ends and document ends break windows. Supported punctuation remains a key action; "
        "escaped punctuation breaks the stream. Base/Shift layers are retained; separate modifier presses are excluded. "
        "Short words, repeated keys, empty tokens and multiple spaces are preserved.", "",
        "Canonical baseline encoding minimizes actions with traditional-grid effort tie-breaking, held fixed across "
        "both fingerings, as in e2. Adapted baseline J1 can therefore differ from the published scoreboard's independently "
        "chosen encoding/fingering; no scoreboard score is replaced.", "",
        "Within-word windows retain the existing Engram order score. Edge-space windows and windows containing "
        "multiple spaces are counted without assigning a thumb or scoring them. For key–space–key, only the two "
        "endpoint keys define hand/finger relationships. The intervening space is not removed from the action stream. "
        "No upstream Engram formula or constant was changed.", "",
        "## Exact window coverage", "",
        "Counts are independent of fingering, but depend on the encoder. Shares use all valid windows after escape resets. "
        "They do not estimate windows inside unmodeled escape keystrokes or an error in J1. Escaped text may bias layout comparisons.", "",
        "| Layout | Corpus | Within word | Edge space | Spanning space | Multiple spaces | Within-word share |",
        "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in result["scores"]:
        if row["public"] and row["scenario"] == "traditional":
            c = row["continuous"]
            lines.append(f"| {row['name']} | {row['corpus']} | " + " | ".join(str(c["category_counts"][k]) for k in CATEGORIES)
                         + f" | {100*c['within_word_share']:.3f}% |")
    for scenario, summary in result["public_summary"].items():
        lines += ["", "## " + scenario + ": equal-weight held-out endpoint rates", "",
            "Each source contributes one third. Lower same-finger movement frequency describes fewer same-finger "
            "moves across a space; hand switching is descriptive and is not assumed better. Same-key repeats are separate. "
            "Every interval retains unsupported endpoint mass with possible values 0 to 1. These are coverage bounds, "
            "not confidence intervals. Supported conditional rates and distance bounds are in the machine data.", "",
            "| Layout | Within-word share | Same key bounds | Same-finger different-key bounds | Opposite-hand bounds | Endpoint coverage |",
            "| --- | --- | --- | --- | --- | --- |"]
        for name, row in sorted(summary.items(), key=lambda p: p[1]["J1"]):
            cells = [f"{100*row['within_word_share']:.3f}%"]
            for event in ("same_key", "same_finger_different_key", "opposite_hand"):
                bounds = row["bounds"][event]
                cells.append(f"{100*bounds['lower']:.3f}–{100*bounds['upper']:.3f}%")
            cells.append(f"{100*row['coverage']:.3f}%")
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
        j, g = summary["Kala Jhor"], summary["Kala Goti"]
        x, y = j["bounds"]["same_finger_different_key"], g["bounds"]["same_finger_different_key"]
        winner = "Kala Jhor" if x["upper"] < y["lower"] else "Kala Goti" if y["upper"] < x["lower"] else None
        lines += ["", (f"{winner} has a lower same-finger different-key endpoint rate than the other Kala map, "
                        "with intervals separated." if winner else "The Kala maps' same-finger different-key intervals overlap.")
                  + " This does not decide overall comfort. All pairwise comparisons are in public-summary.json."]
    lines += ["", "## Benchmark and verification", "",
        "Encoding includes token counting and comparison with frozen e2 counts. Scan time covers the full running-text "
        "boundary pass. Memory is process-lifetime peak working set/RSS and can include an earlier job in a reused worker.", "",
        "| Encoder | Corpus | Cached word types | Encoding seconds | Scan seconds | Peak process bytes |",
        "| --- | --- | --- | --- | --- | --- |"]
    for job in result["jobs"]:
        b = job["benchmark"]
        lines.append(f"| {job['identity']} | {job['corpus']} | {b['cached_word_types']} | "
                     f"{b['encoding_seconds']} | {b['scan_seconds']} | {b['peak_process_memory_bytes']} |")
    lines += ["", "Every rebuilt job matches e2 unigrams, pairs and within-word triples exactly. Running word frequencies "
        "and first/last-paragraph counts match the token table. Edge windows match the word-table formulas. "
        "A full-action scanner checks the first 50 paragraphs of each corpus. The full-run window total independently "
        "equals the sum of max(run length − 2, 0) over uninterrupted action runs. Synthetic randomized tests cover the "
        "optimized scanner and separate full-action scanner.", "",
        "## Retained candidates and scope", "",
        f"{len(result['candidates'])} retained A/D maps reuse style-specific label windows. All three held-out sources "
        "and both fingerings are reported. Training diagnostics use the original 50/50 Wikipedia/newspaper mix, "
        "separately for each style. No candidates are selected and no new layouts are searched. Existing held-out "
        "comparisons are exploratory; future selection would need independent confirmatory validation.", "",
        "Original J1, published layouts, challenge DATA_VERSION, acceptance and leaderboard ordering are unchanged. "
        "The optional challenge diagnostics can read the hashed committed style windows without running-text downloads.", "",
        "## Reproduce", "", "```powershell", '$env:PYTHONPATH = "src"',
        "python -m bangla_dh.experimental.continuous_run --out work/evaluator-experiments/continuous-repeat --workers 4",
        "```", "", "Add --rebuild-counts to scan the pinned local corpus/token files. All writers use the repository "
        "guard and require a new output directory. Deterministic compressed counts contain no corpus text. "
        "Code/input/output hashes, policies, timings and preservation checks are in run-manifest.json. "
        "Rescoring preserves original counting benchmarks; it does not claim to repeat those timings.", ""]
    return "\n".join(lines)


def run(out=DEFAULT, workers=4, rebuild_counts=False, counts_from=DEFAULT, heldout_only=False):
    if not 1 <= workers <= 16:
        raise ValueError("workers must be 1 through 16")
    target = new_run_directory(out)
    before = protected_hashes()
    # e3 must also preserve earlier diagnostic seasons.
    earlier_paths = [p for root in ("evaluator-e1", "evaluator-e2")
                     for p in (PROJECT_ROOT / "results" / root).rglob("*") if p.is_file()]
    earlier = hash_outputs(earlier_paths)
    fidelity = audit()
    e2_scores, e2_score_path = verified_result(E2, "scores.json.gz")
    order = {(r["id"], r["corpus"], r["scenario"]): r["engram_order"] for r in e2_scores["scores"]}
    candidates, inputs = load_candidates(True)
    inputs += [e2_score_path, E2 / "run-manifest.json"]
    entries = baselines.load_registry()
    inputs += [baselines.REGISTRY, *[baselines.source_path(e) for e in entries], *MODELS.values()]
    corpora = HELDOUT if heldout_only else (*HELDOUT, *TRAIN)
    jobs = [("style", s, c) for c in corpora for s in ("A", "D")]
    jobs += [("baseline", e, c) for c in HELDOUT for e in entries]
    caches = {}
    benchmarks = {}
    prior_jobs = None
    rebuilt = []
    inputs += [unit_path(c) for c in corpora] + [frequency_path(s, c) for s in ("A", "D") for c in corpora]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {}
        for kind, identity, corpus in jobs:
            name = identity if kind == "style" else identity["name"]
            key = (kind, name, corpus)
            saved = Path(counts_from) / "counts" / cache_name(*key)
            if saved.exists() and not rebuild_counts:
                cache, path = load_verified(Path(counts_from), *key)
                if cache["version"] != VERSION or cache["corpus_sha256"] != read_json(unit_path(corpus))["corpus_sha256"]:
                    raise ValueError("continuous cache version/corpus mismatch")
                caches[key] = cache
                inputs += [path, Path(counts_from) / "run-manifest.json"]
                if prior_jobs is None:
                    previous, score_path = verified_result(Path(counts_from), "scores.json.gz")
                    prior_jobs = {(j["kind"], j["identity"], j["corpus"]): j for j in previous["jobs"]}
                    inputs.append(score_path)
                previous_job = prior_jobs[key]
                benchmarks[key] = previous_job["benchmark"]
            else:
                futures[pool.submit(build_job, kind, identity, corpus)] = key
        for future in as_completed(futures):
            key = futures[future]
            caches[key] = future.result()
            rebuilt.append(key)
            cache = caches[key]
            benchmarks[key] = cache.pop("benchmark")
            print(f"Counted {key}: {cache['category_counts']}; benchmark {benchmarks[key]}", flush=True)
    written = []
    for key, cache in sorted(caches.items()):
        path = target / "counts" / cache_name(*key)
        with gzip_text_writer(path) as stream:
            json.dump(cache, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
        written.append(path)
        inputs.append(path)
        if key in rebuilt:
            record = read_json(unit_path(key[2]))
            inputs += [PROJECT_ROOT / record["corpus_file"], PROJECT_ROOT / record["token_table"],
                       E2 / "counts" / cache_name(*key), E2 / "run-manifest.json"]
    models = {s: KeyModel.from_grid(p) for s, p in MODELS.items()}
    result = {"season": "e3", "version": VERSION, "source_fidelity": fidelity,
              "published_season_changed": False, "scores": [], "candidates": [], "public_summary": {},
              "comparisons": {}, "jobs": [{k: cache[k] for k in ("kind", "identity", "corpus", "checks")} | {"benchmark": benchmarks[key]}
                                           for key, cache in sorted(caches.items())]}
    for candidate in candidates:
        assignment = candidate.assignment()
        name = next((n for n in candidate.names if n.startswith("Kala ")), candidate.id)
        training = {s: [] for s in models}
        for corpus in corpora:
            cache = caches["style", candidate.style, corpus]
            tables = from_style(read_json(frequency_path(candidate.style, corpus)), assignment)
            for scenario, model in models.items():
                row = {"id": candidate.id, "name": name, "style": candidate.style, "public": name.startswith("Kala "),
                       "corpus": corpus, "scenario": scenario, "reference": j_reference(tables, model),
                       "continuous": evaluate_cache(cache, model, assignment)}
                if corpus in HELDOUT:
                    row["engram_order"] = order[candidate.id, corpus, scenario]
                    result["scores"].append(row)
                else:
                    training[scenario].append(row)
        summary = candidate.json()
        summary["training"] = {s: average(rows, {c: 0.5 for c in TRAIN}) for s, rows in training.items()} if not heldout_only else None
        result["candidates"].append(summary)
        if len(result["candidates"]) % 20 == 0:
            print(f"Scored {len(result['candidates'])}/{len(candidates)} retained maps", flush=True)
    history = read_json(PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json")
    import math
    for entry in entries:
        for corpus in HELDOUT:
            cache = caches["baseline", entry["name"], corpus]
            tables = ActionTables.from_json(cache["action_tables"])
            actual = j_reference(tables, models["traditional"])
            expected = history["baselines"][entry["name"]]["scores"][corpus]["traditional_unrounded"]
            if any(not math.isclose(actual[k], expected[k], rel_tol=0, abs_tol=1e-10) for k in ("J0", "J1")):
                raise ValueError("baseline historical score mismatch")
            for scenario, model in models.items():
                result["scores"].append({"id": "baseline:" + entry["name"], "name": entry["name"],
                    "style": None, "public": True, "corpus": corpus, "scenario": scenario,
                    "reference": j_reference(tables, model), "continuous": evaluate_cache(cache, model),
                    "engram_order": order["baseline:" + entry["name"], corpus, scenario]})
    result["scores"].sort(key=lambda r: (r["id"], r["corpus"], r["scenario"]))
    for scenario in models:
        rows = [r for r in result["scores"] if r["public"] and r["scenario"] == scenario]
        result["public_summary"][scenario] = {name: average([r for r in rows if r["name"] == name], {c: 1/3 for c in HELDOUT})
                                               for name in sorted({r["name"] for r in rows})}
        result["comparisons"][scenario] = comparisons(result["public_summary"][scenario])
    if protected_hashes() != before or hash_outputs(earlier_paths) != earlier:
        raise ValueError("published scientific/earlier diagnostic files changed")
    result["checks"] = {"frozen_counts_and_running_boundaries": all(all(c["checks"].values()) for c in caches.values()),
                        "baseline_historical_scores": True, "published_and_prior_seasons_preserved": True}
    score_path = target / "scores.json.gz"
    with gzip_text_writer(score_path) as stream:
        json.dump(result, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")
    rows = []
    for r in result["scores"]:
        c = r["continuous"]
        flat = {k: r[k] for k in ("id", "name", "style", "public", "corpus", "scenario")}
        flat.update(J1=r["reference"]["J1"], **c["category_counts"], within_word_share=c["within_word_share"],
                    endpoint_coverage=c["coverage"], shifted_spanning_count=c["shift_involving_spanning_count"],
                    same_finger_distance_u_per_spanning_window=c["same_finger_distance_u_per_spanning_window"])
        flat.update({f"{event}_{side}": c["bounds"][event][side] for event in EVENTS for side in ("lower", "upper")})
        flat.update({f"within_word_engram_order_{side}": r["engram_order"]["bounds"][side] for side in ("lower", "upper")})
        rows.append(flat)
    public = {"season": "e3", "version": VERSION, "layout_count": 8, "candidate_count": len(candidates),
              "public_summary": result["public_summary"], "comparisons": result["comparisons"],
              "corpus_scores": [r for r in result["scores"] if r["public"]], "checks": result["checks"]}
    written += [score_path, write_json(target / "public-summary.json", public),
                write_json(target / "candidates.json", result["candidates"]),
                write_json(target / "source-fidelity.json", fidelity),
                write_text(target / "scores.csv", csv_text(rows, list(rows[0]))), write_text(target / "REPORT.md", render(result))]
    inputs += [PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json"]
    inputs += [p for p in (PROJECT_ROOT / "src/bangla_dh").rglob("*.py")]
    from .mechanics import SOURCE
    inputs += [SOURCE / "source-lock.json", *[SOURCE / f["file"] for f in read_json(SOURCE / "source-lock.json")["files"]]]
    revision, clean = repo_state()
    write_json(target / "run-manifest.json", {"season": "e3", "version": VERSION,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "git_revision": revision,
        "working_tree_clean": clean, "python": platform.python_version(), "seeds": "no new search; retained original seeds",
        "published_season_changed": False, "parameters": {"workers": workers, "rebuild_counts": rebuild_counts,
            "heldout_only": heldout_only, "corpora": list(corpora), "training_weights": {c: 0.5 for c in TRAIN},
            "heldout_weights": {c: 1/3 for c in HELDOUT}, "scenarios": list(models), "categories": list(CATEGORIES),
            "boundary_policy": "literal spaces; reset at escapes/paragraph/document; own word encoder; modifiers excluded",
            "baseline_encoding": "e2 canonical minimum actions; traditional-grid effort tie-break; frozen across fingerings",
            "denominator": "all valid key-space-key windows including unsupported endpoints; unknown binary values 0..1",
            "thumb_policy": "unassigned; edge/multiple-space windows counted only", "reference_audit_paragraphs": 50,
            "candidate_selection": "none", "official_ranking_effect": "none"},
        "input_sha256": hash_outputs(sorted(set(inputs))), "output_sha256": hash_outputs(written),
        "protected_original_sha256": before, "protected_prior_evaluations_sha256": earlier, "checks": result["checks"]})
    print(f"E3 complete: {target / 'REPORT.md'}", flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--rebuild-counts", action="store_true")
    parser.add_argument("--counts-from", type=Path, default=DEFAULT)
    parser.add_argument("--heldout-only", action="store_true", help="stage one: public held-out corpora, without training passes")
    args = parser.parse_args(argv)
    try:
        run(args.out, args.workers, args.rebuild_counts, args.counts_from, args.heldout_only)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Continuous evaluation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
