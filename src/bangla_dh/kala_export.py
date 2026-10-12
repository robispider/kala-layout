"""Kala keyboards: the mixed-corpus A and D layouts as Kala layout files
(owner request, 11 October 2026).

``kala-export`` writes ``results/kala-keyboards/``:

* ``kala-goti.json`` (style A, "Kala Goti") and ``kala-jhor.json`` (style D,
  "Kala Jhor"): Kala *fixed* layouts, imported in Kala with *Import Kala
  layout* (``kala/Layouts/NativeLayoutReader.cs``). Each file carries an
  ``about`` block for Kala's layout page: how to type, how the layout was
  found, its scores and the leaderboard of every fixed layout tested;
* ``verification.json``: the checks below;
* ``README.md`` and ``run-manifest.json``.

How the styles run on Kala's fixed-layout engine
(``kala/Keyboard/FixedLayoutManager.cs``): every key types its label (a vowel
key types its sign; ড় ঢ় য় are typed precomposed, as in Kala's UniJoy). The
engine keeps what it typed since its last reset (space, punctuation, digit,
the অ key, Backspace, caret or window change) and replaces the longest
``combinations.sequences`` key that ends it.

* A: ``্`` + sign → independent vowel, the ten sequences of Kala's UniJoy.
* D: no sequences. The file holds the key map; the context vowel rule
  (RESEARCH_SPEC section 7.1) is described in ``about.style.typingRule`` for
  Kala to implement in code for D-style keyboards. Until it does, D's vowel
  keys type the sign only.

Both files use only pass-through rules (no suppression rules), so Kala types
what the research typing machine (``bangla.styles``) types.

Checks: the files pass a port of Kala's import validation; every label sits
on its key; for A a port of the engine (``KalaFixedEngine``) types, from a
fresh word, the research encoder's keystrokes of the most frequent word types
of the three held-out texts and must give each word exactly, and random key
sequences must give the research decoder's text.
"""
from __future__ import annotations

import datetime as _dt
import itertools
import json
import math
import platform
import random
import re
import unicodedata
from pathlib import Path

from . import __version__
from .bangla.grammar import Escape, nfc
from .bangla.inventory import HASANT
from .bangla.styles import INHERENT, Style
from .corpus.frequency import read_token_table
from .crosscheck import RESULTS as CROSSCHECK, unit_record
from .mix import HELDOUT, RESULTS as MIX, SEARCH as MIX_SEARCH, mixed_best_layout
from .paths import PROJECT_ROOT, RESULTS_ROOT, hash_outputs, kala_path, relative_to_project, write_json, write_text
from .reference import sha256_file
from .scoring.layouts import VK_TO_KEY
from .search.problem import PROBLEM_FILE, load_problem, parse_slot

RESULTS = RESULTS_ROOT / "kala-keyboards"
PHASE4 = RESULTS_ROOT / "phase4"  # not imported from phase4, which needs OR-Tools
RELEASE_DATE = "2026-10-11"
LAYOUT_VERSION = "1.0"
ABOUT_SCHEMA = "kala-layout-about-v1"
ALPHABET = "kala/layout/bn/Alphabet.json"  # the character classes Kala gives fixed layouts
STYLES = ("A", "D")
KEYBOARDS = {
    "A": {"file": "kala-goti.json", "id": "kala-goti", "name": "Kala Goti", "name_bn": "Kala গতি",
          "meaning": "Goti (গতি): speed", "style_name": "UniJoy-style vowels",
          "style_name_bn": "ইউনিজয়-ধাঁচের স্বরবর্ণ"},
    "D": {"file": "kala-jhor.json", "id": "kala-jhor", "name": "Kala Jhor", "name_bn": "Kala ঝড়",
          "meaning": "Jhor (ঝড়): storm", "style_name": "context vowels",
          "style_name_bn": "প্রসঙ্গ-নির্ভর স্বরবর্ণ"},
}
CORPUS_LABELS = {
    "bnwiki": ("Bangla Wikipedia articles", "বাংলা উইকিপিডিয়ার নিবন্ধ"),
    "newspaper": ("Prothom Alo newspaper articles (many sections)", "প্রথম আলো সংবাদপত্রের লেখা (নানা বিভাগ)"),
    "bard-novel": ("BARD news articles that share no sentence with the newspaper set (never used in the search)",
                   "BARD সংবাদ-নিবন্ধ, সংবাদপত্রের সংগ্রহের সঙ্গে কোনো বাক্য মেলে না (অনুসন্ধানে কখনো ব্যবহৃত হয়নি)"),
}
HELDOUT_KEYS = {"bnwiki/heldout": "wikipedia", "newspaper/heldout": "newspaper", "bard-novel/heldout": "unseenNews"}
TRAIN = ("bnwiki/train", "newspaper/train")

KEY_TO_VK = {key: vk for vk, key in VK_TO_KEY.items()}
LAYER_NAMES = {"base": "normal", "shift": "shift"}
# ড় ঢ় য়: NFC keeps them as letter + nukta; Kala's keys type the single code point.
PRECOMPOSED = {unicodedata.normalize("NFD", chr(c)): chr(c) for c in (0x09DC, 0x09DD, 0x09DF)}
# Keys outside the research model keep their US symbol, so every key types something.
US_SYMBOLS = {
    "base": {"`": "`", "-": "-", "=": "=", "[": "[", "]": "]", "\\": "\\", ";": ";", "'": "'", ",": ",", ".": ".",
             "/": "/"},
    "shift": {"`": "~", "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*", "9": "(",
              "0": ")", "-": "_", "=": "+", "[": "{", "]": "}", "\\": "|", ";": ":", "'": '"', ",": "<", ".": ">",
              "/": "?"},
}
PASS_THROUGH = ("vowel", "digit", "punctuation", "other")
# NativeLayoutReader: fields and limits of a Kala layout file (this export adds "about").
KALA_FIELDS = {"$schema", "type", "version", "language", "name", "layers", "combinations", "rules", "options",
               "developer", "comment", "about"}
