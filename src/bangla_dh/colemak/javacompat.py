"""Reproduce the JVM numeric and text semantics the original analyzer relies on.

The reference implementation (Kotlin, JVM) stores frequencies as 32-bit
``Float`` and formats results with ``java.util.Formatter``. Python floats are
64-bit and Python formatting rounds half-to-even on the exact binary value, so
both are emulated here to make results comparable digit for digit.
"""
from __future__ import annotations

import struct
import unicodedata
from decimal import ROUND_HALF_UP, Decimal


def f32(value: float) -> float:
    """Round a double to the nearest IEEE-754 binary32 value (round-half-even).

    A single +, -, * or / of two binary32 operands evaluated in binary64 and
    then rounded once to binary32 equals the correctly rounded binary32 result,
    so ``f32(f32(a) / f32(b))`` reproduces Kotlin's ``Float / Float``.
    """
    if value != value:  # NaN
        return value
    try:
        return struct.unpack("<f", struct.pack("<f", value))[0]
    except OverflowError:
        return float("inf") if value > 0 else float("-inf")


def shortest_f32_repr(value: float) -> str:
    """Shortest decimal string that round-trips to the same binary32 value."""
    if value != value or value in (float("inf"), float("-inf")):
        return repr(value)
    for precision in range(1, 10):
        text = f"{value:.{precision}g}"
        if f32(float(text)) == value:
            return text
    return repr(value)


def java_format_fixed(value: float, decimals: int, *, is_float32: bool = False,
                      space_flag: bool = False) -> str:
    """Emulate Java ``%.Nf`` (and ``% .Nf`` when ``space_flag``).

    Java's Formatter rounds HALF_UP the shortest decimal representation of the
    value (``Double.toString`` digits; JDK 19+ produces the shortest repr, the
    same digits as Python's ``repr``). Float arguments use the binary32
    shortest representation.
    """
    if value != value:
        text = "NaN"
    elif value in (float("inf"), float("-inf")):
        text = "Infinity" if value > 0 else "-Infinity"
    else:
        digits = shortest_f32_repr(value) if is_float32 else repr(float(value))
        quantum = Decimal(1).scaleb(-decimals)
        text = format(Decimal(digits).quantize(quantum, rounding=ROUND_HALF_UP), "f")
    if space_flag and not text.startswith("-"):
        text = " " + text
    return text


def java_upper_char(ch: str) -> str:
    """``Character.toUpperCase(char)``: never expands to several characters."""
    upper = ch.upper()
    return upper if len(upper) == 1 else ch


def java_lower_char(ch: str) -> str:
    lower = ch.lower()
    return lower if len(lower) == 1 else ch


# Other_Alphabetic code points in the Bengali block (Unicode PropList).
# Java's Character.isAlphabetic includes them; Python's str.isalpha does not.
_BENGALI_OTHER_ALPHABETIC = frozenset(
    list(range(0x0981, 0x0984)) + list(range(0x09BE, 0x09C5)) + [0x09C7, 0x09C8, 0x09CB, 0x09CC, 0x09D7, 0x09E2, 0x09E3]
)


def java_is_alphabetic(ch: str) -> bool:
    """``Character.isAlphabetic``: letters, letter numbers and Other_Alphabetic.

    Other_Alphabetic is only tabulated for the Bengali block, which is the
    only non-Latin script this project feeds through the original model.
    """
    if unicodedata.category(ch) in ("Lu", "Ll", "Lt", "Lm", "Lo", "Nl"):
        return True
    return ord(ch) in _BENGALI_OTHER_ALPHABETIC


def java_is_lower_case(ch: str) -> bool:
    return unicodedata.category(ch) == "Ll"


def java_split(text: str, sep: str) -> list[str]:
    """``io.github.colemakmods.chars.StringSplitter.split``: drops empty tokens."""
    return [token for token in text.split(sep) if token]


def kotlin_trim(text: str) -> str:
    """Kotlin ``String.trim()`` removes Unicode whitespace at both ends."""
    return text.strip()


def kotlin_trim_ascii(text: str) -> str:
    """Kotlin ``trim { it <= ' ' }`` removes control characters and spaces."""
    start, end = 0, len(text)
    while start < end and text[start] <= " ":
        start += 1
    while end > start and text[end - 1] <= " ":
        end -= 1
    return text[start:end]


def strip_comment(line: str) -> str:
    position = line.find("#")
    return line if position < 0 else line[:position]
