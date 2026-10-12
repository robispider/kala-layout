"""Optional reports for challenge files; official scoring and ranking stay separate."""
from __future__ import annotations

import argparse
import datetime
from fractions import Fraction
import hashlib
import math
from pathlib import Path
import platform
import sys

from .. import challenge
from ..paths import PROJECT_ROOT, hash_outputs, repo_state, write_json, write_text
from ..phase3 import problem_fixed
from ..reference import sha256_file
from ..scoring.model import KeyModel
from ..search.problem import load_problem
from .actions import from_style, j_reference, diagnostics
from .evaluate import MODELS
from .inputs import TRAIN, HELDOUT, frequency_path, read_json, validate_layout
from .preferences import PairPreferences, SOURCE
from .report import csv_text
from .safety import new_run_directory, protected_hashes

MAX_BYTES = 64_000


def _markup(value):
    """Submission names are data, not Markdown or HTML."""
    value = " ".join(str(value).split())
    for char in ("\\", "`", "*", "_", "[", "]", "|", "#"):
        value = value.replace(char, "\\" + char)
    return value.replace("<", "&lt;").replace(">", "&gt;")


def _score_map(style, placed, corpora, models, preference, public, data, public_model):
    validate_layout(style, placed)
    assignment = {**placed, **problem_fixed(load_problem())}
    rows = []
    official_actions = {**placed, **{k: tuple(v) for k, v in data["styles"][style]["fixed"].items()}}
    for corpus in (*TRAIN, *HELDOUT):
        record = corpora[style, corpus]
        tables = from_style(record, assignment)
        source = data["styles"][style]["corpora" if corpus in TRAIN else "heldout"][corpus]
        expected = float(public.corpus_j1(source, official_actions, public_model))
        for scenario, model in models.items():
            reference = j_reference(tables, model)
            if scenario == "model-optimal" and not math.isclose(reference["J1"], expected, rel_tol=0, abs_tol=1e-11):
                raise ValueError("diagnostic action score disagrees with the official challenge corpus score")
            rows.append({"corpus": corpus, "scenario": scenario,
                         "reference": reference, "diagnostics": diagnostics(tables, model),
                         "preference": preference.score(tables, model)})
    return rows


