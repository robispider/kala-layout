"""The v1 optimization problem (Phase 3, task 1): ``data/problem-v1.json``.

Owner decisions of 10 October 2026 (RESEARCH_SPEC section 4): the 26 letter
keys of an ANSI keyboard with a base and a Shift layer give 52 slots; each
vowel-entry style searches exactly 52 symbols; digits and US punctuation are
fixed; ZWNJ/ZWJ get no key; ঽ ॥ — wait for the third layer. The file is
built from the frozen inventory and the style definitions, so every placed
or tracked unit has exactly one role in every style; ``check_problem``
verifies that.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..bangla.inventory import INVENTORY_FILE, load_inventory
from ..bangla.styles import (FIXED_OUTSIDE_INVENTORY, FIXED_PUNCTUATION, NO_KEY, STYLES, THIRD_LAYER, Alphabet,
                             Style)
from ..paths import DATA, relative_to_project
from ..reference import sha256_file
from ..scoring.model import ANSI_GRID

PROBLEM_VERSION = "bangla-dh-problem-v1"
PROBLEM_FILE = DATA / "problem-v1.json"
SEARCHED_KEYS = tuple("QWERTYUIOP") + tuple("ASDFGHJKL") + tuple("ZXCVBNM")
LAYERS = ("base", "shift")


def slots() -> list[tuple[str, str]]:
    """The 52 v1 slots, base layer first, keys in row order."""
    return [(key, layer) for layer in LAYERS for key in SEARCHED_KEYS]


def slot_name(slot: tuple[str, str]) -> str:
    return f"{slot[0]}/{slot[1]}"


def parse_slot(name: str) -> tuple[str, str]:
    key, layer = name.rsplit("/", 1)
    return key, layer


def fixed_assignment(alphabet: Alphabet) -> dict[str, tuple[str, str]]:
    """Bangla digits on the number row (base layer), ASCII punctuation at US positions."""
    digits = {d: (str(i), "base") for i, d in enumerate(alphabet.digits)}
    return {**digits, **FIXED_PUNCTUATION}


def build_problem(inventory: dict | None = None) -> dict:
    inventory = inventory or load_inventory()
    alphabet = Alphabet.from_inventory(inventory)
    fixed = fixed_assignment(alphabet)
    all_units = [e["symbol"] for e in inventory["symbols"]]
    styles = {}
    for name in STYLES:
        style = Style(name, alphabet)
        by_rule = sorted(set(all_units) - set(style.searched) - set(fixed) - set(THIRD_LAYER) - set(NO_KEY))
        styles[name] = {"description": style.description, "searched_symbols": list(style.searched),
                        "typed_by_rule": by_rule}
    problem = {
        "version": PROBLEM_VERSION,
        "decisions": "Owner decisions D1, D2, D4 of 10 October 2026 (RESEARCH_SPEC sections 4, 6.6, 7.1, 13); "
                     "D3 default (model-optimal fingering), D6 default (middle-index benefit kept)",
        "inventory": {"file": relative_to_project(INVENTORY_FILE),
                      "symbol_list_sha256": inventory["symbol_list_sha256"]},
        "keyboard": {"type": "ANSI row-staggered", "effort_grid": relative_to_project(ANSI_GRID),
                     "effort_grid_sha256": sha256_file(ANSI_GRID)},
        "searched_keys": list(SEARCHED_KEYS),
        "layers": list(LAYERS),
        "slots": [slot_name(s) for s in slots()],
        "fixed": {symbol: slot_name(slot) for symbol, slot in fixed.items()},
        "fixed_outside_inventory": {symbol: slot_name(slot) for symbol, slot in FIXED_OUTSIDE_INVENTORY.items()},
        "not_on_keys": {"third_layer": list(THIRD_LAYER), "no_key": list(NO_KEY)},
        "objective": {"primary": "J1 = J0 + sum_i u_i M(L(c_i)); M = K(RShift) for a shifted left-hand key, "
                                 "K(LShift) for a shifted right-hand key; lambda_m = 1, Q = 0",
                      "reported": ["J0", "J1"], "space": "thumb, K = 0, no bigram penalty",
                      "repeats": "the same key twice costs its effort twice and no bigram penalty"},
        "styles": styles,
    }
    canonical = json.dumps({k: problem[k] for k in ("slots", "fixed", "not_on_keys", "styles")}, ensure_ascii=False,
                           sort_keys=True)
    problem["problem_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return problem


def check_problem(problem: dict, inventory: dict | None = None) -> list[str]:
    """Problems with a problem file (empty when consistent)."""
    inventory = inventory or load_inventory()
    units = {e["symbol"] for e in inventory["symbols"]}
    out = []
    slot_names = problem["slots"]
    if len(slot_names) != len(set(slot_names)) or len(slot_names) != 52:
        out.append("slots are not 52 distinct key/layer pairs")
    fixed_slots = list(problem["fixed"].values()) + list(problem["fixed_outside_inventory"].values())
    if len(fixed_slots) != len(set(fixed_slots)) or set(fixed_slots) & set(slot_names):
        out.append("fixed symbols overlap each other or the searched slots")
    for name, style in problem["styles"].items():
        searched = style["searched_symbols"]
        if len(searched) != len(slot_names) or len(set(searched)) != len(searched):
            out.append(f"style {name}: {len(searched)} searched symbols for {len(slot_names)} slots")
        roles = searched + list(problem["fixed"]) + style["typed_by_rule"] + \
            problem["not_on_keys"]["third_layer"] + problem["not_on_keys"]["no_key"]
        if sorted(roles) != sorted(units):
            out.append(f"style {name}: units without exactly one role: "
                       f"{sorted(set(units) ^ set(roles)) or 'duplicates'}")
    return out


def load_problem(path: Path = PROBLEM_FILE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
