"""Phase 4 driver: integer model, certified bounds, scoped proofs and
parameter sensitivity (RESEARCH_SPEC sections 8, 9 and 13).

Steps (each a CLI command, see ``cli.py``):

``certify``          results/phase4/certificates/<style>.json (tasks 1–3)
``certify-lp``       results/phase4/certificates/<style>-lp.json and the LP
                     duals (task 2; can run beside ``certify``)
``sensitivity``      results/phase4/sensitivity.json (task 4)
``evaluate-phase4``  independent checks, REPORT.md, phase4.json,
                     run-manifest.json

Scope of every certificate: the v1 problem of one style (52 searched labels
on the 52 v1 slots, fixed keys as in ``data/problem-v1.json``), objective J1
(D2), the model-optimal ANSI grid (D3 default), the middle–index benefit kept
(D6 default), keystroke frequencies of bnwiki/train (the frequencies the
Phase 3 search optimized), integer scale 10^6 (D5 default). A claim about
held-out or news text, another grid or the full 90-slot keyboard is outside
that scope.
"""
from __future__ import annotations

import datetime as _dt
import gzip
import json
import multiprocessing as mp
import platform
import random
import statistics
import time
from fractions import Fraction
from pathlib import Path

from . import __version__
from .bangla.inventory import INVENTORY_FILE
from .bangla.styles import STYLES
from .corpus import frequency as freq
from .paths import repo_state, PROJECT_ROOT, RESULTS_ROOT, hash_outputs, output_path, relative_to_project, write_json
from .phase2 import frequency_record
from .phase3 import (HELDOUT, TRAIN, best_layout, corpus_file, frequency_file, instance as float_instance,
                     problem_fixed, score_layout)
from .reference import sha256_file
from .scoring import baselines, sensitivity as sens
from .scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from .scoring.verify import verify_style
from .search import bounds, cpsat
from .search.anneal import Instance, State, iterated_local_search
from .search.integer import SCALE, IntegerInstance
from .search.lp_bound import CellLP
from .search.problem import PROBLEM_FILE, load_problem, slots

RESULTS = RESULTS_ROOT / "phase4"
CERTIFICATES = RESULTS / "certificates"
SCOPE = ("v1 problem of the style: 52 searched labels on the 52 v1 slots (26 letter keys × base/Shift), digits and "
         "US punctuation fixed as in data/problem-v1.json; objective J1 (D2); model-optimal ANSI grid (D3 default); "
         "middle-index benefit kept (D6 default); keystroke frequencies of bnwiki/train; integer scale 10^6 (D5 default)")
CERTIFY_SETTINGS = {
    "scale": SCALE, "objective": "J1", "frequencies": TRAIN,
    "exchange_k": 5,
    "lp": {"solver": "PDLP", "time_limit": 3600, "threads": 16,
           "note": "GLOP (simplex) did not solve the 481,390-column LP in 30 min; PDLP's duals are certified exactly"},
    "cpsat_full": {"time_limit": 900, "workers": 16, "seed": 20261012},
    "subproblems": {"sizes": [12, 16, 20, 24, 28, 32, 36, 40, 44, 48], "time_limit": 600, "workers": 16,
                    "order": "the k labels with the highest keystroke counts (ties by label), the others fixed"},
    "layers": {"time_limit": 600, "workers": 16},
    "exhaustive_check": {"size": 9},
}
SENSITIVITY_SETTINGS = {"samples": 1000, "seed": 20261013, "corpus": HELDOUT, "ranges": sens.RANGES,
                        "nominal": sens.NOMINAL, "one_at_a_time_points": 5,
                        "regret": {"thetas": "each parameter at the low and the high end of its range, the others "
                                             "nominal", "frequencies": TRAIN, "ils_iterations": 1000,
                                   "ils_strength": [2, 6], "seed": 20261014}}


# --- tasks 1–3: certificates ---------------------------------------------------------