KALA_FIXED_LAYERS = {"normal", "shift", "rightalt", "leftctrl"}
KALA_MAX_FILE_BYTES = 1024 * 1024


def kala_text(symbol: str) -> str:
    return PRECOMPOSED.get(symbol, symbol)


def bn_digits(text: str) -> str:
    return text.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def bn_group(n: int) -> str:
    """Bangla digits with Indian grouping: 557890 → ৫,৫৭,৮৯০."""
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join(re.findall(r"\d{1,2}", head[::-1]))[::-1]
        s = f"{head},{tail}"
    return bn_digits(s)


def bn_crore(n: float) -> str:
    return bn_digits(f"{n / 1e7:.1f}") + " কোটি"


# --- layout -------------------------------------------------------------------

def research_layout(style: str, problem: dict) -> dict[str, tuple[str, str]]:
    """Every label of the style → (key, layer): the mixed search's best layout plus the fixed keys."""
    layout = mixed_best_layout(style)
    layout.update({label: parse_slot(slot) for label, slot in problem["fixed"].items()})
    layout.update({label: parse_slot(slot) for label, slot in problem["fixed_outside_inventory"].items()})
    return layout


def kala_layers(layout: dict[str, tuple[str, str]]) -> dict[str, dict[str, str]]:
    keys = {layer: dict(symbols) for layer, symbols in US_SYMBOLS.items()}
    for label, (key, layer) in layout.items():
        if label in US_SYMBOLS[layer].values() and keys[layer].get(key) != label:
            raise ValueError(f"fixed key {label!r} is not at its US position")
        keys[layer][key] = kala_text(label)
    layers = {}
    for layer, mapping in keys.items():
        vk = {32: " "} | {KEY_TO_VK[key]: text for key, text in mapping.items()}
        layers[LAYER_NAMES[layer]] = {str(k): vk[k] for k in sorted(vk)}
    return layers


def sequences(style: Style) -> dict[str, str]:
    """A: ্ + sign → independent vowel (as Kala's UniJoy). D: none; Kala applies its rule in code."""
    return {HASANT + sign: vowel for sign, vowel in style.vowel_of.items()} if style.name == "A" else {}


def typing_rule(style: Style) -> dict:
    """The vowel rule of the style, for Kala's engine (RESEARCH_SPEC section 7.1)."""
    if style.name == "A":
        return {"id": "hasant-sign", "vowelKeys": "sign",
                "independentVowel": "hasant then the sign (combinations.sequences)"}
    return {"id": "context-vowel", "vowelKeys": "sign",
            "afterConsonant": "sign",
            "elsewhere": "independent vowel (word start, after a vowel, a sign, hasant, ং ঃ ঁ ৎ, punctuation)",
            "consonants": "ক–হ and ড় ঢ় য়",
            "repeatAfterConsonant": "presses of the same vowel key pair from the end: a single press is the sign, "
                                    "a pair the independent vowel (2 = ই, 3 = ি ই, 4 = ই ই, 5 = ি ই ই)",
            "repeatElsewhere": "each press adds one more independent vowel",
            "examples": ["ব ি ি = বই", "ত ি ন ি ি ি = তিনিই", "ি = ই at word start", "া ি = আই"]}


def keyboard_file(style: Style, layout: dict[str, tuple[str, str]], about: dict) -> dict:
    info = KEYBOARDS[style.name]
    comment = (f"{info['name']} ({info['name_bn']}): Bangla-DH Pure style {style.name}, {info['style_name']}. "
               f"Arranged by computer search for the least finger effort on Wikipedia and newspaper text "
               f"(Colemak Mod-DH effort model). Research: colemak-bangla in the Kala repository.")
    data = {"type": "fixed", "version": LAYOUT_VERSION, "language": "bn", "name": info["name"],
            "developer": "Kala — Bangla-DH Pure research", "comment": comment,
            "layers": kala_layers(layout)}
    if sequences(style):
        data["combinations"] = {"sequences": sequences(style)}
    data["rules"] = [{"pattern": t, "action": "pass_through"} for t in PASS_THROUGH]
    data["about"] = about
    return data


# --- Kala's engine and import checks, ported for verification ------------------

class KalaFixedEngine:
    """Port of ``FixedLayoutManager.TranslateKey`` (kala/Keyboard/FixedLayoutManager.cs)."""

    def __init__(self, layout: dict, alphabet: dict):
        layers = layout["layers"]
        self.normal = {int(k): v for k, v in layers.get("normal", {}).items()}
        self.shift = {int(k): v for k, v in layers.get("shift", {}).items()}
        seq = layout.get("combinations", {}).get("sequences", {})
        # Kala scans the sequences longest first (a stable sort) for the first key ending the buffer; a match
        # must end with the character just typed, so the scan is split by last character, order kept.
        self.sequences: dict[str, list[tuple[str, str]]] = {}
        for key, value in sorted(seq.items(), key=lambda kv: -len(kv[0])):
            self.sequences.setdefault(key[-1], []).append((key, value))
        self.rules = layout.get("rules", [])
        self.classes = [("consonant", set(alphabet["consonants"])), ("vowel", set(alphabet["vowels"])),
                        ("matra", set(alphabet["matras"])), ("halant", {alphabet.get("halant", HASANT)}),
                        ("digit", set(alphabet["digits"])), ("punctuation", set(alphabet["punctuation"])),
                        ("other", set(alphabet["other"]))]
        self.buffer = ""

    def reset(self) -> None:
        self.buffer = ""

    def kind(self, text: str) -> str:
        for name, members in self.classes:
            if text in members:
                return name
        return "none"

    def translate(self, vk: int, shift: bool = False) -> tuple[str, int] | None:
        """(output, backspaces), or None for an unmapped key (passed to the system)."""
        if vk in (32, 13):
            self.reset()
            return (" " if vk == 32 else "\n"), 0
        text = self.shift.get(vk) if shift and vk in self.shift else self.normal.get(vk)
        if not text:
            return None
        if any(r["action"] == "pass_through" and r["pattern"] == self.kind(text) for r in self.rules):
            self.reset()
            return text, 0
        potential = self.buffer + text
        for rule in self.rules:
            if rule["action"] != "suppress_input":
                continue
            parts = rule["pattern"].split("+")
            if len(potential) >= len(parts) and all(
                    self.kind(c) == p for c, p in zip(potential[-len(parts):], parts)):
                return "", 0
        self.buffer += text
        for key, value in self.sequences.get(text[-1], ()):
            if self.buffer.endswith(key):
                self.buffer = value
                return value, len(key) - 1
        return text, 0


