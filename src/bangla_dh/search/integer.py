"""Integer coefficients for certification (Phase 4, task 1; RESEARCH_SPEC 8.4).

Frozen rule (decision D5 default, scale S = 10^6):

* frequencies are the raw integer counts of the keystroke tables
  (``label_counts``, ``pair_counts``), not the floats u = count / N;
* ``K̂(key) = S · K(key)``, ``M̂ = K̂(other hand's Shift)`` and
  ``B̂ = S · B``, converted through ``Decimal(repr(x))``. The effort grid
  stores K with six decimals and B is a multiple of 0.1, so every product is
  an integer; the conversion refuses any value for which it is not.

The integer objective of a layout p is

    Z(p) = const + Σ_i U[i][p_i] + Σ_{i<j} W[i][j] · B̂[p_i][p_j]

with the same folding of the fixed labels as ``search.anneal.Instance``, and
``J(p) = Z(p) / (N · S)`` holds **exactly** (as rationals) for the decimal
values in the grid file. So a bound on Z is a bound on J with no rounding
error. The only rounding left is the grid's own: its efforts are the Fitts
formula rounded to six decimals, so against the unrounded formula
``|J_formula − J| ≤ 5·10^-7 · (keystrokes + Shift presses) / N``
(``formula_rounding_bound``).
"""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

from ..scoring.model import KeyModel

SCALE = 10 ** 6
GRID_DECIMALS = 6


def to_int(value: float, scale: int = SCALE) -> int:
    exact = Decimal(repr(value)) * scale
    if exact != exact.to_integral_value():
        raise ValueError(f"{value!r} · {scale} is not an integer: the integer model would not be exact")
    return int(exact)


class IntegerInstance:
    """One style's v1 problem with integer coefficients."""

    def __init__(self, labels: list[str], slots: list[tuple[str, str]], fixed: dict[str, tuple[str, str]],
                 record: dict, model: KeyModel, objective: str = "J1", scale: int = SCALE):
        if objective not in ("J0", "J1"):
            raise ValueError(objective)
        if len(labels) != len(slots):
            raise ValueError("the v1 problem is a bijection: as many labels as slots")
        self.labels, self.slots, self.fixed, self.objective, self.scale = list(labels), list(slots), dict(fixed), objective, scale
        self.n = n = len(labels)
        self.N = record["N"]
        counts = record["label_counts"]
        pairs = record["pair_counts"]
        self.keystrokes = record["keystrokes_excluding_space"]

        def cost(slot) -> int:
            key, layer = slot
            extra = model.modifier_effort(key, layer) if objective == "J1" else 0.0
            if extra is None:
                raise ValueError("AltGr has no v1 cost")
            return to_int(model.effort(key), scale) + to_int(extra, scale)

        def penalty(s, t) -> int:
            return to_int(model.penalty_keys(s[0], t[0], s == t)[1], scale)

        fixed_labels = list(fixed)
        self.C = [cost(s) for s in slots]
        self.B = [[penalty(s, t) for t in slots] for s in slots]
        index = {label: i for i, label in enumerate(labels)}
        findex = {label: f for f, label in enumerate(fixed_labels)}
        BF = [[penalty(s, fixed[f]) for f in fixed_labels] for s in slots]
        W = [[0] * n for _ in range(n)]
        WF = [[0] * len(fixed_labels) for _ in range(n)]
        const = 0
        for a, b, c in pairs:
            if a == b:
                continue
            if a in index and b in index:
                W[index[a]][index[b]] += c
                W[index[b]][index[a]] += c
            elif a in index and b in findex:
                WF[index[a]][findex[b]] += c
            elif b in index and a in findex:
                WF[index[b]][findex[a]] += c
            elif a in findex and b in findex:
                const += c * penalty(fixed[a], fixed[b])
        self.W = W
        self.u = [counts.get(label, 0) for label in labels]
        self.U = [[self.u[i] * self.C[s] + sum(w * BF[s][f] for f, w in enumerate(WF[i]) if w) for s in range(n)]
                  for i in range(n)]
        self.const = const + sum(counts.get(f, 0) * cost(fixed[f]) for f in fixed_labels)
        self.shift_presses_bound = sum(self.u)  # every searched keystroke could be shifted
        self.fixed_shift_presses = sum(counts.get(f, 0) for f in fixed_labels if fixed[f][1] == "shift")

    # --- objective ---------------------------------------------------------------

    def score(self, perm: list[int]) -> int:
        total = self.const + sum(self.U[i][perm[i]] for i in range(self.n))
        for i in range(self.n):
            Wi, Bi = self.W[i], self.B[perm[i]]
            total += sum(Wi[j] * Bi[perm[j]] for j in range(i + 1, self.n) if Wi[j])
        return total

    def to_j(self, z: int | Fraction) -> Fraction:
        """The J value of an integer objective value, exactly."""
        return Fraction(z, self.N * self.scale)

    def perm_of(self, assignment: dict[str, tuple[str, str]]) -> list[int]:
        slot_index = {s: k for k, s in enumerate(self.slots)}
        return [slot_index[assignment[label]] for label in self.labels]

    def assignment(self, perm: list[int]) -> dict[str, tuple[str, str]]:
        return {self.labels[i]: self.slots[perm[i]] for i in range(self.n)}

    def g_table(self, perm: list[int]) -> list[list[int]]:
        """G[i][s]: the cost of label i on slot s given every other label at perm."""
        n, W, B, U = self.n, self.W, self.B, self.U
        return [[U[i][s] + sum(W[i][k] * B[s][perm[k]] for k in range(n) if W[i][k] and k != i) for s in range(n)]
                for i in range(n)]

    def formula_rounding_bound(self, model: KeyModel) -> Fraction:
        """Largest |J_formula − J| over all layouts: each grid effort is within
        half a unit of the sixth decimal of the formula, and a layout has at
        most (all keystrokes + one Shift press per keystroke) such terms per N."""
        half_unit = Fraction(1, 2 * 10 ** GRID_DECIMALS)
        presses = self.keystrokes + (self.shift_presses_bound + self.fixed_shift_presses
                                     if self.objective == "J1" else 0)
        return half_unit * presses / self.N
