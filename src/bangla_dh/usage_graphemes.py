"""Unicode 15.0 default extended clusters, UAX #29 revision 41 (GB1–GB999).

Deliberately uses the historical study's Unicode version, not the host Python's
Unicode database or the later Indic-conjunct rule. No third-party runtime.
"""
from bisect import bisect_right
from functools import lru_cache
import hashlib
import json

from .paths import DATA

VERSION = "uax29-41-unicode-15.0.0"
ROOT = DATA / "unicode/15.0.0"


@lru_cache(maxsize=1)
def _tables():
    manifest = json.loads((ROOT / "SOURCES.json").read_bytes())
    tables = []
    for name, selected in (("GraphemeBreakProperty.txt", None), ("emoji-data.txt", "Extended_Pictographic")):
        raw = (ROOT / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest["files"][name]["sha256"]:
            raise ValueError("Unicode property checksum mismatch")
        ranges = []
        for line in raw.decode("utf-8").splitlines():
            content = line.split("#", 1)[0].strip()
            if not content:
                continue
            code, prop = map(str.strip, content.split(";"))
            if selected is not None and prop != selected:
                continue
            ends = code.split("..")
            ranges.append((int(ends[0], 16), int(ends[-1], 16), prop))
        ranges.sort()
        tables.append(([r[0] for r in ranges], ranges))
    return tables


def _property(code, table, fallback):
    starts, ranges = table
    i = bisect_right(starts, code) - 1
    return ranges[i][2] if i >= 0 and code <= ranges[i][1] else fallback


def graphemes(text):
    if not text:
        return []
    gb, emoji = _tables()
    props = [_property(ord(c), gb, "Other") for c in text]
    pict = [_property(ord(c), emoji, None) is not None for c in text]
    starts = [0]
    controls = {"Control", "CR", "LF"}
    ri_run = int(props[0] == "Regional_Indicator")
    for i in range(1, len(text)):
        a, b = props[i - 1], props[i]
        if a == "CR" and b == "LF":  # GB3
            join = True
        elif a in controls or b in controls:  # GB4/5
            join = False
        elif a == "L" and b in {"L", "V", "LV", "LVT"}:  # GB6
            join = True
        elif a in {"LV", "V"} and b in {"V", "T"}:  # GB7
            join = True
        elif a in {"LVT", "T"} and b == "T":  # GB8
            join = True
        elif b in {"Extend", "ZWJ", "SpacingMark"} or a == "Prepend":  # GB9/9a/9b
            join = True
        elif a == "ZWJ" and pict[i]:  # GB11
            j = i - 2
            while j >= 0 and props[j] == "Extend":
                j -= 1
            join = j >= 0 and pict[j]
        elif a == b == "Regional_Indicator":  # GB12/13
            join = ri_run % 2 == 1
        else:  # GB999
            join = False
        if not join:
            starts.append(i)
        ri_run = ri_run + 1 if b == "Regional_Indicator" else 0
    starts.append(len(text))
    return [text[a:b] for a, b in zip(starts, starts[1:])]
