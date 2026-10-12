"""Physical key model for J0: key effort K, finger, row, and the bigram
penalty B of the frozen Colemak-DH model (docs/colemak-model-spec.md,
section 2-3).

B(a, b) for two consecutive key actions a, b:

* the same action twice: 0 (repeated characters are free);
* same finger: 2.5 / 3.0 / 4.0 by row difference (capped at 2), including two
  different actions on one key (e.g. base and Shift layer: row difference 0);
* adjacent fingers of one hand: the penalty row of the outer finger
  (pinky–ring 0.5/1.0/1.5, ring–middle 0.1/0.2/0.3, middle–index
  −0.2/−0.1/0.0, decision D6 default: keep the middle–index benefit);
* anything else, including the space thumb: 0.

M(a), the modifier effort of J1 (RESEARCH_SPEC 6.6, owner decision D2 of
10 October 2026): 0 on the base layer; a Shift-layer action adds one press of
the *other* hand's Shift key, with that key's effort from the same grid
(K(RShift) for a left-hand key, K(LShift) for a right-hand key). Shift is
pressed for every shifted symbol and adds no bigram penalty (Q = 0). AltGr
has no v1 cost, so J1 is undefined for layouts that use it.

Fingers are numbered as in the original: 0 left pinky … 3 left index,
6 right index … 9 right pinky.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from ..reference import PROJECT_ROOT

ANSI_GRID = PROJECT_ROOT / "results" / "phase1" / "effort-grids" / "ansi-optimal.json"
ANSI_TRADITIONAL_GRID = PROJECT_ROOT / "results" / "phase1" / "effort-grids" / "ansi-traditional.json"
SAME_FINGER = (2.5, 3.0, 4.0)
NEIGHBOUR = ((0.5, 1.0, 1.5), (0.1, 0.2, 0.3), (-0.2, -0.1, 0.0))  # by outer finger: pinky, ring, middle
FINGER_NUMBER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "R3": 6, "R2": 7, "R1": 8, "R0": 9}
# The 30 main keys of v1 (RESEARCH_SPEC section 4) and the number row.
MAIN_BLOCK = tuple("QWERTYUIOP") + tuple("ASDFGHJKL;") + tuple("ZXCVBNM,./")
NUMBER_ROW = tuple("1234567890")


@dataclass(frozen=True)
class PhysicalKey:
    name: str
    effort: float
    finger: int
    row: int


def _left_equivalent(finger: int) -> int:
    return finger if finger <= 4 else 9 - finger


class KeyModel:
    def __init__(self, keys: dict[str, PhysicalKey], description: str,
                 same_finger=SAME_FINGER, neighbour=NEIGHBOUR):
        self.keys = keys
        self.description = description
        self.same_finger = tuple(same_finger)
        self.neighbour = tuple(tuple(r) for r in neighbour)

    @classmethod
    def from_grid(cls, path: Path = ANSI_GRID, decimals: int | None = None) -> "KeyModel":
        grid = json.loads(Path(path).read_text(encoding="utf-8"))
        keys = {}
        for k in grid["keys"]:
            effort = k["effort"]
            if decimals is not None:
                effort = float(Decimal(repr(effort)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP))
            keys[k["key"]] = PhysicalKey(k["key"], effort, FINGER_NUMBER[k["finger"]], int(k["y"]))
        label = f"{grid['keyboard']} {grid['fingers']} P_d={grid['distance_scale']}"
        return cls(keys, label + (f", rounded to {decimals} decimal(s)" if decimals is not None else ", unrounded"))

    def effort(self, key: str) -> float:
        physical = self.keys.get(key)
        return physical.effort if physical is not None else 0.0

    def modifier_effort(self, key: str, layer: str) -> float | None:
        """M of an action: Shift of the other hand on the Shift layer, 0 on
        the base layer (and on the analyzer's numbered English layers), None
        for AltGr (no v1 cost)."""
        if layer == "altgr":
            return None
        if layer != "shift":
            return 0.0
        physical = self.keys[key]
        return self.effort("RSHIFT" if physical.finger <= 4 else "LSHIFT")

    def penalty_keys(self, key1: str, key2: str, same_action: bool) -> tuple[str, float]:
        """(kind, value) of B for consecutive actions on key1 then key2."""
        if same_action:
            return "none", 0.0
        a, b = self.keys.get(key1), self.keys.get(key2)
        if a is None or b is None:
            return "none", 0.0
        rowdiff = min(2, abs(a.row - b.row))
        if a.finger == b.finger:
            return "same_finger", self.same_finger[rowdiff]
        if abs(a.finger - b.finger) == 1:
            outer = a.finger if _left_equivalent(a.finger) < _left_equivalent(b.finger) else b.finger
            value = self.neighbour[_left_equivalent(outer)][rowdiff]
            return ("neighbour_benefit" if value < 0 else "neighbour_penalty"), value
        return "none", 0.0

    def describe(self) -> dict:
        return {"keys": self.description, "same_finger": list(self.same_finger),
                "neighbour_by_outer_finger": {"pinky-ring": list(self.neighbour[0]),
                                              "ring-middle": list(self.neighbour[1]),
                                              "middle-index": list(self.neighbour[2])},
                "row_difference_cap": 2, "space": "thumb, K = 0, no bigram penalty (D2 default)",
                "layers": "J0: Shift and AltGr cost nothing (the original model). J1 adds M = the other hand's "
                          f"Shift key (K(LShift) = {self.effort('LSHIFT'):.6f}, K(RShift) = {self.effort('RSHIFT'):.6f}), "
                          "lambda_m = 1, Q = 0 (D2, 10 October 2026)"}
