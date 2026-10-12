"""Independent J0 verifier (RESEARCH_SPEC section 9).

Recomputes J0 of a single-action layout straight from corpus text, sharing
no code with ``scoring.j0``, ``scoring.model``, ``bangla.grammar`` or the
frequency tables: it reads only data files (the inventory JSON, the effort
grid JSON, the corpus JSON lines) and implements its own unit splitting,
finger rules and penalty table. Agreement with the table-based scorer checks
segmentation, counting, normalization and the penalty logic together.
"""
from __future__ import annotations

import gzip
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

_SAME = {0: 2.5, 1: 3.0, 2: 4.0}
# Unordered pair of finger types on one hand → penalty by row difference.
_NEIGHBOUR = {frozenset(("pinky", "ring")): {0: 0.5, 1: 1.0, 2: 1.5},
              frozenset(("ring", "middle")): {0: 0.1, 1: 0.2, 2: 0.3},
              frozenset(("middle", "index")): {0: -0.2, 1: -0.1, 2: 0.0}}
_TYPE = {"0": "pinky", "1": "ring", "2": "middle", "3": "index"}
_NUKTA_PAIRS = {"ড়", "ঢ়", "য়"}


def verify_j0(corpus_files: list[Path], layout: dict[str, str], inventory_file: Path, grid_file: Path) -> dict:
    """J0 of ``layout`` (unit → key name; one action per unit, all on the
    base layer or on distinct keys) over the given corpus files."""
    inventory = json.loads(Path(inventory_file).read_text(encoding="utf-8"))
    counted = {e["symbol"] for e in inventory["symbols"]} | {" "}
    grid = {k["key"]: k for k in json.loads(Path(grid_file).read_text(encoding="utf-8"))["keys"]}

    def penalty(unit_a: str, unit_b: str) -> float:
        if unit_a == unit_b:
            return 0.0
        key_a, key_b = layout.get(unit_a), layout.get(unit_b)
        if key_a is None or key_b is None:
            return 0.0
        ga, gb = grid[key_a], grid[key_b]
        rows = min(2, abs(int(ga["y"]) - int(gb["y"])))
        if ga["finger"] == gb["finger"]:
            return _SAME[rows]
        if ga["finger"][0] != gb["finger"][0]:
            return 0.0
        table = _NEIGHBOUR.get(frozenset((_TYPE[ga["finger"][1]], _TYPE[gb["finger"][1]])))
        return table[rows] if table else 0.0

    n = 0
    effort = 0.0
    bigram = 0.0
    for path in corpus_files:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                for paragraph in json.loads(line)["paragraphs"]:
                    previous = None
                    i = 0
                    while i < len(paragraph):
                        pair = paragraph[i:i + 2]
                        unit = pair if pair in _NUKTA_PAIRS else paragraph[i]
                        i += len(unit)
                        if unit not in counted:
                            previous = None
                            continue
                        n += 1
                        key = layout.get(unit)
                        if key is not None:
                            effort += grid[key]["effort"]
                        if previous is not None:
                            bigram += penalty(previous, unit)
                        previous = unit
    return {"N": n, "E1": effort / n, "E2": bigram / n, "J0": (effort + bigram) / n}


# --- Phase 3: vowel-entry styles and J1 -----------------------------------------
#
# ``verify_style`` recomputes J0 and J1 of a style layout from corpus text. It
# shares no code with ``bangla.styles`` (which simulates typing and searches
# for the label sequence): here every style is written as direct rules on the
# previous unit and on ``pending``, the label of the previous keystroke when
# a repeat of that key would change its output (A: ্; B, D: the sign key of an
# open run of repeated presses, which a single press would re-pair; C: an
# independent vowel from one press). B and D runs (owner rule of 10 October
# 2026): a run of n presses gives the sign once if n is odd, then n // 2
# independent vowels, so after a run the independent vowel is two more
# presses and the run stays open.

def _style_keystrokes(style: str, unit: str, previous_unit, pending, kind: str, sign_of: dict, vowel_of: dict,
                      consonants: set, keyed: set):
    """(labels or None for an escape, new pending)."""
    if kind == "vowel" and unit in sign_of:          # independent vowel other than অ
        sign = sign_of[unit]
        if style == "A":
            return ["্", sign], None
        if style == "B":
            return [sign, sign], sign
        if style == "C":
            return (None, None) if pending == unit else ([unit], unit)
        if previous_unit in consonants or pending == sign:   # D: a run after a consonant
            return [sign, sign], sign
        return [sign], None
    if kind == "vowel_sign":
        if style == "A":
            return (None, None) if pending == "্" else ([unit], None)
        if style == "B":
            return (None, None) if pending == unit else ([unit], unit)
        if style == "C":
            vowel = vowel_of[unit]
            return (None, None) if pending == vowel else ([vowel, vowel], None)
        return ([unit], unit) if previous_unit in consonants else (None, None)
    if unit in keyed:
        return [unit], ("্" if unit == "্" and style == "A" else None)
    return None, None