def type_word(engine: KalaFixedEngine, presses) -> str:
    """Screen text of ``presses`` typed from a fresh word; Kala refuses deletions beyond the word."""
    engine.reset()
    screen = ""
    for vk, shift in presses:
        result = engine.translate(vk, shift)
        if result is None:
            raise ValueError(f"key {vk} is not mapped")
        out, backspaces = result
        if backspaces > len(screen):
            raise ValueError("a sequence deletes beyond the word being typed")
        screen = screen[:len(screen) - backspaces] + out
    return screen


def kala_import_problems(raw: bytes) -> list[str]:
    """The checks of ``NativeLayoutReader.Read`` for a fixed layout; empty when Kala accepts the file."""
    problems = []
    if not raw or len(raw) > KALA_MAX_FILE_BYTES:
        return ["file is empty or larger than 1 MiB"]

    def pairs(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            problems.append("duplicate field")
        return dict(items)

    root = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs)

    def tree(value, depth: int) -> None:
        if depth > 16:
            problems.append("nesting deeper than 16")
        if isinstance(value, dict):
            for v in value.values():
                tree(v, depth + 1)
        elif isinstance(value, list):
            if len(value) > 4096:
                problems.append("array longer than 4096")
            for v in value:
                tree(v, depth + 1)
        elif isinstance(value, str):
            text(value, 4096, metadata=True)
        elif value is None:
            problems.append("null value")

    def text(value, limit: int, metadata: bool = False) -> None:
        if not isinstance(value, str) or len(value.encode("utf-16-le")) // 2 > limit:
            problems.append(f"text missing or longer than {limit}: {str(value)[:40]!r}")
            return
        if any(unicodedata.category(c) == "Cc" and not (metadata and c in "\r\n\t") for c in value):
            problems.append(f"control character in {value[:40]!r}")

    def keymap(value, virtual: bool) -> None:
        if not isinstance(value, dict) or len(value) > (256 if virtual else 4096):
            problems.append("map invalid or too large")
            return
        for k, v in value.items():
            text(k, 64)
            text(v, 64)
            if not k or virtual and not (k.isdigit() and 1 <= int(k) <= 255 and str(int(k)) == k):
                problems.append(f"invalid key {k!r}")

    tree(root, 1)
    if set(root) - KALA_FIELDS:
        problems.append(f"unsupported fields {sorted(set(root) - KALA_FIELDS)}")
    if (root.get("type"), root.get("version"), root.get("language")) != ("fixed", "1.0", "bn"):
        problems.append("not a Bangla fixed layout version 1.0")
    if not str(root.get("name", "")).strip() or len(root.get("name", "")) > 1024:
        problems.append("name missing or too long")
    layers = root.get("layers", {})
    if not isinstance(layers, dict) or set(layers) - KALA_FIXED_LAYERS:
        problems.append("unsupported layer")
    for layer in layers.values():
        keymap(layer, virtual=True)
    normal = layers.get("normal", {})
    if not any(normal.values()) or normal.get("32") != " ":
        problems.append("normal layer empty or Space not a space")
    for name, value in root.get("combinations", {}).items():
        if name not in ("single", "sequences"):
            problems.append("unsupported combinations")
        keymap(value, virtual=False)
    rules = root.get("rules", [])
    if not isinstance(rules, list) or len(rules) > 128:
        problems.append("invalid rules")
    for rule in rules:
        if set(rule) - {"pattern", "action", "lexicon", "map"} or rule.get("action") not in (
                "pass_through", "suppress_input") or len(rule.get("pattern", "")) > 128:
            problems.append(f"invalid rule {rule}")
    if not isinstance(root.get("about", {}), dict):
        problems.append("about is not an object")
    for field, limit in (("developer", 1024), ("comment", 4096)):
        if field in root:
            text(root[field], limit, metadata=True)
    return problems


# --- the about block -----------------------------------------------------------

def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _r(x: float, digits: int = 4) -> float:
    return round(float(x), digits)


def sources() -> dict[str, Path]:
    return {"mix": MIX / "mix-search.json", "search_A": MIX_SEARCH / "A.json", "search_D": MIX_SEARCH / "D.json",
            "crosscheck": CROSSCHECK / "crosscheck.json", "phase4": PHASE4 / "phase4.json", "problem": PROBLEM_FILE}


