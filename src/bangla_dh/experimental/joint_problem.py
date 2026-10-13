"""e4: unchanged J1 and exact cross-space movement as separate objectives."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import math

from ..mix import mixed_frequencies
from ..phase3 import problem_fixed
from ..scoring.model import ANSI_GRID, KeyModel
from ..search.anneal import Instance, State
from ..search.integer import IntegerInstance
from ..search.problem import load_problem, slots
from .actions import SPACE_ACTION
from .continuous_counts import DEFAULT, VERSION, load_verified
from .inputs import TRAIN, frequency_path, read_json

WEIGHTS = {c: Fraction(1, 2) for c in TRAIN}
DIRECTIONS = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9)


class MovementModel:
    """Symmetric binary cost: same finger, different physical endpoint keys.

    Used only to construct a separate pair instance. It changes no J0/J1 cost.
    Identical labels/physical keys have zero different-key movement cost.
    """
    def __init__(self, model):
        self.model = model

    def effort(self, key):
        return 0.0

    def penalty_keys(self, a, b, same_action):
        if a == b or "SPACE" in (a, b):
            return "movement", 0.0
        return "movement", float(self.model.keys[a].finger == self.model.keys[b].finger)


def endpoint_counts(cache):
    if cache["version"] != VERSION or not all(cache["checks"].values()):
        raise ValueError("unsupported or unverified e3 counts")
    pairs = Counter()
    for a, b, c, n in cache["boundary_triples"]:
        if tuple(b) == SPACE_ACTION and tuple(a) != SPACE_ACTION and tuple(c) != SPACE_ACTION:
            if a[1] != "base" or c[1] != "base":
                raise ValueError("style endpoints must be abstract base-layer labels")
            pairs[a[0], c[0]] += n
    if sum(pairs.values()) != cache["category_counts"]["spanning_space"] or not pairs:
        raise ValueError("spanning-window totals differ or are empty")
    return pairs


def achievement(j, s, reference_j, reference_s, direction):
    """Relative Chebyshev exploration, not a fitted ergonomic comfort total.

    0 means a J1-only exploration. For 0 < direction < 1, negative energy
    implies both objectives improve. Final acceptance uses exact fractions.
    """
    if not 0 <= direction < 1 or reference_j <= 0 or reference_s <= 0:
        raise ValueError("invalid exploration direction/reference")
    dj = j / reference_j - 1
    if direction == 0:
        return dj
    return max((1 - direction) * dj, direction * (s / reference_s - 1))


class JointProblem:
    def __init__(self, style, reference, counts_root=DEFAULT):
        if style not in ("A", "D"):
            raise ValueError("joint search supports A and D only")
        self.style = style
        problem = load_problem()
        self.model = KeyModel.from_grid(ANSI_GRID)
        self.labels = problem["styles"][style]["searched_symbols"]
        self.slots, self.fixed = slots(), problem_fixed(problem)
        u, v = mixed_frequencies(style, {c: float(w) for c, w in WEIGHTS.items()})
        self.j1 = Instance(self.labels, self.slots, self.fixed, u, v, self.model, "J1")
        movement, self.raw_pairs, self.integer = {}, {}, {}
        for corpus, weight in WEIGHTS.items():
            cache, _ = load_verified(counts_root, "style", style, corpus)
            counts = endpoint_counts(cache)
            total = sum(counts.values())
            self.raw_pairs[corpus] = (counts, total)
            for pair, n in counts.items():
                if any(label not in {*self.labels, *self.fixed} for label in pair):
                    raise ValueError("endpoint label missing from frozen symbol problem")
                movement[pair] = movement.get(pair, 0.0) + float(weight) * n / total
            self.integer[corpus] = IntegerInstance(self.labels, self.slots, self.fixed,
                read_json(frequency_path(style, corpus)), self.model)
        self.movement = Instance(self.labels, self.slots, self.fixed, {}, movement,
                                 MovementModel(self.model), "J0")
        self.reference_perm = self.j1.perm_of(reference)
        self.reference_j, self.reference_s = self.exact(self.reference_perm)
        self.ref_j, self.ref_s = float(self.reference_j), float(self.reference_s)
        self.verify(self.reference_perm)

    def assignment(self, perm):
        return self.j1.assignment(perm)

    def exact(self, perm):
        if sorted(perm) != list(range(len(self.labels))):
            raise ValueError("layout is not a bijection")
        j = sum((w * self.integer[c].to_j(self.integer[c].score(perm)) for c, w in WEIGHTS.items()), Fraction())
        assignment = {**self.assignment(perm), **self.fixed}
        movement = Fraction()
        for corpus, weight in WEIGHTS.items():
            counts, total = self.raw_pairs[corpus]
            n = sum(count for (a, b), count in counts.items()
                    if assignment[a][0] != assignment[b][0]
                    and self.model.keys[assignment[a][0]].finger == self.model.keys[assignment[b][0]].finger)
            movement += weight * Fraction(n, total)
        return j, movement

    def verify(self, perm):
        j, s = self.exact(perm)
        if not math.isclose(self.j1.score(perm), float(j), abs_tol=1e-10, rel_tol=0):
            raise ValueError("fast J1 differs from exact integer model")
        if not math.isclose(self.movement.score(perm), float(s), abs_tol=1e-12, rel_tol=0):
            raise ValueError("fast movement differs from exact endpoint count")
        return j, s

    def success(self, j, s):
        return j < self.reference_j and s < self.reference_s


class JointState:
    def __init__(self, problem, perm, direction):
        self.problem, self.direction = problem, direction
        self.j = State(problem.j1, perm)
        self.s = State(problem.movement, perm)

    @property
    def perm(self):
        return self.j.perm

    @property
    def energy(self):
        return achievement(self.j.score, self.s.score, self.problem.ref_j, self.problem.ref_s, self.direction)

    def delta(self, i, k):
        dj, ds = self.j.delta(i, k), self.s.delta(i, k)
        new = achievement(self.j.score + dj, self.s.score + ds,
                          self.problem.ref_j, self.problem.ref_s, self.direction)
        return new - self.energy, dj, ds

    def swap(self, i, k, dj, ds):
        self.j.swap(i, k, dj)
        self.s.swap(i, k, ds)

    def reset(self, perm):
        self.j.perm = list(perm)
        self.s.perm = list(perm)
        self.j.rebuild()
        self.s.rebuild()

    def rebuild(self):
        self.j.rebuild()
        self.s.rebuild()
