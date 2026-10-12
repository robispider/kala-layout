"""Seeded candidate search (Phase 3, task 4; RESEARCH_SPEC section 7).

The v1 problem of one style is a quadratic assignment with a linear term:
52 key labels on 52 slots (a bijection), some labels fixed outside the
searched slots. For a layout p (label i on slot p_i):

    J(p) = const + Σ_i U[i][p_i] + Σ_{i<j} W[i][j] · B[p_i][p_j]

* ``U[i][s] = u_i · C[s] + Σ_f W[i][f] · B[s][slot_f]`` folds in the fixed
  labels f; ``C[s] = K(key) + M(slot)`` for J1, ``K(key)`` for J0;
* ``W[i][j] = v_ij + v_ji`` (B is symmetric, repeats are excluded);
* ``const`` holds the fixed labels' own effort and their mutual penalties.

``J`` equals the table scorer's J1 (or J0) for the same layout exactly up to
float rounding; tests and the Phase 3 driver check that.

Delta scoring: the search keeps ``G[i][s] = U[i][s] + Σ_k W[i][k] B[s][p_k]``,
the cost of label i on slot s given the others. Swapping labels i and j
(slots a and b) changes J by

    Δ = G[i][b] − G[i][a] + G[j][a] − G[j][b] + 2 W[i][j] B[a][b]

in O(1), and an accepted swap updates every row of G in O(n²).

Search per seed: simulated annealing over pair swaps (any two labels, so
base↔Shift exchanges are included) with a geometric temperature schedule
calibrated from the start layout, then steepest descent to a swap-local
optimum, then iterated local search (perturbation by random pair swaps and
whole-key exchanges, descent, keep if not worse). Deterministic for a seed.
Every result is "best found" (RESEARCH_SPEC section 14), never "optimal".
"""
from __future__ import annotations

import math
import random
import time

from ..scoring.model import KeyModel


class Instance:
    def __init__(self, labels: list[str], slots: list[tuple[str, str]], fixed: dict[str, tuple[str, str]],
                 u: dict[str, float], v: dict[tuple[str, str], float], model: KeyModel, objective: str = "J1"):
        if len(labels) != len(slots):
            raise ValueError("the v1 problem is a bijection: as many labels as slots")
        if objective not in ("J0", "J1"):
            raise ValueError(objective)
        self.labels, self.slots, self.fixed, self.objective = list(labels), list(slots), dict(fixed), objective
        self.n = n = len(labels)
        fixed_labels = list(fixed)
        fixed_slots = [fixed[f] for f in fixed_labels]

        def cost(slot) -> float:
            key, layer = slot
            extra = model.modifier_effort(key, layer) if objective == "J1" else 0.0
            if extra is None:
                raise ValueError("AltGr has no v1 cost")
            return model.effort(key) + extra

        def penalty(s, t) -> float:
            return model.penalty_keys(s[0], t[0], s == t)[1]

        self.C = [cost(s) for s in slots]
        self.B = [[penalty(s, t) for t in slots] for s in slots]
        if any(self.B[a][b] != self.B[b][a] for a in range(n) for b in range(n)):
            raise ValueError("bigram penalty table is not symmetric")
        BF = [[penalty(s, t) for t in fixed_slots] for s in slots]
        index = {label: i for i, label in enumerate(labels)}
        findex = {label: f for f, label in enumerate(fixed_labels)}
        W = [[0.0] * n for _ in range(n)]
        WF = [[0.0] * len(fixed_labels) for _ in range(n)]
        const_pairs = 0.0
        for (a, b), freq in v.items():
            if a == b:
                continue
            if a in index and b in index:
                W[index[a]][index[b]] += freq
                W[index[b]][index[a]] += freq
            elif a in index and b in findex:
                WF[index[a]][findex[b]] += freq
            elif b in index and a in findex:
                WF[index[b]][findex[a]] += freq
            elif a in findex and b in findex:
                const_pairs += freq * penalty(fixed[a], fixed[b])
        self.W = W
        self.u = [u.get(label, 0.0) for label in labels]
        self.U = [[self.u[i] * self.C[s] + sum(w * BF[s][f] for f, w in enumerate(WF[i]) if w)
                   for s in range(n)] for i in range(n)]
        self.const = const_pairs + sum(u.get(f, 0.0) * cost(fixed[f]) for f in fixed_labels)

    def score(self, perm: list[int]) -> float:
        """J of the layout with label i on slot perm[i]."""
        total = self.const + sum(self.U[i][perm[i]] for i in range(self.n))
        B, W = self.B, self.W
        for i in range(self.n):
            Wi, Bi = W[i], B[perm[i]]
            total += sum(Wi[j] * Bi[perm[j]] for j in range(i + 1, self.n))
        return total

    def assignment(self, perm: list[int]) -> dict[str, tuple[str, str]]:
        return {self.labels[i]: self.slots[perm[i]] for i in range(self.n)}

    def perm_of(self, assignment: dict[str, tuple[str, str]]) -> list[int]:
        slot_index = {s: k for k, s in enumerate(self.slots)}
        return [slot_index[assignment[label]] for label in self.labels]

    def greedy(self) -> list[int]:
        """Frequency-sorted start: most frequent label on the cheapest slot."""
        order = sorted(range(self.n), key=lambda i: (-self.u[i], self.labels[i]))
        slots = sorted(range(self.n), key=lambda s: (self.C[s], s))
        perm = [0] * self.n
        for i, s in zip(order, slots):
            perm[i] = s
        return perm