def leaderboard(mix: dict, crosscheck: dict) -> list[dict]:
    """Held-out J1 of the two Kala keyboards and every fixed baseline (each at its best fingering grid)."""
    rows = []
    for style in STYLES:
        scores = mix["styles"][style]["mixed"]["scores"]
        info = KEYBOARDS[style]
        rows.append({"name": info["name"], "nameBn": info["name_bn"], "kind": "kala",
                     "developer": "Kala — Bangla-DH Pure research",
                     "fingering": "model-optimal (Colemak Mod-DH)",
                     "j1": {HELDOUT_KEYS[c]: _r(scores[c]["J1"]) for c in HELDOUT}})
    for name, baseline in crosscheck["baselines"].items():
        entry = baseline["entry"]
        if entry["kind"] == "kala":
            developer = "Kala's built-in UniJoy (Kala's Bijoy file has the same keys)"
        else:
            match = re.search(r"developer (.+?); options", entry.get("provenance", ""))
            developer = match.group(1) if match else ""
        rows.append({"name": name, "nameBn": name, "kind": "market", "developer": developer,
                     "fingering": "best of model-optimal and traditional fingering",
                     "j1": {HELDOUT_KEYS[c]: _r(min(g["J1"] for g in baseline["scores"][c].values()))
                            for c in HELDOUT}})
    for row in rows:
        row["average"] = _r(sum(row["j1"].values()) / len(row["j1"]))
    rows.sort(key=lambda row: row["average"])
    unijoy = next(row["average"] for row in rows if row["name"] == "UniJoy")
    best = rows[0]["average"]
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
        row["score"] = round(100 * best / row["average"], 1)
        row["effortIndex"] = round(100 * row["average"] / unijoy, 1)
        row["lessEffortThanUniJoyPercent"] = round(100 * (1 - row["average"] / unijoy), 1)
    return [{k: row[k] for k in ("rank", "name", "nameBn", "kind", "developer", "score", "average", "effortIndex",
                                 "lessEffortThanUniJoyPercent", "j1", "fingering")} for row in rows]


def key_names(style: Style, layout: dict, labels) -> str:
    out = []
    for label in labels:
        key, layer = layout[label]
        out.append(("Shift+" if layer == "shift" else "") + key)
    return " ".join(out)


def examples(style: Style, layout: dict) -> list[dict]:
    words = ["আমি", "কী", "বই", "এবং", "তিনিই", "আকাশ"]
    rows = []
    for word in words:
        steps = style.encode(word)
        if any(isinstance(s, Escape) for s in steps):
            continue
        rows.append({"text": word, "keys": key_names(style, layout, steps),
                     "presses": " ".join(kala_text(s) for s in steps)})
    return rows


def how_to_type(style: Style, layout: dict) -> dict:
    hasant = key_names(style, layout, [HASANT])
    inherent = key_names(style, layout, [INHERENT])
    if style.name == "A":
        en = ["Every vowel sign (kar) has its own key: ক + ি = কি.",
              f"A full vowel is hasant ({hasant}) and then its sign: ্ + ি = ই, ্ + া = আ (as in UniJoy).",
              f"অ is {inherent}.",
              "Hasant also joins consonants: ক + ্ + ষ = ক্ষ."]
        bn = ["প্রতিটি কার-চিহ্নের নিজস্ব কী আছে: ক + ি = কি।",
              f"পূর্ণ স্বরবর্ণ: আগে হসন্ত ({hasant}), তারপর কার: ্ + ি = ই, ্ + া = আ (ইউনিজয়ের মতো)।",
              f"অ পাওয়া যায় {inherent} চাপলে।",
              "হসন্ত দিয়ে যুক্তবর্ণও হয়: ক + ্ + ষ = ক্ষ।"]
    else:
        en = ["One key per vowel; Kala picks its form from the letter before it.",
              "After a consonant it gives the sign (kar): ক + ি = কি.",
              "Anywhere else it gives the full vowel: at the start of a word ি = ই; after a vowel া + ি = আই.",
              "Press the same vowel key twice after a consonant for the full vowel: ব + ি + ি = বই.",
              "Three presses give sign + vowel: ত ি ন ি ি ি = তিনিই.",
              f"অ is {inherent}; hasant ({hasant}) joins consonants: ক + ্ + ষ = ক্ষ."]
        bn = ["প্রতিটি স্বরের একটি কী; আগের বর্ণ দেখে Kala ঠিক রূপটি বেছে নেয়।",
              "ব্যঞ্জনবর্ণের পরে কার হয়: ক + ি = কি।",
              "অন্য সব জায়গায় পূর্ণ স্বরবর্ণ হয়: শব্দের শুরুতে ি = ই; স্বরের পরে া + ি = আই।",
              "ব্যঞ্জনবর্ণের পরে একই স্বর-কী দুবার চাপলে পূর্ণ স্বরবর্ণ: ব + ি + ি = বই।",
              "তিনবার চাপলে কার + স্বরবর্ণ: ত ি ন ি ি ি = তিনিই।",
              f"অ পাওয়া যায় {inherent} চাপলে; হসন্ত ({hasant}) দিয়ে যুক্তবর্ণ: ক + ্ + ষ = ক্ষ।"]
    return {"en": en, "bn": bn, "examples": examples(style, layout)}


