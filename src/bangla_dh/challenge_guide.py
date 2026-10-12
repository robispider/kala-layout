"""The challenge kit's public texts: ``README.md`` (landing page) and
``USER_GUIDE.md`` (for challengers). Built from the embedded data by
``challenge-kit`` so every number, symbol list and key table matches the
script."""
from __future__ import annotations

import unicodedata
from fractions import Fraction

ROWS = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
FINGERS = {0: "L pinky", 1: "L ring", 2: "L middle", 3: "L index",
           6: "R index", 7: "R middle", 8: "R ring", 9: "R pinky"}
FINGER_SHORT = {0: "LP", 1: "LR", 2: "LM", 3: "LI", 6: "RI", 7: "RM", 8: "RR", 9: "RP"}
# How each style types a few words (key labels pressed), from the Phase 3 report.
EXAMPLES = {
    "A": [("আমি", "◌্ ◌া ম ◌ি"), ("বই", "ব ◌্ ◌ি"), ("কাজ", "ক ◌া জ"), ("এই", "◌্ ◌ে ◌্ ◌ি"),
          ("প্রতিষ্ঠান", "প ◌্ র ত ◌ি ষ ◌্ ঠ ◌া ন")],
    "D": [("আমি", "◌া ম ◌ি"), ("বই", "ব ◌ি ◌ি"), ("কাজ", "ক ◌া জ"), ("এই", "◌ে ◌ি"),
          ("তিনিই", "ত ◌ি ন ◌ি ◌ি ◌ি"), ("প্রতিষ্ঠান", "প ◌্ র ত ◌ি ষ ◌্ ঠ ◌া ন")],
}
STYLE_TEXT = {
    "A": "UniJoy-style. Vowel signs have their own keys; an independent vowel is typed as ্ followed by its "
         "sign (্ + া = আ).",
    "D": "Context. One key per vowel: after a consonant it gives the vowel sign, elsewhere the independent "
         "vowel. Pressing the same vowel key again right after a sign turns it into the independent vowel "
         "(ব ি ি = বই); a longer run pairs from the end (three presses after a consonant = sign + "
         "independent vowel, as in তিনিই).",
}


def show(symbol: str) -> str:
    return "◌" + symbol if symbol and unicodedata.category(symbol[0]) in ("Mn", "Mc") else symbol


def _cell(symbol: str) -> str:
    return show(symbol).replace("|", "\\|") or " "


def reference_tables(layout: dict[str, list[str]]) -> list[str]:
    out = []
    for row in ROWS:
        out.append("| | " + " | ".join(row) + " |")
        out.append("| --- |" + " --- |" * len(row))
        out.append("| Shift | " + " | ".join(_cell(layout[k][1]) for k in row) + " |")
        out.append("| base | " + " | ".join(_cell(layout[k][0]) for k in row) + " |")
        out.append("")
    return out


def effort_tables(data: dict) -> list[str]:
    keys = data["model"]["keys"]
    out = []
    for row in ROWS:
        out.append("| | " + " | ".join(row) + " |")
        out.append("| --- |" + " --- |" * len(row))
        out.append("| effort | " + " | ".join(f"{float(keys[k][0]):.2f}" for k in row) + " |")
        out.append("| finger | " + " | ".join(FINGER_SHORT[keys[k][1]] for k in row) + " |")
        out.append("")
    return out


def symbol_shares(data: dict, style: str) -> list[tuple[str, float]]:
    """Share of keystrokes per symbol of the style, weighted like J1."""
    spec = data["styles"][style]
    weights = {n: float(Fraction(w)) for n, w in data["objective"]["weights"].items()}
    share: dict[str, float] = {}
    for name, corpus in spec["corpora"].items():
        total = sum(corpus["labels"].values())
        for symbol, count in corpus["labels"].items():
            if symbol in spec["symbols"]:
                share[symbol] = share.get(symbol, 0.0) + weights[name] * count / total
    return sorted(share.items(), key=lambda kv: (-kv[1], kv[0]))


