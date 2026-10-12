"""Existing Bangla keyboard layouts scored as baselines.

The registry ``data/baselines/registry.json`` lists every baseline; reports
score all of them, so adding a layout needs a registry entry and, for a
layout Kala does not ship, one key-map file in ``data/baselines/`` (format in
``data/baselines/README.md``). Kinds:

``kala``    a fixed layout file in Kala's format (virtual-key layers
            ``normal``/``shift``/``altgr`` and ``combinations.sequences``),
            vendored under ``data/kala/``;
``avro-fixed``  a layout imported into Kala from Avro (the ``layout.json`` of
            a Kala package, vendored under ``data/baselines/layouts/``), typed
            with Kala's formatting rules (``scoring.avro_fixed``);
``keymap``  a project file: ``layers`` = {"base"|"shift"|"altgr": {key name:
            output}} with ANSI key names (``Q``, ``;``, ``/``, ``1``, ...) and
            optional ``sequences`` = {typed outputs: result}, as in Kala.

The registry's optional ``discover`` folders add every fixed layout found there
(none by default, so results do not depend on one computer). Only fixed
layouts are baselines: phonetic layouts (Avro Phonetic, Shohoj, any type
containing "phonetic") are never compared (owner decision, 10 October 2026).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from ..bangla.grammar import Action, KeyMap
from ..paths import DATA, PROJECT_ROOT, kala_path
from ..reference import sha256_file
from . import avro_fixed
from .layouts import kala_fixed_actions
from .model import KeyModel

REGISTRY = DATA / "baselines" / "registry.json"
LAYERS = ("base", "shift", "altgr")


def is_phonetic(layout_type: str | None) -> bool:
    return "phonetic" in (layout_type or "").lower()


def discover(folder: str) -> tuple[list[dict], list[dict]]:
    """(fixed layouts, skipped packages) of a Kala layouts folder."""
    root = Path(os.path.expandvars(folder))
    found, skipped = [], []
    for path in sorted(root.glob("*/layout.json")) if root.is_dir() else []:
        data = json.loads(path.read_text(encoding="utf-8"))
        kind = data.get("type")
        if kind != "avro-fixed":
            skipped.append({"file": path.as_posix(), "type": kind,
                            "reason": "phonetic layouts are never compared" if is_phonetic(kind) else "not a fixed layout type"})
            continue
        found.append({"name": data["name"], "kind": "avro-fixed", "file": path.as_posix(), "fingering": "traditional",
                      "discovered_in": folder,
                      "provenance": f"Kala package {path.parent.name}; developer {data.get('developer', '?')}; "
                                    f"options {json.dumps(data.get('options', {}), sort_keys=True)}"})
    return found, skipped


def load_registry(path: Path = REGISTRY, with_skipped: bool = False):
    """Registry entries plus every fixed layout in the discovery folders
    (a name already listed wins)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = [e for e in data["baselines"] if not is_phonetic(e.get("kind"))]
    skipped = []
    for folder in data.get("discover", []):
        found, missed = discover(folder)
        names = {e["name"] for e in entries}
        entries.extend(e for e in found if e["name"] not in names)
        skipped.extend(missed)
    return (entries, skipped) if with_skipped else entries


def source_path(entry: dict) -> Path:
    if entry["kind"] == "kala":
        return kala_path(entry["file"])
    path = Path(os.path.expandvars(entry["file"]))
    return path if path.is_absolute() else PROJECT_ROOT / path


def describe(entry: dict) -> dict:
    return {**entry, "sha256": sha256_file(source_path(entry))}


def keymap(entry: dict, model: KeyModel) -> KeyMap:
    data = json.loads(source_path(entry).read_text(encoding="utf-8"))
    if entry["kind"] == "avro-fixed":
        return avro_fixed.AvroFixedKeyMap(entry["name"], data["layers"], data.get("options", {}), model.effort)
    if entry["kind"] == "kala":
        actions = kala_fixed_actions(data["layers"])
        sequences = data.get("combinations", {}).get("sequences", {})
    elif entry["kind"] == "keymap":
        unknown = set(data["layers"]) - set(LAYERS)
        if unknown:
            raise ValueError(f"{entry['name']}: unknown layers {sorted(unknown)}")
        bad = [k for layer in data["layers"].values() for k in layer if k not in model.keys]
        if bad:
            raise ValueError(f"{entry['name']}: keys not on the ANSI grid: {bad}")
        actions = [Action(key, layer, output) for layer, mapping in data["layers"].items()
                   for key, output in mapping.items() if output]
        sequences = data.get("sequences", {})
    else:
        raise ValueError(f"{entry['name']}: unknown kind {entry['kind']}")
    return KeyMap(entry["name"], actions, sequences, effort=model.effort)
