"""Challenge kit: a standalone scorer people can use to try to beat the
Bangla-DH A and D layouts (owner request, 11 October 2026).

``challenge-kit`` writes ``challenge/``:

* ``bangla_dh_challenge.py``: the public scorer (``challenge_template.py``
  with the data embedded, standard library only);
* ``README.md`` and ``USER_GUIDE.md``: landing page and guide for
  challengers (``challenge_guide.py``);
* ``A-reference.json``, ``D-reference.json``: the reference layouts as
  example submissions;
* ``challenge-data.json``: the embedded data, readable;
* ``run-manifest.json``.

The embedded data is what J1 needs and nothing else: the key model of the
model-optimal ANSI grid (efforts, fingers, rows, penalties, Shift keys), and
for each style and training text of the mixed search the text's N, the
keystroke count of every placed symbol and the count of every consecutive
pair of placed symbols. Counts are aggregate statistics; no text is included.
The objective and the reference layouts are those of ``mix-optimize``.

The build checks that the standalone scorer gives exactly (as rationals) the
integer model's J1 of the reference and earlier layouts, and the mixed
search's J1 to float precision.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import importlib.util
import json
import platform
import zlib
from fractions import Fraction
from pathlib import Path

from . import __version__
from .challenge_guide import readme, user_guide
from .crosscheck import RESULTS as CROSSCHECK, style_record
from .mix import HELDOUT, RESULTS as MIX, SEARCH as MIX_SEARCH, earlier_layouts, mixed_best_layout
from .paths import PROJECT_ROOT, repo_state, RESULTS_ROOT, hash_outputs, relative_to_project, write_json, write_text
from .phase3 import RESULTS as PHASE3, problem_fixed
from .reference import sha256_file
from .scoring.model import ANSI_GRID, KeyModel
from .search.integer import IntegerInstance
from .search.problem import PROBLEM_FILE, load_problem, slots

RESULTS = PROJECT_ROOT / "challenge"  # user-facing, top level of the repository
TEMPLATE = Path(__file__).with_name("challenge_template.py")
SCRIPT = RESULTS / "bangla_dh_challenge.py"
DATA_VERSION = "bangla-dh-shared-challenge-v1"
LEGACY_DATA_VERSION = "bangla-dh-challenge-v1"
STYLES = ("A", "D")


def _dec(value: float) -> str:
    return repr(float(value))


def build_data(problem: dict) -> dict:
    model = KeyModel.from_grid(ANSI_GRID)
    mix = {style: json.loads((MIX_SEARCH / f"{style}.json").read_text(encoding="utf-8")) for style in STYLES}
    weights = mix[STYLES[0]]["settings"]["frequencies"]
    if any(m["settings"]["frequencies"] != weights for m in mix.values()):
        raise ValueError("the styles were searched with different weights")
    fixed = problem_fixed(problem)
    keys_used = sorted({k for k, _ in slots()} | {k for k, _ in fixed.values()})
    data = {
        "version": LEGACY_DATA_VERSION,
        "objective": {
            "name": "J1",
            "weights": {name: str(Fraction(w).limit_denominator(1000)) for name, w in weights.items()},
            "description": "J1 = effort per character, lower is better: key effort + Shift + bigram penalties "
                           "(Colemak Mod-DH model, ANSI, model-optimal fingering), averaged "
                           + " + ".join(f"{Fraction(w).limit_denominator(1000)} x {n}" for n, w in weights.items())
                           + ". Same objective as the Bangla-DH mixed search of 10 October 2026.",
        },
        "model": {
            "grid": model.description,
            "keys": {k: [_dec(model.keys[k].effort), model.keys[k].finger, model.keys[k].row] for k in keys_used},
            "shift_keys": {name: _dec(model.effort(name)) for name in ("LSHIFT", "RSHIFT")},
            "same_finger": [_dec(x) for x in model.same_finger],
            "neighbour_by_outer_finger": [[_dec(x) for x in row] for row in model.neighbour],
        },
        "styles": {},
    }
    for style in STYLES:
        spec = problem["styles"][style]
        searched = spec["searched_symbols"]
        placed = set(searched) | set(fixed)
        corpora, heldout = {}, {}
        for names, target in ((list(weights), corpora), (list(HELDOUT), heldout)):
            for name in names:
                record, _, _ = style_record(style, name)
                labels = {s: c for s, c in record["label_counts"].items() if s in placed}
                pairs = [[a, b, c] for a, b, c in record["pair_counts"] if a != b and a in placed and b in placed]
                target[name] = {"N": record["N"], "labels": labels, "pairs": pairs}
        best = mix[style]["best"]
        layout = {key: ["", ""] for key in "QWERTYUIOPASDFGHJKLZXCVBNM"}
        for symbol, slot in best["layout"].items():
            key, layer = slot.split("/")
            layout[key][0 if layer == "base" else 1] = symbol
        data["styles"][style] = {
            "description": spec["description"], "symbols": searched,
            "fixed": {s: list(slot) for s, slot in fixed.items()}, "corpora": corpora, "heldout": heldout,
            "reference": {"name": f"Bangla-DH {style} (mixed search, 10 October 2026)", "layout": layout,
                          "J1_exact": None, "J1_search": best["J1"]},
        }
    data["public_layouts"] = public_layouts()
    return data


# Held-out texts in the order of the leaderboard columns.
HELDOUT_COLUMNS = {"bnwiki/heldout": "wikipedia", "newspaper/heldout": "newspaper", "bard-novel/heldout": "unseenNews"}


def public_layouts() -> dict:
    """The held-out leaderboard of Kala's layouts and the public fixed layouts (from ``kala-export``)."""
    board = json.loads((RESULTS_ROOT / "kala-keyboards" / "kala-jhor.json").read_text(encoding="utf-8"))["about"]["leaderboard"]
    return {"metric": board["metric"], "note": board["note"], "texts": HELDOUT_COLUMNS,
            "entries": [{"name": e["name"], "kind": e["kind"], "developer": e["developer"], "j1": e["j1"],
                         "average": e["average"], "fingering": e["fingering"]} for e in board["entries"]]}


