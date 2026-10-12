"""Keyboard layout, key and configuration model of the original analyzer.

Port of ``Key.kt``, ``KeyboardLayout.kt``, ``KeyboardMapping.kt`` and
``KeyboardConfig.kt`` from stevep99/keyboard-layout-analysis-tool (pinned in
``reference/sources.lock.json``). Behavior, including quirks, is preserved;
deviations are documented in ``docs/colemak-model-spec.md``.

Fingers are numbered 0-9 from the left pinky to the right pinky; 4 and 5 are
the thumbs. Rows are numbered from the top of the layout file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .javacompat import (
    java_is_alphabetic, java_is_lower_case, java_lower_char, java_split, java_upper_char,
    kotlin_trim, kotlin_trim_ascii, strip_comment,
)

KEYBOARD_TYPES = ("STD", "ANGLE", "MATRIX_SIMPLE", "MATRIX_ERGODOX")
SECTIONS = ("FINGERS", "EFFORT", "PENALTIES", "TYPE")

_DEFAULT_SHIFTED = {
    "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")",
    "'": '"', "-": "_", "=": "+", "[": "{", "]": "}", ";": ":", ",": "<", ".": ">", "/": "?",
}


def default_shifted(ch: str) -> str | None:
    if java_is_alphabetic(ch):
        # Caseless letters (all of Bangla) "shift" to themselves, so the key
        # carries the same character twice. See the model spec, section 6.
        return java_upper_char(ch) if java_is_lower_case(ch) else java_lower_char(ch)
    return _DEFAULT_SHIFTED.get(ch)


def default_finger(col: int) -> int:
    if col <= 3:
        return col
    if col == 4:
        return 3
    if col == 5:
        return 6
    if col <= 9:
        return col
    return 9


def hand_of(finger: int) -> str:
    return "LEFT" if finger <= 4 else "RIGHT"


@dataclass(eq=False)
class Key:
    """A physical key. Identity-hashed, like the Kotlin class."""

    row: int
    col: int
    chars: str
    finger: int
    effort: float = 0.0

    @classmethod
    def create(cls, row: int, col: int, input_chars: str) -> "Key":
        chars = input_chars
        if len(input_chars) == 1:
            shifted = default_shifted(input_chars)
            if shifted is not None:
                chars = input_chars + shifted
        return cls(row, col, chars, default_finger(col))

    def has_char(self, ch: str) -> bool:
        # Kotlin: chars.any { it == ch.uppercaseChar() }
        target = java_upper_char(ch)
        return target in self.chars

    @property
    def name(self) -> str:
        return java_upper_char(self.chars[0])

    @property
    def primary_char(self) -> str:
        return self.chars[0]

    @property
    def hand(self) -> str:
        return hand_of(self.finger)


@dataclass
class KeyboardLayout:
    name: str
    keys: list[Key] = field(default_factory=list)
    cols: int = 0
    rows: int = 0
    penalty_same_finger: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    penalty_neighbour_finger: list[list[float]] = field(default_factory=lambda: [[0.0] * 3 for _ in range(4)])
    keyboard_type: str = "STD"

    def add_key(self, row: int, col: int, chars: str) -> None:
        key = Key.create(row, col, chars)
        self.keys.append(key)
        self.cols = max(self.cols, key.col + 1)
        self.rows = max(self.rows, key.row + 1)

    def lookup_char(self, ch: str) -> Key | None:
        for key in self.keys:
            if key.has_char(ch):
                return key
        return None

    def lookup_pos(self, row: int, col: int) -> Key | None:
        for key in self.keys:
            if key.row == row and key.col == col:
                return key
        return None

    def alphabet(self) -> str:
        return "".join(key.chars for key in self.keys)

    def primary_chars(self) -> str:
        return "".join(key.primary_char for key in self.keys)

    def missing_letters(self) -> list[str]:
        letters = self.alphabet()
        return [f"Warning: letter {chr(c)} is missing from layout. "
                for c in range(ord("A"), ord("Z") + 1) if chr(c) not in letters]

    def duplicate_letters(self) -> list[str]:
        letters = self.alphabet()
        return [f"Warning: letter {c} appears more than once on layout. "
                for i, c in enumerate(letters) if letters.find(c, i + 1) >= 0]

    def validate(self) -> list[str]:
        return self.missing_letters() + self.duplicate_letters()

    def get_penalty_same_finger(self, rowdiff: int) -> float:
        return self.penalty_same_finger[rowdiff]

    @staticmethod
    def _left_equivalent(finger: int) -> int:
        return finger if finger <= 4 else 9 - finger

    def get_penalty_neighbour_finger(self, outermost_finger: int, rowdiff: int) -> float:
        index = self._left_equivalent(outermost_finger)
        if len(self.penalty_neighbour_finger) <= index:
            return 0.0
        return self.penalty_neighbour_finger[index][rowdiff]

    def has_penalty_neighbour_finger(self, outermost_finger: int) -> bool:
        index = self._left_equivalent(outermost_finger)
        if len(self.penalty_neighbour_finger) <= index:
            return False
        return any(value > 0 for value in self.penalty_neighbour_finger[index][:3])


def is_same_finger(f1: int, f2: int) -> bool:
    return f1 == f2


def is_neighbour_finger(f1: int, f2: int) -> bool:
    return abs(f1 - f2) == 1


def outermost_finger(f1: int, f2: int) -> int:
    left1 = f1 if f1 <= 4 else 9 - f1
    left2 = f2 if f2 <= 4 else 9 - f2
    return f1 if left1 < left2 else f2


def parse_layout(text: str, name: str) -> KeyboardLayout:
    """``KeyboardMapping.read``: one row per non-empty line, space separated."""
    layout = KeyboardLayout(name)
    row = 0
    for raw in text.splitlines():
        line = kotlin_trim_ascii(strip_comment(raw))
        if not line:
            continue
        for col, chars in enumerate(java_split(line, " ")):
            layout.add_key(row, col, chars)
        row += 1
    return layout


class ConfigError(ValueError):
    pass


def apply_config(layout: KeyboardLayout, text: str) -> list[str]:
    """``KeyboardConfig.read``: apply finger, effort, penalty and type sections.

    Returns the diagnostics the original prints to stderr (invalid section
    names are reported and ignored there as well).
    """
    diagnostics: list[str] = []
    section, section_rows, row = "FINGERS", 3, 0
    for raw in text.splitlines():
        line = kotlin_trim(strip_comment(raw))
        if not line:
            continue
        if ":" in line:
            tokens = java_split(line, ":")
            name = tokens[0].upper() if tokens else ""
            if name in SECTIONS:
                section = name
                section_rows = int(kotlin_trim_ascii(tokens[1])) if len(tokens) > 1 else 3
                row = 0
            else:
                diagnostics.append(f"Invalid section {tokens[0] if tokens else ''}")
            continue
        tokens = java_split(line, " ")
        if section in ("EFFORT", "FINGERS"):
            keyboard_row = row + (layout.rows - section_rows)
            if keyboard_row >= 0:
                for col, token in enumerate(tokens):
                    key = layout.lookup_pos(keyboard_row, col)
                    if key is None:
                        continue
                    if section == "EFFORT":
                        key.effort = float(token)
                    else:
                        key.finger = int(token)
        elif section == "PENALTIES":
            for rowdiff, token in enumerate(tokens):
                if row == 0:
                    layout.penalty_same_finger[rowdiff] = float(token)
                else:
                    layout.penalty_neighbour_finger[row - 1][rowdiff] = float(token)
        elif section == "TYPE":
            keyboard_type = tokens[0].upper()
            if keyboard_type not in KEYBOARD_TYPES:
                raise ConfigError(f"Invalid KeyboardType {tokens[0]}")
            layout.keyboard_type = keyboard_type
        row += 1
    return diagnostics


def load_layout(layout_path: str | Path, *config_paths: str | Path, name: str | None = None) -> KeyboardLayout:
    layout_path = Path(layout_path)
    layout = parse_layout(layout_path.read_text(encoding="utf-8"), name or layout_path.name)
    for config_path in config_paths:
        apply_config(layout, Path(config_path).read_text(encoding="utf-8"))
    return layout
