"""Physical keyboard geometries in standard key units (u).

Coordinates: x grows to the right, y grows downward; a key occupies
[x, x + width] x [y, y + height]. Rows: 0 number, 1 top, 2 home, 3 bottom.
Key names are the Qwerty legends; wide keys use upper-case words.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicalKey:
    name: str
    x: float
    y: float
    width: float = 1.0
    height: float = 1.0
    half: str | None = None  # "L"/"R" on split boards: only that hand can reach it

    @property
    def row(self) -> int:
        return int(self.y)

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2


@dataclass(frozen=True)
class Keyboard:
    name: str
    keys: tuple[PhysicalKey, ...]
    approach_angle_deg: float
    home_keys: dict  # finger id -> key name; ids "L0".."L3" and "R0".."R3" (0 = pinky, 3 = index)

    def key(self, name: str) -> PhysicalKey:
        for key in self.keys:
            if key.name == name:
                return key
        raise KeyError(name)


def _row(y: float, x: float, items) -> list[PhysicalKey]:
    keys = []
    for item in items:
        name, width = (item, 1.0) if isinstance(item, str) else item
        keys.append(PhysicalKey(name, x, y, width))
        x += width
    return keys


_HOME = {"L0": "A", "L1": "S", "L2": "D", "L3": "F", "R3": "J", "R2": "K", "R1": "L", "R0": ";"}
_NUMBER_ROW = ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", ("BACKSPACE", 2.0)]


def iso_staggered() -> Keyboard:
    """ISO row-staggered board, the geometry of the published effort grids."""
    keys = (_row(0, 0, _NUMBER_ROW)
            + _row(1, 0, [("TAB", 1.5), "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", ("ENTER", 1.5)])
            + _row(2, 0, [("CAPS", 1.75), "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "#", ("ENTER_LOW", 1.25)])
            + _row(3, 0, [("LSHIFT", 1.25), "\\", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", ("RSHIFT", 2.75)]))
    return Keyboard("iso-staggered", tuple(keys), 10.0, dict(_HOME))


def ansi_staggered() -> Keyboard:
    """ANSI row-staggered board (Bangla-DH Pure v1 target).

    The 30 main keys and the number row sit exactly where they do on ISO; the
    differences are the 1.5u backslash, the 2.25u Enter and the 2.25u left Shift.
    """
    keys = (_row(0, 0, _NUMBER_ROW)
            + _row(1, 0, [("TAB", 1.5), "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", ("\\", 1.5)])
            + _row(2, 0, [("CAPS", 1.75), "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", ("ENTER", 2.25)])
            + _row(3, 0, [("LSHIFT", 2.25), "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", ("RSHIFT", 2.75)]))
    return Keyboard("ansi-staggered", tuple(keys), 10.0, dict(_HOME))


_MATRIX_LEFT = (("N_L0", "1", "2", "3", "4", "5", "N_L6"), ("TAB", "Q", "W", "E", "R", "T", "T_L6"),
                ("CAPS", "A", "S", "D", "F", "G", "H_L6"), ("LSHIFT", "Z", "X", "C", "V", "B"))
_MATRIX_RIGHT = (("N_R0", "0", "9", "8", "7", "6", "N_R6"), ("T_R0", "P", "O", "I", "U", "Y", "T_R6"),
                 ("H_R0", ";", "L", "K", "J", "H", "H_R6"), ("RSHIFT", "/", ".", ",", "M", "N"))


def matrix_split() -> Keyboard:
    """Split column-aligned board of model.html's matrix grid (no approach angle).

    Each half has a 1.5u outer column, five finger columns and, on rows 0-2, an
    inner column; the right half mirrors the left. Halves are 4u apart and
    each key can only be typed by its own hand.
    """
    keys: list[PhysicalKey] = []
    right_edge = 7.0 + 4.0 + 7.0
    for half, rows in (("L", _MATRIX_LEFT), ("R", _MATRIX_RIGHT)):
        for y, names in enumerate(rows):
            for c, name in enumerate(names):
                width = 1.5 if c == 0 else 1.0
                x = -0.5 if c == 0 else float(c)
                if half == "R":
                    x = right_edge - (x + width)
                keys.append(PhysicalKey(name, x, float(y), width, half=half))
    return Keyboard("matrix-split", tuple(keys), 0.0, dict(_HOME))


KEYBOARDS = {"iso": iso_staggered, "ansi": ansi_staggered, "matrix": matrix_split}