def integer_instance(style: str, model: KeyModel | None = None, problem: dict | None = None) -> IntegerInstance:
    model = model or KeyModel.from_grid(ANSI_GRID)
    problem = problem or load_problem()
    record = json.loads(frequency_file(style, TRAIN).read_text(encoding="utf-8"))
    return IntegerInstance(problem["styles"][style]["searched_symbols"], slots(), problem_fixed(problem), record,
                           model, "J1")


def top_labels(inst: IntegerInstance, k: int) -> list[int]:
    return sorted(range(inst.n), key=lambda i: (-inst.u[i], inst.labels[i]))[:k]


def _j(inst: IntegerInstance, z: int | None) -> float | None:
    return None if z is None else float(inst.to_j(z))


def _cp_summary(inst: IntegerInstance, result: dict, ub: int) -> dict:
    out = {k: v for k, v in result.items() if k != "perm"}
    out["bound_J"] = _j(inst, result.get("best_bound_Z"))
    out["solution_J"] = _j(inst, result.get("Z"))
    out["proven_optimal_hint"] = result["status"] == "OPTIMAL" and result.get("best_bound_Z") == ub \
        and result.get("Z") == ub
    if result.get("Z") is not None and result["Z"] < ub:
        out["improved_layout"] = {inst.labels[i]: "/".join(inst.slots[s]) for i, s in enumerate(result["perm"])}
    return out


def lsa_check(cost: list[list[int]]) -> int:
    """The same linear assignment by OR-Tools (an independent implementation)."""
    from ortools.graph.python import linear_sum_assignment

    lsa = linear_sum_assignment.SimpleLinearSumAssignment()
    n = len(cost)
    for i in range(n):
        for s in range(n):
            lsa.add_arc_with_cost(i, s, cost[i][s])
    if lsa.solve() != lsa.OPTIMAL:
        raise RuntimeError("OR-Tools linear sum assignment failed")
    return lsa.optimal_cost()


def lp_duals_file(style: str) -> Path:
    return CERTIFICATES / f"{style}-lp-duals.json.gz"


