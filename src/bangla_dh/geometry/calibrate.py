"""Recover the unpublished distance scale P_d from the published effort grids.

Every published value is rounded to one decimal, so a candidate P_d
"matches" a key when the model value rounds (half-up) to the published one.
The score of a P_d is the number of matched 1u keys over the three published
grids (ISO with optimal fingers, ISO with traditional fingers, split matrix).
Wide keys are reported but not scored: their footprints were inferred from
the images, not published.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .effort_model import EffortParams, effort_grid, traditional_fingers
from .keyboards import Keyboard, iso_staggered, matrix_split


def round1(value: float) -> float:
    return float(Decimal(repr(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


@dataclass
class GridComparison:
    grid: str
    key: str
    published: float
    model: float
    finger: str
    one_unit: bool

    @property
    def matches(self) -> bool:
        return round1(self.model) == self.published

    @property
    def deviation(self) -> float:
        return self.model - self.published


def grid_cases(published: dict) -> list[tuple[str, Keyboard, dict | None, dict]]:
    grids = published["effort_grids"]
    iso, matrix = iso_staggered(), matrix_split()
    return [
        ("iso_optimal_fingers", iso, None, grids["iso_optimal_fingers"]["values"]),
        ("iso_traditional_fingers", iso, traditional_fingers(iso), grids["iso_traditional_fingers"]["values"]),
        ("matrix_optimal_fingers", matrix, None, grids["matrix_optimal_fingers"]["values"]),
    ]


def compare_grids(published: dict, params: EffortParams) -> list[GridComparison]:
    rows = []
    for name, keyboard, assignment, values in grid_cases(published):
        grid = effort_grid(keyboard, params, assignment)
        for key_name, value in values.items():
            key = keyboard.key(key_name)
            cell = grid[key_name]
            rows.append(GridComparison(name, key_name, float(value), cell.effort, cell.finger, key.width == 1.0))
    return rows


def scan_distance_scale(published: dict, base: EffortParams | None = None,
                        start: float = 0.9, stop: float = 1.3, step: float = 0.0005) -> dict:
    base = base or EffortParams()
    count = int(round((stop - start) / step))
    scores = []
    for i in range(count + 1):
        pd = round(start + i * step, 6)
        rows = compare_grids(published, base.with_distance_scale(pd))
        scored = [r for r in rows if r.one_unit]
        scores.append((pd, sum(r.matches for r in scored), len(scored)))
    best = max(score for _, score, _ in scores)
    intervals, current = [], None
    for pd, score, _ in scores:
        if score == best:
            current = [pd, pd] if current is None else [current[0], pd]
        elif current is not None:
            intervals.append(current)
            current = None
    if current is not None:
        intervals.append(current)
    widest = max(intervals, key=lambda iv: iv[1] - iv[0])
    return {
        "range": [start, stop], "step": step, "scored_keys": scores[0][2],
        "best_matches": best, "best_intervals": intervals,
        "widest_best_interval": widest,
        "curve": [{"distance_scale": pd, "matches": score} for pd, score, _ in scores],
    }


def config_grid_consistency(published: dict, resource) -> list[dict]:
    """Compare the image-transcribed ISO grids with the analyzer config files
    the comparison table actually used. Returns every disagreement."""
    from ..colemak.keyboard import load_layout
    from .analyzer_config import position_rows

    checks = [("iso_optimal_fingers", "effort_ergonomic_config.dat", "angle"),
              ("iso_traditional_fingers", "effort_traditional_config.dat", "std")]
    problems = []
    for grid_name, config, bottom in checks:
        values = published["effort_grids"][grid_name]["values"]
        layout = load_layout(resource("layout_full/qwerty.keyb"), resource("config/" + config))
        for row, names in enumerate(position_rows(bottom)):
            for col, name in enumerate(names):
                key = layout.lookup_pos(row, col)
                if key is not None and key.effort != values[name]:
                    problems.append({"grid": grid_name, "config": config, "key": name,
                                     "config_value": key.effort, "image_value": values[name]})
    return problems


def summarize(rows: list[GridComparison]) -> dict:
    out = {}
    for name in dict.fromkeys(r.grid for r in rows):
        sub = [r for r in rows if r.grid == name]
        one = [r for r in sub if r.one_unit]
        out[name] = {
            "keys": len(sub), "one_unit_keys": len(one),
            "one_unit_matches": sum(r.matches for r in one),
            "all_matches": sum(r.matches for r in sub),
            "max_abs_deviation_one_unit": max(abs(r.deviation) for r in one),
            "max_abs_deviation_all": max(abs(r.deviation) for r in sub),
            "mismatches": [{"key": r.key, "published": r.published, "model": round(r.model, 4),
                            "finger": r.finger, "one_unit": r.one_unit} for r in sub if not r.matches],
        }
    return out