def reference_score(data: dict, style: str) -> float:
    return float(Fraction(data["styles"][style]["reference"]["J1_exact"]))


REPOSITORY = "https://github.com/robispider/kala-layout (submissions/ folder and docs/CHALLENGE.md)"


def readme(data: dict, data_sha256: str, leaderboard: str | None) -> str:
    board = f"Leaderboard and submissions: {leaderboard or REPOSITORY}"
    return f"""# Bangla-DH layout challenge

Can you place the Bangla letters on a keyboard better than Bangla-DH?

| Style | Score to beat (J1, lower is better) |
| --- | --- |
| A (UniJoy-style vowels) | {reference_score(data, 'A'):.6f} |
| D (context vowels) | {reference_score(data, 'D'):.6f} |

```bash
python bangla_dh_challenge.py --reference
python bangla_dh_challenge.py --template D --out my-layout.json
python bangla_dh_challenge.py my-layout.json
```

Python 3.10 or newer, nothing else. Read the **[user guide](USER_GUIDE.md)**
for the rules, the file format, how the score works and tips.

{board}

Files: `bangla_dh_challenge.py` (the scorer), `USER_GUIDE.md`,
`A-reference.json` and `D-reference.json` (the layouts to beat, as example
files). Data `{data['version']}`, SHA-256 `{data_sha256}`.
"""


