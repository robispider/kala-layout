"""Cell-level RLT lower bound (Phase 4, task 2), solved with OR-Tools (GLOP or
PDLP) and re-checked in exact integer arithmetic.

The penalty B of two slots depends only on their *cells* (finger, row): two
slots of one cell (base and Shift of a key, or two keys of one finger row)
are a same-finger pair with row difference 0. The 52 v1 slots form 19 cells.
The LP relaxes the integer program

    min  Σ U[i][s] x_is + Σ_{i<j} W_ij Σ_{c,d} β(c,d) z_ijcd
    x a permutation matrix,  y_ic = Σ_{s∈c} x_is,
    Σ_d z_ijcd = y_ic,  Σ_c z_ijcd = y_jd                  (z is the joint cell
                                                           distribution of i, j)
    Σ_{j≠i} z_(ij)cd = (|d| − [c = d]) · y_ic               (with i in cell c, the
                                                           other labels fill d)

to 0 ≤ x, z ≤ 1. Every constraint holds for every layout, so the LP minimum
is a lower bound (the first-level reformulation–linearization technique,
aggregated to cells).

Certification does not trust the solver. For **any** multipliers y of the
equality rows, weak duality gives

    Z* ≥ const + Σ_r b_r y_r + Σ_v min(0, c_v − Σ_r a_rv y_r)

(each variable lies in [0, 1]). ``certify`` evaluates that expression with
the integer coefficients of ``IntegerInstance`` and the solver's duals rounded
to integers (any integers are valid), so the certified bound is exact and
needs no tolerance.
"""
from __future__ import annotations

import time

from ..scoring.model import KeyModel
from .integer import IntegerInstance


def cells_of(inst: IntegerInstance, model: KeyModel) -> tuple[list[tuple[int, int]], list[int]]:
    """(cells, cell index of every slot); checks that B depends on cells only."""
    keys = [model.keys[key] for key, _layer in inst.slots]
    cells = sorted({(k.finger, k.row) for k in keys})
    index = {c: n for n, c in enumerate(cells)}
    cell_of = [index[(k.finger, k.row)] for k in keys]
    n = inst.n
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            rep_s = next(a for a in range(n) if cell_of[a] == cell_of[s] and a != t)
            rep_t = next(b for b in range(n) if cell_of[b] == cell_of[t] and b != rep_s)
            if inst.B[s][t] != inst.B[rep_s][rep_t]:
                raise ValueError("B is not a function of the cells")
    return cells, cell_of


class CellLP:
    """The LP above as explicit sparse columns (shared by the solver and the
    exact certificate)."""

    def __init__(self, inst: IntegerInstance, model: KeyModel):
        self.inst = inst
        n = inst.n
        self.cells, self.cell_of = cells_of(inst, model)
        m = len(self.cells)
        self.size = [self.cell_of.count(c) for c in range(m)]
        rep = [self.cell_of.index(c) for c in range(m)]
        beta = [[0] * m for _ in range(m)]
        for c in range(m):
            for d in range(m):
                s = rep[c]
                t = next((t for t in range(n) if self.cell_of[t] == d and t != s), None)
                beta[c][d] = inst.B[s][t] if t is not None else 0
        self.beta = beta
        rows: list[int] = []        # right-hand sides
        self.row_names: list[tuple] = []

        def row(name, rhs) -> int:
            rows.append(rhs)
            self.row_names.append(name)
            return len(rows) - 1

        assign_label = [row(("label", i), 1) for i in range(n)]
        assign_slot = [row(("slot", s), 1) for s in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        marg_i = {(i, j, c): row(("marg_i", i, j, c), 0) for i, j in pairs for c in range(m)}
        marg_j = {(i, j, d): row(("marg_j", i, j, d), 0) for i, j in pairs for d in range(m)}
        cap = {(i, c, d): row(("cap", i, c, d), 0) for i in range(n) for c in range(m) for d in range(m)}
        self.rhs = rows
        # Columns: (cost, [(row, coefficient), ...]).
        columns: list[tuple[int, list[tuple[int, int]]]] = []
        self.x_index = [[0] * n for _ in range(n)]
        for i in range(n):
            for s in range(n):
                c = self.cell_of[s]
                entries = [(assign_label[i], 1), (assign_slot[s], 1)]
                entries += [(marg_i[(i, j, c)], -1) for j in range(i + 1, n)]
                entries += [(marg_j[(h, i, c)], -1) for h in range(i)]
                entries += [(cap[(i, c, d)], -(self.size[d] - (c == d))) for d in range(m)]
                self.x_index[i][s] = len(columns)
                columns.append((inst.U[i][s], entries))
        for i, j in pairs:
            w = inst.W[i][j]
            for c in range(m):
                for d in range(m):
                    entries = [(marg_i[(i, j, c)], 1), (marg_j[(i, j, d)], 1), (cap[(i, c, d)], 1), (cap[(j, d, c)], 1)]
                    columns.append((w * beta[c][d], entries))
        self.columns = columns

    def solve(self, time_limit: float = 3600.0, method: str = "GLOP", threads: int = 1) -> dict:
        """Solve with GLOP (simplex) or PDLP (first-order; approximate duals are
        still certified exactly) in J units; returns the duals in Z units."""
        from ortools.linear_solver import pywraplp

        started = time.time()
        solver = pywraplp.Solver.CreateSolver(method)
        solver.SetTimeLimit(int(time_limit * 1000))
        solver.SetNumThreads(threads)
        unit = self.inst.N * self.inst.scale
        constraints = [solver.Constraint(rhs, rhs) for rhs in self.rhs]
        objective = solver.Objective()
        for k, (cost, entries) in enumerate(self.columns):
            var = solver.NumVar(0.0, 1.0, f"v{k}")
            if cost:
                objective.SetCoefficient(var, cost / unit)
            for r, a in entries:
                constraints[r].SetCoefficient(var, a)
        objective.SetMinimization()
        built = time.time() - started
        status = solver.Solve()
        names = {pywraplp.Solver.OPTIMAL: "OPTIMAL", pywraplp.Solver.FEASIBLE: "FEASIBLE",
                 pywraplp.Solver.INFEASIBLE: "INFEASIBLE", pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
                 pywraplp.Solver.ABNORMAL: "ABNORMAL", pywraplp.Solver.UNBOUNDED: "UNBOUNDED"}
        duals = [round(con.dual_value() * unit) for con in constraints]
        return {"status": names.get(status, str(status)), "solver_objective_J": objective.Value() + self.inst.const / unit,
                "duals_Z": duals, "rows": len(self.rhs), "columns": len(self.columns),
                "build_seconds": round(built, 1), "seconds": round(time.time() - started, 1),
                "solver": f"OR-Tools {_ortools_version()} {method}"}

    def certify(self, duals: list[int]) -> int:
        """Weak-duality bound on Z for integer multipliers (exact)."""
        total = self.inst.const + sum(b * y for b, y in zip(self.rhs, duals) if b)
        for cost, entries in self.columns:
            reduced = cost - sum(a * duals[r] for r, a in entries)
            if reduced < 0:
                total += reduced
        return total


def _ortools_version() -> str:
    import ortools

    return ortools.__version__