def limits(style: str) -> dict:
    en = ["Scores come from the Colemak Mod-DH effort model on real text, not from timed typing; typing tests "
          "with people are the next research step.",
          "The layout is the best found by the search (many independent runs reach it); it is not proven optimal.",
          "Two layers only (normal and Shift): ZWNJ, ZWJ, ঽ, ॥, — and ৳ have no key yet (a third layer is planned)."]
    bn = ["স্কোরগুলো আসল লেখার ওপর Colemak Mod-DH আঙুল-পরিশ্রম মডেলের হিসাব, ঘড়ি ধরে টাইপের মাপ নয়; "
          "মানুষকে দিয়ে টাইপিং পরীক্ষা গবেষণার পরের ধাপ।",
          "এটি অনুসন্ধানে পাওয়া সেরা বিন্যাস (বহু স্বাধীন অনুসন্ধান একই ফলে পৌঁছেছে); গাণিতিকভাবে সর্বোত্তম প্রমাণিত নয়।",
          "কেবল দুটি স্তর (সাধারণ ও Shift): ZWNJ, ZWJ, ঽ, ॥, — ও ৳-এর কী এখনো নেই (তৃতীয় স্তর পরিকল্পনায় আছে)।"]
    if style == "D":
        en.append("The vowel rule (sign after a consonant, full vowel elsewhere, double press) needs Kala's "
                  "D-style engine; this file describes it in about.style.typingRule. Until Kala implements it, the "
                  "vowel keys type the sign only.")
        bn.append("স্বরের নিয়ম (ব্যঞ্জনের পরে কার, অন্যত্র পূর্ণ স্বর, দুবার চাপা) Kala-র D-ধাঁচের ইঞ্জিনে চলবে; এই "
                  "ফাইলের about.style.typingRule-এ তা লেখা আছে। Kala তা চালু না করা পর্যন্ত স্বর-কী শুধু কার দেয়।")
    return {"en": en, "bn": bn}


