"""Kala's imported Avro fixed layouts (``avro-fixed``) as a typing machine.

``decode`` is a line-by-line port of ``kala/Keyboard/AvroFixedLayoutManager.cs``
(Kala's adaptation of Avro's modern formatting): a vowel sign typed where a
dead key is pending (word start, after a vowel or a sign) becomes the
independent vowel; ``্`` + vowel sign gives the independent vowel; ``্`` ``্``
gives ``্`` + ZWNJ; the reph key moves ``র্`` in front of the consonant
cluster just typed; ``ঁ`` typed before a vowel sign moves after it; ``্য``
after ``র`` gives ``র‍্য``. Space and any unmapped key reset the session.

``encode`` finds, per token, the fewest keystrokes (then the least effort)
whose decoded output is the NFC text, by dynamic programming over the text
with the machine's state; units it cannot reach are escaped. Only the base and
Shift layers are used, because AltGr has no v1 cost (D2); every Kala layout
types its frequent text without AltGr thanks to the rules above.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Callable

from ..bangla.grammar import Action, Escape, ESCAPE_KEYSTROKES
from .layouts import VK_TO_KEY

HALANT, CHANDRA, ZWNJ, ZWJ, NUKTA = "্", "ঁ", "‌", "‍", "়"
KARS = "ািীুূৃেৈোৌৄৢৣ"
FORMATTING_KARS = "ািীুূৃেৈৌৄৢৣ"  # Avro's IsKar omits O-kar (kept by Kala)
CONSONANTS = "কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎৰৱ"
INDEPENDENT = {"া": "আ", "ি": "ই", "ী": "ঈ", "ু": "উ", "ূ": "ঊ", "ৃ": "ঋ", "ে": "এ", "ৈ": "ঐ", "ো": "ও", "ৌ": "ঔ"}
_DEAD = set("০১২৩৪৫৬৭৮৯" + KARS + "অআইঈউঊঋএঐওঔঌৡৠংঃৎ।৳ৗ৲৴৵৶৷৸৹" + "`~!@#$%^+*-_=+\\|\"/;:,./?><()[]{}'")
LAYERS = {"normal": "base", "shift": "shift"}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_dead_key(c: str) -> bool:
    return c in _DEAD or (c.isascii() and c.isalnum())


def _is_consonant_at(text: str, k: int) -> int:
    """Length (1 or 2) of the consonant ending at text[k], 0 if none. NFC
    spells ড় ঢ় য় as consonant + nukta; Kala's raw text has one code point."""
    if text[k] in CONSONANTS:
        return 1
    if text[k] == NUKTA and k > 0 and text[k - 1] in "ডঢয":
        return 2
    return 0


def reph_suffix_length(text: str) -> int:
    """``RephSuffixLength`` on NFC text (consonant + nukta counts as one consonant)."""
    start = len(text)
    if start > 0 and text[start - 1] == CHANDRA:
        start -= 1
    if start > 0 and text[start - 1] in FORMATTING_KARS:
        start -= 1
    if start == 0:
        return 0
    size = _is_consonant_at(text, start - 1)
    if not size:
        return 0
    start -= size
    while start >= 2 and text[start - 1] == HALANT:
        size = _is_consonant_at(text, start - 2)
        if not size or len(text) - start >= 98:
            break
        start -= 1 + size
    return len(text) - start