def certify_style(style: str, settings: dict = CERTIFY_SETTINGS, steps: set[str] | None = None, log=print) -> dict:
    steps = {"cpsat", "subproblems", "layers", "exchange"} if steps is None else steps
    started = time.time()
    model = KeyModel.from_grid(ANSI_GRID)
    problem = load_problem()
    inst = integer_instance(style, model, problem)
    perm = inst.perm_of(best_layout(style))
    ub = inst.score(perm)
    finst = float_instance(style, model, problem=problem)
    float_j = finst.score(finst.perm_of(best_layout(style)))
    cert: dict = {"style": style, "scope": SCOPE, "settings": settings,
                  "frequencies": relative_to_project(frequency_file(style, TRAIN)),
                  "frequencies_sha256": sha256_file(frequency_file(style, TRAIN)),
                  "problem_sha256": problem["problem_sha256"], "N": inst.N, "scale": inst.scale}
    cert["integer_model"] = {
        "exact": True,  # IntegerInstance refuses any coefficient that is not an exact integer at this scale
        "UB_Z": ub, "UB_J": _j(inst, ub), "float_search_J": float_j,
        "float_vs_exact_difference": abs(float_j - _j(inst, ub)),
        "formula_rounding_bound_J": float(inst.formula_rounding_bound(model)),
        "max_abs_coefficient": max(max(abs(x) for x in row) for row in inst.U + inst.W),
    }
    log(f"{style}: UB J1 {cert['integer_model']['UB_J']:.9f}")

    lb = {"LB0": bounds.lb0(inst)}
    gl = bounds.gilmore_lawler(inst)
    lb["Gilmore-Lawler"] = gl["Z"]
    cert["gilmore_lawler"] = {"Z": gl["Z"], "J": _j(inst, gl["Z"]), "assignment_value_2Z": gl["assignment_value_2Z"],
                              "ortools_assignment_value_2Z": lsa_check(bounds.gilmore_lawler_costs(inst)),
                              "seconds": gl["seconds"]}
    log(f"{style}: LB0 {_j(inst, lb['LB0']):.6f}, Gilmore-Lawler {_j(inst, gl['Z']):.6f}")

    if "cpsat" in steps:
        s = settings["cpsat_full"]
        result = cpsat.solve(inst, model, perm, s["time_limit"], workers=s["workers"], seed=s["seed"])
        cert["cpsat_full"] = _cp_summary(inst, result, ub)
        if result.get("best_bound_Z") is not None:
            lb["CP-SAT"] = result["best_bound_Z"]
        log(f"{style}: CP-SAT full {result['status']}, bound {cert['cpsat_full']['bound_J']}")

    proofs = {}
    k = settings["exhaustive_check"]["size"]
    free = top_labels(inst, k)
    enum = bounds.exhaustive_subproblem(inst, perm, free)
    cp = cpsat.solve(inst, model, perm, 600, workers=settings["subproblems"]["workers"], free=free)
    proofs["exhaustive_check"] = {
        "size": k, "free": [inst.labels[i] for i in free], "arrangements": enum["arrangements"],
        "enumeration_Z_min": enum["Z_min"], "cpsat_status": cp["status"], "cpsat_Z": cp.get("Z"),
        "cpsat_bound_Z": cp.get("best_bound_Z"), "agree": cp["status"] == "OPTIMAL" and cp.get("Z") == enum["Z_min"]
        and cp.get("best_bound_Z") == enum["Z_min"], "hint_optimal": enum["Z_min"] == ub,
        "seconds": enum["seconds"] + cp["seconds"]}
    log(f"{style}: exhaustive top-{k} vs CP-SAT agree: {proofs['exhaustive_check']['agree']}")

    if "exchange" in steps:
        proofs["exchange"] = bounds.exchange_certificate(inst, perm, settings["exchange_k"])
        log(f"{style}: no better layout moving ≤ {settings['exchange_k']} labels: {proofs['exchange']['proven']} "
            f"({proofs['exchange']['seconds']} s)")

    if "subproblems" in steps:
        s = settings["subproblems"]
        rows = []
        for size in s["sizes"]:
            free = top_labels(inst, size)
            result = _cp_summary(inst, cpsat.solve(inst, model, perm, s["time_limit"], workers=s["workers"], free=free), ub)
            result["size"] = size
            rows.append(result)
            log(f"{style}: top-{size} sub-problem {result['status']} proven {result['proven_optimal_hint']} "
                f"({result['seconds']} s)")
            if not result["proven_optimal_hint"]:
                break
        proofs["top_k"] = {"order": s["order"], "runs": rows,
                           "largest_proven": max([r["size"] for r in rows if r["proven_optimal_hint"]], default=0)}

    if "layers" in steps:
        s = settings["layers"]
        for layer in ("base", "shift"):
            free = [i for i in range(inst.n) if inst.slots[perm[i]][1] == layer]
            result = _cp_summary(inst, cpsat.solve(inst, model, perm, s["time_limit"], workers=s["workers"], free=free), ub)
            proofs[f"{layer}_layer"] = result
            log(f"{style}: {layer}-layer sub-problem {result['status']} proven {result['proven_optimal_hint']}")
    cert["proofs"] = proofs

    cert["lower_bounds_Z"] = lb
    cert["seconds"] = round(time.time() - started, 1)
    return cert


def certificate_file(style: str) -> Path:
    return CERTIFICATES / f"{style}.json"


def lp_file(style: str) -> Path:
    return CERTIFICATES / f"{style}-lp.json"


def run_certify(styles=STYLES, steps: set[str] | None = None) -> list[Path]:
    written = []
    for style in styles:
        cert = certify_style(style, steps=steps)
        written.append(write_json(certificate_file(style), cert, indent=1))
    return written


