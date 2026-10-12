"""Lower bounds and local certificates without a solver (Phase 4, task 2).

Everything here works on ``search.integer.IntegerInstance`` in exact integer
arithmetic, so every bound is a valid bound on the integer objective Z and,
through ``Z / (N · S)``, on J with no rounding error.

* ``lb0``: the elementary bound of RESEARCH_SPEC 8.3 (rearrangement minimum
  of the linear part, every searched pair at the smallest penalty).
* ``gilmore_lawler``: the Gilmore–Lawler bound for a QAP with a linear term.
  For label i on slot s, the cheapest its pairs could possibly be is half the
  minimum scalar product of its weights W[i][·] (others) with the penalties
  B[s][·] (other slots), sorted against each other; a linear assignment over
  U + that estimate is a lower bound (each pair is counted from both ends,
  hence the half). Computed on 2Z to stay integral.
* ``exchange_certificate``: exhaustive check that no layout differing from
  a given one in at most k labels has a lower Z (every derangement of every
  set of at most k labels). A proof for exactly that neighbourhood.
"""
from __future__ import annotations

import itertools
import multiprocessing as mp
import time

from .integer import IntegerInstance


def hungarian(cost: list[list[int]]) -> tuple[int, list[int]]:
    """Minimum linear assignment (shortest augmenting paths, O(n^3)); exact
    for integer costs. Returns (value, column of each row)."""
    n = len(cost)
    INF = float("inf")
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta, j1 = INF, 0
            row = cost[i0 - 1]
            ui0 = u[i0]
            for j in range(1, n + 1):
                if not used[j]:
                    cur = row[j - 1] - ui0 - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    assign = [0] * n
    for j in range(1, n + 1):
        assign[p[j] - 1] = j - 1
    return sum(cost[i][assign[i]] for i in range(n)), assign


def _ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def min_scalar_product(weights: list[int], values: list[int]) -> int:
    return sum(w * b for w, b in zip(sorted(weights, reverse=True), sorted(values)))


def lb0(inst: IntegerInstance) -> int:
    """RESEARCH_SPEC 8.3 bound on Z: fixed constant + rearrangement minimum of
    Σ u_i C(slot) + each label's cheapest fixed-pair term + every searched pair
    at the smallest penalty (if negative)."""
    n = inst.n
    e1 = sum(a * b for a, b in zip(sorted(inst.u, reverse=True), sorted(inst.C)))
    fixed_terms = sum(min(inst.U[i][s] - inst.u[i] * inst.C[s] for s in range(n)) for i in range(n))
    min_b = min(min(row) for row in inst.B)
    pair_mass = sum(sum(row) for row in inst.W) // 2
    return inst.const + e1 + fixed_terms + min(0, min_b) * pair_mass


def gilmore_lawler_costs(inst: IntegerInstance) -> list[list[int]]:
    """2 × the Gilmore–Lawler cost of label i on slot s."""
    n, W, B, U = inst.n, inst.W, inst.B, inst.U
    others_w = [[W[i][j] for j in range(n) if j != i] for i in range(n)]
    others_b = [[B[s][t] for t in range(n) if t != s] for s in range(n)]
    return [[2 * U[i][s] + min_scalar_product(others_w[i], others_b[s]) for s in range(n)] for i in range(n)]


def gilmore_lawler(inst: IntegerInstance) -> dict:
    """Gilmore–Lawler bound on Z and the linear assignment that attains it."""
    started = time.time()
    value2, assign = hungarian(gilmore_lawler_costs(inst))
    return {"Z": inst.const + _ceil_div(value2, 2), "assignment_value_2Z": value2, "assignment": assign,
            "seconds": round(time.time() - started, 2)}


def linear_minimum(inst: IntegerInstance) -> int:
    """const + min Σ U (not a bound: it ignores the negative penalties)."""
    return inst.const + hungarian(inst.U)[0]


# --- exchange certificates ------------------------------------------------------------

def derangements(k: int) -> list[tuple[int, ...]]:
    return [p for p in itertools.permutations(range(k)) if all(p[i] != i for i in range(k))]


_cert: dict = {}


def _cert_init(inst: IntegerInstance, perm: list[int], G: list[list[int]]) -> None:
    _cert.update(inst=inst, perm=perm, G=G, der={k: derangements(k) for k in range(2, 7)})


