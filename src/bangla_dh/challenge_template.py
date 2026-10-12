#!/usr/bin/env python3
"""Bangla-DH layout challenge: score a Bangla keyboard layout.

Can you place the Bangla letters on a keyboard better than Bangla-DH?

This one file is the whole scorer: Python 3.10 or newer, standard library
only, no downloads. It scores a layout for one of two typing styles with the
ergonomic model Bangla-DH was optimized with, and tells you whether it beats
the Bangla-DH reference layout of that style.

    python bangla_dh_challenge.py --reference                 # the layouts to beat
    python bangla_dh_challenge.py --template D --out my.json  # start from one
    python bangla_dh_challenge.py my.json                     # score it
    python bangla_dh_challenge.py a.json b.json --json        # several, as JSON
    python bangla_dh_challenge.py --public                    # the public layouts to compare with

Rules
-----
* Style A (UniJoy-style: independent vowel = ্ + vowel sign) or style D
  (context: a vowel key gives the sign after a consonant, the independent
  vowel elsewhere). The style fixes which 52 symbols you place; you choose
  where they go.
* Place exactly those 52 symbols, each once, on the 26 letter keys
  Q…M, base and Shift layer (52 slots). Digits and punctuation stay where
  they are (listed by ``--reference``).
* Lower score is better. You beat a layout only with a strictly lower score;
  scores are compared exactly (as fractions), so there is no rounding.

The score (J1)
--------------
For each training text c (Bangla Wikipedia and newspaper text, weight 1/2
each), with keystroke counts from typing the whole text in the chosen style:

    J_c = ( Σ_keystrokes K(key) + M(shift)  +  Σ_consecutive pairs B(key1, key2) ) / N_c

* K: effort of each key (Colemak Mod-DH model, ANSI keyboard): home row
  cheapest, reaches and the pinky dearer;
* M: a Shift-layer symbol adds a press of the other hand's Shift key;
* B: bigram penalty: same finger twice 2.5 / 3.0 / 4.0 by row distance,
  neighbouring fingers of one hand a small penalty (pinky–ring, ring–middle)
  or a bonus (middle–index rolls); space is the thumb and costs nothing;
* N_c: number of characters of the text.

J1 = ½ J_wiki + ½ J_news is the effort per character typed. The keystroke
counts are fixed per style (they do not depend on the layout), so only the
placement changes the score. The embedded data holds those counts and the
key model; ``--dump-data`` writes it out as JSON.

Held-out check and public layouts
---------------------------------
Winning is decided by the training score above. As a second check the scorer
also types three texts no search has seen (Wikipedia and newspaper articles
held out, and BARD news articles unseen by any search) and places your layout
on the leaderboard of Kala Goti, Kala Jhor and the public fixed layouts
(Windows Default, Probhat, Munir Optima, Bornona, National, UniJoy), whose
held-out scores were computed by the full Bangla-DH pipeline. A real
improvement should be lower on the held-out texts too.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import unicodedata
import zlib
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

SCRIPT_VERSION = "1.1.0"
SCALE = 10 ** 6  # efforts have six decimals and penalties one: ×10^6 makes every coefficient an integer
LETTER_KEYS = "QWERTYUIOPASDFGHJKLZXCVBNM"
ROWS = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
LAYERS = ("base", "shift")
DOTTED_CIRCLE = "◌"
FINGER_NAMES = {0: "left pinky", 1: "left ring", 2: "left middle", 3: "left index",
                6: "right index", 7: "right middle", 8: "right ring", 9: "right pinky"}
ROW_NAMES = {0: "number", 1: "top", 2: "home", 3: "bottom"}

_DATA = "@@DATA@@"


# --- data ------------------------------------------------------------------------

def _int(value: str) -> int:
    exact = Decimal(value) * SCALE
    if exact != exact.to_integral_value():
        raise ValueError(f"{value} is not exact at scale {SCALE}")
    return int(exact)


class Model:
    def __init__(self, data: dict):
        model = data["model"]
        self.keys = {k: {"effort": _int(e), "finger": f, "row": r} for k, (e, f, r) in model["keys"].items()}
        self.same_finger = [_int(x) for x in model["same_finger"]]
        self.neighbour = [[_int(x) for x in row] for row in model["neighbour_by_outer_finger"]]
        self.shift = {name: _int(x) for name, x in model["shift_keys"].items()}

    def cost(self, key: str, layer: str) -> int:
        k = self.keys[key]
        return k["effort"] + (self.shift["RSHIFT" if k["finger"] <= 4 else "LSHIFT"] if layer == "shift" else 0)

    def penalty(self, key1: str, key2: str) -> tuple[str, int]:
        a, b = self.keys[key1], self.keys[key2]
        rowdiff = min(2, abs(a["row"] - b["row"]))
        if a["finger"] == b["finger"]:
            return "same_finger", self.same_finger[rowdiff]
        if abs(a["finger"] - b["finger"]) == 1:
            left = lambda f: f if f <= 4 else 9 - f  # noqa: E731
            outer = a["finger"] if left(a["finger"]) < left(b["finger"]) else b["finger"]
            value = self.neighbour[left(outer)][rowdiff]
            return ("neighbour_benefit" if value < 0 else "neighbour_penalty"), value
        return "none", 0


def load_data() -> tuple[dict, str]:
    raw = zlib.decompress(base64.b64decode(_DATA))
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


# --- layouts ---------------------------------------------------------------------

def clean(symbol: str) -> str:
    """NFC, without the dotted circle people use to draw vowel signs (◌া → া)."""
    return unicodedata.normalize("NFC", str(symbol).replace(DOTTED_CIRCLE, "").strip())


def read_layout_file(path: str | Path) -> dict:
    text = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            return json.loads(text.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"{path}: not a JSON file in UTF-8 or UTF-16")


def parse_layout(submission: dict, data: dict) -> tuple[str, dict[str, tuple[str, str]], list[str]]:
    """(style, symbol → (key, layer), problems). The layout is
    {"Q": ["base symbol", "shift symbol"], ...} or {"Q": {"base": .., "shift": ..}}."""
    if not isinstance(submission, dict):
        return "", {}, ['the file must be a JSON object with "style" and "layout"']
    problems = []
    style = str(submission.get("style", "")).strip().upper()
    if style not in data["styles"]:
        return style, {}, [f"style must be one of {', '.join(data['styles'])} (got {style!r})"]
    keys = submission.get("layout")
    if not isinstance(keys, dict):
        return style, {}, ['"layout" must map each letter key (Q … M) to [base, shift]']
    placed: dict[str, tuple[str, str]] = {}
    seen_keys = set()
    for key, value in keys.items():
        name = str(key).strip().upper()
        if name not in LETTER_KEYS:
            problems.append(f"{key!r} is not a letter key (only Q … M can be changed)")
            continue
        if name in seen_keys:
            problems.append(f"key {name} given twice")
            continue
        seen_keys.add(name)
        if isinstance(value, dict):
            value = [value.get("base", ""), value.get("shift", "")]
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            problems.append(f"key {name}: give exactly two symbols, [base, shift]")
            continue
        for layer, symbol in zip(LAYERS, value):
            symbol = clean(symbol)
            if not symbol:
                problems.append(f"key {name} {layer}: empty")
            elif symbol in placed:
                problems.append(f"{symbol} placed twice ({'/'.join(placed[symbol])} and {name}/{layer})")
            else:
                placed[symbol] = (name, layer)
    missing_keys = [k for k in LETTER_KEYS if k not in seen_keys]
    if missing_keys:
        problems.append(f"keys missing: {' '.join(missing_keys)}")
    wanted = set(data["styles"][style]["symbols"])
    extra = sorted(set(placed) - wanted)
    missing = sorted(wanted - set(placed))
    if extra:
        problems.append(f"not a style {style} symbol: {' '.join(extra)}")
    if missing:
        problems.append(f"style {style} symbols not placed: {' '.join(missing)}")
    return style, placed, problems


def layout_hash(style: str, placed: dict[str, tuple[str, str]]) -> str:
    """Identifies a layout: the same placement always gives the same hash."""
    canonical = style + "|" + "|".join(f"{key}/{layer}={symbol}" for symbol, (key, layer)
                                       in sorted(placed.items(), key=lambda kv: (kv[1], kv[0])))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --- scoring ---------------------------------------------------------------------

def score(style: str, placed: dict[str, tuple[str, str]], data: dict, model: Model | None = None) -> dict:
    """Score a valid placement of a style's symbols. J1 is exact (a Fraction)."""
    model = model or Model(data)
    spec = data["styles"][style]
    actions = {**placed, **{s: tuple(slot) for s, slot in spec["fixed"].items()}}
    weights = {name: Fraction(w) for name, w in data["objective"]["weights"].items()}
    j1 = Fraction(0)
    parts = {"E1 (key effort)": 0.0, "M (Shift)": 0.0, "same finger": 0.0, "neighbour penalty": 0.0,
             "neighbour benefit": 0.0}
    stats = {"keystrokes": 0.0, "shift": 0.0, "pairs": 0.0, "same_finger_pairs": 0.0,
             "hand": {"left": 0.0, "right": 0.0}, "row": dict.fromkeys(ROW_NAMES.values(), 0.0),
             "finger": dict.fromkeys(FINGER_NAMES.values(), 0.0)}
    for name, corpus in spec["corpora"].items():
        w, n = weights[name], corpus["N"]
        e1 = m = 0
        pen = {"same_finger": 0, "neighbour_penalty": 0, "neighbour_benefit": 0}
        keystrokes = shift = pairs = sf_pairs = 0
        for symbol, count in corpus["labels"].items():
            key, layer = actions[symbol]
            k = model.keys[key]
            e1 += count * k["effort"]
            m += count * (model.cost(key, layer) - k["effort"])
            keystrokes += count
            shift += count if layer == "shift" else 0
            stats["hand"]["left" if k["finger"] <= 4 else "right"] += float(w) * count
            stats["row"][ROW_NAMES[k["row"]]] += float(w) * count
            stats["finger"][FINGER_NAMES[k["finger"]]] += float(w) * count
        for a, b, count in corpus["pairs"]:
            kind, value = model.penalty(actions[a][0], actions[b][0])
            pairs += count
            if kind != "none":
                pen[kind] += count * value
            if kind == "same_finger":
                sf_pairs += count
        z = e1 + m + sum(pen.values())
        j1 += w * Fraction(z, n * SCALE)
        for label, value in (("E1 (key effort)", e1), ("M (Shift)", m), ("same finger", pen["same_finger"]),
                             ("neighbour penalty", pen["neighbour_penalty"]),
                             ("neighbour benefit", pen["neighbour_benefit"])):
            parts[label] += float(w) * value / (n * SCALE)
        stats["keystrokes"] += float(w) * keystrokes
        stats["shift"] += float(w) * shift
        stats["pairs"] += float(w) * pairs
        stats["same_finger_pairs"] += float(w) * sf_pairs
    total = stats["keystrokes"]
    ergonomics = {
        "same-finger bigrams (% of key pairs)": 100 * stats["same_finger_pairs"] / stats["pairs"],
        "Shift presses (% of keystrokes)": 100 * stats["shift"] / total,
        "left / right hand (%)": [100 * stats["hand"]["left"] / total, 100 * stats["hand"]["right"] / total],
        "rows (% of keystrokes)": {r: 100 * v / total for r, v in stats["row"].items()},
        "fingers (% of keystrokes)": {f: 100 * v / total for f, v in stats["finger"].items()},
    }
    return {"J1": j1, "parts": parts, "ergonomics": ergonomics}


