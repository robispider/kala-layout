"""The Kala application files this research uses, vendored under ``data/kala/``.

The layout research was done inside the Kala repository. To make it
repeatable outside it, the few small files it reads are copied here at their
original relative paths (``data/kala/<path in the Kala repository>``) and
pinned by SHA-256 in ``data/kala/SOURCES.json``. The large text corpora are
not part of this list: they come from the public ``ban-dataset-collection``
(``bangla_dh.datasets``).
"""
from __future__ import annotations

import json

from .paths import KALA_INPUTS
from .reference import sha256_file

SOURCES_FILE = KALA_INPUTS / "SOURCES.json"

# (path in the Kala repository, role, description)
TRACKED_SOURCES = [
    ("data/bn/Alphabet.json", "character-inventory", "Consonants, vowels, vowel signs, hasant, digits used by Kala"),
    ("kala/layout/bn/Alphabet.json", "character-inventory", "Runtime copy of the Bangla alphabet"),
    ("kala/layout/bn/conjuncts.json", "character-inventory", "Conjunct inventory (consonant + hasant + consonant)"),
    ("kala/layout/bn/UniJoy.json", "baseline-layout", "UniJoy fixed layout (normal/shift layers by virtual-key code)"),
    ("kala/layout/bn/bn_bijoy_layout.json", "baseline-layout", "Bijoy fixed layout (a copy of UniJoy)"),
    ("tools/kala-eval/datasets/top20k.tsv", "word-list", "Top 20k Bangla words with corpus counts (round-trip checks)"),
    ("tools/kala-eval/datasets/err_frequent_gold.tsv", "word-list", "Frequent gold words (round-trip checks)"),
    ("tools/kala-eval/datasets/err_inflected.tsv", "word-list", "Inflected word forms (round-trip checks)"),
    ("tools/kala-eval/datasets/err_rare_gold.tsv", "word-list", "Rare gold words (round-trip checks)"),
    ("tools/kala-eval/datasets/err_usage_dev.tsv", "word-list", "Usage development words (round-trip checks)"),
    ("tools/kala-eval/datasets/err_usage_test.tsv", "word-list", "Usage test words (round-trip checks)"),
]


def inventory() -> dict:
    """The vendored Kala inputs with their sizes and SHA-256."""
    sources = []
    for relative, role, description in TRACKED_SOURCES:
        path = KALA_INPUTS / relative
        entry = {"path": relative, "role": role, "description": description, "location": "data/kala",
                 "present": path.is_file()}
        if entry["present"]:
            entry.update(bytes=path.stat().st_size, sha256=sha256_file(path))
        sources.append(entry)
    return {"description": "Small Kala application files vendored under data/kala/ and read by the research.",
            "sources": sources}


def write_sources_file() -> None:
    SOURCES_FILE.write_text(json.dumps(inventory(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
