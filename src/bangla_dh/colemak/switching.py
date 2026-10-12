"""Switching difficulty between two layouts: port of ``KeyboardCompare`` and
``ExperienceCurve``.

    d = sum_k  m_k * C(100 * f_k) * S2_k / S1_k
    C(f) = f^(p+1) / (p+1),   p = log2(b),   b = 0.8

m is the movement score (0, 0.25, 0.5, 0.75, 1 or a per-key override), f the
binary32 character frequency (so 100 * f is a binary32 percentage), and S1/S2
the key effort of the old/new position. The implementation includes the
S2/S1 ratio; learn.html's closing summary formula omits it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from .frequency import CharFreq
from .javacompat import f32
from .keyboard import KeyboardLayout

EXPERIENCE_B = 0.8


class ExperienceCurve:
    def __init__(self, b: float = EXPERIENCE_B):
        self.b = b
        self.p = math.log(b) / math.log(2.0)

    def instant_cost(self, freq: float) -> float:
        return freq ** self.p

    def integrated_cost(self, freq: float) -> float:
        return freq ** (self.p + 1) / (self.p + 1)


MOVEMENT_CLASSES = ("unchanged", "same_finger", "same_hand", "equivalent_finger_other_hand",
                    "other_finger_other_hand", "override")


@dataclass
class KeySwitch:
    char: str
    movement: float
    movement_class: str
    freq: float | None
    freq_cost: float | None
    effort_ratio: float
    score: float | None


@dataclass
class SwitchingResult:
    keys: list[KeySwitch] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=lambda: {c: 0 for c in MOVEMENT_CLASSES})
    keys_moved_index: float = 0.0  # sum of m over all primary keys
    total_freq: float = 0.0
    switching_difficulty: float = 0.0  # d

    @property
    def keys_moved(self) -> int:
        c = self.counts
        return c["same_finger"] + c["same_hand"] + c["equivalent_finger_other_hand"] + c["other_finger_other_hand"]

    @property
    def keys_moved_finger(self) -> int:
        c = self.counts
        return c["same_hand"] + c["equivalent_finger_other_hand"] + c["other_finger_other_hand"]


def parse_properties(text: str) -> dict[str, str]:
    """Minimal ``java.util.Properties`` reader (key=value / key:value lines)."""
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line[0] in "#!":
            continue
        for i, ch in enumerate(line):
            if ch in "=:":
                result[line[:i].strip()] = line[i + 1:].strip()
                break
        else:
            result[line] = ""
    return result


def compare_layouts(old: KeyboardLayout, new: KeyboardLayout, char_freqs: list[CharFreq],
                    overrides: dict[str, str] | None = None, b: float = EXPERIENCE_B) -> SwitchingResult:
    curve = ExperienceCurve(b)
    result = SwitchingResult()
    for ch in old.primary_chars().upper():
        key1, key2 = old.lookup_char(ch), new.lookup_char(ch)
        override = overrides.get(ch) if overrides is not None else None
        if override is not None:
            movement, cls = float(override), "override"
        elif key1 is not None and key2 is not None:
            if key1.col == key2.col and key1.row == key2.row:
                movement, cls = 0.0, "unchanged"
            elif key1.finger == key2.finger:
                movement, cls = 0.25, "same_finger"
            elif key1.hand == key2.hand:
                movement, cls = 0.5, "same_hand"
            elif key1.finger + key2.finger == 9:
                movement, cls = 0.75, "equivalent_finger_other_hand"
            else:
                movement, cls = 1.0, "other_finger_other_hand"
        else:
            movement, cls = 1.0, "other_finger_other_hand"
        result.counts[cls] += 1
        result.keys_moved_index += movement
        ratio = key2.effort / key1.effort if key1 is not None and key2 is not None else 1.0
        cf = next((c for c in char_freqs if c.char == ch), None)
        if cf is None:
            result.keys.append(KeySwitch(ch, movement, cls, None, None, ratio, None))
            continue
        freq_cost = curve.integrated_cost(f32(100 * cf.freq))
        score = movement * freq_cost * ratio
        result.keys.append(KeySwitch(ch, movement, cls, cf.freq, freq_cost, ratio, score))
        result.total_freq += cf.freq
        result.switching_difficulty += score
    return result


def load_overrides(path: str | Path) -> dict[str, str]:
    return parse_properties(Path(path).read_text(encoding="utf-8"))
