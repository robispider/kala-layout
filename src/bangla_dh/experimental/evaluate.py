"""Season e1 driver: additional read-only evaluation, never an optimizer."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import math
import platform
from pathlib import Path

from ..bangla.grammar import Action
from ..paths import PROJECT_ROOT, write_json, write_text, repo_state, hash_outputs
from ..reference import sha256_file
from ..scoring import baselines
from ..scoring.j0 import score_units
from ..scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from .actions import from_style, from_tokens, j_reference, diagnostics
from .inputs import (TRAIN, HELDOUT, read_json, frequency_path, unit_path, token_rows, load_candidates)
from .preferences import PairPreferences, SOURCE
from .report import render, csv_text
from .safety import new_run_directory, protected_hashes

MODELS = {"model-optimal": ANSI_GRID, "traditional": ANSI_TRADITIONAL_GRID}


def _baseline_job(entry, corpus):
    record = read_json(unit_path(corpus))
    tokens = PROJECT_ROOT / record["token_table"]
    if sha256_file(tokens) != record["token_table_sha256"]:
        raise ValueError("baseline token table hash mismatch")
    km = baselines.keymap(entry, KeyModel.from_grid(ANSI_TRADITIONAL_GRID))
    tables = from_tokens(token_rows(tokens), km, record)
    history = read_json(PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json")
    old = history["baselines"][entry["name"]]["scores"][corpus]["traditional_unrounded"]
    current = j_reference(tables, KeyModel.from_grid(ANSI_TRADITIONAL_GRID))
    if not all(math.isclose(current[k], old[k], rel_tol=0, abs_tol=1e-10) for k in ("J0", "J1")):
        raise ValueError("canonical baseline scores disagree with historical traditional scores")
    return tables


def _row(cid, name, style, public, corpus, scenario, tables, model, preference):
    return {"id": cid, "name": name, "style": style, "public": public,
            "corpus": corpus, "scenario": scenario,
            "reference": j_reference(tables, model),
            "diagnostics": diagnostics(tables, model), "preference": preference.score(tables, model)}


def descriptive_frontier(rows):
    """Training-only descriptive frontier. Preference scores cannot enter."""
    def vector(row):
        return (row["training_J1"], row["training_shift_per_unit"], row["training_sfb_per_unit"])
    def dominates(a, b):
        return all(x <= y + 1e-12 for x, y in zip(a, b)) and any(x < y - 1e-12 for x, y in zip(a, b))
    return sorted(r["id"] for r in rows if not any(
        o["id"] != r["id"] and dominates(vector(o), vector(r)) for o in rows))


def run(command, out, workers=4, corpora=HELDOUT, include_baselines=True, log=print):
    if workers < 1 or workers > 16:
        raise ValueError("workers must be 1 through 16")
    if not corpora or len(set(corpora)) != len(corpora) or any(c not in HELDOUT for c in corpora):
        raise ValueError("choose distinct known held-out corpora")
    preference = PairPreferences()
    evidence = preference.evidence()
    protected = protected_hashes()
    target = new_run_directory(out)
    inputs = [SOURCE / "source-lock.json", *[SOURCE / f["file"] for f in preference.lock["files"]],
              ANSI_GRID, ANSI_TRADITIONAL_GRID, PROJECT_ROOT / "data/problem-v1.json",
              PROJECT_ROOT / "data/bangla-symbols-v1.json"]
    result = {"season": "e1", "command": command, "evidence": evidence, "scores": [], "candidates": [],
              "checks": {"pinned_source_lookup": True}, "stored_search_run_count": 0,
              "comfort_ranking": None, "comfort_frontier": None, "comfort_shortlist": None}
    written = [write_json(target / "evidence.json", evidence)]
    if command != "audit":
        candidates, paths = load_candidates(command == "candidates")
        inputs += paths
        models = {k: KeyModel.from_grid(v) for k, v in MODELS.items()}
        frequencies = {(s, c): read_json(frequency_path(s, c)) for s in ("A", "D") for c in (*TRAIN, *corpora)}
        inputs += [frequency_path(s, c) for s, c in frequencies]
        summaries = []
        for candidate in candidates:
            training = {}
            for corpus in (*TRAIN, *corpora):
                record = frequencies[candidate.style, corpus]
                tables = from_style(record, candidate.assignment())
                for scenario, model in models.items():
                    reference = j_reference(tables, model)
                    assignment = {k: Action(*v, k) for k, v in candidate.assignment().items()}
                    independent = score_units(assignment,
                        {k: v / record["N"] for k, v in record["label_counts"].items()},
                        {(a, b): n / record["N"] for a, b, n in record["pair_counts"]}, model)
                    if not all(math.isclose(reference[k], independent[k], rel_tol=0, abs_tol=1e-11)
                               for k in ("J0", "J1")):
                        raise ValueError("action reference disagrees with published table scorer")
                    row = _row(candidate.id, ", ".join(candidate.names) or candidate.id,
                               candidate.style, any(n.startswith("Kala ") for n in candidate.names),
                               corpus, scenario, tables, model, preference)
                    if corpus in TRAIN and scenario == "model-optimal":
                        training[corpus] = row
                    if corpus in corpora:
                        result["scores"].append(row)
            summary = candidate.json()
            summary["training_J1"] = sum(r["reference"]["J1"] for r in training.values()) / 2
            summary["training_shift_per_unit"] = sum(r["reference"]["M"] for r in training.values()) / 2
            summary["training_sfb_per_unit"] = sum(r["diagnostics"]["same_finger_different_key_per_unit"] for r in training.values()) / 2
            # M is weighted Shift effort, not raw Shift count: keep the name explicit.
            summary["training_shift_effort_per_unit"] = summary.pop("training_shift_per_unit")
            summaries.append(summary)
            result["stored_search_run_count"] += sum(o["kind"] == "runs" for o in candidate.origins)
        # Frontier uses M (existing model's Shift effort), not an invented balance weight.
        for style in ("A", "D"):
            part = [s for s in summaries if s["style"] == style]
            adapted = [{**s, "training_shift_per_unit": s["training_shift_effort_per_unit"]} for s in part]
            frontier = set(descriptive_frontier(adapted))
            for s in part:
                s["descriptive_training_frontier"] = s["id"] in frontier
        result["candidates"] = summaries
        result["checks"].update({"candidate_inventory_and_bijection": True,
                                  "action_reference_matches_existing_scorer": True})
        log(f'Scored {len(candidates)} distinct style layouts; preference ranking withheld.', flush=True)
        if include_baselines:
            entries = baselines.load_registry()
            inputs += [baselines.REGISTRY, PROJECT_ROOT / "results/phase3-crosscheck/crosscheck.json"]
            inputs += [baselines.source_path(e) for e in entries]
            inputs += [unit_path(c) for c in corpora]
            inputs += [PROJECT_ROOT / read_json(unit_path(c))["token_table"] for c in corpora]
            jobs = [(e, c) for e in entries for c in corpora]
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(_baseline_job, e, c): (e, c) for e, c in jobs}
                for future in as_completed(futures):
                    entry, corpus = futures[future]
                    tables = future.result()
                    cache_name = entry["name"].lower().replace(" ", "-").replace("(", "").replace(")", "")
                    written.append(write_json(target / "action-tables" / f'{cache_name}-{corpus.replace("/", "-")}.json', tables.json()))
                    for scenario, model in models.items():
                        result["scores"].append(_row("baseline:" + entry["name"], entry["name"], None, True,
                                                     corpus, scenario, tables, model, preference))
                    log(f'Verified {entry["name"]}: {corpus} ({tables.round_trip_types} token types).', flush=True)
            result["checks"]["all_baseline_NFC_round_trips"] = True
            result["checks"]["baseline_traditional_reference_matches_history"] = True
        result["scores"].sort(key=lambda r: (r["id"], r["corpus"], r["scenario"]))
        rows = [{"id": r["id"], "name": r["name"], "corpus": r["corpus"], "scenario": r["scenario"],
                 "J0": r["reference"]["J0"], "J1": r["reference"]["J1"],
                 "partial_pair_preference": r["preference"]["conditional_pair_preference"],
                 "pair_support": r["preference"]["supported_pair_share"],
                 "escaped_unit_share": r["diagnostics"]["escaped_unit_share"],
                 "keystrokes_per_non_space_unit": r["diagnostics"]["keystrokes_per_non_space_unit"],
                 "preference_ranking_allowed": False} for r in result["scores"]]
        written += [write_text(target / "scores.csv", csv_text(rows, list(rows[0]))),
                    write_json(target / "candidates.json", result["candidates"])]
        ranks = []
        for style in ("A", "D"):
            ordered = sorted((c for c in summaries if c["style"] == style), key=lambda c: (c["training_J1"], c["id"]))
            for rank, c in enumerate(ordered, 1):
                ranks.append({"style": style, "id": c["id"], "training_J1": c["training_J1"],
                              "J1_order": rank, "descriptive_frontier": c["descriptive_training_frontier"],
                              "comfort_rank": None})
        written.append(write_text(target / "rankings.csv", csv_text(ranks, list(ranks[0]))))
    if protected_hashes() != protected:
        raise ValueError("a protected original input/output changed during evaluation")
    result["checks"]["original_files_byte_identical"] = True
    written += [write_json(target / "scores.json", result), write_text(target / "REPORT.md", render(result))]
    inputs += [p for p in (PROJECT_ROOT / "src/bangla_dh").rglob("*.py")]
    revision, clean = repo_state()
    manifest = {"season": "e1", "published_season_changed": False, "command": command,
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "git_revision": revision, "working_tree_clean": clean, "python": platform.python_version(),
                "parameters": {"corpora": list(corpora), "workers": workers, "include_baselines": include_baselines,
                    "training_weights": {c: 0.5 for c in TRAIN}, "scenarios": list(MODELS),
                    "canonical_encoding": "minimum presses; traditional-grid key-effort ties, held fixed across scorers",
                    "pair_boundaries": "directed and repeat-preserving; escapes break chains; explicit spaces; no document crossing",
                    "preference_policy": "base-layer source pairs with traditional matching fingers; no imputation",
                    "frontier": "per-style training-only J1, existing M, same-finger/different-key count per unit",
                    "selection": "no preference ranking, comfort frontier, shortlist or new search"},
                "input_sha256": hash_outputs(list(set(inputs))), "output_sha256": hash_outputs(written),
                "protected_original_sha256": protected, "checks": result["checks"], "evidence": evidence}
    write_json(target / "run-manifest.json", manifest)
    log(f'Report: {target / "REPORT.md"}', flush=True)
    return result
