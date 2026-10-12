"""Text normalization applied to every corpus before counting (version
``bangla-dh-text-v1``).

1. Unicode NFC. ড় ঢ় য় become consonant + nukta (U+09BC); ো ৌ stay composed.
2. Character mappings (each one is a typing-equivalent spelling):
   curly double quotes → ``"``, curly single quotes → ``'``, hyphen and
   non-breaking hyphen → ``-``, BENGALI CURRENCY NUMERATOR FOUR (U+09F7,
   a common legacy stand-in for the danda) → ``।``.
3. Invisible format characters other than ZWJ/ZWNJ are removed (soft hyphen,
   zero-width space, BOM, direction marks).
4. Whitespace: every space-like character becomes U+0020, runs collapse to
   one space, and lines are stripped. Line breaks separate paragraphs and are
   never typing units.
"""
from __future__ import annotations

import re
import unicodedata

VERSION = "bangla-dh-text-v1"

CHARACTER_MAP = {
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "‐": "-", "‑": "-",
    "৷": "।",
}
REMOVED = "­​‎‏⁠﻿‪‫‬‭‮"
SPACES = "\t               　"

_TABLE = str.maketrans({**CHARACTER_MAP, **{c: None for c in REMOVED}, **{c: " " for c in SPACES}})
_SPACE_RUN = re.compile(" {2,}")


def normalize_line(line: str) -> str:
    text = unicodedata.normalize("NFC", line).translate(_TABLE)
    # Mappings never create or break canonical compositions, but stay safe.
    text = unicodedata.normalize("NFC", text)
    return _SPACE_RUN.sub(" ", text).strip()


def normalize_text(text: str) -> list[str]:
    """Normalized non-empty lines of ``text``."""
    lines = (normalize_line(line) for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    return [line for line in lines if line]


def describe() -> dict:
    return {
        "version": VERSION,
        "unicode_normalization": "NFC",
        "unicode_version": unicodedata.unidata_version,
        "character_map": {f"U+{ord(k):04X}": v for k, v in CHARACTER_MAP.items()},
        "removed": [f"U+{ord(c):04X}" for c in REMOVED],
        "to_space": [f"U+{ord(c):04X}" for c in SPACES],
        "joiners": "ZWJ (U+200D) and ZWNJ (U+200C) are kept",
        "lines": "space runs collapsed, lines stripped, empty lines dropped; a line break is not a typing unit",
    }
