"""Seeded two-objective exploration with bounded training Pareto archives."""
from __future__ import annotations

import math
import random
import time

from ..search.anneal import _random_pair
from .joint_problem import JointState, achievement


class Archive:
    """Deterministic bounded non-dominated archive, sorted by J1 then movement.

    Crowding uses evenly spaced J1-order indices and preserves both endpoints.
    This bounds memory; it does not claim an exhaustive Pareto frontier.
    """
    def __init__(self, limit=64, reference=None):
        if limit < 2:
            raise ValueError("archive limit must be at least 2")
        self.limit, self.rows = limit, []
        self.reference, self.goal = reference, None

    def offer(self, j, s, perm):
        if self.reference and j < self.reference[0] and s < self.reference[1]:
            if self.goal is None or (j, s, tuple(perm)) < (self.goal["j"], self.goal["s"], tuple(self.goal["perm"])):
                self.goal = {"j": j, "s": s, "perm": list(perm)}
        if any(r["j"] <= j and r["s"] <= s for r in self.rows):
            return
        row = {"j": j, "s": s, "perm": list(perm)}
        self.rows = [r for r in self.rows if not (j <= r["j"] and s <= r["s"])]
        self.rows.append(row)
        self.rows.sort(key=lambda r: (r["j"], r["s"], r["perm"]))
        if len(self.rows) > self.limit:
            last = len(self.rows) - 1
            indices = sorted({round(k * last / (self.limit - 1)) for k in range(self.limit)})
            self.rows = [self.rows[i] for i in indices]

    def retained(self):
        rows = list(self.rows)
        if self.goal and not any(r["perm"] == self.goal["perm"] for r in rows):
            rows.append(self.goal)
        return sorted(rows, key=lambda r: (r["j"], r["s"], r["perm"]))


def descend(state, archive):
    moves = 0
    while True:
        best, selected = -1e-14, None
        for i in range(state.problem.j1.n - 1):
            for k in range(i + 1, state.problem.j1.n):
                delta = state.delta(i, k)
                if delta[0] < best:
                    best, selected = delta[0], (i, k, delta)
        if selected is None:
            return moves
        i, k, (_, dj, ds) = selected
        state.swap(i, k, dj, ds)
        archive.offer(state.j.score, state.s.score, state.perm)
        moves += 1


def search(problem, seed, direction, start, steps, ils_iterations, archive_limit=64, t_ratio=1e-3):
    started = time.perf_counter()
    rng = random.Random(seed)
    archive = Archive(archive_limit, (problem.ref_j, problem.ref_s))
    archive.offer(problem.ref_j, problem.ref_s, problem.reference_perm)
    state = JointState(problem, start, direction)
    archive.offer(state.j.score, state.s.score, state.perm)
    uphill = [d for d in (state.delta(*_random_pair(rng, problem.j1.n))[0] for _ in range(2000)) if d > 0]
    temperature = sum(uphill) / len(uphill) / math.log(2) if uphill else 1e-3
    initial_temperature = temperature
    factor = t_ratio ** (1 / max(1, steps - 1))
    best_energy, best_perm = min((0.0, list(problem.reference_perm)),
        (state.energy, list(start)), key=lambda x: (x[0], x[1]))
    accepted = 0
    for _ in range(steps):
        i, k = _random_pair(rng, problem.j1.n)
        d, dj, ds = state.delta(i, k)
        if d <= 0 or rng.random() < math.exp(-d / temperature):
            state.swap(i, k, dj, ds)
            accepted += 1
            if accepted % 20_000 == 0:
                state.rebuild()
            archive.offer(state.j.score, state.s.score, state.perm)
            if state.energy < best_energy - 1e-14:
                best_energy, best_perm = state.energy, list(state.perm)
        temperature *= factor
    state.reset(best_perm)
    descent_moves = descend(state, archive)
    best_perm, best_energy = list(state.perm), state.energy
    # ILS includes whole-key exchanges, preserving both layers together.
    by_key = {}
    for i, (key, _) in enumerate(problem.slots):
        by_key.setdefault(key, []).append(i)
    key_pairs = [v for v in by_key.values() if len(v) == 2]
    improvements = 0
    for _ in range(ils_iterations):
        undo = []
        inverse = {slot: label for label, slot in enumerate(state.perm)}
        for _ in range(rng.randint(2, 6)):
            if rng.random() < .5 or len(key_pairs) < 2:
                pairs = [_random_pair(rng, problem.j1.n)]
            else:
                a, b = rng.sample(key_pairs, 2)
                pairs = [(inverse[a[0]], inverse[b[0]]), (inverse[a[1]], inverse[b[1]])]
            for i, k in pairs:
                _, dj, ds = state.delta(i, k)
                state.swap(i, k, dj, ds)
                undo.append((i, k))
                inverse[state.perm[i]], inverse[state.perm[k]] = i, k
        # Record descent swaps so unsuccessful ILS trials can undo cheaply.
        state.j.log, state.s.log = [], []
        descend(state, archive)
        if state.energy < best_energy - 1e-14:
            improvements += 1
            best_perm, best_energy = list(state.perm), state.energy
        elif state.energy > best_energy + 1e-14:
            descent_log = list(state.j.log)
            state.j.log = state.s.log = None
            for i, k in reversed(undo + descent_log):
                _, dj, ds = state.delta(i, k)
                state.swap(i, k, dj, ds)
        else:
            best_perm, best_energy = list(state.perm), state.energy
        state.j.log = state.s.log = None
    state.reset(best_perm)
    archive.offer(state.j.score, state.s.score, state.perm)
    # Keep the attained-direction endpoint even when bounded archive pruning
    # omitted it; parent verification decides exact dominance and success.
    endpoint = {"j": state.j.score, "s": state.s.score, "perm": list(state.perm)}
    rows = archive.retained()
    if not any(r["perm"] == endpoint["perm"] for r in rows):
        rows.append(endpoint)
    verified = []
    for row in rows:
        j, s = problem.verify(row["perm"])
        verified.append({"j": float(j), "s": float(s), "perm": row["perm"]})
    return {"seed": seed, "direction": direction, "steps": steps, "ils_iterations": ils_iterations,
            "accepted": accepted, "initial_temperature": initial_temperature, "t_ratio": t_ratio,
            "descent_moves": descent_moves, "ils_improvements": improvements,
            "endpoint_energy": achievement(state.j.score, state.s.score, problem.ref_j, problem.ref_s, direction),
            "archive": verified, "seconds": round(time.perf_counter() - started, 3), "verified": True}