def about_block(style: Style, layout: dict, data: dict, board: list[dict]) -> dict:
    name = style.name
    info = KEYBOARDS[name]
    mix, crosscheck, phase4, search = data["mix"], data["crosscheck"], data["phase4"], data[f"search_{name}"]
    corpora = crosscheck["corpora"]
    settings, stats = search["settings"], search["statistics"]
    slots = len(search["slots"])
    arrangements = math.factorial(slots)
    exponent = len(str(arrangements)) - 1
    mantissa = arrangements / 10 ** exponent
    moves = stats["runs"] * settings["sa_steps"]
    cpu_seconds = stats["seconds_total"] + sum(r["seconds"] for r in search["polish"] + search["confirmation"])

    def corpus_rows(names):
        rows = []
        for c in names:
            source = c.split("/")[0]
            rows.append({"name": c, "label": CORPUS_LABELS[source][0], "labelBn": CORPUS_LABELS[source][1],
                         "articles": corpora[c]["documents"], "words": corpora[c]["tokens"],
                         "typedCharacters": corpora[c]["N"]})
        return rows

    training, heldout = corpus_rows(TRAIN), corpus_rows(HELDOUT)
    train_docs, train_words = sum(r["articles"] for r in training), sum(r["words"] for r in training)
    test_docs, test_words = sum(r["articles"] for r in heldout), sum(r["words"] for r in heldout)
    scores = mix["styles"][name]["mixed"]["scores"]
    mine = next(row for row in board if row["name"] == info["name"])
    index, less = mine["effortIndex"], mine["lessEffortThanUniJoyPercent"]
    summary = phase4["summaries"][name]
    samples = phase4["sensitivity"]["samples"]["summary"][f"Bangla-DH {name}"]
    beats_all = min(v for k, v in samples.items() if k.startswith("R vs "))
    method_en = (
        f"Bangla-DH Pure applies the Colemak Mod-DH effort model (how far each key is, which finger presses it, "
        f"same-finger and awkward key pairs, and Shift) to Bangla. The computer arranged {slots} Bangla symbols on "
        f"{slots} key positions, a space of {mantissa:.2f} × 10^{exponent} possible layouts, with "
        f"{stats['runs']:,} independent searches of {settings['sa_steps']:,} moves each: more than "
        f"{moves / 1e6:,.0f} million candidate layouts scored. It learned from {train_docs:,} Wikipedia and "
        f"newspaper articles ({train_words / 1e6:.1f} million words) and was tested on {test_docs:,} articles it "
        f"had never seen ({test_words / 1e6:.1f} million words).")
    method_bn = (
        f"Bangla-DH Pure গবেষণায় Colemak Mod-DH-এর আঙুল-পরিশ্রম মডেল (কী কত দূরে, কোন আঙুলে চাপতে হয়, একই "
        f"আঙুলে পরপর বা অস্বস্তিকর কী-জোড়া, আর Shift) বাংলায় প্রয়োগ করা হয়েছে। {bn_digits(str(slots))}টি বাংলা "
        f"প্রতীককে {bn_digits(str(slots))}টি কী-অবস্থানে সাজানোর {bn_digits(f'{mantissa:.2f}')} × "
        f"১০^{bn_digits(str(exponent))}টি সম্ভাব্য বিন্যাসের মধ্যে কম্পিউটার {bn_group(stats['runs'])}টি স্বাধীন "
        f"অনুসন্ধান চালিয়েছে (প্রতিটিতে {bn_group(settings['sa_steps'])} ধাপ): {bn_crore(moves)}র বেশি বিন্যাস "
        f"যাচাই হয়েছে। {bn_group(train_docs)}টি উইকিপিডিয়া ও সংবাদপত্রের লেখা ({bn_crore(train_words)} শব্দ) "
        f"থেকে শিখে, আগে না-দেখা {bn_group(test_docs)}টি লেখায় ({bn_crore(test_words)} শব্দ) পরীক্ষা করা হয়েছে।")
    if name == "D":
        tagline = ("The lowest-effort Bangla layout the research found: one key per vowel, and Kala picks the "
                   "sign or the full vowel for you.",
                   "গবেষণায় পাওয়া সবচেয়ে কম পরিশ্রমের বাংলা বিন্যাস: প্রতিটি স্বরের একটি কী, কার না পূর্ণ "
                   "স্বরবর্ণ তা Kala নিজেই বেছে নেয়।")
    else:
        tagline = ("Familiar UniJoy-style vowel typing on keys arranged by computer search for far less finger work.",
                   "পরিচিত ইউনিজয়-ধাঁচের স্বরবর্ণ টাইপিং, আর কী-গুলো কম্পিউটার-অনুসন্ধানে সাজানো, আঙুলের পরিশ্রম "
                   "অনেক কম।")
    certified = (f"The Wikipedia-trained version of style {name} was certified within {summary['gap_percent']:.2f} % "
                 f"of the lowest J1 any layout of its scope can reach (Phase 4 lower bound "
                 f"{summary['LB_J']:.4f}); this layout, searched on Wikipedia + news, was not re-certified.")
    if name == "D":
        certified += " It has the same base layer as that certified layout."
    return {
        "schema": ABOUT_SCHEMA,
        "id": info["id"],
        "name": {"en": info["name"], "bn": info["name_bn"]},
        "meaning": info["meaning"],
        "tagline": {"en": tagline[0], "bn": tagline[1]},
        "family": "Bangla-DH Pure",
        "version": LAYOUT_VERSION,
        "released": RELEASE_DATE,
        "style": {"code": name, "name": {"en": info["style_name"], "bn": info["style_name_bn"]},
                  "description": style.description, "typingRule": typing_rule(style)},
        "howToType": how_to_type(style, layout),
        "research": {
            "summary": {"en": method_en, "bn": method_bn},
            "model": "Colemak Mod-DH effort model (key effort, same-finger and neighbour bigram penalties) with a "
                     "Shift cost, J1 (RESEARCH_SPEC section 6.6); model-optimal ANSI fingering; space on the thumb",
            "searchSpace": {"symbols": slots, "keyPositions": slots, "possibleLayouts": f"{mantissa:.2f}e{exponent}"},
            "search": {"method": "simulated annealing, steepest descent and iterated local search",
                       "independentRuns": stats["runs"], "movesPerRun": settings["sa_steps"],
                       "candidateLayoutsScored": moves,
                       "localSearchIterationsPerRun": settings["ils_iterations"],
                       "polishAndConfirmationRuns": len(search["polish"]) + len(search["confirmation"]),
                       "runsReachingThisLayout": stats["runs_reaching_best"],
                       "cpuHours": round(cpu_seconds / 3600, 1)},
            "training": training,
            "testing": heldout,
            "objectiveWeights": mix["weights"],
            "classification": "best found (RESEARCH_SPEC section 14)",
            "certification": certified,
            "sensitivity": f"Under 1,000 random settings of the model's parameters the Wikipedia-trained style "
                           f"{name} layout beat every market layout in {100 * beats_all:.0f} % of them.",
            "reports": ["colemak-bangla/results/mix-search/REPORT.md",
                        "colemak-bangla/results/phase3-crosscheck/REPORT.md",
                        "colemak-bangla/results/phase4/REPORT.md",
                        "colemak-bangla/results/kala-keyboards/README.md"],
        },
        "scores": {
            "metric": "J1: modelled finger effort per typed character (lower is better)",
            "rank": mine["rank"], "score": mine["score"], "average": mine["average"],
            "effortIndex": mine["effortIndex"], "lessEffortThanUniJoyPercent": mine["lessEffortThanUniJoyPercent"],
            "heldout": {HELDOUT_KEYS[c]: {"J1": _r(scores[c]["J1"]), "keyEffort": _r(scores[c]["E1"]),
                                          "keyPairPenalty": _r(scores[c]["E2"]), "shift": _r(scores[c]["M"]),
                                          "keystrokesPerCharacter": _r(crosscheck["keystroke_tables"][
                                              f"{name} {c}"]["keystrokes_per_non_space_unit"])}
                        for c in HELDOUT},
        },
        "scoreGuide": {
            "en": f"Effort (J1) is the modelled finger work per typed character, averaged over Wikipedia, "
                  f"newspaper and unseen news text; lower is better. Effort index: UniJoy = 100, so {info['name']}'s "
                  f"{index:.0f} means about {less:.0f} % less finger work for the same text. Score: 100 for the "
                  f"lowest-effort layout tested; a layout with score 80 needs 25 % more work than it. Market layouts "
                  f"are scored at their best fingering. These are model scores, not measured typing speed.",
            "bn": f"পরিশ্রম (J1) হলো প্রতিটি টাইপ করা বর্ণে মডেল-হিসাবে আঙুলের কাজ, উইকিপিডিয়া, সংবাদপত্র ও আগে "
                  f"না-দেখা সংবাদের লেখার গড়; যত কম তত ভালো। পরিশ্রম-সূচক: ইউনিজয় = ১০০, তাই {info['name_bn']}-এর "
                  f"{bn_digits(f'{index:.0f}')} মানে একই লেখায় প্রায় {bn_digits(f'{less:.0f}')} % কম আঙুলের কাজ। "
                  f"স্কোর: পরীক্ষিত সবচেয়ে কম পরিশ্রমের বিন্যাস ১০০; স্কোর ৮০ মানে তার চেয়ে ২৫ % বেশি কাজ। বাজারের "
                  f"বিন্যাসগুলো তাদের সবচেয়ে সুবিধাজনক আঙুল-বিন্যাসে মাপা হয়েছে। এগুলো মডেলের হিসাব, টাইপিং-গতির "
                  f"মাপ নয়।",
        },
        "leaderboard": {
            "metric": "average held-out J1 (Wikipedia, newspaper, unseen news); lower is better",
            "note": "Only fixed layouts are compared (phonetic layouts such as Avro Phonetic are not). Market "
                    "layouts are the fixed layouts installed in Kala when the research ran.",
            "entries": board,
        },
        "limits": limits(name),
    }


# --- verification ----------------------------------------------------------------

def presses_of(layout: dict) -> dict[str, tuple[int, bool]]:
    return {label: (KEY_TO_VK[key], layer == "shift") for label, (key, layer) in layout.items()}