def corpus_j1(corpus: dict, actions: dict, model: Model) -> Fraction:
    """J for one text: (key effort + Shift + bigram penalties) / N."""
    z = 0
    for symbol, count in corpus["labels"].items():
        z += count * model.cost(*actions[symbol])
    for a, b, count in corpus["pairs"]:
        z += count * model.penalty(actions[a][0], actions[b][0])[1]
    return Fraction(z, corpus["N"] * SCALE)


def held_out(style: str, placed: dict[str, tuple[str, str]], data: dict, model: Model | None = None) -> dict:
    """J1 on the held-out texts and the layout's place among the public layouts."""
    model = model or Model(data)
    spec = data["styles"][style]
    actions = {**placed, **{s: tuple(slot) for s, slot in spec["fixed"].items()}}
    columns = data["public_layouts"]["texts"]
    j1 = {columns[name]: float(corpus_j1(corpus, actions, model)) for name, corpus in spec["heldout"].items()}
    average = sum(j1.values()) / len(j1)
    entries = data["public_layouts"]["entries"]
    ahead = [e["name"] for e in entries if e["average"] < round(average, 4)]
    return {"J1": {k: round(v, 6) for k, v in j1.items()}, "average": round(average, 6),
            "public_rank": len(ahead) + 1, "public_layouts": len(entries), "ahead_of_you": ahead}