def certify_lp(style: str, settings: dict = CERTIFY_SETTINGS, log=print) -> dict:
    model = KeyModel.from_grid(ANSI_GRID)
    inst = integer_instance(style, model)
    ub = inst.score(inst.perm_of(best_layout(style)))
    lp = CellLP(inst, model)
    s = settings["lp"]
    solved = lp.solve(s["time_limit"], method=s["solver"], threads=s["threads"])
    certified = lp.certify(solved["duals_Z"])
    path = output_path(lp_duals_file(style))
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        json.dump({"style": style, "rows": solved["rows"], "duals_Z": solved["duals_Z"]}, stream)
    record = {k: v for k, v in solved.items() if k != "duals_Z"}
    record.update({"style": style, "settings": s, "frequencies_sha256": sha256_file(frequency_file(style, TRAIN)),
                   "UB_Z": ub, "certified_Z": certified, "certified_J": _j(inst, certified),
                   "gap_percent": 100 * (ub - certified) / ub, "duals_file": relative_to_project(path)})
    log(f"{style}: cell LP {solved['status']} {solved['solver_objective_J']:.6f}, certified {record['certified_J']:.6f}, "
        f"gap {record['gap_percent']:.2f} % ({solved['seconds']} s)")
    return record


def run_certify_lp(styles=STYLES) -> list[Path]:
    return [write_json(lp_file(style), certify_lp(style), indent=1) for style in styles]


def summarize(cert: dict, lp: dict | None) -> dict:
    """Bounds of one style from its certificate and cell LP record."""
    ub = cert["integer_model"]["UB_Z"]
    unit = cert["N"] * cert["scale"]
    lb = dict(cert["lower_bounds_Z"])
    if lp is not None:
        lb["cell LP"] = lp["certified_Z"]
    best = max(lb, key=lb.get)
    proofs = cert["proofs"]
    improved = [r for r in [cert.get("cpsat_full", {}), proofs.get("base_layer", {}), proofs.get("shift_layer", {})]
                + proofs.get("top_k", {}).get("runs", []) if "improved_layout" in r]
    return {"UB_J": ub / unit, "LB_J": lb[best] / unit, "LB_source": best,
            "gap_percent": 100 * (ub - lb[best]) / ub, "proven_optimal": lb[best] >= ub,
            "classification": "proven optimal" if lb[best] >= ub else "bounded near-optimum",
            "improved_by_solver": bool(improved),
            "bounds": {name: {"Z": z, "J": z / unit, "gap_percent": 100 * (ub - z) / ub} for name, z in lb.items()}}


# --- task 4: sensitivity ------------------------------------------------------------------

def _baseline_tables_job(job) -> tuple[str, str, dict]:
    entry, fingering, table, n = job
    grid = ANSI_TRADITIONAL_GRID if fingering == "traditional" else ANSI_GRID
    keymap = baselines.keymap(entry, KeyModel.from_grid(grid))
    return entry["name"], fingering, sens.token_actions(keymap, freq.read_token_table(PROJECT_ROOT / table), n)


def _regret_job(job) -> dict:
    style, label, theta, settings = job
    model = sens.theta_model(theta, "optimal")
    inst = float_instance(style, model)
    state = State(inst, inst.perm_of(best_layout(style)))
    start = state.score
    state.descend()
    r = settings["regret"]
    iterated_local_search(state, random.Random(r["seed"]), r["ils_iterations"], tuple(r["ils_strength"]))
    final = inst.score(state.perm)
    moved = sum(a != b for a, b in zip(state.perm, inst.perm_of(best_layout(style))))
    return {"style": style, "theta_label": label, "theta": theta, "phase3_layout_J1": start, "reoptimized_J1": final,
            "regret_percent": 100 * (start - final) / start, "labels_moved": moved}