def user_guide(data: dict, data_sha256: str, script_version: str, leaderboard: str | None) -> str:
    weights = data["objective"]["weights"]
    shift = data["model"]["shift_keys"]
    sf = [float(x) for x in data["model"]["same_finger"]]
    nb = [[float(x) for x in row] for row in data["model"]["neighbour_by_outer_finger"]]
    L: list[str] = []
    w = L.append
    w("# Bangla-DH layout challenge: user guide")
    w("")
    w("Bangla-DH is a Bangla keyboard layout designed by computer search with the ergonomic model of "
      "Colemak Mod-DH. This challenge asks: **can you find a layout with a lower effort score than ours?** "
      "You get one script that scores any layout in a fraction of a second and tells you whether it beats "
      "the Bangla-DH layout.")
    w("")
    w(f"Scorer version {script_version}, data `{data['version']}` (SHA-256 `{data_sha256}`).")
    w("")
    w("## Contents")
    w("")
    for i, title in enumerate(("What you need", "Quick start", "The two styles", "Rules", "The layout file",
                               "Reading your result", "How the score works", "Tips for a better layout",
                               "Using the scorer from your own code", "Submitting", "FAQ"), 1):
        w(f"{i}. [{title}](#{i}-{title.lower().replace(' ', '-')})")
    w("")
    w("## 1. What you need")
    w("")
    w("* Python 3.10 or newer (`python --version`). Nothing to install; no internet needed.")
    w("* `bangla_dh_challenge.py` from this kit.")
    w("* A text editor that saves UTF-8 (Notepad, VS Code, …) and a way to type Bangla, or copy and paste.")
    w("")
    w("## 2. Quick start")
    w("")
    w("```bash")
    w("python bangla_dh_challenge.py --reference")
    w("```")
    w("")
    w("shows both layouts to beat, their scores, the symbols each style places and the fixed keys.")
    w("")
    w("```bash")
    w("python bangla_dh_challenge.py --template D --out my-layout.json")
    w("```")
    w("")
    w("writes the style D reference layout to `my-layout.json`. Open it, move symbols between keys and save.")
    w("")
    w("```bash")
    w("python bangla_dh_challenge.py my-layout.json")
    w("```")
    w("")
    w("scores it. Several files at once are ranked:")
    w("")
    w("```bash")
    w("python bangla_dh_challenge.py try1.json try2.json try3.json")
    w("```")
    w("")
    w("On Windows use `py` instead of `python` if `python` is not found. Write files with `--out` rather "
      "than `>`: PowerShell's `>` writes UTF-16 (the scorer reads it, but other tools may not).")
    w("")
    w("## 3. The two styles")
    w("")
    w("A style is the rule for typing vowels. It fixes which 52 symbols get keys and how many presses "
      "each word needs; you only decide where the symbols go. Each style has its own score to beat.")
    w("")
    w("| Style | Score to beat (J1) |")
    w("| --- | --- |")
    for style in ("A", "D"):
        w(f"| {style} | {reference_score(data, style):.6f} |")
    w("")
    for style in ("A", "D"):
        spec = data["styles"][style]
        w(f"### Style {style}")
        w("")
        w(STYLE_TEXT[style])
        w("")
        w("| Word | Keys pressed |")
        w("| --- | --- |")
        for word, keys in EXAMPLES[style]:
            w(f"| {word} | {keys} |")
        w("")
        w(f"Symbols to place (52): {' '.join(show(s) for s in sorted(spec['symbols']))}")
        w("")
        w(f"The layout to beat ({spec['reference']['name']}):")
        w("")
        L.extend(reference_tables(spec["reference"]["layout"]))
    w("## 4. Rules")
    w("")
    w("1. Choose style A or D.")
    w("2. Place exactly the style's 52 symbols, each once, on the 26 letter keys Q … M: one on the base "
      "layer and one on the Shift layer of every key.")
    w("3. Digits and punctuation are fixed and cannot move: "
      + ", ".join(f"{s} on {k}{' (Shift)' if l == 'shift' else ''}"
                  for s, (k, l) in data["styles"]["A"]["fixed"].items()) + ".")
    w("4. Lower J1 is better. A layout beats another only with a **strictly lower** score. Scores are exact "
      "fractions (`J1_exact`), so there is no rounding and a tie is a real tie.")
    w("5. The keyboard is a standard ANSI (US) keyboard with the finger assignment shown in section 7. "
      "Conjunct keys, a third layer and moving the digits are not part of this challenge.")
    w("")
    w("## 5. The layout file")
    w("")
    w("```json")
    w("{")
    w('  "style": "D",')
    w('  "name": "your name or a name for the layout",')
    w('  "layout": {')
    ref = data["styles"]["D"]["reference"]["layout"]
    w(f'    "Q": ["{ref["Q"][0]}", "{ref["Q"][1]}"],')
    w(f'    "W": ["{ref["W"][0]}", "{ref["W"][1]}"],')
    w('    "…": ["base symbol", "Shift symbol"],')
    w(f'    "M": ["{ref["M"][0]}", "{ref["M"][1]}"]')
    w("  }")
    w("}")
    w("```")
    w("")
    w("* All 26 keys Q … M, each with `[base, Shift]`. `{\"base\": …, \"shift\": …}` also works.")
    w("* Vowel signs may be written with or without the dotted circle: `◌া` and `া` are the same.")
    w("* ড় ঢ় য় may be typed as one character or as letter + nukta; both are accepted.")
    w("* Save as UTF-8. Key names are not case-sensitive.")
    w("* If something is wrong the scorer says what: a symbol placed twice, a symbol missing, a symbol that "
      "is not in the style, a key missing.")
    w("")
    w("## 6. Reading your result")
    w("")
    w("```text")
    w("my layout style D: J1 = 1.808796   (reference 1.808796, +0.0000 %)")
    w("  does not beat the Bangla-DH reference")
    w("  parts: E1 (key effort) 1.4936, M (Shift) 0.2779, same finger 0.0496, neighbour penalty 0.0080, "
      "neighbour benefit -0.0203")
    w("  same-finger bigrams 2.38 % of key pairs, Shift 8.77 % of keystrokes, hands 54.5 / 45.5 %")
    w("  rows: number 1.8 %, top 21.8 %, home 54.7 %, bottom 21.7 %")
    w("  fingers: left pinky 5.8 %, left ring 9.4 %, …")
    w("  held-out J1: unseenNews 1.7830, wikipedia 1.8348, newspaper 1.7822; average 1.8000")
    w("  among 8 public layouts (average held-out J1) you would rank 1: first")
    w(f"  layout id 5642cc695d29dd6a…, data {data['version']} ({data_sha256[:12]}…)")
    w("```")
    w("")
    w("| Line | Meaning |")
    w("| --- | --- |")
    w("| J1 | The score: effort per character typed. Lower is better. The percentage compares it with the "
      "reference (negative = better). |")
    w("| E1 (key effort) | Effort of the keys pressed (section 7). |")
    w("| M (Shift) | Effort of the Shift presses for Shift-layer symbols. |")
    w("| same finger | Penalty for two keys in a row on the same finger. |")
    w("| neighbour penalty / benefit | Penalty for awkward neighbouring-finger pairs, bonus (negative) for "
      "middle-to-index rolls. |")
    w("| same-finger bigrams … | Not part of the score; ergonomic facts about the layout to help you "
      "improve it. |")
    w("| held-out J1 | Not part of the win condition. Your layout typed on three texts no search has seen "
      "(Wikipedia and newspaper articles held out, and BARD news articles unseen by any search), and its "
      "place by average among Kala Jhor, Kala Goti and the public fixed layouts. A real improvement should "
      "be lower here too. |")
    w("| layout id | A fingerprint of the layout: the same layout always gets the same id. |")
    w("")
    w("J1 is the sum of the five parts. `--json` prints all of it for programs, including the exact "
      "fraction `J1_exact`.")
    w("")
    w("## 7. How the score works")
    w("")
    w("The scorer types two training texts in the chosen style: Bangla Wikipedia and newspaper text, "
      + " and ".join(f"weight {v}" for v in weights.values()) + ". For each text it adds up:")
    w("")
    w("* **Key effort** of every keystroke, from the table below (Colemak Mod-DH model, ANSI keyboard; "
      "home row cheapest, stretches and little fingers dearer).")
    w(f"* **Shift**: a Shift-layer symbol also costs a press of the other hand's Shift key "
      f"(left-hand keys use right Shift, {float(shift['RSHIFT']):.2f}; right-hand keys use left Shift, "
      f"{float(shift['LSHIFT']):.2f}).")
    w(f"* **Same finger** twice in a row (two different keys, or base and Shift of one key): "
      f"{sf[0]:g} on the same row, {sf[1]:g} one row apart, {sf[2]:g} two or more rows apart.")
    w(f"* **Neighbouring fingers** of one hand, by the outer finger of the pair and row distance 0 / 1 / 2: "
      f"pinky–ring {' / '.join(f'{x:g}' for x in nb[0])}, ring–middle {' / '.join(f'{x:g}' for x in nb[1])}, "
      f"middle–index {' / '.join(f'{x:g}' for x in nb[2])} (negative = a bonus).")
    w("* Space is pressed by the thumb and costs nothing; pressing the same key twice costs no penalty.")
    w("")
    w("The total is divided by the number of characters in the text, and the two texts are averaged:")
    w("")
    w("```text")
    w("J1 = " + " + ".join(f"{v} × J({n})" for n, v in weights.items()))
    w("J(text) = (Σ key effort + Σ Shift + Σ pair penalties) / characters in the text")
    w("```")
    w("")
    w("Key effort and finger (LP = left pinky … RI = right index … RP = right pinky). The bottom row uses "
      "the angle-mod fingering, so B, N and M are right-index keys:")
    w("")
    L.extend(effort_tables(data))
    w("The keystroke and pair counts are fixed per style (they come from typing the texts in that style) "
      "and are built into the script; `--dump-data data.json` writes them out. They are counts only; the "
      "texts themselves are not included.")
    w("")
    w("## 8. Tips for a better layout")
    w("")
    w("* Most-typed symbols of each style (share of keystrokes, weighted like J1):")
    w("")
    w("| Style | Top 12 symbols |")
    w("| --- | --- |")
    for style in ("A", "D"):
        top = symbol_shares(data, style)[:12]
        w(f"| {style} | " + ", ".join(f"{show(s)} {p * 100:.1f} %" for s, p in top) + " |")
    w("")
    w("* Frequent symbols belong on the cheapest keys (F J D K S L A) and on the base layer.")
    w("* Shift is expensive: the reference layouts already shift only about 9 % of keystrokes.")
    w("* Avoid putting symbols that often follow each other on the same finger.")
    w("* Small changes matter: try swapping two keys and re-scoring. Swaps between base and Shift count too.")
    w("* For serious attempts, write a search program (simulated annealing, local search) around the "
      "scorer (section 9).")
    w("* Our layouts are the best of 512 searches per style, so expect improvements to be small.")
    w("")
    w("## 9. Using the scorer from your own code")
    w("")
    w("Put your script next to `bangla_dh_challenge.py`:")
    w("")
    w("```python")
    w("import json")
    w("import bangla_dh_challenge as ch")
    w("")
    w("data, data_sha256 = ch.load_data()")
    w("model = ch.Model(data)")
    w('layout = json.load(open("my-layout.json", encoding="utf-8"))')
    w("result = ch.evaluate(layout, data, data_sha256, model)")
    w('print(result["valid"], result.get("J1"), result.get("beats_reference"))')
    w("```")
    w("")
    w("`evaluate` returns the same fields as `--json`. It takes a few milliseconds; for a search that tries "
      "millions of layouts, read the counts (`--dump-data`) and compute score changes incrementally. The "
      "data file has `model.keys` (key → [effort, finger, row]), `model.shift_keys`, the penalty tables, "
      "and per style `symbols`, `fixed` and `corpora` (per text: `N`, `labels` = keystrokes per symbol, "
      "`pairs` = [first, second, count]). Check your own scorer against `evaluate`.")
    w("")
    w("## 10. Submitting")
    w("")
    if leaderboard:
        where = f"Submit your layout file at {leaderboard}."
    else:
        where = ("Submit your layout file by adding it to the `submissions/` folder of "
                 "https://github.com/robispider/kala-layout in a pull request (see `docs/CHALLENGE.md`).")
    w(where + " The leaderboard re-scores every file itself with this script, so send the JSON layout file, not "
      "a screenshot or a score. Identical layouts count once (the first submission keeps the place). Add "
      '"author" (your GitHub name) next to "name" in the file.')
    w("")
    w("## 11. FAQ")
    w("")
    w("**Does a lower score mean the layout is more comfortable?** It means less effort in this model. The "
      "model is a well-tested approximation; real comfort is measured with typing tests.")
    w("")
    w("**Can I change the typing style, add conjunct keys or move digits?** Not in this challenge: the "
      "style and fixed keys are part of the rules so that scores compare.")
    w("")
    w("**What is the held-out check?** The win condition is the training score, as the search used it. The "
      "held-out line shows the same layout on texts the search never saw. If you beat the reference only on "
      "the training score, the layout may be fitted to the training counts; maintainers check held-out "
      "scores before they credit a win.")
    w("")
    w("**Why two texts?** So a layout is good for both encyclopedic and news Bangla, not tuned to one.")
    w("")
    w("**My score equals the reference.** Then you have found the same layout or an equally good one; "
      "only a strictly lower score beats it.")
    w("")
    w("**The script says my file is not valid JSON.** Check commas and quotes, and save as UTF-8. Start "
      "from `--template` to avoid mistakes.")
    w("")
    w("**Bangla shows as boxes in my terminal.** Use Windows Terminal or another UTF-8 terminal; the "
      "scores are correct either way, and `--json` output can be opened in an editor.")
    w("")
    return "\n".join(L)
