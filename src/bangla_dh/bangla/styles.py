"""Vowel-entry styles A–D (Phase 3, task 2; RESEARCH_SPEC section 7.1).

v1 has 52 slots: 41 fixed-role symbols (35 consonants, ্, ং ঃ ঁ ৎ, ।) plus
one vowel set of 11 keys. A style says which vowel form sits on the keys and
how the other form is typed:

======  ========================  =========================================
Style   Vowel keys                The other form
======  ========================  =========================================
A       10 vowel signs + অ        independent vowel = ্ then the sign (UniJoy)
B       10 vowel signs + অ        independent vowel = the sign key twice
C       11 independent vowels     vowel sign = the vowel key twice
D       10 vowel signs + অ        context: after a consonant one tap gives the
                                  sign, anywhere else the independent vowel;
                                  the same key again right after it gave a
                                  sign turns that sign into the vowel (বই)
======  ========================  =========================================

Repeated presses in B and D (owner rule of 10 October 2026, timing-free):
consecutive presses of one vowel key form a *run* whenever its first press
gave a sign (always in B; after a consonant in D). The run is split into
pairs, with one single press at the start when its length is odd: a single
is the sign, a pair the independent vowel, so 2 presses give ই, 3 give ি ই
(তিনিই), 4 give ই ই and 5 give ি ই ই. The next different key, an escape or
a space ends the run; no timer is involved. The decoder rewrites the run's
output on every press, so its screen always equals the buffered result.
In D a run that starts anywhere else (one tap gives the independent vowel)
does not pair: every press gives one more independent vowel (ইই).

A keystroke is identified by its **label**: the symbol the key carries in
the problem file (a vowel key of A, B and D is labelled by its sign, a vowel
key of C by its independent vowel, অ by itself). Labels do not depend on the
layout, so a style turns a text into the same label stream for every layout,
and per-style label frequencies feed the search directly.

Every style is a small typing machine (``Style.press``): the decoder only
sees labels, never the intended text. The encoder tries, for each unit, the
label sequences that could type it (fewest keystrokes first), simulates them
and keeps the first one whose output is exactly the text so far. A unit no
sequence can type is an ``Escape``: typed outside the model, it breaks
bigrams. That covers the units v1 puts on no key (ZWNJ, ZWJ, ঽ ॥ —, the third
layer), characters outside the inventory, invalid text (hasant directly
followed by a vowel sign) and the rare *collisions* of a repeat rule (C
cannot type the same independent vowel twice, আআ; B and D cannot type an
independent vowel followed by its own sign, ইি, which is not valid text).

``round_trip`` checks RESEARCH_SPEC 4.1 for a style: the label stream is
decoded from scratch and must equal the NFC text.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from .grammar import Escape, nfc, segment
from .inventory import HASANT, load_inventory

STYLES = ("A", "B", "C", "D")
STYLE_NAMES = {"A": "UniJoy-style (independent vowel = ্ + sign)",
               "B": "sign key, double tap (independent vowel = sign twice; a run of presses pairs from the end, "
                    "3 = sign + independent)",
               "C": "vowel key, double tap (vowel sign = vowel twice)",
               "D": "context (sign after a consonant, else independent; same key again = independent; a run after "
                    "a consonant pairs from the end, 3 = sign + independent)"}
INHERENT = "অ"  # the independent vowel without a sign
# Placed units v1 puts on no key: the third (conjunct/rare) layer, and the joiners (no key, D1).
THIRD_LAYER = ("ঽ", "॥", "—")
NO_KEY = ("‌", "‍")
# Fixed v1 keys (RESEARCH_SPEC section 4): digits on the number row, ASCII
# punctuation at its US position. '.' is fixed too but is outside the
# symbol inventory, so it is not a typing unit.
FIXED_PUNCTUATION = {",": (",", "base"), ";": (";", "base"), ":": (";", "shift"), "'": ("'", "base"),
                     '"': ("'", "shift"), "(": ("9", "shift"), ")": ("0", "shift"), "-": ("-", "base"),
                     "!": ("1", "shift"), "?": ("/", "shift")}
FIXED_OUTSIDE_INVENTORY = {".": (".", "base")}


@dataclass(frozen=True)
class Alphabet:
    """The unit classes the styles need, from the frozen inventory."""
    consonants: frozenset[str]
    vowels: tuple[str, ...]            # independent vowels, অ first
    signs: tuple[str, ...]             # vowel signs, in the order of ``vowels[1:]``
    others: tuple[str, ...]            # ্ ং ঃ ঁ ৎ ।: one key each in every style
    digits: tuple[str, ...]

    @classmethod
    def from_inventory(cls, inventory: dict | None = None) -> "Alphabet":
        inventory = inventory or load_inventory()
        by_class: dict[str, list[str]] = {}
        for entry in inventory["symbols"]:
            by_class.setdefault(entry["class"], []).append(entry["symbol"])
        signs = tuple(by_class["vowel_sign"])
        vowels = [INHERENT] + [_vowel_of_sign(s) for s in signs]
        if sorted(vowels) != sorted(by_class["vowel"]):
            raise ValueError("inventory vowels do not pair with its vowel signs")
        others = (HASANT,) + tuple(s for s in by_class["sign"] if s not in THIRD_LAYER) + ("।",)
        return cls(frozenset(by_class["consonant"]), tuple(vowels), signs, others, tuple(by_class["digit"]))

    @property
    def sign_of(self) -> dict[str, str]:
        return dict(zip(self.vowels[1:], self.signs))

    @property
    def vowel_of(self) -> dict[str, str]:
        return dict(zip(self.signs, self.vowels[1:]))


def _vowel_of_sign(sign: str) -> str:
    """আ for া etc., from the Unicode names (BENGALI VOWEL SIGN AA → BENGALI LETTER AA)."""
    return unicodedata.lookup(unicodedata.name(sign).replace("VOWEL SIGN", "LETTER"))


class Style:
    """One vowel-entry style: its key labels and its typing machine."""

    def __init__(self, name: str, alphabet: Alphabet | None = None):
        if name not in STYLES:
            raise ValueError(f"unknown style {name}")
        self.name = name
        self.alphabet = alphabet = alphabet or Alphabet.from_inventory()
        self.description = STYLE_NAMES[name]
        self.sign_of = alphabet.sign_of
        self.vowel_of = alphabet.vowel_of
        vowel_keys = alphabet.vowels if name == "C" else (INHERENT,) + alphabet.signs
        self.searched = tuple(sorted(alphabet.consonants)) + alphabet.others + vowel_keys
        self.fixed = alphabet.digits + tuple(FIXED_PUNCTUATION)
        self.labels = frozenset(self.searched + self.fixed)
        self._options = self._build_options()
        self._cache: dict[str, tuple] = {}

    # --- the typing machine -------------------------------------------------
    # State: (output units, last) where last is (label, what that press did)
    # for the previous keystroke, or None after an escape or at the start.
    # A B/D run is (label, "run", presses): its output, the last
    # ceil(presses / 2) units, is rewritten on every press.

    def _run_output(self, sign: str, presses: int) -> list[str]:
        vowel = self.vowel_of[sign]
        return [sign] * (presses % 2) + [vowel] * (presses // 2)

    def press(self, out: list[str], last, label: str):
        """Type ``label`` onto ``out`` (mutated); return the new ``last``."""
        style = self.name
        if style in ("A", "B", "D") and label in self.vowel_of:
            if style == "A":
                if last == (HASANT, "put") and out and out[-1] == HASANT:
                    out[-1] = self.vowel_of[label]
                    return label, "converted"
                out.append(label)
                return label, "sign"
            if last is not None and last[:2] == (label, "run"):   # B and D: the run goes on
                presses = last[2] + 1
                del out[len(out) - (last[2] + 1) // 2:]
                out.extend(self._run_output(label, presses))
                return label, "run", presses
            if style == "B" or (out and out[-1] in self.alphabet.consonants):
                out.append(label)
                return label, "run", 1
            out.append(self.vowel_of[label])      # D outside a consonant context
            return label, "vowel"
        if style == "C" and label in self.sign_of:
            if last == (label, "vowel"):
                out[-1] = self.sign_of[label]
                return label, "converted"
            out.append(label)
            return label, "vowel"
        if label not in self.labels:
            raise KeyError(f"style {style} has no key labelled {label!r}")
        out.append(label)
        return label, "put"

    def decode(self, steps) -> str:
        out: list[str] = []
        last = None
        for step in steps:
            if isinstance(step, Escape):
                out.append(step.char)
                last = None
            else:
                last = self.press(out, last, step)
        return nfc("".join(out))

    # --- encoding -------------------------------------------------------------

    def _build_options(self) -> dict[str, tuple[tuple[str, ...], ...]]:
        """Label sequences that may type each unit, fewest keystrokes first."""
        options: dict[str, tuple[tuple[str, ...], ...]] = {label: ((label,),) for label in self.labels}
        for vowel, sign in self.sign_of.items():
            if self.name == "A":
                options[vowel] = ((HASANT, sign),)
                options[sign] = ((sign,),)
            elif self.name == "B":
                options[vowel] = ((sign, sign),)
                options[sign] = ((sign,),)
            elif self.name == "C":
                options[vowel] = ((vowel,),)
                options[sign] = ((vowel, vowel),)
            else:
                options[vowel] = ((sign,), (sign, sign))
                options[sign] = ((sign,),)
        return options

    def encode(self, text: str) -> tuple:
        """Labels (and Escapes) typing NFC ``text``; see the module docstring."""
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        out: list[str] = []
        last = None
        steps: list = []
        for unit in segment(text):
            # A press rewrites at most the previous unit or the open run's output.
            lo = max(0, len(out) - max(1, (last[2] + 1) // 2 if last and last[1] == "run" else 1))
            for option in self._options.get(unit, ()):
                trial, trial_last = out[lo:], last
                for label in option:
                    trial_last = self.press(trial, trial_last, label)
                if trial == out[lo:] + [unit]:
                    out.append(unit)
                    last = trial_last
                    steps.extend(option)
                    break
            else:
                out.append(unit)
                last = None
                steps.append(Escape(unit))
        result = tuple(steps)
        if len(self._cache) < 200_000:
            self._cache[text] = result
        return result

    def round_trip(self, text: str) -> tuple[bool, int]:
        """(decoded text equals NFC text, number of escaped units/characters)."""
        target = nfc(text)
        steps = self.encode(target)
        return self.decode(steps) == target, sum(isinstance(s, Escape) for s in steps)


def load_styles(inventory: dict | None = None) -> dict[str, Style]:
    alphabet = Alphabet.from_inventory(inventory)
    return {name: Style(name, alphabet) for name in STYLES}
