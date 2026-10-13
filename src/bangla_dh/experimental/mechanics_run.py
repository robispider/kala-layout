"""Season e2: source-verified mechanics on every fixed layout and retained map."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import math
import platform
import json
from pathlib import Path

from ..paths import PROJECT_ROOT, write_json, write_text, hash_outputs, repo_state, gzip_text_writer
from ..scoring import baselines
from ..scoring.model import KeyModel
from .actions import from_style, j_reference, diagnostics
from .evaluate import MODELS
from .inputs import TRAIN, HELDOUT, read_json, frequency_path, unit_path, load_candidates
from .mechanics import SOURCE, METRICS, evaluator, audit, verify_sources
from .mechanics_counts import build_job, triples_json, triples_from_json, map_triples, read_counts
from .report import csv_text
from .safety import new_run_directory, protected_hashes

DEFAULT = PROJECT_ROOT / "results/evaluator-e2/run-v1"


def averaged(rows):
    """Equal source weights, including each source's unsupported mass."""
    result = {}
    for name in sorted({r["name"] for r in rows}):
        group = [r for r in rows if r["name"] == name]
        result[name] = {"J1": sum(r["reference"]["J1"] for r in group) / len(group),
                        "coverage": sum(r["mechanics"]["pair_coverage"] for r in group) / len(group),
                        "escape_share": sum(r["diagnostics"]["escaped_unit_share"] for r in group) / len(group)}
        for metric in METRICS:
            result[name][metric] = {side: sum(r["mechanics"]["bounds"][metric][side] for r in group) / len(group)
                                   for side in ("lower", "upper")}
        result[name]["engram_order"] = {side: sum(r["engram_order"]["bounds"][side] for r in group) / len(group)
                                          for side in ("lower", "upper")}
    return result


def comparisons(averages):
    result = []
    names = sorted(averages)
    for i, a in enumerate(names):
        for b in names[i+1:]:
            row = {"a": a, "b": b, "lower_J1": a if averages[a]["J1"] < averages[b]["J1"] else b}
            for metric in (*METRICS, "engram_order"):
                x, y = averages[a][metric], averages[b][metric]
                row[metric] = {"higher": a if x["lower"] > y["upper"] else b if y["lower"] > x["upper"] else None,
                               "a_minus_b": [x["lower"] - y["upper"], x["upper"] - y["lower"]]}
            result.append(row)
    return result


