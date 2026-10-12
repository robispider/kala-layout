# Bangla-DH layout challenge: user guide

Bangla-DH is a Bangla keyboard layout designed by computer search with the ergonomic model of Colemak Mod-DH. This challenge asks: **can you find a layout with a lower effort score than ours?** You get one script that scores any layout in a fraction of a second and tells you whether it beats the Bangla-DH layout.

Scorer version 1.1.0, data `bangla-dh-challenge-v1` (SHA-256 `2388d17bd9f375763eff19eac4dc2d4397d62c1f28d574d2597d414febb55b0a`).

## Contents

1. [What you need](#1-what-you-need)
2. [Quick start](#2-quick-start)
3. [The two styles](#3-the-two-styles)
4. [Rules](#4-rules)
5. [The layout file](#5-the-layout-file)
6. [Reading your result](#6-reading-your-result)
7. [How the score works](#7-how-the-score-works)
8. [Tips for a better layout](#8-tips-for-a-better-layout)
9. [Using the scorer from your own code](#9-using-the-scorer-from-your-own-code)
10. [Submitting](#10-submitting)
11. [FAQ](#11-faq)

## 1. What you need

* Python 3.10 or newer (`python --version`). Nothing to install; no internet needed.
* `bangla_dh_challenge.py` from this kit.
* A text editor that saves UTF-8 (Notepad, VS Code, …) and a way to type Bangla, or copy and paste.

## 2. Quick start

```bash
python bangla_dh_challenge.py --reference
```

shows both layouts to beat, their scores, the symbols each style places and the fixed keys.

```bash
python bangla_dh_challenge.py --template D --out my-layout.json
```

writes the style D reference layout to `my-layout.json`. Open it, move symbols between keys and save.

```bash
python bangla_dh_challenge.py my-layout.json
```

scores it. Several files at once are ranked:

```bash
python bangla_dh_challenge.py try1.json try2.json try3.json
```

On Windows use `py` instead of `python` if `python` is not found. Write files with `--out` rather than `>`: PowerShell's `>` writes UTF-16 (the scorer reads it, but other tools may not).

## 3. The two styles

A style is the rule for typing vowels. It fixes which 52 symbols get keys and how many presses each word needs; you only decide where the symbols go. Each style has its own score to beat.

| Style | Score to beat (J1) |
| --- | --- |
| A | 1.849686 |
| D | 1.808796 |

### Style A

UniJoy-style. Vowel signs have their own keys; an independent vowel is typed as ্ followed by its sign (্ + া = আ).

| Word | Keys pressed |
| --- | --- |
| আমি | ◌্ ◌া ম ◌ি |
| বই | ব ◌্ ◌ি |
| কাজ | ক ◌া জ |
| এই | ◌্ ◌ে ◌্ ◌ি |
| প্রতিষ্ঠান | প ◌্ র ত ◌ি ষ ◌্ ঠ ◌া ন |

Symbols to place (52): । ◌ঁ ◌ং ◌ঃ অ ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ড় ঢ ঢ় ণ ত থ দ ধ ন প ফ ব ভ ম য য় র ল শ ষ স হ ◌া ◌ি ◌ী ◌ু ◌ূ ◌ৃ ◌ে ◌ৈ ◌ো ◌ৌ ◌্ ৎ

The layout to beat (Bangla-DH A (mixed search, 10 October 2026)):

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ◌ঃ | ঝ | ঠ | ◌ৈ | ◌ৌ | ঘ | ষ | ড় | ◌ঁ | ঙ |
| base | গ | দ | ল | ◌ো | ◌ী | শ | স | য় | প | হ |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ফ | ণ | খ | অ | ঢ় | ড | চ | ◌ং | ভ |
| base | ব | ন | র | ◌া | । | জ | ক | ◌্ | ◌ে |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঢ | ৎ | ◌ূ | ◌ৃ | ঞ | ধ | থ |
| base | ট | ম | ◌ি | ◌ু | ছ | য | ত |

### Style D

Context. One key per vowel: after a consonant it gives the vowel sign, elsewhere the independent vowel. Pressing the same vowel key again right after a sign turns it into the independent vowel (ব ি ি = বই); a longer run pairs from the end (three presses after a consonant = sign + independent vowel, as in তিনিই).

| Word | Keys pressed |
| --- | --- |
| আমি | ◌া ম ◌ি |
| বই | ব ◌ি ◌ি |
| কাজ | ক ◌া জ |
| এই | ◌ে ◌ি |
| তিনিই | ত ◌ি ন ◌ি ◌ি ◌ি |
| প্রতিষ্ঠান | প ◌্ র ত ◌ি ষ ◌্ ঠ ◌া ন |

Symbols to place (52): । ◌ঁ ◌ং ◌ঃ অ ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ড় ঢ ঢ় ণ ত থ দ ধ ন প ফ ব ভ ম য য় র ল শ ষ স হ ◌া ◌ি ◌ী ◌ু ◌ূ ◌ৃ ◌ে ◌ৈ ◌ো ◌ৌ ◌্ ৎ

The layout to beat (Bangla-DH D (mixed search, 10 October 2026)):

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঢ | ঙ | ঠ | ◌ৈ | ◌ঃ | ঘ | ধ | ◌ং | ণ | ◌ঁ |
| base | ট | দ | ল | ◌ো | । | শ | স | প | য | গ |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ফ | ড় | ষ | ◌ূ | ঢ় | ড | ছ | ভ | অ |
| base | ব | ন | র | ◌া | ◌ী | জ | ক | ◌ে | ◌ি |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ৎ | ঞ | ◌ৃ | ◌ৌ | ঝ | খ | থ |
| base | হ | ম | ◌্ | ◌ু | চ | য় | ত |

## 4. Rules

1. Choose style A or D.
2. Place exactly the style's 52 symbols, each once, on the 26 letter keys Q … M: one on the base layer and one on the Shift layer of every key.
3. Digits and punctuation are fixed and cannot move: ০ on 0, ১ on 1, ২ on 2, ৩ on 3, ৪ on 4, ৫ on 5, ৬ on 6, ৭ on 7, ৮ on 8, ৯ on 9, , on ,, ; on ;, : on ; (Shift), ' on ', " on ' (Shift), ( on 9 (Shift), ) on 0 (Shift), - on -, ! on 1 (Shift), ? on / (Shift).
4. Lower J1 is better. A layout beats another only with a **strictly lower** score. Scores are exact fractions (`J1_exact`), so there is no rounding and a tie is a real tie.
5. The keyboard is a standard ANSI (US) keyboard with the finger assignment shown in section 7. Conjunct keys, a third layer and moving the digits are not part of this challenge.

## 5. The layout file

```json
{
  "style": "D",
  "name": "your name or a name for the layout",
  "layout": {
    "Q": ["ট", "ঢ"],
    "W": ["দ", "ঙ"],
    "…": ["base symbol", "Shift symbol"],
    "M": ["ত", "থ"]
  }
}
```

* All 26 keys Q … M, each with `[base, Shift]`. `{"base": …, "shift": …}` also works.
* Vowel signs may be written with or without the dotted circle: `◌া` and `া` are the same.
* ড় ঢ় য় may be typed as one character or as letter + nukta; both are accepted.
* Save as UTF-8. Key names are not case-sensitive.
* If something is wrong the scorer says what: a symbol placed twice, a symbol missing, a symbol that is not in the style, a key missing.

## 6. Reading your result

```text
my layout style D: J1 = 1.808796   (reference 1.808796, +0.0000 %)
  does not beat the Bangla-DH reference
  parts: E1 (key effort) 1.4936, M (Shift) 0.2779, same finger 0.0496, neighbour penalty 0.0080, neighbour benefit -0.0203
  same-finger bigrams 2.38 % of key pairs, Shift 8.77 % of keystrokes, hands 54.5 / 45.5 %
  rows: number 1.8 %, top 21.8 %, home 54.7 %, bottom 21.7 %
  fingers: left pinky 5.8 %, left ring 9.4 %, …
  held-out J1: unseenNews 1.7830, wikipedia 1.8348, newspaper 1.7822; average 1.8000
  among 8 public layouts (average held-out J1) you would rank 1: first
  layout id 5642cc695d29dd6a…, data bangla-dh-challenge-v1 (2388d17bd9f3…)
```

| Line | Meaning |
| --- | --- |
| J1 | The score: effort per character typed. Lower is better. The percentage compares it with the reference (negative = better). |
| E1 (key effort) | Effort of the keys pressed (section 7). |
| M (Shift) | Effort of the Shift presses for Shift-layer symbols. |
| same finger | Penalty for two keys in a row on the same finger. |
| neighbour penalty / benefit | Penalty for awkward neighbouring-finger pairs, bonus (negative) for middle-to-index rolls. |
| same-finger bigrams … | Not part of the score; ergonomic facts about the layout to help you improve it. |
| held-out J1 | Not part of the win condition. Your layout typed on three texts no search has seen (Wikipedia and newspaper articles held out, and BARD news articles unseen by any search), and its place by average among Kala Jhor, Kala Goti and the public fixed layouts. A real improvement should be lower here too. |
| layout id | A fingerprint of the layout: the same layout always gets the same id. |

J1 is the sum of the five parts. `--json` prints all of it for programs, including the exact fraction `J1_exact`.

## 7. How the score works

The scorer types two training texts in the chosen style: Bangla Wikipedia and newspaper text, weight 1/2 and weight 1/2. For each text it adds up:

* **Key effort** of every keystroke, from the table below (Colemak Mod-DH model, ANSI keyboard; home row cheapest, stretches and little fingers dearer).
* **Shift**: a Shift-layer symbol also costs a press of the other hand's Shift key (left-hand keys use right Shift, 4.61; right-hand keys use left Shift, 3.31).
* **Same finger** twice in a row (two different keys, or base and Shift of one key): 2.5 on the same row, 3 one row apart, 4 two or more rows apart.
* **Neighbouring fingers** of one hand, by the outer finger of the pair and row distance 0 / 1 / 2: pinky–ring 0.5 / 1 / 1.5, ring–middle 0.1 / 0.2 / 0.3, middle–index -0.2 / -0.1 / 0 (negative = a bonus).
* Space is pressed by the thumb and costs nothing; pressing the same key twice costs no penalty.

The total is divided by the number of characters in the text, and the two texts are averaged:

```text
J1 = 1/2 × J(bnwiki/train) + 1/2 × J(newspaper/train)
J(text) = (Σ key effort + Σ Shift + Σ pair penalties) / characters in the text
```

Key effort and finger (LP = left pinky … RI = right index … RP = right pinky). The bottom row uses the angle-mod fingering, so B, N and M are right-index keys:

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| effort | 3.02 | 2.50 | 2.10 | 2.30 | 2.61 | 3.36 | 2.22 | 2.00 | 2.43 | 2.97 |
| finger | LP | LR | LM | LI | LI | RI | RI | RM | RR | RP |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| effort | 1.60 | 1.30 | 1.10 | 1.00 | 2.89 | 2.89 | 1.00 | 1.10 | 1.30 |
| finger | LP | LR | LM | LI | LI | RI | RI | RM | RR |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| effort | 2.69 | 2.38 | 1.83 | 2.24 | 3.75 | 2.24 | 1.83 |
| finger | LR | LM | LI | LI | RI | RI | RI |

The keystroke and pair counts are fixed per style (they come from typing the texts in that style) and are built into the script; `--dump-data data.json` writes them out. They are counts only; the texts themselves are not included.

## 8. Tips for a better layout

* Most-typed symbols of each style (share of keystrokes, weighted like J1):

| Style | Top 12 symbols |
| --- | --- |
| A | ◌্ 10.3 %, ◌া 10.0 %, ◌ে 8.6 %, র 8.1 %, ◌ি 6.6 %, ন 4.9 %, ক 4.2 %, ব 3.5 %, ত 3.4 %, স 3.0 %, ল 2.8 %, ম 2.6 % |
| D | ◌া 10.4 %, ◌ে 8.9 %, র 8.4 %, ◌ি 6.9 %, ◌্ 6.6 %, ন 5.1 %, ক 4.4 %, ব 3.6 %, ত 3.6 %, স 3.1 %, ল 2.9 %, ম 2.7 % |

* Frequent symbols belong on the cheapest keys (F J D K S L A) and on the base layer.
* Shift is expensive: the reference layouts already shift only about 9 % of keystrokes.
* Avoid putting symbols that often follow each other on the same finger.
* Small changes matter: try swapping two keys and re-scoring. Swaps between base and Shift count too.
* For serious attempts, write a search program (simulated annealing, local search) around the scorer (section 9).
* Our layouts are the best of 512 searches per style, so expect improvements to be small.

## 9. Using the scorer from your own code

Put your script next to `bangla_dh_challenge.py`:

```python
import json
import bangla_dh_challenge as ch

data, data_sha256 = ch.load_data()
model = ch.Model(data)
layout = json.load(open("my-layout.json", encoding="utf-8"))
result = ch.evaluate(layout, data, data_sha256, model)
print(result["valid"], result.get("J1"), result.get("beats_reference"))
```

`evaluate` returns the same fields as `--json`. It takes a few milliseconds; for a search that tries millions of layouts, read the counts (`--dump-data`) and compute score changes incrementally. The data file has `model.keys` (key → [effort, finger, row]), `model.shift_keys`, the penalty tables, and per style `symbols`, `fixed` and `corpora` (per text: `N`, `labels` = keystrokes per symbol, `pairs` = [first, second, count]). Check your own scorer against `evaluate`.

## 10. Submitting

Submit your layout file by adding it to the `submissions/` folder of https://github.com/robispider/kala-layout in a pull request (see `docs/CHALLENGE.md`). The leaderboard re-scores every file itself with this script, so send the JSON layout file, not a screenshot or a score. Identical layouts count once (the first submission keeps the place). Add "author" (your GitHub name) next to "name" in the file.

## 11. FAQ

**Does a lower score mean the layout is more comfortable?** It means less effort in this model. The model is a well-tested approximation; real comfort is measured with typing tests.

**Can I change the typing style, add conjunct keys or move digits?** Not in this challenge: the style and fixed keys are part of the rules so that scores compare.

**What is the held-out check?** The win condition is the training score, as the search used it. The held-out line shows the same layout on texts the search never saw. If you beat the reference only on the training score, the layout may be fitted to the training counts; maintainers check held-out scores before they credit a win.

**Why two texts?** So a layout is good for both encyclopedic and news Bangla, not tuned to one.

**My score equals the reference.** Then you have found the same layout or an equally good one; only a strictly lower score beats it.

**The script says my file is not valid JSON.** Check commas and quotes, and save as UTF-8. Start from `--template` to avoid mistakes.

**Bangla shows as boxes in my terminal.** Use Windows Terminal or another UTF-8 terminal; the scores are correct either way, and `--json` output can be opened in an editor.