def token_table(corpus: str) -> Path:
    path = Path(unit_record(corpus)["token_table"])
    return path if path.is_absolute() else PROJECT_ROOT / path


def check_words(style: Style, engine: KalaFixedEngine, keys: dict, corpus: str, top: int) -> dict:
    tested = typed = skipped = 0
    count_all = count_typed = count_skipped = 0
    failures = []
    for word, count in itertools.islice(read_token_table(token_table(corpus)), top):
        tested += 1
        count_all += count
        steps = style.encode(word)
        if any(isinstance(s, Escape) for s in steps):
            skipped += 1
            count_skipped += count
            continue
        try:
            screen = nfc(type_word(engine, [keys[s] for s in steps]))
        except ValueError as error:
            screen = f"error: {error}"
        if screen == word:
            typed += 1
            count_typed += count
        elif len(failures) < 20:
            failures.append({"word": word, "kala": screen, "presses": " ".join(steps)})
    failed = tested - typed - skipped
    return {"word_types": tested, "typed_exactly": typed, "failures": failed,
            "skipped_need_keys_outside_v1": skipped,
            "running_words_typed_exactly_share": count_typed / count_all,
            "running_words_skipped_share": count_skipped / count_all, "failure_examples": failures}


def fuzz(style: Style, engine: KalaFixedEngine, keys: dict, count: int, seed: int) -> dict:
    """Random key sequences: Kala's engine against the research decoder."""
    rng = random.Random(seed)
    pool = ["ক", "য়", "ষ", "র", "ত", HASANT, "ং", "ঁ", "ৎ", "।", ",", "১", INHERENT, "ি", "া", "ে", "ু", "ৌ"]
    agree = 0
    mismatches = []
    for _ in range(count):
        seq = [rng.choice(pool)]
        for _ in range(rng.randint(0, 15)):
            seq.append(seq[-1] if rng.random() < 0.6 else rng.choice(pool))
        expected = style.decode(seq)
        got = nfc(type_word(engine, [keys[s] for s in seq]))
        if got == expected:
            agree += 1
        elif len(mismatches) < 20:
            mismatches.append({"presses": " ".join(seq), "research": expected, "kala": got})
    return {"sequences": count, "seed": seed, "agree": agree, "mismatches": count - agree,
            "mismatch_examples": mismatches}


def key_map_problems(layout: dict, keyboard: dict) -> list[str]:
    """Every label of the style types itself on its research key."""
    layers = keyboard["layers"]
    return [f"{label} not on {key}/{layer}" for label, (key, layer) in layout.items()
            if layers[LAYER_NAMES[layer]].get(str(KEY_TO_VK[key])) != kala_text(label)]


def verify(style: Style, layout: dict, keyboard: dict, alphabet: dict, raw: bytes, top: int, fuzz_count: int) -> dict:
    """Import and key-map checks; for A also typing through the engine port (D's vowel rule lives in Kala)."""
    result = {"kala_import_problems": kala_import_problems(raw), "key_map_problems": key_map_problems(layout, keyboard),
              "file_bytes": len(raw), "sequences": len(keyboard.get("combinations", {}).get("sequences", {}))}
    ok = not result["kala_import_problems"] and not result["key_map_problems"]
    if style.name == "A":
        keys, engine = presses_of(layout), KalaFixedEngine(keyboard, alphabet)
        result["heldout_words"] = {c: check_words(style, engine, keys, c, top) for c in HELDOUT}
        result["random_key_sequences"] = fuzz(style, engine, keys, fuzz_count, seed=20261111)
        ok = (ok and all(w["failures"] == 0 for w in result["heldout_words"].values())
              and result["random_key_sequences"]["mismatches"] == 0)
    result["pass"] = ok
    return result


# --- report ------------------------------------------------------------------------

def _key_table(layout: dict, rows: list[list[str]]) -> list[str]:
    at = {slot: kala_text(label) for label, slot in layout.items()}
    lines = []
    for row in rows:
        lines += ["| | " + " | ".join(row) + " |", "| --- " * (len(row) + 1) + "|",
                  "| Shift | " + " | ".join(at.get((k, "shift"), "") for k in row) + " |",
                  "| base | " + " | ".join(at.get((k, "base"), "") for k in row) + " |", ""]
    return lines