def run_sensitivity(settings: dict = SENSITIVITY_SETTINGS, workers: int | None = None) -> list[Path]:
    started = time.time()
    problem = load_problem()
    fixed = problem_fixed(problem)
    corpus = settings["corpus"]
    record = frequency_record(corpus)
    tables: dict[str, dict] = {}
    ours = {}
    for style in STYLES:
        style_record = json.loads(frequency_file(style, corpus).read_text(encoding="utf-8"))
        layout = {**best_layout(style), **fixed}
        tables[f"Bangla-DH {style}"] = {"optimal": sens.style_actions(style_record, layout)}
        ours[f"Bangla-DH {style}"] = style
    entries = baselines.load_registry()
    jobs = [(e, f, record["token_table"], record["N"]) for e in entries for f in ("optimal", "traditional")]
    with mp.Pool(workers or max(1, min(len(jobs), mp.cpu_count() - 4))) as pool:
        for name, fingering, table in pool.imap_unordered(_baseline_tables_job, jobs):
            tables.setdefault(name, {})[fingering] = table
    print(f"action tables: {time.time() - started:.0f} s", flush=True)
    base_names = [e["name"] for e in entries]

    def evaluate(theta: dict) -> dict[str, float]:
        models = {f: sens.theta_model(theta, f) for f in ("optimal", "traditional")}
        out = {}
        for name, by_fingering in tables.items():
            values = [sens.j1(t, models[f]) for f, t in by_fingering.items()]
            values = [v for v in values if v is not None]
            out[name] = min(values) if values else None
        return out

    # Nominal θ must reproduce the Phase 3 and cross-check numbers.
    nominal = evaluate(settings["nominal"])
    model = KeyModel.from_grid(ANSI_GRID)
    expected = {name: score_layout(style, best_layout(style), corpus, model, fixed)["J1"] for name, style in ours.items()}
    crosscheck = json.loads((RESULTS_ROOT / "phase3-crosscheck" / "crosscheck.json").read_text(encoding="utf-8"))
    for name in base_names:
        scores = crosscheck["baselines"].get(name, {}).get("scores", {}).get(corpus, {})
        candidates = [scores[g]["J1"] for g in ("unrounded", "traditional_unrounded") if scores.get(g, {}).get("J1")]
        expected[name] = min(candidates) if candidates else None
    nominal_check = {name: {"theta_J1": nominal[name], "reference_J1": expected.get(name),
                            "difference": None if expected.get(name) is None else abs(nominal[name] - expected[name])}
                     for name in tables}

    thetas = sens.sample_thetas(settings["samples"], settings["seed"])
    values = [evaluate(t) for t in thetas]
    names = list(tables)
    summary = {}
    for name in ours:
        row = {"J1": _quantiles([v[name] for v in values])}
        for b in base_names:
            pairs = [(v[name], v[b]) for v in values if v[b] is not None]
            row[f"R vs {b}"] = sum(a <= c for a, c in pairs) / len(pairs)
            row[f"ratio to {b}"] = _quantiles([a / c for a, c in pairs])
        summary[name] = row
    rank = {name: sum(min(ours, key=lambda n: v[n]) == name for v in values) / len(values) for name in ours}
    pairwise = {f"{a} ≤ {b}": sum(v[a] <= v[b] for v in values) / len(values) for a in ours for b in ours if a < b}
    sweep = [{"parameter": p, "theta": t, "J1": evaluate(t)} for p, t in sens.one_at_a_time(settings["one_at_a_time_points"])]
    print(f"samples and sweeps: {time.time() - started:.0f} s", flush=True)

    regret_thetas = []
    for p, (low, high) in sens.RANGES.items():
        regret_thetas += [(f"{p} low", {**sens.NOMINAL, p: low}), (f"{p} high", {**sens.NOMINAL, p: high})]
    regret_jobs = [(style, label, theta, settings) for style in STYLES for label, theta in regret_thetas]
    with mp.Pool(workers or max(1, min(len(regret_jobs), mp.cpu_count() - 4))) as pool:
        regret = list(pool.imap(_regret_job, regret_jobs))
    print(f"regret: {time.time() - started:.0f} s", flush=True)
    result = {"settings": settings, "corpus": corpus, "token_table_sha256": record["token_table_sha256"],
              "layouts": names, "baselines": base_names, "nominal_check": nominal_check,
              "samples": {"count": len(thetas), "summary": summary, "best_style_share": rank, "pairwise": pairwise},
              "one_at_a_time": sweep, "regret": regret, "seconds": round(time.time() - started, 1)}
    return [write_json(RESULTS / "sensitivity.json", result, indent=1)]