def evaluate(submission: dict, data: dict, data_sha256: str, model: Model | None = None) -> dict:
    style, placed, problems = parse_layout(submission, data)
    name = (submission.get("name") or submission.get("author") or "") if isinstance(submission, dict) else ""
    result = {"name": str(name)[:100], "style": style,
              "valid": not problems, "problems": problems, "script_version": SCRIPT_VERSION,
              "data_version": data["version"], "data_sha256": data_sha256}
    if problems:
        return result
    scored = score(style, placed, data, model)
    reference = Fraction(data["styles"][style]["reference"]["J1_exact"])
    result.update({
        "layout_sha256": layout_hash(style, placed), "J1": round(float(scored["J1"]), 9),
        "J1_exact": f"{scored['J1'].numerator}/{scored['J1'].denominator}",
        "reference_J1": round(float(reference), 9),
        "difference_vs_reference_percent": round(float((scored["J1"] - reference) / reference * 100), 6),
        "beats_reference": scored["J1"] < reference,
        "parts": {k: round(v, 6) for k, v in scored["parts"].items()},
        "ergonomics": scored["ergonomics"],
        "held_out": held_out(style, placed, data, model),
    })
    return result


# --- output ----------------------------------------------------------------------

def show(symbol: str) -> str:
    """Vowel signs and other marks drawn on a dotted circle (া → ◌া)."""
    return DOTTED_CIRCLE + symbol if symbol and unicodedata.category(symbol[0]) in ("Mn", "Mc") else symbol