class State:
    """A layout with its G table for O(1) swap deltas."""

    def __init__(self, inst: Instance, perm: list[int]):
        self.inst = inst
        self.perm = list(perm)
        self.log: list[tuple[int, int]] | None = None  # swaps since the last mark, for undo
        self.rebuild()

    def rebuild(self) -> None:
        inst, perm = self.inst, self.perm
        n, B, W, U = inst.n, inst.B, inst.W, inst.U
        self.G = [[U[i][s] + sum(W[i][k] * B[s][perm[k]] for k in range(n) if W[i][k]) for s in range(n)]
                  for i in range(n)]
        self.score = inst.score(perm)

    def delta(self, i: int, j: int) -> float:
        a, b = self.perm[i], self.perm[j]
        Gi, Gj = self.G[i], self.G[j]
        return Gi[b] - Gi[a] + Gj[a] - Gj[b] + 2.0 * self.inst.W[i][j] * self.inst.B[a][b]

    def swap(self, i: int, j: int, delta: float) -> None:
        a, b = self.perm[i], self.perm[j]
        Ba, Bb = self.inst.B[a], self.inst.B[b]
        D = [x - y for x, y in zip(Bb, Ba)]
        Wi, Wj = self.inst.W[i], self.inst.W[j]
        G = self.G
        for k in range(self.inst.n):
            c = Wi[k] - Wj[k]
            if c:
                G[k] = [g + c * d for g, d in zip(G[k], D)]
        self.perm[i], self.perm[j] = b, a
        self.score += delta
        if self.log is not None:
            self.log.append((i, j))

    def undo(self) -> None:
        """Revert every swap logged since ``log`` was set to []."""
        log, self.log = self.log, None
        for i, j in reversed(log):
            self.swap(i, j, self.delta(i, j))
        self.log = []

    def descend(self) -> int:
        """Steepest descent over all pair swaps to a swap-local optimum."""
        n, moves = self.inst.n, 0
        while True:
            best, best_pair = -1e-12, None
            for i in range(n - 1):
                for j in range(i + 1, n):
                    d = self.delta(i, j)
                    if d < best:
                        best, best_pair = d, (i, j)
            if best_pair is None:
                return moves
            self.swap(*best_pair, best)
            moves += 1


def _random_pair(rng: random.Random, n: int) -> tuple[int, int]:
    i = rng.randrange(n)
    j = rng.randrange(n - 1)
    return i, j + (j >= i)


