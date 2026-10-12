"""Typing grammar (Phase 2, task 2): text → typing units, and text ↔ key
actions for any key map.

Units
    ``segment`` splits NFC text into units: one code point each, except
    ড ঢ য + nukta, which form one unit (ড় ঢ় য়). Independent vowels and vowel
    signs are different code points, so they are different units; hasant is a
    unit of its own, so a conjunct is consonant, hasant, consonant. Whether a
    unit is in the inventory is the caller's question (``UnitSet``).

Key maps
    A ``KeyMap`` is a set of actions (physical key + layer → output string)
    plus optional *sequences*: typing the outputs in the sequence key yields
    the sequence value instead (UniJoy: ্ then া gives আ). ``decode``
    simulates typing; ``encode`` finds the action sequence with the fewest
    keystrokes (ties: lowest summed key effort) whose decoded, NFC-normalized
    output equals the text. Characters a map cannot produce become
    ``Escape`` steps: they are typed outside the model and break bigrams.

The invariant of RESEARCH_SPEC section 4.1 is checked by ``round_trip``:
``NFC(decode(encode(T))) == NFC(T)`` for every text the map covers.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Iterable

from .inventory import NUKTA, NUKTA_BASES, SPACE, load_inventory


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def segment(text: str) -> list[str]:
    """Typing units of NFC ``text`` (nukta consonants merged)."""
    units: list[str] = []
    append = units.append
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if i + 1 < n and text[i + 1] == NUKTA and ch in NUKTA_BASES:
            append(ch + NUKTA)
            i += 2
        else:
            append(ch)
            i += 1
    return units


@dataclass(frozen=True)
class UnitSet:
    placed: frozenset[str]
    tracked: frozenset[str]

    @classmethod
    def from_inventory(cls, inventory: dict | None = None) -> "UnitSet":
        inventory = inventory or load_inventory()
        return cls(frozenset(e["symbol"] for e in inventory["symbols"] if e["placed"]),
                   frozenset(e["symbol"] for e in inventory["symbols"] if not e["placed"]))

    @property
    def counted(self) -> frozenset[str]:
        """Units that enter the frequency tables: placed, tracked and space."""
        return self.placed | self.tracked | {SPACE}

    def is_unit(self, unit: str) -> bool:
        return unit in self.placed or unit in self.tracked or unit == SPACE


@dataclass(frozen=True)
class Action:
    key: str
    layer: str
    output: str

    def __str__(self) -> str:
        return f"{self.key}{'' if self.layer == 'base' else '+' + self.layer}"


@dataclass(frozen=True)
class Escape:
    """A character the key map cannot produce; typed outside the model."""
    char: str


ESCAPE_KEYSTROKES = 10 ** 6


@dataclass
class KeyMap:
    name: str
    actions: list[Action]
    sequences: dict[str, str] = field(default_factory=dict)
    effort: Callable[[str], float] = lambda key: 0.0

    def __post_init__(self) -> None:
        self._candidates: dict[str, list[tuple[str, tuple[Action, ...], tuple[int, float]]]] = {}
        self._sequence_keys = tuple(self.sequences)
        self._longest_sequence = max((len(k) for k in self.sequences), default=0)
        for action in self.actions:
            self._add(nfc(action.output), (action,))
        for typed, result in self.sequences.items():
            chain = self._chain(typed)
            if chain is not None:
                self._add(nfc(result), chain)
        self._cache: dict[str, tuple] = {}

    def _add(self, output: str, steps: tuple[Action, ...]) -> None:
        if not output:
            return
        cost = (len(steps), sum(self.effort(a.key) for a in steps))
        self._candidates.setdefault(output[0], []).append((output, steps, cost))

    def _chain(self, typed: str) -> tuple[Action, ...] | None:
        """Cheapest action chain whose raw outputs concatenate to ``typed``."""
        best: dict[int, tuple[tuple[int, float], tuple[Action, ...]]] = {0: ((0, 0.0), ())}
        for i in range(len(typed)):
            if i not in best:
                continue
            (count, effort), steps = best[i]
            for action in self.actions:
                if action.output and typed.startswith(action.output, i):
                    j = i + len(action.output)
                    cost = (count + 1, effort + self.effort(action.key))
                    if j not in best or cost < best[j][0]:
                        best[j] = (cost, steps + (action,))
        return best[len(typed)][1] if len(typed) in best else None

    def producible(self) -> set[str]:
        return {output for options in self._candidates.values() for output, _, _ in options}

    def encode(self, text: str) -> tuple:
        """Cheapest step sequence (Actions and Escapes) for NFC ``text``."""
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        n = len(text)
        inf = (float("inf"), float("inf"))
        best: list[tuple] = [inf] * (n + 1)
        back: list = [None] * (n + 1)
        best[0] = (0, 0.0)
        for i in range(n):
            here = best[i]
            if here == inf:
                continue
            for output, steps, (count, effort) in self._candidates.get(text[i], ()):
                if text.startswith(output, i) and not self._completes_sequence(text, i, output, steps):
                    j = i + len(output)
                    cost = (here[0] + count, here[1] + effort)
                    if cost < best[j]:
                        best[j], back[j] = cost, (i, steps)
            cost = (here[0] + ESCAPE_KEYSTROKES, here[1])
            if cost < best[i + 1]:
                best[i + 1], back[i + 1] = cost, (i, (Escape(text[i]),))
        out: list = []
        j = n
        while j > 0:
            i, steps = back[j]
            out[:0] = steps
            j = i
        result = tuple(out)
        if len(self._cache) < 200_000:
            self._cache[text] = result
        return result

    def _completes_sequence(self, text: str, i: int, output: str, steps: tuple[Action, ...]) -> bool:
        """True if a single action typed after text[:i] would trigger a
        sequence by accident (e.g. ্ then ী becomes ঈ in UniJoy). Such text
        (here an invalid hasant + vowel sign) cannot be typed with that action."""
        if len(steps) != 1 or not self._sequence_keys:
            return False
        tail = text[max(0, i - self._longest_sequence):i] + output
        return any(tail.endswith(typed) for typed in self._sequence_keys)

    def decode(self, steps: Iterable) -> str:
        """Simulate typing: append outputs, apply sequences at the tail.
        Escaped characters are inserted outside the keyboard and trigger nothing."""
        buffer = ""
        for step in steps:
            if isinstance(step, Escape):
                buffer += step.char
                continue
            buffer += step.output
            for typed, result in self.sequences.items():
                if buffer.endswith(typed):
                    buffer = buffer[: len(buffer) - len(typed)] + result
                    break
        return nfc(buffer)

    def round_trip(self, text: str) -> tuple[bool, int]:
        """(decoded text equals NFC text, number of escapes)."""
        target = nfc(text)
        steps = self.encode(target)
        return self.decode(steps) == target, sum(isinstance(s, Escape) for s in steps)


def single_action_keymap(name: str, assignment: dict[str, tuple[str, str]],
                         effort: Callable[[str], float] = lambda key: 0.0) -> KeyMap:
    """Key map of a Bangla-DH layout: each unit → one (key, layer) action."""
    return KeyMap(name, [Action(key, layer, unit) for unit, (key, layer) in assignment.items()], effort=effort)