def _quantiles(values: list[float]) -> dict:
    s = sorted(values)
    pick = lambda q: s[min(len(s) - 1, int(q * (len(s) - 1) + 0.5))]  # noqa: E731
    return {"min": s[0], "p05": pick(0.05), "median": statistics.median(s), "p95": pick(0.95), "max": s[-1]}


# --- evaluation ----------------------------------------------------------------------------

def _verify_job(job) -> tuple[str, dict]:
    style, corpus_files, layout = job
    return style, verify_style([Path(p) for p in corpus_files], style, layout, INVENTORY_FILE, ANSI_GRID)


def run_evaluation(verify: bool = True) -> dict:
    started = time.time()
    problem = load_problem()
    certificates = {s: json.loads(certificate_file(s).read_text(encoding="utf-8")) for s in STYLES}
    lps = {s: json.loads(lp_file(s).read_text(encoding="utf-8")) if lp_file(s).exists() else None for s in STYLES}
    ev: dict = {"scope": SCOPE, "certificates": certificates, "cell_lp": lps,
                "summaries": {s: summarize(certificates[s], lps[s]) for s in STYLES},
                "sensitivity": json.loads((RESULTS / "sensitivity.json").read_text(encoding="utf-8"))}
    checks = {}
    model = KeyModel.from_grid(ANSI_GRID)
    for style in STYLES:
        inst = integer_instance(style, model, problem)
        perm = inst.perm_of(best_layout(style))
        ub = inst.score(perm)
        cert = certificates[style]
        c = {"UB_Z_recomputed": ub, "UB_matches_certificate": ub == cert["integer_model"]["UB_Z"],
             "frequencies_unchanged": sha256_file(frequency_file(style, TRAIN)) == cert["frequencies_sha256"],
             "bounds_below_UB": all(b["Z"] <= ub for b in ev["summaries"][style]["bounds"].values()),
             "gilmore_lawler_lsa_agrees": cert["gilmore_lawler"]["assignment_value_2Z"]
             == cert["gilmore_lawler"]["ortools_assignment_value_2Z"]}
        lp = lps[style]
        if lp is not None:
            with gzip.open(PROJECT_ROOT / lp["duals_file"], "rt", encoding="utf-8") as stream:
                duals = json.load(stream)["duals_Z"]
            c["cell_lp_rechecked_Z"] = CellLP(inst, model).certify(duals)
            c["cell_lp_recheck_agrees"] = (c["cell_lp_rechecked_Z"] == lp["certified_Z"] and lp["UB_Z"] == ub
                                           and lp["frequencies_sha256"] == cert["frequencies_sha256"])
        checks[style] = c
    if verify:
        print("Independent verifier on the training split ...", flush=True)
        jobs = [(style, [str(corpus_file(TRAIN))], {**{label: "/".join(slot) for label, slot in best_layout(style).items()},
                                                     **problem["fixed"]}) for style in STYLES]
        with mp.Pool(len(jobs)) as pool:
            verified = dict(pool.map(_verify_job, jobs))
        for style in STYLES:
            record = json.loads(frequency_file(style, TRAIN).read_text(encoding="utf-8"))
            v = verified[style]
            ub_j = certificates[style]["integer_model"]["UB_J"]
            ub_exact = Fraction(certificates[style]["integer_model"]["UB_Z"], certificates[style]["N"] * certificates[style]["scale"])
            checks[style].update({"verifier": v, "verifier_vs_integer_relative_difference": abs(v["J1"] - ub_j) / ub_j,
                                  "verifier_equals_integer_exactly": Fraction(v["J1_exact"]) == ub_exact,
                                  "verifier_counts_match": v["N"] == record["N"]
                                  and v["keystrokes_excluding_space"] == record["keystrokes_excluding_space"]
                                  and v["escaped_units"] == record["escaped_unit_count"]})
    ev["checks"] = checks
    ev["seconds"] = round(time.time() - started, 1)
    return ev