def anneal(state: State, rng: random.Random, steps: int, t_ratio: float, rebuild_every: int = 20_000) -> dict:
    """Simulated annealing over pair swaps; returns the schedule used. The
    state ends on the best layout seen."""
    n = state.inst.n
    uphill = [d for d in (state.delta(*_random_pair(rng, n)) for _ in range(2000)) if d > 0]
    t0 = (sum(uphill) / len(uphill)) / math.log(2) if uphill else 1e-3  # mean uphill move accepted with p = 1/2
    t1 = t0 * t_ratio
    factor = (t1 / t0) ** (1.0 / max(1, steps - 1))
    best_score, best_perm = state.score, list(state.perm)
    temperature = t0
    accepted = 0
    random_ = rng.random
    for step in range(steps):
        i, j = _random_pair(rng, n)
        d = state.delta(i, j)
        if d <= 0 or random_() < math.exp(-d / temperature):
            state.swap(i, j, d)
            accepted += 1
            if accepted % rebuild_every == 0:
                state.rebuild()
            if state.score < best_score - 1e-12:
                best_score, best_perm = state.score, list(state.perm)
        temperature *= factor
    state.perm = best_perm
    state.rebuild()
    return {"steps": steps, "T0": t0, "T_end": t1, "geometric_factor": factor, "accepted": accepted,
            "T0_rule": "mean uphill delta of 2000 random swaps from the start / ln 2"}


def perturb(state: State, rng: random.Random, strength: int, key_pairs: list[tuple[int, int]]) -> None:
    """Random pair swaps and whole-key exchanges (base and Shift together)."""
    slot_label = {s: i for i, s in enumerate(state.perm)}
    n = state.inst.n
    for _ in range(strength):
        if rng.random() < 0.5:
            i, j = _random_pair(rng, n)
            pairs = [(i, j)]
        else:
            (a1, a2), (b1, b2) = rng.sample(key_pairs, 2)
            pairs = [(slot_label[a1], slot_label[b1]), (slot_label[a2], slot_label[b2])]
        for i, j in pairs:
            d = state.delta(i, j)
            state.swap(i, j, d)
            a, b = state.perm[i], state.perm[j]
            slot_label[a], slot_label[b] = i, j


def iterated_local_search(state: State, rng: random.Random, iterations: int, strength: tuple[int, int]) -> dict:
    slots = state.inst.slots
    by_key: dict[str, list[int]] = {}
    for k, (key, _layer) in enumerate(slots):
        by_key.setdefault(key, []).append(k)
    key_pairs = [tuple(v) for v in by_key.values() if len(v) == 2]
    best_perm, best_score = list(state.perm), state.score
    improvements = 0
    for _ in range(iterations):
        state.log = []
        perturb(state, rng, rng.randint(*strength), key_pairs)
        state.descend()
        if state.score <= best_score + 1e-12:
            if state.score < best_score - 1e-12:
                improvements += 1
            best_perm, best_score = list(state.perm), state.score
        else:
            state.undo()
    state.log = None
    state.perm = best_perm
    state.rebuild()
    return {"iterations": iterations, "perturbation_strength": list(strength), "improvements": improvements}


def run(inst: Instance, seed: int, start: str, sa_steps: int, t_ratio: float, ils_iterations: int,
        ils_strength: tuple[int, int] = (2, 6)) -> dict:
    """One seeded search; deterministic for (instance, seed, settings)."""
    started = time.time()
    rng = random.Random(seed)
    if start == "greedy":
        perm = inst.greedy()
    elif start == "random":
        perm = list(range(inst.n))
        rng.shuffle(perm)
    else:
        raise ValueError(start)
    state = State(inst, perm)
    start_score = state.score
    schedule = anneal(state, rng, sa_steps, t_ratio)
    after_sa = state.score
    descent_moves = state.descend()
    after_descent = state.score
    ils = iterated_local_search(state, rng, ils_iterations, ils_strength)
    exact = inst.score(state.perm)
    return {"seed": seed, "start": start, "start_score": start_score, "after_annealing": after_sa,
            "after_descent": after_descent, "descent_moves": descent_moves, "best_score": exact,
            "incremental_drift": abs(exact - state.score), "schedule": schedule, "ils": ils,
            "perm": state.perm, "seconds": round(time.time() - started, 2)}
