"""Bangla symbol inventory v1, built from Kala's alphabet and validated
against Unicode (Phase 2, task 1).

Decision D1 is still open; this module implements its default: the Kala
alphabet (both copies: ``data/bn/Alphabet.json`` and the runtime
``kala/layout/bn/Alphabet.json``) plus ং ঃ ঁ ৎ । and the Bangla digits, every
entry validated. Each symbol is one typing unit:

* a single NFC code point, or
* one of the three nukta consonants ড় ঢ় য়, whose NFC form is two code
  points (base + U+09BC) because the precomposed characters are composition
  exclusions. One key emits the two-code-point sequence.

``placed`` symbols are what a Bangla-DH layout must put on keys. ``tracked``
units (ZWNJ, ZWJ) are counted in the frequency tables but are not placed
until the owner decides D1; Kala's alphabet does not list them.

Kala's conjunct lists are validated here too (they are not symbols in v1:
a conjunct is typed consonant + hasant + consonant).
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

from ..paths import DATA, kala_path
from ..reference import sha256_file

INVENTORY_VERSION = "bangla-symbols-v1"
INVENTORY_FILE = DATA / f"{INVENTORY_VERSION}.json"

ALPHABET_SOURCES = ("data/bn/Alphabet.json", "kala/layout/bn/Alphabet.json")
CONJUNCT_SOURCES = ("data/bn/Alphabet.json#conjuncts", "kala/layout/bn/conjuncts.json")

HASANT = "্"
NUKTA = "়"
NUKTA_BASES = {"ড": "ড়", "ঢ": "ঢ়", "য": "য়"}  # base -> precomposed
SPACE = " "
ZWNJ, ZWJ = "‌", "‍"

# Kala alphabet sections -> inventory class
SECTION_CLASS = {"consonants": "consonant", "vowels": "vowel", "matras": "vowel_sign", "halant": "hasant",
                 "digits": "digit", "punctuation": "punctuation", "other": "sign"}
# D1 default additions (already present in Kala's alphabet; listed so the
# default is explicit and checked).
D1_DEFAULT_REQUIRED = ["ং", "ঃ", "ঁ", "ৎ", "।"] + [chr(0x09E6 + d) for d in range(10)]
# Kala entries that normalization maps onto another symbol.
NORMALIZED_AWAY = {"‑": "normalized to '-' (bangla-dh-text-v1)"}
TRACKED = [(ZWNJ, "joiner"), (ZWJ, "joiner")]

# Punctuation outside the Bengali block that Bangla text uses. U+0964/U+0965
# are in the Devanagari block, but their Script_Extensions include Bengali.
PUNCTUATION_ALLOWED = set("।॥,?!;:\"'()-.—/%")


def _cp(text: str) -> list[str]:
    return [f"U+{ord(c):04X}" for c in text]


def _is_bengali(ch: str) -> bool:
    return 0x0980 <= ord(ch) <= 0x09FF


def is_consonant_unit(unit: str) -> bool:
    if len(unit) == 2:
        return unit[0] in NUKTA_BASES and unit[1] == NUKTA
    return len(unit) == 1 and (0x0995 <= ord(unit) <= 0x09B9) and unicodedata.category(unit) == "Lo"


def validate_symbol(symbol: str, cls: str) -> list[str]:
    """Problems with a candidate symbol (empty when valid)."""
    problems = []
    if unicodedata.normalize("NFC", symbol) != symbol:
        problems.append("not NFC")
    if cls == "consonant":
        if not is_consonant_unit(symbol):
            problems.append("not a Bengali consonant unit")
    elif cls == "vowel":
        if not (len(symbol) == 1 and 0x0985 <= ord(symbol) <= 0x0994 and unicodedata.category(symbol) == "Lo"):
            problems.append("not a Bengali independent vowel")
    elif cls == "vowel_sign":
        if not (len(symbol) == 1 and 0x09BE <= ord(symbol) <= 0x09CC and unicodedata.category(symbol) in ("Mc", "Mn")):
            problems.append("not a Bengali dependent vowel sign")
    elif cls == "hasant":
        if symbol != HASANT:
            problems.append("not BENGALI SIGN VIRAMA")
    elif cls == "sign":
        if not (len(symbol) == 1 and _is_bengali(symbol)
                and unicodedata.category(symbol) in ("Mn", "Mc", "Lo")
                and symbol in "ঁংঃঽৎ"):
            problems.append("not a Bengali sign (ঁ ং ঃ ঽ ৎ)")
    elif cls == "digit":
        if not (len(symbol) == 1 and _is_bengali(symbol) and unicodedata.category(symbol) == "Nd"):
            problems.append("not a Bengali digit")
    elif cls == "punctuation":
        if not (len(symbol) == 1 and symbol in PUNCTUATION_ALLOWED and unicodedata.category(symbol).startswith("P")):
            problems.append("punctuation outside the allowed set")
    elif cls == "joiner":
        if symbol not in (ZWNJ, ZWJ):
            problems.append("not ZWJ/ZWNJ")
    else:
        problems.append(f"unknown class {cls}")
    return problems


def _symbol_entry(symbol: str, cls: str, placed: bool, sources: list[str], kala_form: str | None = None) -> dict:
    entry = {"symbol": symbol, "code_points": _cp(symbol), "class": cls, "placed": placed,
             "names": [unicodedata.name(c, "?") for c in symbol], "sources": sources}
    if kala_form is not None and kala_form != symbol:
        entry["kala_form"] = _cp(kala_form)
        entry["note"] = "Kala stores the precomposed character; NFC decomposes it (composition exclusion)"
    return entry


def _load_alphabets() -> dict[str, dict]:
    return {path: json.loads(kala_path(path).read_text(encoding="utf-8")) for path in ALPHABET_SOURCES}


def build_inventory() -> tuple[dict, dict]:
    """Return (inventory, validation report)."""
    alphabets = _load_alphabets()
    order: list[tuple[str, str]] = []  # (NFC symbol, class) in first-seen order
    sources: dict[str, list[str]] = {}
    kala_forms: dict[str, str] = {}
    rejected = []
    for path, alphabet in alphabets.items():
        for section, cls in SECTION_CLASS.items():
            values = alphabet.get(section, [])
            for raw in [values] if isinstance(values, str) else values:
                raw = raw.strip()
                if raw in NORMALIZED_AWAY:
                    rejected.append({"kala": _cp(raw), "file": path, "section": section, "reason": NORMALIZED_AWAY[raw]})
                    continue
                symbol = unicodedata.normalize("NFC", raw)
                problems = validate_symbol(symbol, cls)
                if problems:
                    rejected.append({"kala": _cp(raw), "file": path, "section": section, "reason": "; ".join(problems)})
                    continue
                if symbol not in sources:
                    order.append((symbol, cls))
                    sources[symbol] = []
                    kala_forms[symbol] = raw
                sources[symbol].append(f"{path}#{section}")
    missing_default = [s for s in D1_DEFAULT_REQUIRED if s not in sources]
    symbols = [_symbol_entry(s, cls, True, sources[s], kala_forms[s]) for s, cls in order]
    symbols += [_symbol_entry(s, cls, False, ["typing grammar (not in Kala's alphabet)"]) for s, cls in TRACKED]
    canonical = json.dumps([[e["symbol"], e["class"], e["placed"]] for e in symbols], ensure_ascii=False)
    inventory = {
        "version": INVENTORY_VERSION,
        "decision": "D1 default: Kala alphabet + ং ঃ ঁ ৎ । + Bangla digits, validated (owner decision pending)",
        "unit_rules": [
            "A unit is one NFC code point, except ড় ঢ় য় (base + U+09BC), which are single units.",
            "Space (U+0020) is an explicit unit that no layout places (thumb key, D2 default).",
            "Placed symbols must each be reachable by exactly one key action on a Bangla-DH layout.",
            "Tracked units are counted but not placed until D1 is decided.",
            "Any other character is out of inventory: it is not a unit and breaks bigrams.",
        ],
        "kala_sources": {path: sha256_file(kala_path(path)) for path in ALPHABET_SOURCES},
        "unicode_version": unicodedata.unidata_version,
        "symbols": symbols,
        "counts": dict(Counter(e["class"] for e in symbols if e["placed"])) | {
            "placed": sum(e["placed"] for e in symbols), "tracked": sum(not e["placed"] for e in symbols)},
        "symbol_list_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
    differences = _alphabet_differences(alphabets)
    report = {"rejected_kala_entries": rejected, "d1_default_missing": missing_default,
              "alphabet_copy_differences": differences, "conjuncts": validate_conjuncts()}
    return inventory, report


def _alphabet_differences(alphabets: dict[str, dict]) -> dict:
    (a_path, a), (b_path, b) = alphabets.items()
    out = {}
    for section in sorted(set(a) | set(b)):
        if section == "conjuncts":
            continue
        va, vb = a.get(section), b.get(section)
        if va == vb:
            continue
        sa = set(va) if isinstance(va, list) else set(va or {})
        sb = set(vb) if isinstance(vb, list) else set(vb or {})
        out[section] = {f"only_in_{a_path}": [_cp(x) for x in sorted(sa - sb)],
                        f"only_in_{b_path}": [_cp(x) for x in sorted(sb - sa)]}
    return out


def classify_cluster(text: str) -> str:
    """'cluster' for consonant (+ hasant + consonant)+, else a reason."""
    nfc = unicodedata.normalize("NFC", text)
    foreign = [c for c in nfc if not _is_bengali(c) and c not in (ZWJ, ZWNJ)]
    if foreign:
        return "non-Bengali code point " + " ".join(_cp("".join(foreign)))
    units = segment_consonants(nfc)
    if units is None:
        return "not consonant (+ hasant + consonant)+"
    return "cluster" if len(units) >= 2 else "single consonant"


def segment_consonants(text: str) -> list[str] | None:
    """Split C্C্C... into consonant units, or None if it is not that shape."""
    units, i, expect_consonant = [], 0, True
    while i < len(text):
        if expect_consonant:
            unit = text[i:i + 2] if i + 1 < len(text) and text[i + 1] == NUKTA else text[i]
            if not is_consonant_unit(unit):
                return None
            units.append(unit)
            i += len(unit)
        else:
            if text[i] != HASANT:
                return None
            i += 1
        expect_consonant = not expect_consonant
    return units if expect_consonant is False else None


def validate_conjuncts() -> dict:
    alphabet = json.loads(kala_path("data/bn/Alphabet.json").read_text(encoding="utf-8"))
    conjunct_map = json.loads(kala_path("kala/layout/bn/conjuncts.json").read_text(encoding="utf-8"))
    lists = {"data/bn/Alphabet.json#conjuncts": alphabet.get("conjuncts", []),
             "kala/layout/bn/conjuncts.json (keys)": list(conjunct_map)}
    out = {}
    for name, entries in lists.items():
        verdicts = Counter()
        problems = []
        seen = Counter(unicodedata.normalize("NFC", e) for e in entries)
        for entry in entries:
            verdict = classify_cluster(entry)
            verdicts["cluster" if verdict == "cluster" else "problem"] += 1
            if verdict != "cluster":
                problems.append({"entry": entry, "code_points": _cp(entry), "problem": verdict})
        out[name] = {"entries": len(entries), "valid_clusters": verdicts["cluster"],
                     "duplicates_after_nfc": sorted(k for k, n in seen.items() if n > 1),
                     "problems": problems}
    remaps = {k: v for k, v in conjunct_map.items() if k != v}
    out["kala/layout/bn/conjuncts.json (non-identity mappings)"] = [
        {"from": k, "to": v, "from_code_points": _cp(k), "to_code_points": _cp(v)} for k, v in remaps.items()]
    return out


def load_inventory(path: Path = INVENTORY_FILE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
