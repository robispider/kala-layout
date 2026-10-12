"""Reconstruction of the Colemak Mod-DH "Typing Effort Grid" (model.html).

    P_total(key, finger) = P_f + sqrt((P_f * F_y)^2 + (P_x * F_x)^2)
    F_x = log2(1 + P_d * D_x),   F_y = log2(1 + P_d * D_y)

D_x / D_y are the lateral / mesial (along-forearm) components of the vector
from the finger's resting point to the nearest point of the key's activation
area. The activation area is the key footprint inset by the margin on every
side. Published constants: P_f, P_x = 2.0, approach angle 10 deg (0 on split
boards), margin 0.3u and the resting displacements. Not published, recovered
by ``calibrate``: P_d, the contact point (Euclidean nearest point of the area,
measured on the keyboard plane) and the rule that a finger's own home key
costs exactly P_f. See docs/colemak-model-spec.md section 3.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from .keyboards import Keyboard, PhysicalKey

FINGER_NAMES = ("pinky", "ring", "middle", "index")
FINGER_FACTOR = {"pinky": 1.6, "ring": 1.3, "middle": 1.1, "index": 1.0}
# model.html: resting point relative to the home-key centre, (x, y) in u with
# y positive upward, for the left hand. The right hand mirrors x.
HOME_DISPLACEMENT = {"pinky": (0.01, 0.09), "ring": (0.00, 0.08), "middle": (0.03, 0.16), "index": (-0.04, -0.32)}


@dataclass(frozen=True)
class EffortParams:
    distance_scale: float = 1.1          # P_d (calibrated; not published)
    lateral_multiplier: float = 2.0      # P_x
    activation_margin: float = 0.3
    approach_angle_deg: float | None = None  # None: use the keyboard's own angle
    finger_factor: dict = field(default_factory=lambda: dict(FINGER_FACTOR))
    home_displacement: dict = field(default_factory=lambda: dict(HOME_DISPLACEMENT))
    mirror_right_displacement: bool = True
    home_key_is_rest: bool = True        # own home key costs exactly P_f

    def with_distance_scale(self, value: float) -> "EffortParams":
        return replace(self, distance_scale=value)


@dataclass(frozen=True)
class Finger:
    finger_id: str      # "L3" = left index, "R0" = right pinky
    hand: str
    name: str
    home_key: str
    rest: tuple[float, float]

    @property
    def analyzer_index(self) -> int:
        """Finger number used by the analyzer configs (0 = left pinky ... 9 = right pinky)."""
        position = FINGER_NAMES.index(self.name)
        return position if self.hand == "L" else 9 - position


def fingers_for(keyboard: Keyboard, params: EffortParams) -> list[Finger]:
    fingers = []
    for finger_id, key_name in keyboard.home_keys.items():
        hand, name = finger_id[0], FINGER_NAMES[int(finger_id[1])]
        dx, dy_up = params.home_displacement[name]
        if hand == "R" and params.mirror_right_displacement:
            dx = -dx
        cx, cy = keyboard.key(key_name).center
        fingers.append(Finger(finger_id, hand, name, key_name, (cx + dx, cy - dy_up)))
    return fingers


def _axes(hand: str, angle_deg: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """Unit vectors (forward, lateral) in keyboard coordinates (y down).

    Forearms converge towards the keyboard centre, so the left hand points up
    and to the right and the right hand up and to the left.
    """
    a = math.radians(angle_deg)
    if hand == "L":
        return (math.sin(a), -math.cos(a)), (math.cos(a), math.sin(a))
    return (-math.sin(a), -math.cos(a)), (math.cos(a), -math.sin(a))


def key_effort(keyboard: Keyboard, key: PhysicalKey, finger: Finger, params: EffortParams) -> float:
    pf = params.finger_factor[finger.name]
    if params.home_key_is_rest and key.name == finger.home_key:
        return pf
    m = params.activation_margin
    x0, x1 = key.x + m, key.x + key.width - m
    y0, y1 = key.y + m, key.y + key.height - m
    hx, hy = finger.rest
    px, py = min(max(hx, x0), x1), min(max(hy, y0), y1)
    angle = keyboard.approach_angle_deg if params.approach_angle_deg is None else params.approach_angle_deg
    forward, lateral = _axes(finger.hand, angle)
    vx, vy = px - hx, py - hy
    d_y = abs(vx * forward[0] + vy * forward[1])
    d_x = abs(vx * lateral[0] + vy * lateral[1])
    f_x = math.log2(1 + params.distance_scale * d_x)
    f_y = math.log2(1 + params.distance_scale * d_y)
    return pf + math.hypot(pf * f_y, params.lateral_multiplier * f_x)


@dataclass(frozen=True)
class GridCell:
    key: str
    effort: float
    finger: str


def effort_grid(keyboard: Keyboard, params: EffortParams | None = None,
                assignment: dict[str, str] | None = None) -> dict[str, GridCell]:
    """Effort of every key: the cheapest finger, or the finger in ``assignment``."""
    params = params or EffortParams()
    fingers = fingers_for(keyboard, params)
    by_id = {f.finger_id: f for f in fingers}
    grid = {}
    for key in keyboard.keys:
        if assignment is not None and key.name in assignment:
            candidates = [by_id[assignment[key.name]]]
        else:
            candidates = [f for f in fingers if key.half is None or f.hand == key.half]
        best = min(((key_effort(keyboard, key, f, params), f.finger_id) for f in candidates),
                   key=lambda item: item[0])
        grid[key.name] = GridCell(key.name, best[0], best[1])
    return grid


_TRADITIONAL_FINGERS = {
    **{k: "L0" for k in ("`", "1", "Q", "A", "Z", "TAB", "CAPS", "LSHIFT")},
    **{k: "L1" for k in ("2", "W", "S", "X")},
    **{k: "L2" for k in ("3", "E", "D", "C")},
    **{k: "L3" for k in ("4", "5", "R", "T", "F", "G", "V", "B")},
    **{k: "R3" for k in ("6", "7", "Y", "U", "H", "J", "N", "M")},
    **{k: "R2" for k in ("8", "I", "K", ",")},
    **{k: "R1" for k in ("9", "O", "L", ".")},
    **{k: "R0" for k in ("0", "-", "=", "P", "[", "]", ";", "'", "#", "/", "BACKSPACE", "ENTER", "ENTER_LOW", "RSHIFT")},
}


def traditional_fingers(keyboard: Keyboard) -> dict[str, str]:
    """Traditional touch-typing finger per key on a row-staggered board (model.html
    "Standard Keyboard with traditional finger pattern"). The backslash key is
    bottom-left on ISO and top-right on ANSI."""
    fingers = dict(_TRADITIONAL_FINGERS)
    fingers["\\"] = "L0" if keyboard.name.startswith("iso") else "R0"
    return {name: finger for name, finger in fingers.items() if any(k.name == name for k in keyboard.keys)}