def _subset_delta(inst, perm, G, subset, new_slots) -> int:
    """Z(after) − Z(before) when the labels of ``subset`` move to ``new_slots``."""
    W, B = inst.W, inst.B
    delta = 0
    k = len(subset)
    for a in range(k):
        i = subset[a]
        old, new = perm[i], new_slots[a]
        delta += G[i][new] - G[i][old]
        Wi = W[i]
        Bn, Bo = B[new], B[old]
        for b in range(k):
            if b != a:
                j = subset[b]
                w = Wi[j]
                if w:
                    # G counted j at its old slot: remove that, add the true pair once (b > a).
                    delta -= w * (Bn[perm[j]] - Bo[perm[j]])
                    if b > a:
                        delta += w * (Bn[new_slots[b]] - Bo[perm[j]])
    return delta


def _cert_job(job: tuple[int, int]) -> dict:
    """All subsets of size k whose smallest label is ``first``."""
    first, k = job
    inst, perm, G, der = _cert["inst"], _cert["perm"], _cert["G"], _cert["der"][k]
    n = inst.n
    best_delta, best_move, checked = None, None, 0
    for rest in itertools.combinations(range(first + 1, n), k - 1):
        subset = (first,) + rest
        slots = [perm[i] for i in subset]
        for d in der:
            new_slots = [slots[d[a]] for a in range(k)]
            delta = _subset_delta(inst, perm, G, subset, new_slots)
            checked += 1
            if best_delta is None or delta < best_delta:
                best_delta, best_move = delta, (subset, new_slots)
    return {"k": k, "checked": checked, "best_delta": best_delta, "best_move": best_move}


def exchange_certificate(inst: IntegerInstance, perm: list[int], k_max: int, workers: int | None = None) -> dict:
    """Every layout that moves 2..k_max labels of ``perm``: the smallest ΔZ
    found (≥ 0 proves ``perm`` optimal in that neighbourhood)."""
    started = time.time()
    G = inst.g_table(perm)
    out = {}
    jobs = [(first, k) for k in range(2, k_max + 1) for first in range(inst.n - k + 1)]
    with mp.Pool(workers or max(1, min(24, mp.cpu_count() - 4)), initializer=_cert_init,
                 initargs=(inst, perm, G)) as pool:
        for result in pool.imap_unordered(_cert_job, jobs, chunksize=1):
            k = result["k"]
            row = out.setdefault(k, {"checked": 0, "best_delta": None, "best_move": None})
            row["checked"] += result["checked"]
            if result["best_delta"] is not None and (row["best_delta"] is None or result["best_delta"] < row["best_delta"]):
                row["best_delta"], row["best_move"] = result["best_delta"], result["best_move"]
    for k, row in out.items():
        subset, new_slots = row.pop("best_move")
        trial = list(perm)
        for i, s in zip(subset, new_slots):
            trial[i] = s
        row["best_move"] = {inst.labels[i]: [inst.slots[perm[i]], inst.slots[s]] for i, s in zip(subset, new_slots)}
        row["best_delta_rechecked"] = inst.score(trial) - inst.score(perm)  # full re-score of the closest rival
        row["layouts_checked_formula"] = f"C(52,{k}) x derangements({k})"
    return {"k_max": k_max, "by_k": {str(k): out[k] for k in sorted(out)},
            "proven": all(row["best_delta"] >= 0 and row["best_delta_rechecked"] >= 0 for row in out.values()),
            "seconds": round(time.time() - started, 1)}


def exhaustive_subproblem(inst: IntegerInstance, perm: list[int], free: list[int]) -> dict:
    """Every arrangement of the ``free`` labels on their own slots (the others
    stay at ``perm``): the minimum Z and its layout. Independent of the
    CP-SAT model, for cross-checking it on a scope small enough to enumerate."""
    started = time.time()
    G = inst.g_table(perm)
    subset = sorted(free)
    slots = [perm[i] for i in subset]
    best_delta, best_slots, checked = 0, list(slots), 0
    for order in itertools.permutations(slots):
        delta = _subset_delta(inst, perm, G, subset, order)
        checked += 1
        if delta < best_delta:
            best_delta, best_slots = delta, list(order)
    best = list(perm)
    for i, s in zip(subset, best_slots):
        best[i] = s
    return {"free": [inst.labels[i] for i in subset], "arrangements": checked, "Z_hint": inst.score(perm),
            "Z_min": inst.score(best), "best_delta": best_delta, "perm": best,
            "seconds": round(time.time() - started, 1)}