def grid(style: str, placed: dict[str, tuple[str, str]], data: dict) -> str:
    where = {slot: symbol for symbol, slot in placed.items()}
    lines = []
    for row in ROWS:
        lines.append("        " + "  ".join(f"{k:<3}" for k in row))
        for layer in ("shift", "base"):
            lines.append(f"{layer:<6}  " + "  ".join(f"{show(where.get((k, layer), '')):<3}" for k in row))
        lines.append("")
    return "\n".join(lines)


def print_result(r: dict, data: dict) -> None:
    title = f"{r['name']} " if r["name"] else ""
    if not r["valid"]:
        print(f"{title}INVALID layout (style {r['style'] or '?'}):")
        for p in r["problems"]:
            print(f"  - {p}")
        return
    print(f"{title}style {r['style']}: J1 = {r['J1']:.6f}   (reference {r['reference_J1']:.6f}, "
          f"{r['difference_vs_reference_percent']:+.4f} %)")
    print("  " + ("BEATS the Bangla-DH reference" if r["beats_reference"] else "does not beat the Bangla-DH reference"))
    print("  parts: " + ", ".join(f"{k} {v:.4f}" for k, v in r["parts"].items()))
    e = r["ergonomics"]
    print(f"  same-finger bigrams {e['same-finger bigrams (% of key pairs)']:.2f} % of key pairs, "
          f"Shift {e['Shift presses (% of keystrokes)']:.2f} % of keystrokes, "
          f"hands {e['left / right hand (%)'][0]:.1f} / {e['left / right hand (%)'][1]:.1f} %")
    print("  rows: " + ", ".join(f"{k} {v:.1f} %" for k, v in e["rows (% of keystrokes)"].items()))
    print("  fingers: " + ", ".join(f"{k} {v:.1f} %" for k, v in e["fingers (% of keystrokes)"].items()))
    h = r["held_out"]
    print("  held-out J1: " + ", ".join(f"{k} {v:.4f}" for k, v in h["J1"].items()) + f"; average {h['average']:.4f}")
    ahead = h["ahead_of_you"]
    print(f"  among {h['public_layouts']} public layouts (average held-out J1) you would rank {h['public_rank']}"
          + (f"; ahead of you: {', '.join(ahead)}" if ahead else ": first"))
    print(f"  layout id {r['layout_sha256'][:16]}…, data {r['data_version']} ({r['data_sha256'][:12]}…)")