class AvroFixedKeyMap:
    def __init__(self, name: str, layers: dict, options: dict, effort: Callable[[str], float] = lambda key: 0.0):
        self.name = name
        self.options = {"VowelFormatting": True, "MoveReph": True, "FixChandrabindu": True, **(options or {})}
        self.actions = [Action(VK_TO_KEY[int(vk)], LAYERS[layer], out)
                        for layer in LAYERS for vk, out in layers.get(layer, {}).items()
                        if out and int(vk) in VK_TO_KEY]
        self.altgr_outputs = sorted({o for layer in ("rightalt", "shiftaltgr") for o in layers.get(layer, {}).values() if o})
        self.effort = effort
        cost = lambda a: (1, effort(a.key))
        best: dict[str, Action] = {}
        for a in self.actions:
            if a.output not in best or cost(a) < cost(best[a.output]):
                best[a.output] = a
        self._by_output = best  # cheapest key for each raw output
        index: dict[str, list[tuple[str, Action]]] = {}
        for mapped, action in best.items():
            firsts = {nfc(mapped)[0]}
            if mapped in INDEPENDENT:
                firsts.add(INDEPENDENT[mapped])
            if mapped == HALANT:
                firsts.add(ZWNJ)
            if mapped == "্য":
                firsts.add(ZWJ)
            for c in firsts:
                index.setdefault(c, []).append((mapped, action))
        self._index = index  # first character a key can produce → keys
        self._halant = best.get(HALANT)
        self._chandra = best.get(CHANDRA)
        self._reph = best.get("র্") if self.options["MoveReph"] else None
        self._cache: dict[str, tuple] = {}

    # --- the machine (port of TranslateKey) -------------------------------------------

    def decode(self, steps) -> str:
        text, dead, done = "", True, ""
        o = self.options
        for step in steps:
            if isinstance(step, Escape):
                done += text + step.char  # typed outside the layout: the session resets
                text, dead = "", True
                continue
            mapped = step.output
            previous = text
            output = mapped
            last = previous[-1] if previous else " "
            if not o["VowelFormatting"]:
                dead = False
            if dead and mapped not in INDEPENDENT:
                dead = False
            if dead and mapped in INDEPENDENT:
                output = INDEPENDENT[mapped]
            elif last == HALANT and mapped in INDEPENDENT:
                previous, output, dead = previous[:-1], INDEPENDENT[mapped], True
            elif last == HALANT and mapped == HALANT:
                output, dead = ZWNJ, True
            elif mapped == "র্":
                length = reph_suffix_length(nfc(previous)) if o["MoveReph"] else 0
                if length:
                    norm = nfc(previous)
                    previous, output = norm[:-length], output + norm[-length:]
            elif mapped == "্য" and last == "র" and (len(previous) < 2 or previous[-2] != HALANT):
                output = ZWJ + "্য"
            else:
                end = mapped[-1]
                if is_dead_key(end) and mapped[0] in FORMATTING_KARS and o["FixChandrabindu"] and last == CHANDRA:
                    previous, output = previous[:-1], output + CHANDRA
                dead = is_dead_key(end)
            text = previous + output
        return nfc(done + text)

    # --- encoder ----------------------------------------------------------------------------

    def _moves(self, s: str, i: int, dead: bool, s0: int):
        """(steps, new text position, dead) for every move from s[:i]; the
        session text is s[s0:i]."""
        o = self.options
        last = s[i - 1] if i > s0 else " "
        for mapped, action in self._index.get(s[i], ()):
            if mapped in INDEPENDENT:
                if dead and o["VowelFormatting"]:
                    out, nd = INDEPENDENT[mapped], True
                elif last == HALANT or (last == CHANDRA and o["FixChandrabindu"] and mapped[0] in FORMATTING_KARS):
                    continue  # rewrites earlier text: only inside the macros below
                else:
                    out, nd = mapped, True
            elif last == HALANT and mapped == HALANT:
                out, nd = ZWNJ, True
            elif mapped == "র্":
                if o["MoveReph"] and reph_suffix_length(s[s0:i]):
                    continue
                out, nd = mapped, False
            elif mapped == "্য" and last == "র" and not (i - s0 >= 2 and s[i - 2] == HALANT):
                out, nd = ZWJ + "্য", False
            else:
                if is_dead_key(mapped[-1]) and mapped[0] in FORMATTING_KARS and o["FixChandrabindu"] and last == CHANDRA:
                    continue
                out, nd = mapped, is_dead_key(mapped[-1])
            out = nfc(out)
            if s.startswith(out, i):
                yield (action,), i + len(out), nd
        # ্ + vowel sign → independent vowel
        if self._halant is not None and last != HALANT:
            for sign, vowel in INDEPENDENT.items():
                if sign in self._by_output and s.startswith(vowel, i):
                    yield (self._halant, self._by_output[sign]), i + len(vowel), True
        # ঁ then a vowel sign → sign + ঁ
        if self._chandra is not None and o["FixChandrabindu"] and last != HALANT:
            for sign in FORMATTING_KARS:
                if sign in self._by_output and s.startswith(nfc(sign + CHANDRA), i):
                    yield (self._chandra, self._by_output[sign]), i + 2, True

    def _best(self, s: str, start: int, dead0: bool, s0: int, end: int) -> tuple | None:
        """Cheapest (cost, steps, dead) typing s[start:end] after s[:start]."""
        buckets: list[dict] = [dict() for _ in range(end + 2)]
        buckets[start][(dead0, s0)] = ((0, 0.0), ())

        def relax(j: int, state: tuple, cost: tuple, steps: tuple) -> None:
            known = buckets[j].get(state)
            if known is None or cost < known[0]:
                buckets[j][state] = (cost, steps)

        for i in range(start, end):
            for (dead, z), (cost, steps) in buckets[i].items():
                moves = self._moves(s, i, dead, z)
                if self._reph is not None and s.startswith("র্", i):
                    moves = list(moves) + list(self._reph_moves(s, i, dead, z, end))
                for move, j, nd in moves:
                    if j <= end:
                        relax(j, (nd, z), (cost[0] + len(move), cost[1] + sum(self.effort(a.key) for a in move)),
                              steps + move)
                relax(i + 1, (True, i + 1), (cost[0] + ESCAPE_KEYSTROKES, cost[1]), steps + (Escape(s[i]),))
        if not buckets[end]:
            return None
        (dead, _), (cost, steps) = min(buckets[end].items(), key=lambda kv: kv[1][0])
        return cost, steps, dead

    def _reph_moves(self, s: str, i: int, dead: bool, s0: int, end: int):
        """Type the cluster X after র্ first, then the reph key moves র্ in front."""
        for j in range(i + 3, min(end, i + 2 + 16) + 1):
            x = s[i + 2:j]
            prefix = s[s0:i]
            if reph_suffix_length(prefix + x) != len(x):
                continue
            sub = self._best(prefix + x, len(prefix), dead, 0, len(prefix) + len(x))
            if sub is None or any(isinstance(t, Escape) for t in sub[1]):
                continue
            yield sub[1] + (self._reph,), j, False

    def encode(self, text: str) -> tuple:
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        result = self._best(text, 0, True, 0, len(text))[1]
        if len(self._cache) < 200_000:
            self._cache[text] = result
        return result

    def round_trip(self, text: str) -> tuple[bool, int]:
        target = nfc(text)
        steps = self.encode(target)
        return self.decode(steps) == target, sum(isinstance(s, Escape) for s in steps)

    def producible(self) -> set[str]:
        """Units this layout can type: alone, or after a consonant for signs."""
        out = set()
        for a in self.actions:
            for text in (a.output, INDEPENDENT.get(a.output, "")):
                if text:
                    out.add(nfc(text))
        out |= set(INDEPENDENT.values()) if self._halant else set()
        return out


def load(path: Path, effort: Callable[[str], float]) -> AvroFixedKeyMap:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("type") != "avro-fixed":
        raise ValueError(f"{path}: not an avro-fixed layout")
    return AvroFixedKeyMap(data["name"], data["layers"], data.get("options", {}), effort)