def render(result):
    audit_result = result["source_fidelity"]
    lines = ["# Dvorak-7 and Engram mechanics: evaluation season e2", "",
             "Eight fixed layouts and all retained A/D maps are evaluated with source-derived upstream scoring code. "
             "Higher mechanics values are better within the stated scope. J1 is lower-is-better modeled effort. "
             "These results describe modeled key movement, not measured speed or comfort.", "",
             "## What the comparison adds", "",
             "Under the unmodified upstream traditional fingering, Goti has higher Dvorak-7 and Engram avg4 "
             "credit than Jhor even after allowing the full range for missing pairs, while Jhor has lower J1. "
             "Under the adapted model-optimal fingering, their pair-model bounds overlap: neither pair model "
             "conclusively orders them. Goti has higher Engram trigram-order credit in both scenarios. "
             "Windows Default has higher trigram-order credit than both Kala maps, but escapes about 2.6% of "
             "text units and the order score ignores Shift effort. Thus the new criteria expose genuine modeled "
             "trade-offs and dependence on fingering; they do not produce an overall comfort winner.", "",
             "## What was verified", "",
             f"Pinned upstream commit: `{audit_result['source_commit']}` (Arno Klein, MIT). "
             f"The unmodified scoring bodies match the original functions for {audit_result['pair_function_cases']:,} "
             f"pairs and {audit_result['triple_function_cases']:,} triples. All {audit_result['distributed_table_rows']:,} "
             f"distributed table rows match (maximum absolute error {audit_result['distributed_table_max_absolute_error']:.3g}). "
             "Source snapshots, license and SHA-256 hashes are under data/evaluators/mechanics-v1. "
             "This proves implementation fidelity, not the ergonomic assumptions.", "",
             "Dvorak-7 is the source's seven-criterion sum divided by seven. Engram avg4 is exactly the generator's "
             "mean of row separation, same-row movement, same-finger movement and outside reach. "
             "The upstream table unifier can average additional columns under the same avg4 name; we deliberately "
             "use the explicit generator formula. Engram key preferences, scissor and half-scissor are reported "
             "as components; Engram trigram order is a separate diagnostic. No new combined comfort total is invented.", "",
             "## Reading the components", "",
             "| Component | What earns credit in the pinned code |", "| --- | --- |",
             "| Dvorak distribution | Different hands: 1; different fingers on one hand: 0.5; same finger: 0 |",
             "| Dvorak strength | Fraction of the two keys assigned to index/middle fingers |",
             "| Dvorak home | Fraction of the two keys on the home row |",
             "| Dvorak row span | Opposite hands or same row: 1; adjacent rows on one hand: 0.5; larger separation: 0 |",
             "| Dvorak columns | Fraction of keys inside the source's eight finger columns |",
             "| Dvorak remote | Source rule for row, finger adjacency and strong-finger pairs; same-row check comes first, so same-row repeats receive 1 here |",
             "| Dvorak inward | Opposite hands or a sequence toward the thumb: 1; same finger or outward sequence: 0 |",
             "| Engram row separation | Opposite hands or same row: 1; adjacent rows: 0.588; larger separation: 0 |",
             "| Engram same row | Opposite hands: 1; same finger: 0; within a row, outward credit is multiplied by 0.779 and remote columns by 0.750; different rows/fingers: 0.5 |",
             "| Engram same finger | Different hands/fingers: 1; same finger, including repeated keys: 0 |",
             "| Engram outside | No outside keys: 1; one: 0.846; two: 0.716 |",
             "| Engram key preference | Source tier values averaged over the two keys; not included in avg4 |",
             "| Engram scissor / half-scissor | Zero for the source's adjacent-column hurdle / reach condition, otherwise 1; not included in avg4 |",
             "| Engram order | Source-defined hand changes or monotonic three-finger sequences: 1; mixed/repeated-finger cases: 0 |", "",
             "J1 adds no pair penalty for repeating the identical action; Engram same-finger gives repeated physical "
             "keys zero credit. The pair mean also measures credit per transition, while J1 measures effort per text "
             "unit and prices extra presses and Shift. These different definitions help explain why the models "
             "can favor Goti's movement patterns while Jhor retains lower J1. The exact numerical component "
             "differences and important transitions are shown below.", "",
             "## Scope and coverage", "",
             "Base and Shift actions are projected to their physical key. Shift presses, chords, timing and "
             "modifier transitions are excluded from these mechanics scores. Shift use remains a separate diagnostic. "
             "Pairs are directed, include repeated keys, and exclude space transitions. Triples are counted within "
             "tokens and never cross a space, escape, paragraph or document boundary. Existing unigram/pair counts "
             "are independently reproduced during triple extraction; token tables are checked against their pinned hashes.", "",
             "The source functions define number-row keys although the distributed tables cover only 32 main keys. "
             "We use those unchanged number-row rules, checked against the original functions. Unsupported physical "
             "keys (such as minus) and AltGr retain their probability mass. Each interval assigns unknown events "
             "the possible range 0 to 1 using the full non-space event denominator. These are missing-coverage bounds, "
             "not statistical confidence intervals. Escape shares are shown separately: untyped text is outside the "
             "mechanics domain and can bias comparisons. There is no whole-typing comfort ranking.", "",
             "Canonical baseline encoding minimizes presses with traditional-grid effort tie-breaking, held fixed "
             "across scorers. Traditional J0/J1 match historical results. The primary scenario preserves upstream "
             "traditional ANSI fingering. The model-optimal scenario changes finger/hand assignments to the frozen "
             "Kala grid, retains physical row/column coordinates and the source inside/outside key set, and reassigns "
             "inside keys to those fingers. It is an explicit adaptation, not an upstream-verified ergonomic model. "
             "Its canonical-baseline J1 can differ from the published board's independently chosen encoding/fingering.", ""]
    for scenario in ("traditional", "model-optimal"):
        summary = result["public_summary"][scenario]
        lines += ["## " + scenario + " fingering: equal-weight held-out averages", "",
                  "| Layout | J1 | Dvorak-7 bounds | Engram avg4 bounds | Engram order bounds | Pair coverage | Escaped text units |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for name, values in sorted(summary.items(), key=lambda p: (p[1]["J1"], p[0])):
            intervals = [f"{values[m]['lower']:.6f}–{values[m]['upper']:.6f}" for m in (*METRICS, "engram_order")]
            lines.append(f"| {name} | {values['J1']:.6f} | " + " | ".join(intervals) +
                         f" | {100*values['coverage']:.3f}% | {100*values['escape_share']:.3f}% |")
        lines += ["", "Each corpus contributes one third: Wikipedia held-out, newspaper held-out and BARD novel held-out. "
                  "Scores for each source are in scores.csv and scores.json.gz; averages do not replace the source-specific comparisons.", ""]
        comparison = result["comparisons"][scenario]
        lines += ["### Agreement and reversals", ""]
        for metric in (*METRICS, "engram_order"):
            decided = [r for r in comparison if r[metric]["higher"]]
            agree = sum(r[metric]["higher"] == r["lower_J1"] for r in decided)
            reversals = [r for r in decided if r[metric]["higher"] != r["lower_J1"]]
            lines.append(f"- {metric}: {len(decided)}/28 pairwise orders are separated by coverage bounds; "
                         f"{agree} agree with J1 and {len(reversals)} reverse it. "
                         "Unseparated intervals remain unresolved.")
            for r in reversals:
                lines.append(f"  - {r[metric]['higher']} has higher {metric}; {r['lower_J1']} has lower J1 "
                             f"({r['a']} minus {r['b']}: {r[metric]['a_minus_b'][0]:+.6f} to {r[metric]['a_minus_b'][1]:+.6f}).")
        lines += ["", "### Why Jhor and Goti differ", "",
                  "Component intervals below are equal-weight means; higher means the source rule awards more credit.", "",
                  "| Criterion | Jhor bounds | Goti bounds |", "| --- | --- | --- |"]
        rows = [r for r in result["scores"] if r["public"] and r["scenario"] == scenario and r["name"] in ("Kala Jhor", "Kala Goti")]
        for criterion in sorted(rows[0]["mechanics"]["bounds"]):
            if criterion in METRICS:
                continue
            values = []
            for name in ("Kala Jhor", "Kala Goti"):
                group = [r for r in rows if r["name"] == name]
                lo = sum(r["mechanics"]["bounds"][criterion]["lower"] for r in group)/len(group)
                hi = sum(r["mechanics"]["bounds"][criterion]["upper"] for r in group)/len(group)
                values.append(f"{lo:.6f}–{hi:.6f}")
            lines.append("| " + criterion + " | " + " | ".join(values) + " |")
        lines += ["", "### Frequent transitions that lose credit", "",
                  "Wikipedia held-out examples show the largest frequency-weighted deficits from the maximum value 1. "
                  "Each contribution is count × (1 − pair score) / all non-space pairs; it is explanatory accounting, "
                  "not a measured discomfort estimate. Full saved top contributions and unsupported pairs are in scores.json.gz.", "",
                  "| Layout | Model | Transition | Count | Deficit contribution |", "| --- | --- | --- | --- | --- |"]
        for row in rows:
            if row["corpus"] != "bnwiki/heldout":
                continue
            for metric in METRICS:
                for pair in row["mechanics"]["top_deficits"][metric][:3]:
                    transition = " → ".join("/".join(pair[k]) for k in ("from", "to"))
                    lines.append(f"| {row['name']} | {metric} | {transition} | {pair['count']} | {pair[metric+'_deficit']:.6f} |")
        lines.append("")
    lines += ["## Every layout and every corpus", "",
              "| Layout | Text | Fingering | Dvorak-7 bounds | Engram avg4 bounds | Engram order bounds |",
              "| --- | --- | --- | --- | --- | --- |"]
    for row in result["scores"]:
        if not row["public"]:
            continue
        bounds = [row["mechanics"]["bounds"][m] for m in METRICS] + [row["engram_order"]["bounds"]]
        lines.append(f"| {row['name']} | {row['corpus']} | {row['scenario']} | " +
                     " | ".join(f"{b['lower']:.6f}–{b['upper']:.6f}" for b in bounds) + " |")
    lines += ["", "## Retained search candidates", "",
              f"{len(result['candidates'])} distinct A/D maps retain provenance for "
              f"{result['stored_search_run_count']} original search starts, earlier bests, polish and confirmation. "
              "All held-out mechanics are reported, including non-public maps. Candidate comparisons and diagnostic "
              "frontiers use only the existing 50/50 training mix and traditional fingering, separately by style. "
              "A map dominates only if its J1 is no higher and both pair-model lower bounds exceed or equal the "
              "other map's upper bounds, with a strict improvement in at least one dimension. "
              "Trigram order is reported but does not select candidates. No new search or replacement layout was produced.", ""]
    for style in ("A", "D"):
        rows = [c for c in result["candidates"] if c["style"] == style]
        frontier = [c for c in rows if c["training_mechanics_frontier"]]
        lines.append(f"- Style {style}: {len(rows)} maps; {len(frontier)} on the conservative training trade-off frontier.")
    lines += ["", "These maps were found under J1; they do not establish best-found or optimal layouts under the new "
              "models. Known held-out benchmarks are used for exploratory comparison, not fresh confirmatory validation. "
              "The source rules share several characteristics with J1, so agreement is robustness to some assumptions "
              "rather than independent scientific validation. No original Phase 4 certificate transfers.", "",
              "## Challenge and website use", "",
              "Source-derived pair mechanics can explain reversals and component trade-offs, so they are suitable for "
              "optional challenge diagnostics. The official J1 objective, acceptance, ties, ranking and DATA_VERSION "
              "remain the published season. Challenge files need only the committed pair counts. Trigram evaluation "
              "is shown when committed style triple counts are available; it is separate from the official score. "
              "The website presents coverage bounds and scope, alongside the original diagnostic and preference limitations.", "",
              "## Reproduce and verification", "",
              "```powershell", '$env:PYTHONPATH = "src"',
              "python -m bangla_dh.experimental.mechanics_run --out work/evaluator-experiments/mechanics-repeat --workers 4",
              "python -m unittest discover -s tests", "```", "",
              "The committed derived triple caches let the comparison rerun without corpus downloads. "
              "Use --rebuild-counts to independently recreate them from the pinned local token tables. "
              "Source refresh is explicit: python -m bangla_dh.experimental.mechanics_sources --fetch. "
              "Output directories must be new; all writers use the repository guard. "
              "Source-fidelity checks, corpus/code/output SHA-256 hashes and original-resource preservation checks "
              "are in source-fidelity.json and run-manifest.json.", ""]
    return "\n".join(lines)


def run(out=DEFAULT, workers=4, rebuild_counts=False, counts_from=DEFAULT):
    if not 1 <= workers <= 16:
        raise ValueError("workers must be 1 through 16")
    before = protected_hashes()
    counts_from = Path(counts_from).resolve()
    target = new_run_directory(out)
    fidelity = audit()
    written = [write_json(target / "source-fidelity.json", fidelity)]
    inputs = [SOURCE / "source-lock.json", *[SOURCE / f["file"] for f in read_json(SOURCE / "source-lock.json")["files"]]]
    candidates, paths = load_candidates(True)
    entries = baselines.load_registry()
    inputs += paths + [baselines.REGISTRY, *MODELS.values(), PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json"]
    inputs += [baselines.source_path(e) for e in entries]
    models = {s: KeyModel.from_grid(p) for s, p in MODELS.items()}
    corpora = (*TRAIN, *HELDOUT)
    inputs += [unit_path(c) for c in corpora] + [frequency_path(s, c) for s in ("A", "D") for c in corpora]
    jobs = [("style", s, c) for s in ("A", "D") for c in corpora]
    jobs += [("baseline", e, c) for e in entries for c in HELDOUT]
    caches = {}
    futures = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for kind, identity, corpus in jobs:
            name = identity if kind == "style" else identity["name"]
            slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            filename = f"{kind}-{slug}-{corpus.replace('/', '-')}.json.gz"
            saved = Path(counts_from) / "counts" / filename
            if not saved.exists():
                saved = saved.with_suffix("")
            key = (kind, name, corpus)
            if saved.exists() and not rebuild_counts:
                manifest = read_json(Path(counts_from) / "run-manifest.json")
                from ..reference import sha256_file
                relative = saved.relative_to(PROJECT_ROOT).as_posix()
                if sha256_file(saved) != manifest["output_sha256"][relative]:
                    raise ValueError("committed triple-cache hash mismatch")
                cache = read_counts(saved)
                record = read_json(unit_path(corpus))
                if cache["token_table_sha256"] != record["token_table_sha256"]:
                    raise ValueError("cached triples use different token data")
                caches[key] = cache
            else:
                futures[pool.submit(build_job, kind, identity, corpus)] = (key, filename)
        for future in as_completed(futures):
            key, filename = futures[future]
            tables, triples = future.result()
            record = read_json(unit_path(key[2]))
            cache = {"kind": key[0], "identity": key[1], "corpus": key[2],
                     "token_table_sha256": record["token_table_sha256"], "action_tables": tables.json(),
                     "triples": triples_json(triples), "boundaries": "within token; space/escape breaks; repeats retained",
                     "action_counts_verified": True}
            caches[key] = cache
            inputs.append(PROJECT_ROOT / record["token_table"])
            print(f"Counted {key[0]} {key[1]} {key[2]}: {tables.round_trip_types} token types", flush=True)
        for key, cache in sorted(caches.items()):
            kind, name, corpus = key
            slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            path = target / "counts" / f"{kind}-{slug}-{corpus.replace('/', '-')}.json.gz"
            with gzip_text_writer(path) as stream:
                json.dump(cache, stream, ensure_ascii=False, separators=(",", ":"))
                stream.write("\n")
            written.append(path)
            # Scoring consumes exactly these copied, verified derived counts.
            # Keep manifests reproducible even when the cache came from work/.
            inputs.append(path)
    result = {"season": "e2", "source_fidelity": fidelity, "scores": [], "candidates": [],
              "stored_search_run_count": sum(o["kind"] == "runs" for c in candidates for o in c.origins),
              "public_summary": {}, "comparisons": {}, "published_season_changed": False}
    style_triples = {(s, c): triples_from_json(caches["style", s, c]["triples"])
                     for s in ("A", "D") for c in corpora}
    for candidate in candidates:
        assignment = candidate.assignment()
        name = next((n for n in candidate.names if n.startswith("Kala ")), candidate.id)
        training = []
        for corpus in corpora:
            tables = from_style(read_json(frequency_path(candidate.style, corpus)), assignment)
            triples = map_triples(style_triples[candidate.style, corpus], assignment)
            for scenario, model in models.items():
                mechanics = evaluator(scenario)
                row = {"id": candidate.id, "name": name, "style": candidate.style, "public": name.startswith("Kala "),
                       "corpus": corpus, "scenario": scenario, "reference": j_reference(tables, model),
                       "diagnostics": diagnostics(tables, model), "mechanics": mechanics.score(tables),
                       "engram_order": mechanics.score_triples(triples)}
                if corpus in HELDOUT:
                    result["scores"].append(row)
                elif scenario == "traditional":
                    training.append(row)
        summary = candidate.json()
        summary["training"] = averaged(training)[name]
        result["candidates"].append(summary)
        if len(result["candidates"]) % 10 == 0:
            print(f"Scored {len(result['candidates'])}/{len(candidates)} retained maps", flush=True)
    history = read_json(PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json")
    from .actions import ActionTables
    for entry in entries:
        for corpus in HELDOUT:
            cache = caches["baseline", entry["name"], corpus]
            tables = ActionTables.from_json(cache["action_tables"])
            expected = history["baselines"][entry["name"]]["scores"][corpus]["traditional_unrounded"]
            actual = j_reference(tables, models["traditional"])
            if any(not math.isclose(actual[k], expected[k], rel_tol=0, abs_tol=1e-10) for k in ("J0", "J1")):
                raise ValueError("new baseline extraction differs from historical J0/J1")
            triples = triples_from_json(cache["triples"])
            for scenario, model in models.items():
                mechanics = evaluator(scenario)
                result["scores"].append({"id": "baseline:" + entry["name"], "name": entry["name"], "style": None,
                    "public": True, "corpus": corpus, "scenario": scenario, "reference": j_reference(tables, model),
                    "diagnostics": diagnostics(tables, model), "mechanics": mechanics.score(tables),
                    "engram_order": mechanics.score_triples(triples)})
    for style in ("A", "D"):
        rows = [c for c in result["candidates"] if c["style"] == style]
        def dominates(a, b):
            x, y = a["training"], b["training"]
            return x["J1"] <= y["J1"] and all(x[m]["lower"] >= y[m]["upper"] for m in METRICS) and (
                x["J1"] < y["J1"] or any(x[m]["lower"] > y[m]["upper"] for m in METRICS))
        for row in rows:
            row["training_mechanics_frontier"] = not any(a["id"] != row["id"] and dominates(a, row) for a in rows)
    result["scores"].sort(key=lambda r: (r["id"], r["corpus"], r["scenario"]))
    for scenario in models:
        result["public_summary"][scenario] = averaged([r for r in result["scores"] if r["public"] and r["scenario"] == scenario])
        result["comparisons"][scenario] = comparisons(result["public_summary"][scenario])
    rows = []
    for row in result["scores"]:
        flat = {k: row[k] for k in ("id", "name", "style", "public", "corpus", "scenario")}
        flat.update({"J1": row["reference"]["J1"], "pair_coverage": row["mechanics"]["pair_coverage"],
                     "triple_coverage": row["engram_order"]["coverage"], "escaped_unit_share": row["diagnostics"]["escaped_unit_share"]})
        for m in METRICS:
            flat.update({m + "_" + side: row["mechanics"]["bounds"][m][side] for side in ("lower", "upper")})
        flat.update({"engram_order_" + side: row["engram_order"]["bounds"][side] for side in ("lower", "upper")})
        rows.append(flat)
    if protected_hashes() != before:
        raise ValueError("protected published scientific files changed")
    verify_sources()
    result["checks"] = {"source_fidelity": True, "frozen_style_counts": True, "baseline_historical_scores": True,
                        "original_scientific_files_byte_identical": True}
    scores_path = target / "scores.json.gz"
    with gzip_text_writer(scores_path) as stream:
        json.dump(result, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")
    public_rows = []
    for row in result["scores"]:
        if row["public"]:
            public_rows.append({k: row[k] for k in ("name", "corpus", "scenario", "reference", "diagnostics")} | {
                "mechanics": {k: row["mechanics"][k] for k in ("bounds", "pair_coverage", "top_deficits")},
                "engram_order": {k: row["engram_order"][k] for k in ("bounds", "coverage")}})
    public = {"season": "e2", "layout_count": len(entries)+2, "candidate_count": len(candidates),
              "source_fidelity": fidelity, "public_summary": result["public_summary"],
              "comparisons": result["comparisons"], "corpus_scores": public_rows, "checks": result["checks"]}
    written += [scores_path, write_json(target / "public-summary.json", public),
                write_json(target / "candidates.json", result["candidates"]),
                write_text(target / "scores.csv", csv_text(rows, list(rows[0]))), write_text(target / "REPORT.md", render(result))]
    inputs += [p for p in (PROJECT_ROOT / "src/bangla_dh").rglob("*.py")]
    revision, clean = repo_state()
    write_json(target / "run-manifest.json", {"season": "e2", "published_season_changed": False,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "git_revision": revision,
        "working_tree_clean": clean, "python": platform.python_version(), "seeds": "no new search; retained origins in candidates.json",
        "parameters": {"workers": workers, "rebuild_counts": rebuild_counts, "corpora": list(corpora),
            "training_weights": {c: 0.5 for c in TRAIN}, "heldout_weights": {c: 1/3 for c in HELDOUT},
            "scenarios": list(models), "layers": "physical-key projection; Shift effort excluded; AltGr unsupported",
            "pair_denominator": "all non-space action pairs, including unsupported keys and repeats",
            "triple_denominator": "all within-token action triples, including unsupported keys and repeats",
            "unknown_values": "retain mass; bound each criterion in 0..1", "official_ranking_effect": "none"},
        "input_sha256": hash_outputs(sorted(set(inputs))), "output_sha256": hash_outputs(written),
        "protected_original_sha256": before, "checks": result["checks"]})
    print(f"Scored {len(candidates)} retained maps and {len(entries)} baselines. Report: {target / 'REPORT.md'}", flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=str(DEFAULT))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--rebuild-counts", action="store_true")
    parser.add_argument("--counts-from", type=Path, default=DEFAULT,
                        help="a previous verified run's derived counts; defaults to the published run")
    args = parser.parse_args(argv)
    try:
        run(args.out, args.workers, args.rebuild_counts, args.counts_from)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Mechanics evaluation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
