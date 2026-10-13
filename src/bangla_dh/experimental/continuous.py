"""Unweighted endpoint movement across one intervening space (season e3)."""
from collections import Counter
import math

from ..geometry.keyboards import ansi_staggered
from .actions import SPACE_ACTION
from .continuous_counts import CATEGORIES, category
from .mechanics_counts import map_triples, triples_from_json

EVENTS = ("same_key", "same_finger_different_key", "same_hand", "opposite_hand")
CENTERS = {k.name: k.center for k in ansi_staggered().keys}
MAX_DISTANCE = max(math.dist(a, b) for a in CENTERS.values() for b in CENTERS.values())


def score_boundaries(triples, model):
    """All spanning windows stay in the denominator, including unknown endpoints."""
    categories = dict.fromkeys(CATEGORIES, 0)
    total = supported = shifted = 0
    counts = Counter(dict.fromkeys(EVENTS, 0))
    missing = Counter()
    distance = 0.0
    contributions = []
    for triple, n in sorted(triples.items()):
        if len(triple) != 3 or not isinstance(n, int) or n <= 0 or category(triple) == "within_word":
            raise ValueError("invalid boundary action triple")
        kind = category(triple)
        categories[kind] += n
        if kind != "spanning_space":
            continue
        a, _, b = triple
        total += n
        shifted += n if "shift" in (a[1], b[1]) else 0
        if (any(x[1] not in ("base", "shift") for x in (a, b))
                or any(x[0] not in model.keys or x[0] not in CENTERS for x in (a, b))):
            missing[" → ".join("/".join(x) for x in triple)] += n
            continue
        supported += n
        fa, fb = model.keys[a[0]].finger, model.keys[b[0]].finger
        same = a[0] == b[0]
        move = fa == fb and not same
        same_hand = (fa <= 4) == (fb <= 4)
        values = {"same_key": same, "same_finger_different_key": move,
                  "same_hand": same_hand, "opposite_hand": not same_hand}
        for event, present in values.items():
            counts[event] += n * present
        if move:
            d = math.dist(CENTERS[a[0]], CENTERS[b[0]])
            distance += n * d
            contributions.append({"from": list(a), "to": list(b), "count": n,
                                  "distance_u": d})
    unknown = total - supported
    bounds = {k: {"lower": v / total, "upper": (v + unknown) / total}
              for k, v in counts.items()} if total else {}
    return {"scope": "endpoint keys with exactly one intervening space; modifiers excluded",
            "fingering": model.description, "ranking_effect": "none", "category_counts": categories,
            "spanning_count": total, "supported_spanning_count": supported,
            "coverage": supported / total if total else None,
            "shift_involving_spanning_count": shifted, "counts": dict(counts),
            "conditional_rates": {k: v / supported for k, v in counts.items()} if supported else {},
            "bounds": bounds, "missing_spanning_windows": dict(missing),
            "same_finger_distance_u_sum": distance,
            "same_finger_distance_u_per_spanning_window": distance / total if total else None,
            "same_finger_distance_bounds": {"lower": distance / total,
                "upper": (distance + unknown * MAX_DISTANCE) / total} if total else None,
            "top_same_finger_moves": sorted(contributions, key=lambda r: (-r["count"], r["from"], r["to"]))[:10],
            "whole_typing_comfort": False}


def evaluate_cache(cache, model, assignment=None):
    triples = triples_from_json(cache["boundary_triples"])
    if assignment is not None:
        triples = map_triples(triples, {**assignment, "SPACE": SPACE_ACTION})
    result = score_boundaries(triples, model)
    counts = cache["category_counts"]
    if any(result["category_counts"][k] != counts[k] for k in CATEGORIES if k != "within_word"):
        raise ValueError("mapped boundary category totals changed")
    total = sum(counts.values())
    result["category_counts"] = counts
    result["total_valid_windows"] = total
    result["within_word_share"] = counts["within_word"] / total if total else None
    result["space_touching_share"] = 1 - result["within_word_share"] if total else None
    return result
