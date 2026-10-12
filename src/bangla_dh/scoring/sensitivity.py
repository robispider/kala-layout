"""Parameter sensitivity of J1 (Phase 4, task 4; RESEARCH_SPEC section 9).

A parameter vector θ = (P_x, P_d, P_f of pinky, ring and middle, λ_m)
rebuilds the ANSI effort grid with the Phase 1 Fitts model
(``geometry.effort_model``; index P_f stays 1.0, the scale of the model) and
scales the Shift cost M by λ_m. Each layout is reduced once to *action
tables*: keystroke counts per (key, layer) and counts of consecutive action
pairs, so

    J1_θ(L) = [Σ_a n_a (K_θ(a) + λ_m M_θ(a)) + Σ_{a≠b} n_ab B_θ(a, b)] / N

costs one pass over a few hundred actions per θ. With model-optimal
fingering the finger of a key is re-chosen for every θ (the cheapest finger,
as in Phase 1), so B_θ can change too.

* Phase 3 layouts use model-optimal fingering (D3 default).
* A baseline is scored with both fingerings and keeps the lower J1 (the same
  generosity as the cross-check). Its typed sequences are encoded once with
  the frozen traditional grid; only their costs vary with θ.

``R(L, baseline) = Pr_θ(J1_θ(L) ≤ J1_θ(baseline))`` is a model-sensitivity
statistic, not a probability of comfort.
"""
from __future__ import annotations

import random
from collections import Counter

from ..bangla.grammar import Escape
from ..geometry.effort_model import FINGER_FACTOR, EffortParams, effort_grid, traditional_fingers
from ..geometry.keyboards import ansi_staggered
from .model import FINGER_NUMBER, KeyModel, PhysicalKey

NOMINAL = {"P_x": 2.0, "P_d": 1.12, "P_f_pinky": FINGER_FACTOR["pinky"], "P_f_ring": FINGER_FACTOR["ring"],
           "P_f_middle": FINGER_FACTOR["middle"], "lambda_m": 1.0}
# Sampling ranges (new Phase 4 parameters, recorded in the run manifest).
RANGES = {"P_x": (1.6, 2.4), "P_d": (0.9, 1.3), "P_f_pinky": (1.6 * 0.85, 1.6 * 1.15),
          "P_f_ring": (1.3 * 0.85, 1.3 * 1.15), "P_f_middle": (1.1 * 0.85, 1.1 * 1.15), "lambda_m": (0.5, 1.5)}


class ThetaModel(KeyModel):
    """A KeyModel whose Shift cost is scaled by λ_m (so the Phase 3 search
    code can re-optimize under θ unchanged)."""

    def __init__(self, keys, description, lambda_m: float):
        super().__init__(keys, description)
        self.lambda_m = lambda_m

    def modifier_effort(self, key: str, layer: str) -> float | None:
        value = super().modifier_effort(key, layer)
        return None if value is None else self.lambda_m * value


def theta_model(theta: dict, fingering: str = "optimal") -> ThetaModel:
    keyboard = ansi_staggered()
    params = EffortParams(distance_scale=theta["P_d"], lateral_multiplier=theta["P_x"],
                          finger_factor={"pinky": theta["P_f_pinky"], "ring": theta["P_f_ring"],
                                         "middle": theta["P_f_middle"], "index": 1.0})
    assignment = traditional_fingers(keyboard) if fingering == "traditional" else None
    grid = effort_grid(keyboard, params, assignment)
    # Six decimals, as the frozen grids (reproduce.grids_for_export): nominal θ gives them exactly.
    keys = {k.name: PhysicalKey(k.name, round(grid[k.name].effort, 6), FINGER_NUMBER[grid[k.name].finger], k.row)
            for k in keyboard.keys}
    return ThetaModel(keys, f"ANSI {fingering} fingering, theta {theta}", theta["lambda_m"])


def sample_thetas(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    return [{name: rng.uniform(*RANGES[name]) for name in NOMINAL} for _ in range(count)]


def one_at_a_time(points: int = 5) -> list[tuple[str, dict]]:
    out = []
    for name, (low, high) in RANGES.items():
        for k in range(points):
            out.append((name, {**NOMINAL, name: low + (high - low) * k / (points - 1)}))
    return out


# --- action tables --------------------------------------------------------------

def style_actions(record: dict, layout: dict[str, tuple[str, str]]) -> dict:
    """Action tables of a style layout from its keystroke table (label → slot)."""
    unigrams: Counter = Counter()
    pairs: Counter = Counter()
    for label, count in record["label_counts"].items():
        if label in layout:
            unigrams[layout[label]] += count
    for a, b, count in record["pair_counts"]:
        if a != b and a in layout and b in layout:
            pairs[(layout[a], layout[b])] += count
    return {"N": record["N"], "unigrams": dict(unigrams), "pairs": dict(pairs)}


def token_actions(keymap, tokens, total_units: int) -> dict:
    """Action tables of a key map over (token, count) pairs; escapes break pairs."""
    unigrams: Counter = Counter()
    pairs: Counter = Counter()
    for token, count in tokens:
        previous = None
        for step in keymap.encode(token):
            if isinstance(step, Escape):
                previous = None
                continue
            action = (step.key, step.layer)
            unigrams[action] += count
            if previous is not None and previous != action:
                pairs[(previous, action)] += count
            previous = action
    return {"N": total_units, "unigrams": dict(unigrams), "pairs": dict(pairs)}


def j1(tables: dict, model: KeyModel) -> float | None:
    """J1 of action tables (with a ``ThetaModel``, M is already scaled by λ_m)."""
    total = 0.0
    for (key, layer), count in tables["unigrams"].items():
        modifier = model.modifier_effort(key, layer)
        if modifier is None:
            return None
        total += count * (model.effort(key) + modifier)
    for ((k1, l1), (k2, l2)), count in tables["pairs"].items():
        total += count * model.penalty_keys(k1, k2, (k1, l1) == (k2, l2))[1]
    return total / tables["N"]