def report(files: dict, layouts: dict, abouts: dict, checks: dict, board: list[dict]) -> str:
    rows = [list("QWERTYUIOP"), list("ASDFGHJKL"), list("ZXCVBNM")]
    a = abouts["D"]["research"]
    w = ["# Kala keyboards: Kala Goti (style A) and Kala Jhor (style D)", "",
         "The two layouts of the mixed-corpus search ([../mix-search/REPORT.md](../mix-search/REPORT.md)) as Kala "
         "layout files. Generated by `bangla-dh kala-export` (`src/bangla_dh/kala_export.py`) from the files "
         "listed in [run-manifest.json](run-manifest.json); checks in [verification.json](verification.json).", "",
         "| File | Name | Style |", "| --- | --- | --- |"]
    for style in STYLES:
        info = KEYBOARDS[style]
        w.append(f"| [{info['file']}]({info['file']}) | {info['name']} ({info['name_bn']}) | {style}, "
                 f"{info['style_name']} |")
    w += ["", "**Install:** in Kala open the layout page, choose *Import Kala layout* and pick the file. Each file is "
          "a Kala fixed layout; its `about` block holds the facts below for Kala's layout page.", "",
          "## How the layouts were found", "", abouts["D"]["research"]["summary"]["en"], "",
          f"Every layout is **best found** (RESEARCH_SPEC section 14). {abouts['D']['research']['certification']} "
          f"{abouts['A']['research']['certification']}", "",
          "## Leaderboard", "",
          "Held-out J1 (modelled finger effort per typed character, lower is better). Market layouts are scored at "
          "their best fingering grid. Score: 100 for the lowest average; effort index: UniJoy = 100.", "",
          "| Rank | Layout | Wikipedia | Newspaper | Unseen news | Average | Score | Effort index | Less effort than UniJoy |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in board:
        name = f"**{row['name']}**" if row["kind"] == "kala" else row["name"]
        j = row["j1"]
        w.append(f"| {row['rank']} | {name} | {j['wikipedia']:.4f} | {j['newspaper']:.4f} | {j['unseenNews']:.4f} | "
                 f"{row['average']:.4f} | {row['score']} | {row['effortIndex']} | {row['lessEffortThanUniJoyPercent']} % |")
    w += ["", "Texts: " + "; ".join(f"{r['name']}: {r['articles']:,} articles, {r['words']:,} words"
                                   for r in a["training"] + a["testing"]) + ". The search used the training splits "
          "(0.5 Wikipedia + 0.5 news); the scores above use only held-out text.", ""]
    for style in STYLES:
        info = KEYBOARDS[style]
        about = abouts[style]
        w += [f"## {info['name']} ({info['name_bn']}): style {style}, {info['style_name']}", ""]
        w += [f"* {line}" for line in about["howToType"]["en"]] + [""]
        w += ["| Text | Keys | Presses |", "| --- | --- | --- |"]
        w += [f"| {e['text']} | {e['keys']} | {e['presses']} |" for e in about["howToType"]["examples"]] + [""]
        w += _key_table(layouts[style], rows)
        w += ["Number row: Bangla digits ০–৯ (Shift: US symbols); other keys type their US symbol. Limits:", ""]
        w += [f"* {line}" for line in about["limits"]["en"]] + [""]
    a_check = checks["A"]
    w += ["## Verification", "",
          "Both files pass a port of Kala's import checks (`NativeLayoutReader`) and every label sits on its research "
          "key. Kala Jhor has no sequences: its vowel rule is described in `about.style.typingRule` for Kala to "
          "implement. For Kala Goti a port of Kala's fixed-layout engine (`FixedLayoutManager`) types, from a fresh "
          "word, the research encoder's keystrokes of the most frequent word types of each held-out text (words that "
          "need a key outside v1, such as ZWNJ, — or Latin letters, are skipped):", "",
          "| Text | Word types | Typed exactly | Failures | Skipped | Running words typed |",
          "| --- | --- | --- | --- | --- | --- |"]
    for corpus, r in a_check["heldout_words"].items():
        w.append(f"| {corpus} | {r['word_types']:,} | {r['typed_exactly']:,} | {r['failures']} | "
                 f"{r['skipped_need_keys_outside_v1']:,} | {100 * r['running_words_typed_exactly_share']:.2f} % |")
    f = a_check["random_key_sequences"]
    w += ["", f"{f['agree']:,} of {f['sequences']:,} random key sequences agree with the research decoder "
          f"(`bangla.styles`).", "",
          "Overall: " + ("PASS" if all(c["pass"] for c in checks.values()) else "FAIL") + ". The port is not "
          "Kala itself: import the files in Kala and type in Word, Notepad and a browser field before release.", ""]
    return "\n".join(w)


# --- driver --------------------------------------------------------------------------

def build(top: int = 200_000, fuzz_count: int = 20_000, write: bool = True) -> dict:
    problem = load_problem()
    data = {key: _load(path) for key, path in sources().items() if key != "problem"}
    alphabet = json.loads(kala_path(ALPHABET).read_text(encoding="utf-8"))
    board = leaderboard(data["mix"], data["crosscheck"])
    files, layouts, abouts, checks = {}, {}, {}, {}
    for name in STYLES:
        style = Style(name)
        layout = research_layout(name, problem)
        about = about_block(style, layout, data, board)
        keyboard = keyboard_file(style, layout, about)
        raw = (json.dumps(keyboard, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        layouts[name], abouts[name], files[name] = layout, about, (keyboard, raw)
        print(f"Checking {KEYBOARDS[name]['name']} ...", flush=True)
        checks[name] = verify(style, layout, keyboard, alphabet, raw, top, fuzz_count)
    if not write:
        return {"files": files, "checks": checks, "board": board}
    written = []
    for name in STYLES:
        target = RESULTS / KEYBOARDS[name]["file"]
        write_text(target, files[name][1].decode("utf-8"))
        written.append(target)
    written.append(write_json(RESULTS / "verification.json",
                              {"settings": {"top_word_types": top, "random_sequences": fuzz_count,
                                            "alphabet": ALPHABET},
                               "styles": checks, "pass": all(c["pass"] for c in checks.values())}))
    written.append(write_text(RESULTS / "README.md", report(files, layouts, abouts, checks, board)))
    inputs = {relative_to_project(p): sha256_file(p) for p in sources().values()}
    inputs[ALPHABET] = sha256_file(kala_path(ALPHABET))
    inputs.update({relative_to_project(token_table(c)): sha256_file(token_table(c)) for c in HELDOUT})
    manifest = {"command": f"bangla-dh kala-export --top {top} --fuzz {fuzz_count}", "version": __version__,
                "created": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
                "python": platform.python_version(), "parameters": {"release_date": RELEASE_DATE},
                "inputs": inputs, "outputs": hash_outputs(written)}
    written.append(write_json(RESULTS / "run-manifest.json", manifest))
    return {"paths": written, "pass": all(c["pass"] for c in checks.values())}


def run_export(top: int = 200_000, fuzz_count: int = 20_000) -> list[Path]:
    result = build(top=top, fuzz_count=fuzz_count)
    print("Checks:", "PASS" if result["pass"] else "FAIL")
    return result["paths"]
