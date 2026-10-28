# From separate arrangements to one shared map

The current provisional result is one B01 arrangement with Goti (A) and Jhor (D) typing styles. The positions are shared; the vowel-entry recipes differ. [Why the transition?](SHARED_LAYOUT.md) explains the practical rationale and mechanical costs; [current maps](LAYOUTS.md) and the [publication report](../results/shared-publication-v1/REPORT.md) carry the new results.

## The shared-layout stage (28 October 2026)

After the original effort searches, movement/order diagnostics and Balance comparisons examined trade-offs. Cross-scoring existing maps showed that none of five tested originals/Balance leaders qualified under the strict policy in both styles. A dedicated shared search first used strict limits, then a separately recorded relaxed +0.75% effort/+7.5% within-word policy. Its four-billion run retained B01 and B02 as two leading trade-offs; the enhanced pilot did not improve that frontier. B01 was selected provisionally for one remembered arrangement, not because it beats the separate designs mechanically. All style-specific calibration remains frozen. [The comparison](../results/shared-top10-comparison-v1/REPORT.md) preserves the evidence and limitations.

## Historical original separate-arrangement research

The account and numeric tables below describe the original season. They do not describe B01's map, search budget or current scores. The old Phase 4 certificates apply only to their stated Wikipedia-trained problems; none certifies the shared publication.


Kala Jhor (কালা ঝড়) and Kala Goti (কালা গতি) were found by a computer search, not drawn by hand. This page explains the chain from the texts to the two layouts, what each step checks, and what the results do and do not claim. Every step can be repeated with the commands in [REPRODUCE.md](REPRODUCE.md).

## The idea in one paragraph

We wrote down how tiring a Bangla keystroke is (which key, which finger, which Shift, which finger pairs) and measured how often each Bangla symbol and symbol pair occurs in large Bangla texts. Then a search tried hundreds of millions of ways to place 52 Bangla symbols on the 26 letter keys, base and Shift, and kept the placement with the lowest total modeled effort per typed character. The best placement for each of two vowel-entry styles became Kala Jhor and Kala Goti.

## The steps