def verify_style(corpus_files: list[Path], style: str, layout: dict[str, str], inventory_file: Path,
                 grid_file: Path) -> dict:
    """J0 and J1 of a style layout (label → "KEY/layer", fixed keys included)
    over the given corpus files, with the keystroke and escape counts. The
    totals are exact rationals of the grid's decimal values (``J1_exact``),
    so they can be compared with Phase 4's integer objective without a
    tolerance."""
    import unicodedata

    inventory = json.loads(Path(inventory_file).read_text(encoding="utf-8"))
    kind_of = {e["symbol"]: e["class"] for e in inventory["symbols"]}
    counted = set(kind_of) | {" "}
    consonants = {s for s, k in kind_of.items() if k == "consonant"}
    sign_of = {}
    for s, k in kind_of.items():
        if k == "vowel_sign":
            sign_of[unicodedata.lookup(unicodedata.name(s).replace("VOWEL SIGN", "LETTER"))] = s
    vowel_of = {s: v for v, s in sign_of.items()}
    grid = {k["key"]: k for k in json.loads(Path(grid_file).read_text(encoding="utf-8"))["keys"]}
    place = {label: tuple(slot.rsplit("/", 1)) for label, slot in layout.items()}
    keyed = set(place)

    def shift(key: str) -> float:
        return grid["RSHIFT" if grid[key]["finger"][0] == "L" else "LSHIFT"]["effort"]

    def penalty(label_a: str, label_b: str) -> float:
        if label_a == label_b:
            return 0.0
        ga, gb = grid[place[label_a][0]], grid[place[label_b][0]]
        rows = min(2, abs(int(ga["y"]) - int(gb["y"])))
        if ga["finger"] == gb["finger"]:
            return _SAME[rows]
        if ga["finger"][0] != gb["finger"][0]:
            return 0.0
        table = _NEIGHBOUR.get(frozenset((_TYPE[ga["finger"][1]], _TYPE[gb["finger"][1]])))
        return table[rows] if table else 0.0

    # Counts, not running float sums: the totals are formed once, exactly, at the end.
    n = keystrokes = escaped = 0
    presses: dict[str, int] = {}
    shifted: dict[str, int] = {}
    penalties: dict[float, int] = {}
    for path in corpus_files:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                for paragraph in json.loads(line)["paragraphs"]:
                    previous_unit = previous_label = pending = None
                    i = 0
                    while i < len(paragraph):
                        pair = paragraph[i:i + 2]
                        unit = pair if pair in _NUKTA_PAIRS else paragraph[i]
                        i += len(unit)
                        if unit == " ":
                            n += 1
                            previous_unit = previous_label = pending = None
                            continue
                        if unit in counted:
                            n += 1
                            labels, pending = _style_keystrokes(style, unit, previous_unit, pending, kind_of[unit],
                                                                sign_of, vowel_of, consonants, keyed)
                        else:
                            labels, pending = None, None
                        previous_unit = unit
                        if labels is None:
                            escaped += unit in counted
                            previous_label = None
                            continue
                        for label in labels:
                            key, layer = place[label]
                            keystrokes += 1
                            presses[key] = presses.get(key, 0) + 1
                            if layer == "shift":
                                shifted[key] = shifted.get(key, 0) + 1
                            if previous_label is not None:
                                value = penalty(previous_label, label)
                                if value:
                                    penalties[value] = penalties.get(value, 0) + 1
                            previous_label = label
    exact = lambda x: Fraction(Decimal(repr(x)))  # noqa: E731  the decimal value written in the grid file
    effort = sum(c * exact(grid[k]["effort"]) for k, c in presses.items())
    modifier = sum(c * exact(shift(k)) for k, c in shifted.items())
    bigram = sum(c * exact(v) for v, c in penalties.items())
    j1 = (effort + bigram + modifier) / n
    return {"N": n, "keystrokes_excluding_space": keystrokes, "escaped_units": escaped,
            "E1": float(effort / n), "E2": float(bigram / n), "M": float(modifier / n),
            "J0": float((effort + bigram) / n), "J1": float(j1),
            "J1_exact": f"{j1.numerator}/{j1.denominator}"}
