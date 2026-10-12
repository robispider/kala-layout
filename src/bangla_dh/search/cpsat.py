"""CP-SAT models of the v1 problem (Phase 4, tasks 2 and 3).

Booleans x_is (label i on slot s, a permutation), y_ic = Σ_{s∈c} x_is (cell
of label i, see ``lp_bound``) and, for every label pair with W_ij > 0 and
every cell pair with β(c, d) ≠ 0, a pair literal z_ijcd:

* β > 0 (penalty): y_ic ∧ y_jd → z  (the minimum sets z only when forced);
* β < 0 (middle–index benefit): z → y_ic and z → y_jd.

So for every layout the model has a solution with objective at most Z/D
(z = the true products), and every model solution is a layout. Objective
coefficients are the integer coefficients of ``IntegerInstance`` (D = 1, the
default; a larger D divides them and rounds **down**, which keeps CP-SAT's
best bound a valid lower bound ``LB_Z = D · bound`` but makes ``OPTIMAL``
mean optimal only up to that rounding). With D = 1, ``OPTIMAL`` and a bound
equal to Z(hint) prove the hint optimal for the stated scope; values stay
below 2^53, so the solver's double-precision bound is exact. Every returned layout is re-scored exactly with
``IntegerInstance.score``; the solver's own objective is never reported as Z.

``free``: only these labels may move (the others stay at the hint), an exact
sub-problem over the free labels' own slots.

``radius``: the extra constraint Σ_i x_{i,p*_i} ≥ n − r restricts the search
to layouts that move at most r labels of p*; ``OPTIMAL`` with Z(p*) proves p*
optimal in that neighbourhood. Gap-based early stopping is disabled
(relative and absolute gap limits 0), so ``OPTIMAL`` means proven.
"""
from __future__ import annotations

import math
import time

from ..scoring.model import KeyModel
from .integer import IntegerInstance
from .lp_bound import cells_of

OBJECTIVE_DIVISOR = 1
EXACT_FLOAT = 2 ** 53  # CP-SAT reports bounds as doubles: exact below this


def _floor_div(a: int, d: int) -> int:
    return a // d


def solve(inst: IntegerInstance, model: KeyModel, hint: list[int], time_limit: float, workers: int = 24,
          radius: int | None = None, free: list[int] | None = None, seed: int = 20261012,
          divisor: int = OBJECTIVE_DIVISOR) -> dict:
    from ortools.sat.python import cp_model

    started = time.time()
    n = inst.n
    cells, cell_of = cells_of(inst, model)
    m = len(cells)
    members = [[s for s in range(n) if cell_of[s] == c] for c in range(m)]
    rep = [members[c][0] for c in range(m)]
    beta = [[0] * m for _ in range(m)]
    for c in range(m):
        for d in range(m):
            t = next((t for t in members[d] if t != rep[c]), None)
            beta[c][d] = inst.B[rep[c]][t] if t is not None else 0

    cp = cp_model.CpModel()
    x = [[cp.NewBoolVar(f"x{i}_{s}") for s in range(n)] for i in range(n)]
    for i in range(n):
        cp.AddExactlyOne(x[i])
    for s in range(n):
        cp.AddExactlyOne([x[i][s] for i in range(n)])
    y = [[cp.NewBoolVar(f"y{i}_{c}") for c in range(m)] for i in range(n)]
    for i in range(n):
        for c in range(m):
            cp.Add(y[i][c] == sum(x[i][s] for s in members[c]))
    terms, coefs = [], []
    for i in range(n):
        for s in range(n):
            coef = _floor_div(inst.U[i][s], divisor)
            if coef:
                terms.append(x[i][s])
                coefs.append(coef)
    pair_literals = 0
    for i in range(n):
        for j in range(i + 1, n):
            w = inst.W[i][j]
            if not w:
                continue
            for c in range(m):
                for d in range(m):
                    b = beta[c][d]
                    if not b or (c == d and len(members[c]) < 2):
                        continue
                    z = cp.NewBoolVar(f"z{i}_{j}_{c}_{d}")
                    if b > 0:
                        cp.AddBoolOr([y[i][c].Not(), y[j][d].Not(), z])
                    else:
                        cp.AddImplication(z, y[i][c])
                        cp.AddImplication(z, y[j][d])
                    terms.append(z)
                    coefs.append(_floor_div(w * b, divisor))
                    pair_literals += 1
    const = _floor_div(inst.const, divisor)
    if inst.score(hint) // divisor >= EXACT_FLOAT:
        raise ValueError("objective too large for an exact double-precision bound; raise the divisor")
    cp.Minimize(sum(c * t for c, t in zip(coefs, terms)) + const)
    if radius is not None:
        cp.Add(sum(x[i][hint[i]] for i in range(n)) >= n - radius)
    if free is not None:
        for i in set(range(n)) - set(free):
            cp.Add(x[i][hint[i]] == 1)
    for i in range(n):
        for s in range(n):
            cp.AddHint(x[i][s], s == hint[i])

    solver = cp_model.CpSolver()
    p = solver.parameters
    p.max_time_in_seconds = float(time_limit)
    p.num_search_workers = workers
    p.random_seed = seed
    p.relative_gap_limit = 0.0
    p.absolute_gap_limit = 0.0
    built = time.time() - started
    status = solver.Solve(cp)
    name = solver.StatusName(status)
    out = {"status": name, "radius": radius, "free": None if free is None else sorted(free), "time_limit": time_limit, "workers": workers, "seed": seed,
           "objective_divisor": divisor, "pair_literals": pair_literals, "build_seconds": round(built, 1),
           "seconds": round(time.time() - started, 1), "solver": f"OR-Tools {_version()} CP-SAT",
           "best_bound_Z": math.floor(solver.BestObjectiveBound()) * divisor if name in ("OPTIMAL", "FEASIBLE") else None}
    if name in ("OPTIMAL", "FEASIBLE"):
        perm = [next(s for s in range(n) if solver.Value(x[i][s])) for i in range(n)]
        out["perm"] = perm
        out["Z"] = inst.score(perm)  # exact re-score, never the solver's objective
    return out


def _version() -> str:
    import ortools

    return ortools.__version__