def render(result):
    lines = ["# Optional challenge diagnostics", "",
             "**Official J1, submission acceptance and leaderboard ordering are unchanged.**", "",
             "The preference table is incomplete and lacks independently reproduced predictive/Bangla validation. "
             "Its supported-pair diagnostic cannot rank whole layouts. No comfort rank or recommendation is produced.", "",
             "The counts below retain repeats and directed pairs. Shift share excludes space; finger load excludes "
             "modifier presses. Same-finger moves count different physical keys. J1 is effort per text unit including space.", ""]
    refs = {r["style"]: r for r in result["references"]}
    for item in result["submissions"]:
        official = item["official"]
        lines += ["## " + _markup(item["file"]) + ": " + _markup(item["name"]), "",
                  f'Style {item["style"]}; official training J1 **{official["J1"]:.6f}**; '
                  f'{official["difference_vs_reference_percent"]:+.4f}% versus the reference. '
                  f'Beats reference: {official["beats_reference"]}.', "",
                  "The exact official score is stored in submissions.json. Numbers here are descriptive, "
                  "not additional challenge objectives. The model-optimal scenario is the official one; "
                  "traditional fingering is a separate scenario.", "",
                  "| Text | Fingering | J1 change vs reference | Same-finger moves per unit (yours / reference) | "
                  "Repeat share of pairs | Shift share of presses | Preference-table support |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        lookup = {(r["corpus"], r["scenario"]): r for r in refs[item["style"]]["scores"]}
        for row in item["scores"]:
            base = lookup[row["corpus"], row["scenario"]]
            d, p = row["diagnostics"], row["preference"]
            delta = 100 * (row["reference"]["J1"] / base["reference"]["J1"] - 1)
            repeat = 100*d["same_physical_key_repeat_count"] / d["non_space_pair_count"] if d["non_space_pair_count"] else 0
            lines.append(f'| {row["corpus"]} | {row["scenario"]} | {delta:+.4f}% | '
                f'{d["same_finger_different_key_per_unit"]:.6f} / '
                f'{base["diagnostics"]["same_finger_different_key_per_unit"]:.6f} | '
                f'{repeat:.2f}% | {100*d["shift_share_of_non_space_presses"]:.2f}% | '
                f'{100*p["supported_pair_share"]:.2f}% |')
        lines += ["", "Detailed per-finger counts, coverage gaps and partial preference values are in submissions.json. "
                  "The partial values refer to different supported subsets and must not be compared as total comfort scores.", ""]
    if result["problems"]:
        lines += ["## Files not evaluated", ""]
        for problem in result["problems"]:
            lines.append("- " + _markup(problem["file"]) + ": " + _markup("; ".join(problem["problems"])))
        lines.append("")
    lines += ["## Verification", "",
              "Each evaluated submission passed the official parser and frozen inventory/bijection check. "
              "Its exact mixed-training J1 matches the repository integer scorer; every model-optimal corpus "
              "score matches the official scorer. The original scientific inputs and outputs stayed byte-identical.", "",
              "Source/data/code hashes and policies are in run-manifest.json. The lookup benchmark verifies arithmetic "
              "only. Missing preference values are never replaced with zero or generated rules. "
              "This report has no effect on official scores, ties, duplicates, acceptance or leaderboard ordering.", ""]
    return "\n".join(lines)


def run(paths, out, *, accepted_pairs=None, log=print):
    """Generate diagnostics. accepted_pairs limits leaderboard reports to accepted entries."""
    public = challenge.load_scorer(challenge.SCRIPT)
    data, data_hash = public.load_data()
    public_model = public.Model(data)
    preference = PairPreferences()
    evidence = preference.evidence()
    before = protected_hashes()
    target = new_run_directory(out)
    problem = load_problem()
    weights = {k: Fraction(v) for k, v in data["objective"]["weights"].items()}
    if set(weights) != set(TRAIN):
        raise ValueError("experimental bridge expects the frozen Wikipedia/newspaper training mix")
    models = {k: KeyModel.from_grid(v) for k, v in MODELS.items()}
    corpora = {(s, c): read_json(frequency_path(s, c)) for s in ("A", "D") for c in (*TRAIN, *HELDOUT)}
    result = {"season": "e1", "command": "submission-diagnostics", "evidence": evidence,
              "official_data_version": data["version"], "official_data_sha256": data_hash,
              "submissions": [], "references": [], "problems": [], "comfort_rank": None,
              "ranking_effect": "none", "checks": {"source_lookup": True}}
    input_files = []
    used_styles = set()
    for filename in paths:
        path = Path(filename)
        try:
            if path.stat().st_size > MAX_BYTES:
                raise ValueError(f"file larger than {MAX_BYTES} bytes")
            initial_hash = sha256_file(path)
            submission = public.read_layout_file(path)
            if sha256_file(path) != initial_hash:
                raise ValueError("input changed during reading")
            input_files.append({"path": path.resolve().as_posix(), "sha256": initial_hash})
            official = public.evaluate(submission, data, data_hash, public_model)
            if not official["valid"]:
                result["problems"].append({"file": path.name, "problems": official["problems"]})
                continue
            if accepted_pairs is not None and (path.name, official["layout_sha256"]) not in accepted_pairs:
                result["problems"].append({"file": path.name,
                                          "problems": ["not an accepted leaderboard entry (reference, duplicate or rejected)"]})
                continue
            style, placed, errors = public.parse_layout(submission, data)
            validate_layout(style, placed)
            exact = challenge.exact_j1(style, placed, weights, problem)
            if exact != Fraction(official["J1_exact"]):
                raise ValueError("official and integer-model J1 disagree")
            scores = _score_map(style, placed, corpora, models, preference, public, data, public_model)
            result["submissions"].append({"file": path.name, "name": str(official["name"] or path.name),
                "style": style, "layout_sha256": official["layout_sha256"], "official": official,
                "scores": scores})
            used_styles.add(style)
        except (OSError, ValueError, KeyError) as error:
            result["problems"].append({"file": path.name, "problems": [str(error)]})
    for style in sorted(used_styles):
        reference = {"style": style, "layout": data["styles"][style]["reference"]["layout"]}
        _, placed, _ = public.parse_layout(reference, data)
        result["references"].append({"style": style, "name": "Kala Goti" if style == "A" else "Kala Jhor",
            "scores": _score_map(style, placed, corpora, models, preference, public, data, public_model)})
    result["checks"]["evaluated_submission_count"] = len(result["submissions"])
    result["checks"]["official_integer_and_action_scores_agree"] = True
    if protected_hashes() != before:
        raise ValueError("a protected scientific input/output changed")
    result["checks"]["scientific_inputs_outputs_byte_identical"] = True
    written = [write_json(target / "submissions.json", result),
               write_json(target / "evidence.json", evidence), write_text(target / "REPORT.md", render(result))]
    rows = []
    for item in result["submissions"]:
        for row in item["scores"]:
            d, p = row["diagnostics"], row["preference"]
            rows.append({"file": item["file"], "style": item["style"], "corpus": row["corpus"],
                "scenario": row["scenario"], "J1": row["reference"]["J1"],
                "same_finger_different_key_per_unit": d["same_finger_different_key_per_unit"],
                "same_physical_key_repeat_count": d["same_physical_key_repeat_count"],
                "shift_share": d["shift_share_of_non_space_presses"],
                "pair_support": p["supported_pair_share"],
                "partial_pair_preference": p["conditional_pair_preference"], "preference_ranking_allowed": False})
    if rows:
        written.append(write_text(target / "scores.csv", csv_text(rows, list(rows[0]))))
    inputs = [challenge.SCRIPT, SOURCE / "source-lock.json", *[SOURCE / f["file"] for f in preference.lock["files"]],
              PROJECT_ROOT / "data/problem-v1.json", PROJECT_ROOT / "data/bangla-symbols-v1.json",
              *MODELS.values(), *[frequency_path(s,c) for s,c in corpora],
              *[p for p in (PROJECT_ROOT / "src/bangla_dh").rglob("*.py")]]
    revision, clean = repo_state()
    write_json(target / "run-manifest.json", {"season": "e1", "command": "submission-diagnostics",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_revision": revision, "working_tree_clean": clean, "python": platform.python_version(),
        "official_data_version": data["version"], "official_data_sha256": data_hash,
        "parameters": {"training_weights": {k:str(v) for k,v in weights.items()},
            "corpora": list((*TRAIN,*HELDOUT)), "scenarios": list(MODELS),
            "input_format": "official challenge parser: UTF-8/BOM or UTF-16, dotted circles and NFC accepted",
            "preference": "supported base-layer source pairs only; no imputation or comfort ranking",
            "leaderboard_accepted_only": accepted_pairs is not None, "ranking_effect": "none"},
        "submission_inputs": input_files, "input_sha256": hash_outputs(inputs),
        "output_sha256": hash_outputs(written), "protected_scientific_sha256": before,
        "checks": result["checks"], "evidence": evidence})
    log(f'Optional diagnostics: {target / "REPORT.md"} (not used for ranking).')
    return result


def report_optional(paths, out, *, accepted_pairs=None):
    """Optional-report faults never change official verification/leaderboard status."""
    try:
        return run(paths, out, accepted_pairs=accepted_pairs)
    except Exception as error:
        print(f"Optional diagnostics unavailable: {type(error).__name__}: {error}. Official results are unchanged.")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--out", type=Path, required=True,
                        help="new directory under work/evaluator-experiments or results/evaluator-e1")
    args = parser.parse_args(argv)
    try:
        result = run(args.files, args.out)
        return 1 if result["problems"] else 0
    except (OSError, ValueError) as error:
        print(f"Diagnostics failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