def load_scorer(path: Path):
    spec = importlib.util.spec_from_file_location("bangla_dh_challenge_built", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exact_j1(style: str, layout: dict[str, tuple[str, str]], weights: dict, problem: dict) -> Fraction:
    """The integer model's J1 of a layout on the weighted training texts."""
    model = KeyModel.from_grid(ANSI_GRID)
    total = Fraction(0)
    for name, w in weights.items():
        record, _, _ = style_record(style, name)
        inst = IntegerInstance(problem["styles"][style]["searched_symbols"], slots(), problem_fixed(problem),
                               record, model)
        total += Fraction(w) * inst.to_j(inst.score(inst.perm_of(layout)))
    return total


def run_build(leaderboard: str | None = None) -> list[Path]:
    problem = load_problem()
    data = build_data(problem)
    weights = {n: Fraction(w) for n, w in data["objective"]["weights"].items()}
    checks = {}
    for style in STYLES:
        exact = exact_j1(style, mixed_best_layout(style), weights, problem)
        data["styles"][style]["reference"]["J1_exact"] = f"{exact.numerator}/{exact.denominator}"
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    blob = base64.b64encode(zlib.compress(raw, 9)).decode("ascii")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count('"@@DATA@@"') != 1:
        raise ValueError("template placeholder missing")
    written = [write_text(SCRIPT, template.replace('"@@DATA@@"', "(\n" + "\n".join(
        f'    "{blob[i:i + 100]}"' for i in range(0, len(blob), 100)) + "\n)"))]
    written.append(write_json(RESULTS / "challenge-data.json", data, indent=1))
    # Checks: the built script against the project's integer model and search.
    scorer = load_scorer(SCRIPT)
    loaded, data_sha256 = scorer.load_data()
    checks["embedded data equals the built data"] = loaded == json.loads(raw)
    for style in STYLES:
        layouts = {"mixed": mixed_best_layout(style), **earlier_layouts(style)}
        for name, layout in layouts.items():
            submission = {"style": style, "layout": _key_layout(layout)}
            result = scorer.evaluate(submission, loaded, data_sha256)
            expected = exact_j1(style, layout, weights, problem)
            checks[f"{style} {name}: valid and exactly the integer model's J1"] = (
                result["valid"] and Fraction(result["J1_exact"]) == expected)
        search_j1 = data["styles"][style]["reference"]["J1_search"]
        exact = Fraction(data["styles"][style]["reference"]["J1_exact"])
        checks[f"{style} reference equals the mixed search's J1"] = abs(float(exact) - search_j1) < 1e-9
    board = {e["name"]: e for e in loaded["public_layouts"]["entries"]}
    for style, name in (("A", "Kala Goti"), ("D", "Kala Jhor")):
        result = scorer.evaluate({"style": style, "layout": data["styles"][style]["reference"]["layout"]}, loaded,
                                 data_sha256)
        row = board[name]
        checks[f"{style} held-out J1 equals the {name} leaderboard row"] = all(
            abs(result["held_out"]["J1"][k] - row["j1"][k]) < 6e-5 for k in row["j1"]) and result["held_out"]["public_rank"] == {"A": 2, "D": 1}[style]
    bad = dict(_key_layout(mixed_best_layout("D")))
    bad["Q"], bad["W"] = bad["W"], ["ক", bad["Q"][1]]
    checks["an invalid layout is refused"] = not scorer.evaluate({"style": "D", "layout": bad}, loaded,
                                                                  data_sha256)["valid"]
    for style in STYLES:
        example = {"style": style, "name": f"Bangla-DH {style} reference",
                   "layout": data["styles"][style]["reference"]["layout"]}
        written.append(write_json(RESULTS / f"{style}-reference.json", example))
    written.append(write_text(RESULTS / "README.md", readme(data, data_sha256, leaderboard)))
    written.append(write_text(RESULTS / "USER_GUIDE.md", user_guide(data, data_sha256, scorer.SCRIPT_VERSION,
                                                                    leaderboard)))
    written.append(write_json(RESULTS / "run-manifest.json", manifest(written, data_sha256, checks)))
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    if not all(checks.values()):
        raise SystemExit(1)
    return written


def run_verify(paths: list[str], diagnostics: str | Path | None = None) -> int:
    """Re-check challenge layout files with the project's own scorers: the
    exact integer-model J1 (must equal the public scorer's) and J1 on the
    held-out texts no search has used."""
    from .crosscheck import score_style
    from .mix import HELDOUT

    problem = load_problem()
    scorer = load_scorer(SCRIPT)
    data, data_sha256 = scorer.load_data()
    weights = {n: Fraction(w) for n, w in data["objective"]["weights"].items()}
    model = KeyModel.from_grid(ANSI_GRID)
    fixed = problem_fixed(problem)
    ok = True
    for path in paths:
        try:
            submission = scorer.read_layout_file(path)
        except (OSError, ValueError) as error:
            print(error)
            ok = False
            continue
        result = scorer.evaluate(submission, data, data_sha256)
        if not result["valid"]:
            print(f"{path}: invalid: {'; '.join(result['problems'])}")
            ok = False
            continue
        style = result["style"]
        _, placed, _ = scorer.parse_layout(submission, data)
        exact = exact_j1(style, placed, weights, problem)
        agree = exact == Fraction(result["J1_exact"])
        ok &= agree
        print(f"{path}: style {style}, J1 {float(exact):.6f} ({result['difference_vs_reference_percent']:+.4f} % "
              f"vs reference), beats reference: {result['beats_reference']}, public scorer agrees exactly: {agree}")
        reference = mixed_best_layout(style)
        for corpus in HELDOUT:
            mine = score_style(style, placed, corpus, model, fixed)["J1"]
            ref = score_style(style, reference, corpus, model, fixed)["J1"]
            print(f"  held-out {corpus}: {mine:.6f} (reference {ref:.6f}, {(mine / ref - 1) * 100:+.4f} %)")
    if diagnostics is not None:
        try:
            from .experimental.submissions import report_optional
            report_optional(paths, diagnostics)
        except Exception as error:
            print(f"Optional diagnostics unavailable: {error}. Official results are unchanged.")
    return 0 if ok else 1


def _key_layout(layout: dict[str, tuple[str, str]]) -> dict[str, list[str]]:
    out = {key: ["", ""] for key in "QWERTYUIOPASDFGHJKLZXCVBNM"}
    for symbol, (key, layer) in layout.items():
        out[key][0 if layer == "base" else 1] = symbol
    return out


def manifest(outputs: list[Path], data_sha256: str, checks: dict) -> dict:
    head, clean = repo_state()
    inputs = {relative_to_project(p): sha256_file(p) for p in (PROBLEM_FILE, ANSI_GRID, TEMPLATE)}
    for style in STYLES:
        inputs[relative_to_project(MIX_SEARCH / f"{style}.json")] = sha256_file(MIX_SEARCH / f"{style}.json")
        for base in (PHASE3, CROSSCHECK):
            path = base / "search" / f"{style}.json"
            if path.exists():
                inputs[relative_to_project(path)] = sha256_file(path)
    inputs[relative_to_project(MIX / "run-manifest.json")] = sha256_file(MIX / "run-manifest.json")
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "repo_commit": head, "working_tree_clean": clean, "data_version": LEGACY_DATA_VERSION, "data_sha256": data_sha256,
            "checks": checks, "inputs": inputs, "outputs": hash_outputs(outputs)}