def acceptance(ev: dict) -> dict[str, bool]:
    certs, checks, sensitivity = ev["certificates"], ev["checks"], ev["sensitivity"]
    out = {
        "integer model exact and equal to the search objective": all(
            c["integer_model"]["exact"] and c["integer_model"]["float_vs_exact_difference"] < 1e-9 for c in certs.values()),
        "certificates match the current layouts and frequencies": all(
            c["UB_matches_certificate"] and c["frequencies_unchanged"] for c in checks.values()),
        "every lower bound is below the best found layout": all(c["bounds_below_UB"] for c in checks.values()),
        "Gilmore-Lawler assignment re-checked by OR-Tools": all(c["gilmore_lawler_lsa_agrees"] for c in checks.values()),
        "CP-SAT model agrees with exhaustive enumeration": all(
            c["proofs"]["exhaustive_check"]["agree"] for c in certs.values()),
        "sensitivity at nominal parameters reproduces Phase 3 and the cross-check": all(
            r["difference"] is not None and r["difference"] < 1e-9 for r in sensitivity["nominal_check"].values()),
    }
    if all("cell_lp_recheck_agrees" in c for c in checks.values()):
        out["cell LP bound re-checked from the stored duals"] = all(c["cell_lp_recheck_agrees"] for c in checks.values())
    if all("verifier" in c for c in checks.values()):
        out["independent verifier equals the integer objective exactly on the training split"] = all(
            c["verifier_equals_integer_exactly"] and c["verifier_counts_match"] for c in checks.values())
    return out


def manifest(outputs: list[Path]) -> dict:
    head, clean = repo_state()
    import ortools

    inputs = {relative_to_project(p): sha256_file(p) for p in (INVENTORY_FILE, PROBLEM_FILE, ANSI_GRID, ANSI_TRADITIONAL_GRID)}
    for style in STYLES:
        for corpus in (TRAIN, HELDOUT):
            inputs[relative_to_project(frequency_file(style, corpus))] = sha256_file(frequency_file(style, corpus))
        path = RESULTS_ROOT / "phase3" / "search" / f"{style}.json"
        inputs[relative_to_project(path)] = sha256_file(path)
    inputs[relative_to_project(corpus_file(TRAIN))] = sha256_file(corpus_file(TRAIN))
    record = frequency_record(HELDOUT)
    inputs[record["token_table"]] = record["token_table_sha256"]
    for entry in baselines.load_registry():
        inputs[f"baseline:{entry['name']}"] = baselines.describe(entry)["sha256"]
    crosscheck = RESULTS_ROOT / "phase3-crosscheck" / "crosscheck.json"
    inputs[relative_to_project(crosscheck)] = sha256_file(crosscheck)
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
            "bangla_dh_version": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "ortools": ortools.__version__, "repo_commit": head, "working_tree_clean": clean,
            "parameters": {"scope": SCOPE, "certify": CERTIFY_SETTINGS, "sensitivity": SENSITIVITY_SETTINGS,
                           "decisions": "D5 default (scale 10^6), D3 default (model-optimal grid), D6 default "
                                        "(middle-index benefit kept); B/D repeated-press rule of 10 October 2026"},
            "inputs": inputs, "outputs": hash_outputs(outputs)}
