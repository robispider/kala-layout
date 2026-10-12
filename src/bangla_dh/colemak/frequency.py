"""Character and bigram frequency tables (``CharDataLoader``, ``BigramDataLoader``,
``CharFreq``, ``BigramFreq`` and ``FreqAnalysis`` of the original analyzer).

Normalized frequencies are binary32 values, as in the original ``Float``
fields: ``freq = count.toFloat() / total`` where the Long total is converted
to Float before the division.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .javacompat import f32, java_split, java_upper_char


@dataclass
class CharFreq:
    char: str
    count: int = 0
    freq: float = 0.0  # binary32 value


@dataclass
class BigramFreq:
    string: str
    count: int = 0
    freq: float = 0.0  # binary32 value


def normalize(items: list) -> None:
    total = sum(item.count for item in items)
    for item in items:
        item.freq = f32(f32(item.count) / f32(total)) if total else float("nan")


def _frequency_lines(text: str):
    for line in text.splitlines():
        tokens = java_split(line, " ")
        if not line.startswith("#") and len(tokens) >= 2:
            yield tokens


def load_char_freqs(alphabet: str, text: str) -> list[CharFreq]:
    result: list[CharFreq] = []
    for tokens in _frequency_lines(text):
        token = tokens[0].upper()
        if len(token) == 1 and token in alphabet:
            result.append(CharFreq(token, int(tokens[1])))
    normalize(result)
    return result


def load_bigram_freqs(alphabet: str, text: str) -> list[BigramFreq]:
    result: list[BigramFreq] = []
    for tokens in _frequency_lines(text):
        bigram = tokens[0].upper()
        if len(bigram) == 2 and bigram[0] in alphabet and bigram[1] in alphabet:
            result.append(BigramFreq(bigram, int(tokens[1])))
    normalize(result)
    return result


def load_frequency_file(alphabet: str, path: str | Path) -> tuple[list[CharFreq], list[BigramFreq]]:
    text = Path(path).read_text(encoding="utf-8")
    return load_char_freqs(alphabet, text), load_bigram_freqs(alphabet, text)


DEFAULT_MAX_UNICODE = 0x10FFFF


class FreqAnalysis:
    """Port of ``FreqAnalysis.kt``: counts characters and alphabet bigrams.

    Characters are processed one code point at a time (the JVM reads UTF-16
    code units; the two agree for the Basic Multilingual Plane, which contains
    all of Bangla). A character with code <= 32 is skipped but still becomes
    the left side of the next bigram, so bigrams never span whitespace.
    """

    def __init__(self, alphabet: str, max_unicode: int = -1):
        self.char_freqs = [CharFreq(c) for c in alphabet]
        self.bigram_freqs = [BigramFreq(a + b) for a in alphabet for b in alphabet]
        self.max_unicode = max_unicode if max_unicode > 0 else DEFAULT_MAX_UNICODE
        self._chars = {cf.char: cf for cf in self.char_freqs}
        self._bigrams = {bf.string: bf for bf in self.bigram_freqs}
        self.units_read = 0

    def feed(self, text: str, previous: str = " ") -> str:
        current = previous
        for raw in text:
            code = ord(raw)
            prior, current = current, java_upper_char(raw)
            if code > 32:
                cf = self._chars.get(current)
                if cf is not None:
                    cf.count += 1
                elif code < self.max_unicode and code != 0xFFFD:
                    # The original stores the raw (not uppercased) character.
                    cf = CharFreq(raw, 1)
                    self.char_freqs.append(cf)
                    self._chars[cf.char] = cf
                bf = self._bigrams.get((prior + current).upper())
                if bf is not None:
                    bf.count += 1
            self.units_read += 1
        return current

    def analyze(self, text: str) -> None:
        self.feed(text)
        self.sort()

    def sort(self) -> None:
        # Collections.sort is stable; sort descending by count.
        self.char_freqs.sort(key=lambda item: -item.count)
        self.bigram_freqs.sort(key=lambda item: -item.count)

    def normalize(self) -> None:
        normalize(self.char_freqs)
        normalize(self.bigram_freqs)

    def frequency_file_text(self, show_normalized: bool = False) -> str:
        lines = []
        for item in self.char_freqs:
            lines.append(f"{item.char} {item.count}" + (f" {item.freq!r}" if show_normalized else ""))
        for item in self.bigram_freqs:
            lines.append(f"{item.string} {item.count}" + (f" {item.freq!r}" if show_normalized else ""))
        return "\n".join(lines) + "\n"