1. **The effort model.** We start from the Colemak Mod-DH analyzer: a cost for every key (home row cheapest, reaches and the little finger dearer), a penalty when one finger presses two keys in a row (2.5, 3.0 or 4.0 by row distance), a small penalty or a bonus for neighbouring fingers, and a cost for Shift that depends on the hand. Space is the thumb and is free. First we reproduced the published Colemak Mod-DH results exactly, then reused that model unchanged. See [colemak-model-spec.md](colemak-model-spec.md) and [results/phase1/REPORT.md](../results/phase1/REPORT.md).
2. **The Bangla symbols.** Bangla text is Unicode, and one drawn letter can be several code points. We built an inventory of 85 symbols from Kala's alphabet, validated against Unicode, and a typing grammar that turns any Bangla word into a stream of key labels and back. See [results/phase2/REPORT.md](../results/phase2/REPORT.md).
3. **The texts.** Bangla Wikipedia, a Bangla newspaper collection and BARD news articles, all from the public [ban-dataset-collection](https://github.com/robispider/ban-dataset-collection). Documents are split 90/10 into training and held-out text. The search sees only training text; every score that is reported as held-out comes from text it never saw. See [DATASETS.md](DATASETS.md).
4. **Four ways to type vowels.** Where the vowel signs and full vowels go changes how many keystrokes a word needs, so the research compared four vowel-entry styles on equal terms. Each style is a small typing machine that is checked to reproduce every test word exactly.
5. **The search problem.** The 26 letter keys give 52 slots (base and Shift). Digits and punctuation keep their usual places. Each style places 52 symbols on the 52 slots: 35 consonants, the hasant, three marks, ৎ, the danda and the style's 11 vowel keys. That is 52 factorial, about 8.07 × 10^67, possible layouts.
6. **The search.** Simulated annealing followed by iterated local search, repeated from 512 different random starts per style (1,000,000 moves each), then polished from the earlier best layouts. The objective is J1: modeled effort per typed character, averaged 50 % Wikipedia and 50 % newspaper training text.
7. **Checks and bounds.** An independent verifier types the texts again and must agree with the fast scorer. For the Wikipedia-trained versions we also computed a certified lower bound: no layout of that problem can score lower than the bound, so the found layout is within 4.0 to 4.3 % of the best possible. The final mixed-text versions were not re-certified.
8. **The choice.** Of the four styles, D (context vowels) scored best, and A keeps UniJoy's familiar recipe for full vowels. The project owner chose A and D for typing tests; both were searched again on the mixed texts and published as Kala Jhor (D) and Kala Goti (A). Style C was proven worse than A, B and D, and B was not carried forward.

## The four vowel-entry styles

| Style | How a full vowel is typed | Keystrokes per non-space unit | Held-out J1 (Wikipedia) |
| --- | --- | --- | --- |
| A | hasant, then the vowel sign (as in UniJoy) | 1.039 | 1.867 |
| B | the sign key twice | 1.038 | 1.880 |
| C | its own vowel key; the sign needs the vowel key twice | 1.267 | 2.153 |
| D | the same key as the sign; Kala picks sign or full vowel from the letter before | 1.002 | 1.834 |

The numbers are from the Wikipedia-trained Phase 3 search ([results/phase3/REPORT.md](../results/phase3/REPORT.md)). UniJoy scores 2.808 on the same text.

## What the results say

Held-out J1 of the final layouts and the other fixed layouts that were installed in Kala (lower is better, effort index UniJoy = 100):

| Layout | Wikipedia | Newspaper | Unseen news | Average | Effort index |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 1.8348 | 1.7822 | 1.7830 | 1.8000 | 64.3 |
| Kala Goti | 1.8689 | 1.8300 | 1.8308 | 1.8432 | 65.9 |
| Windows Default | 2.1435 | 2.1510 | 2.1549 | 2.1498 | 76.8 |
| Probhat | 2.6022 | 2.5337 | 2.5299 | 2.5553 | 91.3 |
| Munir Optima (uni) | 2.5898 | 2.5783 | 2.5885 | 2.5855 | 92.4 |
| Bornona | 2.6534 | 2.5923 | 2.5900 | 2.6119 | 93.4 |
| UniJoy | 2.7976 | 2.7948 | 2.7998 | 2.7974 | 100.0 |
| National (Jatiya) | 2.8913 | 2.8503 | 2.8554 | 2.8657 | 102.4 |

Existing layouts are scored at the better of the model-optimal and the traditional fingering grid, so a Kala win does not depend on the fingering choice. Phonetic layouts such as Avro Phonetic are not compared.

## What the results do not say

* **Modeled effort is not measured speed.** The model is an agreed ergonomic estimate. Whether people type faster or more comfortably on Kala Jhor or Kala Goti is a question for typing tests with people, which are the next research step.
* **Best found is not proven best.** The search reached each final layout from many independent starts, but there is no proof that no better layout exists for the mixed texts. For the Wikipedia-trained versions the proven statement is the 4.0 to 4.3 % gap above.
* **Two layers only.** ZWNJ, ZWJ, ঽ, ॥, the long dash and ৳ have no key yet; text that needs them is typed outside the model.
* **The weights are a judgment.** The Colemak Mod-DH weights come from its author. A sensitivity study varied 1,000 sets of parameters and style D had the lowest J1 in every one, which supports the ranking but does not make the weights true.

## Try to beat it

Two things make this research easy to challenge. The scorer is a single standard-library Python file that anyone can run, and the whole search is repeatable. See [CHALLENGE.md](CHALLENGE.md) for the rules and [REPRODUCE.md](REPRODUCE.md) to run the search yourself.

## Where each step lives

| Step | Report | Code |
| --- | --- | --- |
| Effort model | [results/phase1/REPORT.md](../results/phase1/REPORT.md) | [src/bangla_dh/colemak/](../src/bangla_dh/colemak) |
| Symbols, texts, scorer | [results/phase2/REPORT.md](../results/phase2/REPORT.md) | [src/bangla_dh/bangla/](../src/bangla_dh/bangla) |
| Styles and search | [results/phase3/REPORT.md](../results/phase3/REPORT.md) | [src/bangla_dh/search/](../src/bangla_dh/search) |
| News check | [results/phase3-crosscheck/REPORT.md](../results/phase3-crosscheck/REPORT.md) | [src/bangla_dh/crosscheck.py](../src/bangla_dh/crosscheck.py) |
| Bounds and proofs | [results/phase4/REPORT.md](../results/phase4/REPORT.md) | [src/bangla_dh/phase4.py](../src/bangla_dh/phase4.py) |
| Mixed search (the final layouts) | [results/mix-search/REPORT.md](../results/mix-search/REPORT.md) | [src/bangla_dh/mix.py](../src/bangla_dh/mix.py) |
| Layout files for Kala | [results/kala-keyboards/README.md](../results/kala-keyboards/README.md) | [src/bangla_dh/kala_export.py](../src/bangla_dh/kala_export.py) |