def print_public(data: dict) -> None:
    board = data["public_layouts"]
    print(board["metric"] + "\n" + board["note"] + "\n")
    columns = ["wikipedia", "newspaper", "unseenNews"]
    print(f"  {'#':>2}  {'layout':<22}" + "".join(f"{c:>12}" for c in columns) + f"{'average':>10}")
    for rank, e in enumerate(sorted(board["entries"], key=lambda e: e["average"]), 1):
        print(f"  {rank:>2}  {e['name']:<22}" + "".join(f"{e['j1'][c]:>12.4f}" for c in columns) + f"{e['average']:>10.4f}")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Score a Bangla keyboard layout against Bangla-DH (styles A, D).")
    parser.add_argument("layouts", nargs="*", help="layout JSON files to score")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    parser.add_argument("--reference", action="store_true", help="show the reference layouts, scores and fixed keys")
    parser.add_argument("--public", action="store_true", help="list the public layouts and their held-out scores")
    parser.add_argument("--template", choices=["A", "D"], help="write a style's reference layout as a starting file")
    parser.add_argument("--out", help="file for --template (default <style>-layout.json)")
    parser.add_argument("--dump-data", metavar="FILE", help="write the embedded data (key model, counts) as JSON")
    args = parser.parse_args(argv)
    data, data_sha256 = load_data()
    if args.dump_data:
        Path(args.dump_data).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {args.dump_data} (sha256 {data_sha256})")
        return 0
    if args.public:
        print_public(data)
        return 0
    if args.template:
        ref = data["styles"][args.template]["reference"]
        out = Path(args.out or f"{args.template}-layout.json")
        body = {"style": args.template, "name": "my layout", "layout": ref["layout"]}
        text = "{\n" + f'  "style": "{args.template}",\n  "name": "my layout",\n  "layout": {{\n'
        text += ",\n".join(f'    "{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in body["layout"].items())
        out.write_text(text + "\n  }\n}\n", encoding="utf-8")
        print(f"wrote {out}: the style {args.template} reference layout, as [base, shift] per key. Edit and score it.")
        return 0
    if args.reference or not args.layouts:
        print(f"Bangla-DH layout challenge, scorer {SCRIPT_VERSION}, data {data['version']} (sha256 {data_sha256})")
        print(data["objective"]["description"] + "\n")
        for style, spec in data["styles"].items():
            ref = spec["reference"]
            _, placed, _ = parse_layout({"style": style, "layout": ref["layout"]}, data)
            print(f"Style {style}: {spec['description']}")
            print(f"Reference: {ref['name']}, J1 = {float(Fraction(ref['J1_exact'])):.6f}\n")
            print(grid(style, placed, data))
            print("Symbols to place: " + " ".join(show(s) for s in sorted(spec["symbols"])))
            print("Fixed keys: " + ", ".join(f"{s} {k}/{l}" for s, (k, l) in spec["fixed"].items()) + "\n")
        if not args.layouts:
            print("Score a layout: python bangla_dh_challenge.py my-layout.json "
                  "(start with --template A or --template D).")
        return 0
    model = Model(data)
    results = []
    for path in args.layouts:
        try:
            submission = read_layout_file(path)
        except (OSError, ValueError) as error:
            results.append({"file": path, "valid": False, "problems": [str(error)], "name": "", "style": ""})
            continue
        result = evaluate(submission, data, data_sha256, model)
        result["file"] = path
        results.append(result)
    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=1))
    else:
        for r in results:
            if not r.get("name"):
                r["name"] = r["file"]
            print_result(r, data)
            print()
        valid = sorted((r for r in results if r["valid"]), key=lambda r: (r["style"], r["J1"]))
        if len(valid) > 1:
            print("Ranking (lower is better):")
            for r in valid:
                print(f"  {r['style']}  {r['J1']:.6f}  {r['name']}")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
