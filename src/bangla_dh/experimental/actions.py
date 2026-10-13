"""Lossless action counts: directed pairs, repeats and explicit space boundaries."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import math

from ..bangla.grammar import Escape, UnitSet, nfc, segment
from ..bangla.inventory import SPACE
from ..geometry.keyboards import ansi_staggered
from ..scoring.model import KeyModel

Action = tuple[str, str]
SPACE_ACTION = ("SPACE", "base")


@dataclass
class ActionTables:
    N: int
    space_units: int
    unigrams: Counter = field(default_factory=Counter)
    pairs: Counter = field(default_factory=Counter)
    escaped_units: int = 0
    outside_inventory: int = 0
    round_trip_types: int = 0

    def validate(self):
        if self.N <= self.space_units or self.space_units < 0:
            raise ValueError("invalid corpus denominator")
        for count in (*self.unigrams.values(), *self.pairs.values(), self.escaped_units, self.outside_inventory):
            if not isinstance(count, int) or count < 0:
                raise ValueError("action counts must be non-negative integers")
        if self.unigrams.get(SPACE_ACTION, 0) != self.space_units:
            raise ValueError("space count mismatch")
        for a in self.unigrams:
            if len(a) != 2 or a[1] not in ("base", "shift", "altgr"):
                raise ValueError("unknown action layer")
        if any(a not in self.unigrams or b not in self.unigrams for a, b in self.pairs):
            raise ValueError("pair endpoint absent from action counts")
        return self

    def json(self):
        return {"N": self.N, "space_units": self.space_units,
                "unigrams": [[*a, c] for a, c in sorted(self.unigrams.items())],
                "pairs": [[*a, *b, c] for (a, b), c in sorted(self.pairs.items())],
                "escaped_units": self.escaped_units, "outside_inventory": self.outside_inventory,
                "round_trip_types": self.round_trip_types}

    @classmethod
    def from_json(cls, data):
        return cls(data["N"], data["space_units"],
                   Counter({(k, l): c for k, l, c in data["unigrams"]}),
                   Counter({((k, l), (j, m)): c for k, l, j, m, c in data["pairs"]}),
                   data["escaped_units"], data["outside_inventory"], data.get("round_trip_types", 0)).validate()


def from_style(record: dict, assignment: dict[str, Action]) -> ActionTables:
    mapping = {**assignment, SPACE: SPACE_ACTION}
    missing = set(record["label_counts"]) - set(mapping)
    if missing:
        raise ValueError("style action mapping is incomplete")
    out = ActionTables(record["N"], record["space_units"],
                       escaped_units=record["escaped_unit_count"],
                       outside_inventory=record["outside_inventory_count"])
    for label, count in record["label_counts"].items():
        out.unigrams[mapping[label]] += count
    for a, b, count in record["pair_counts"]:
        out.pairs[mapping[a], mapping[b]] += count
    if sum(c for a, c in out.unigrams.items() if a != SPACE_ACTION) != record["keystrokes_excluding_space"]:
        raise ValueError("style keystroke counts disagree")
    return out.validate()


def from_tokens(rows, keymap, record: dict, units: UnitSet | None = None) -> ActionTables:
    """Encode once using caller's frozen policy. No word text is serialized."""
    units = units or UnitSet.from_inventory()
    out = ActionTables(record["N"], record["space_units"],
                       outside_inventory=record.get("out_of_inventory_characters", 0))
    running_tokens = computed_units = 0
    for token, count, first, last in rows:
        if count <= 0 or not 0 <= first <= count or not 0 <= last <= count:
            raise ValueError("invalid token boundary counts")
        target = nfc(token)
        steps = keymap.encode(target)
        if keymap.decode(steps) != target:
            raise ValueError("baseline encoder failed NFC round trip")
        out.round_trip_types += 1
        running_tokens += count
        computed_units += count * sum(units.is_unit(u) for u in segment(target))
        previous = None
        for step in steps:
            if isinstance(step, Escape):
                out.escaped_units += count * units.is_unit(step.char)
                previous = None
                continue
            action = (step.key, step.layer)
            out.unigrams[action] += count
            if previous is not None:
                out.pairs[previous, action] += count
            previous = action
        if steps:
            if not isinstance(steps[0], Escape):
                out.pairs[SPACE_ACTION, (steps[0].key, steps[0].layer)] += count - first
            if not isinstance(steps[-1], Escape):
                out.pairs[(steps[-1].key, steps[-1].layer), SPACE_ACTION] += count - last
    if computed_units + out.space_units != out.N or running_tokens != record["tokens"]:
        raise ValueError("token table disagrees with corpus unit/token counts")
    out.unigrams[SPACE_ACTION] = out.space_units
    return out.validate()


def j_reference(tables: ActionTables, model: KeyModel) -> dict:
    tables.validate()
    e1 = modifier = 0.0
    modifier_known = True
    parts = dict.fromkeys(("same_finger", "neighbour_penalty", "neighbour_benefit"), 0.0)
    for (key, layer), count in tables.unigrams.items():
        if key == "SPACE":
            continue
        if key not in model.keys:
            raise ValueError("unknown physical key in reference scoring")
        e1 += count * model.effort(key)
        m = model.modifier_effort(key, layer)
        if m is None:
            modifier_known = False
        else:
            modifier += count * m
    for (a, b), count in tables.pairs.items():
        kind, value = model.penalty_keys(a[0], b[0], a == b)
        if kind != "none":
            parts[kind] += count * value
    n = tables.N
    e2 = sum(parts.values()) / n
    j0 = e1 / n + e2
    return {"J0": j0, "J1": j0 + modifier / n if modifier_known else None,
            "E1": e1 / n, "E2": e2, "M": modifier / n if modifier_known else None,
            **{"E2_" + k: v / n for k, v in parts.items()}}


def diagnostics(tables: ActionTables, model: KeyModel) -> dict:
    keyboard = ansi_staggered()
    centers = {k.name: k.center for k in keyboard.keys}
    nonspace = tables.N - tables.space_units
    presses = sum(c for a, c in tables.unigrams.items() if a != SPACE_ACTION)
    shift = sum(c for (k, layer), c in tables.unigrams.items() if layer == "shift")
    load = Counter()
    for (key, _), count in tables.unigrams.items():
        if key != "SPACE":
            load[model.keys[key].finger] += count
    pairs = repeats = same_finger = cross_hand = 0
    distance = 0.0
    for (a, b), count in tables.pairs.items():
        if "SPACE" in (a[0], b[0]):
            continue
        pairs += count
        fa, fb = model.keys[a[0]].finger, model.keys[b[0]].finger
        if a[0] == b[0]:
            repeats += count
        elif fa == fb:
            same_finger += count
            distance += count * math.dist(centers[a[0]], centers[b[0]])
        if (fa <= 4) != (fb <= 4):
            cross_hand += count
    return {"keystrokes_excluding_space": presses, "keystrokes_per_non_space_unit": presses / nonspace,
            "escaped_unit_share": tables.escaped_units / tables.N,
            "escaped_units": tables.escaped_units, "outside_inventory_count": tables.outside_inventory,
            "shift_share_of_non_space_presses": shift / presses if presses else None,
            "non_space_pair_count": pairs,
            "same_physical_key_repeat_count": repeats,
            "same_finger_different_key_count": same_finger,
            "cross_hand_pair_count": cross_hand,
            "same_finger_different_key_per_unit": same_finger / tables.N,
            "same_finger_center_distance_u_per_unit": distance / tables.N,
            "finger_presses_excluding_modifiers": {str(f): c for f, c in sorted(load.items())},
            "round_trip_token_types": tables.round_trip_types}
