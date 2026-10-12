"""Key maps scored in Phase 2: Kala's fixed Bangla layouts (baselines) and
the original analyzer's English layouts (scorer cross-check)."""
from __future__ import annotations

import json
from pathlib import Path

from ..bangla.grammar import Action, KeyMap
from ..colemak.keyboard import KeyboardLayout
from ..paths import kala_path
from .model import KeyModel, PhysicalKey

UNIJOY = "kala/layout/bn/UniJoy.json"
BIJOY = "kala/layout/bn/bn_bijoy_layout.json"

# Windows virtual-key codes used by Kala's layout files → ANSI key names.
VK_TO_KEY = {**{48 + d: str(d) for d in range(10)}, **{65 + i: chr(65 + i) for i in range(26)},
             186: ";", 187: "=", 188: ",", 189: "-", 190: ".", 191: "/", 192: "`",
             219: "[", 220: "\\", 221: "]", 222: "'"}
LAYER_NAMES = {"normal": "base", "shift": "shift", "altgr": "altgr"}


def kala_fixed_actions(layers: dict) -> list[Action]:
    actions = []
    for layer, mapping in layers.items():
        for vk, output in mapping.items():
            if int(vk) == 32:
                continue  # space: the thumb unit, outside the key model
            actions.append(Action(VK_TO_KEY[int(vk)], LAYER_NAMES[layer], output))
    return actions


def unijoy_keymap(model: KeyModel) -> KeyMap:
    data = json.loads(kala_path(UNIJOY).read_text(encoding="utf-8"))
    sequences = data.get("combinations", {}).get("sequences", {})
    return KeyMap("UniJoy (Kala)", kala_fixed_actions(data["layers"]), sequences, effort=model.effort)


def bijoy_matches_unijoy() -> bool:
    unijoy = json.loads(kala_path(UNIJOY).read_text(encoding="utf-8"))["layers"]
    bijoy = json.loads(kala_path(BIJOY).read_text(encoding="utf-8"))
    return unijoy == bijoy


def english_model_and_assignment(layout: KeyboardLayout) -> tuple[KeyModel, dict[str, Action]]:
    """Key model and char → action map of a configured analyzer layout."""
    keys, assignment = {}, {}
    for key in layout.keys:
        name = f"r{key.row}c{key.col}"
        keys[name] = PhysicalKey(name, key.effort, key.finger, key.row)
        for layer, ch in enumerate(key.chars):
            assignment.setdefault(ch, Action(name, str(layer), ch))
    model = KeyModel(keys, f"analyzer config of {layout.name}", same_finger=layout.penalty_same_finger,
                     neighbour=layout.penalty_neighbour_finger[:3])
    return model, assignment


def load_english_frequencies(path: Path, alphabet: str) -> tuple[dict[str, float], dict[tuple[str, str], float]]:
    """Unigram and bigram frequencies of an analyzer ``.freq`` file, each list
    normalized over the layout's characters in binary64 (the analyzer uses
    binary32)."""
    chars, bigrams = {}, {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split(" ")
        if line.startswith("#") or len(parts) < 2:
            continue
        token, count = parts[0].upper(), int(parts[1])
        if len(token) == 1 and token in alphabet:
            chars[token] = chars.get(token, 0) + count
        elif len(token) == 2 and token[0] in alphabet and token[1] in alphabet:
            bigrams[(token[0], token[1])] = bigrams.get((token[0], token[1]), 0) + count
    total_c, total_b = sum(chars.values()), sum(bigrams.values())
    return ({c: n / total_c for c, n in chars.items()}, {b: n / total_b for b, n in bigrams.items()})
