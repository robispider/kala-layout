# Balance v1: candidate analysis, layout differences and public-layout comparison

**This report compares experimental candidates. It does not replace Kala Goti or Kala Jhor.** The leading eligible saved candidates are A-a280bdc4ca72c6c7 and D-9ad5412603069cd6 under the frozen four-component Balance v1 score. Scores are modeled diagnostics; held-out comparisons are exploratory.

Report 1, MATH_AND_SELECTION.md, gives the complete formula, eligibility, frozen calibration and worked calculations. This report profiles the top five of each style, both published references, and earlier requested trade-offs. Full source/fingering metrics, calibration, rankings and every same-style symbol difference are supplied as CSV/JSON artifacts.

## 1. Reading the measurements

E=J1 effort per text unit; X=cross-space SF different-key distance in key-pitch units per spanning window; W=within-word SF different-key distance per text unit. Lower is better. Engram pair/order and Dvorak-7 are credit: higher is better, with unsupported-event coverage bounds. Shift share counts shifted nonspace actions. Escapes are text units typed outside the movement domain. Repeated physical keys are counted separately from different-key movement.

Training results below use the 50/50 source mix and same-style reference. Held-out averages give each of the three already examined sources one third; counts are not pooled. Fingering scenarios are kept separate. Percentage changes are modeled changes, never typing-speed percentages.

Published reference identifiers: **Kala Goti = A-18fe73cb912ae3f1**, **Kala Jhor = D-e4a6be48881da590**. Rankings remain separate by style. The diagrams show the 26 searched letter keys and both layers; fixed punctuation/digits are omitted from the pictures and retained in scoring.

## 2. Primary training summary

### Style A: Goti / UniJoy-style independent vowels

| Candidate | Eligible rank | R | J1 | E change % | X change % | W change % | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-18fe73cb912ae3f1 | 368 | 0.490656 | 1.849686 | +0.000 | +0.00 | +0.00 | 0.76472–0.77325 |
| A-a280bdc4ca72c6c7 | 1 | 0.072760 | 1.855008 | +0.288 | +18.81 | -14.63 | 0.82298–0.83151 |
| A-36f3428c3f344a54 | 2 | 0.182291 | 1.856545 | +0.371 | -21.15 | -16.74 | 0.76906–0.77759 |
| A-3270b803ada27b63 | 3 | 0.184447 | 1.856569 | +0.372 | -21.18 | -16.85 | 0.76908–0.77760 |
| A-cd1cedf0ef5f7fe3 | 4 | 0.185457 | 1.856581 | +0.373 | -21.17 | -16.97 | 0.76912–0.77765 |
| A-70dc91ce76c7391e | 5 | 0.189786 | 1.856631 | +0.375 | -21.18 | -17.26 | 0.76916–0.77768 |
| A-4dfc1837861ac886 | 376 | 0.491679 | 1.856178 | +0.351 | -25.69 | -0.63 | 0.77966–0.78819 |
| A-7c36e8f26e6c7142 | — | ineligible | 1.912502 | +3.396 | -46.78 | -26.08 | 0.74267–0.75120 |
### Style D: Jhor / context vowels

| Candidate | Eligible rank | R | J1 | E change % | X change % | W change % | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-e4a6be48881da590 | 110 | 0.240274 | 1.808796 | +0.000 | +0.00 | +0.00 | 0.74957–0.75836 |
| D-9ad5412603069cd6 | 1 | 0.139416 | 1.813731 | +0.273 | -12.81 | -8.24 | 0.75915–0.76795 |
| D-eb3bf7d2da4f048e | 2 | 0.161370 | 1.813962 | +0.286 | -12.84 | -8.25 | 0.75915–0.76795 |
| D-a3a1484044fb8d5e | 3 | 0.161653 | 1.813498 | +0.260 | -11.72 | -9.22 | 0.75327–0.76206 |
| D-c4028c28dc54b209 | 4 | 0.164988 | 1.813992 | +0.287 | -11.71 | -9.20 | 0.75327–0.76206 |
| D-f4e1710b3ec62eb8 | 5 | 0.182134 | 1.809815 | +0.056 | -1.06 | -2.19 | 0.75006–0.75885 |
| D-48319b4b30582e8c | 37 | 0.201139 | 1.810300 | +0.083 | -2.64 | -4.95 | 0.74732–0.75611 |
| D-8e3f1abe1434b3ea | 464 | 0.533369 | 1.817834 | +0.500 | -21.38 | +0.16 | 0.76419–0.77299 |
| D-8ed0c088f68ad80a | — | ineligible | 1.826100 | +0.957 | -33.42 | -5.53 | 0.77389–0.78268 |
| D-072c558b633d1019 | — | ineligible | 1.812142 | +0.185 | -15.81 | +6.40 | 0.72705–0.73584 |

The top-five ordering follows R, not one movement metric. A’s leader accepts a cross-space regression for a larger within-word/order improvement. D’s leader improves both primary distances at a small effort cost. The larger cross-space gains of several earlier trade-offs do not automatically produce a lower worst-case balance cost.

## 3. Individual candidate profiles

### A-18fe73cb912ae3f1 — published reference, retained

**Balance v1:** eligible rank 368, R=0.490656484. Primary changes versus its published reference: effort +0.000%, cross distance +0.00%, within distance +0.00%.

Assignment changes versus A-18fe73cb912ae3f1: 0 symbols; 0 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 45 symbols, 45 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 4357 retained records. First record: `{"file": "results/mix-search/search/A.json", "kind": "published", "seed": 20261117}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.287%, X -15.83%, and W +17.14%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.06679, -0.04973]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-21 (weights [6, 1, 1.25, 0.75], rho 0.075), within-word distance is the largest weighted deviation. B+ is 1.374779223, the frozen optimistic calibration cost is 0.884122739, and their shortfall is R=0.490656484. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.000%, X +0.00%, W +0.00%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.531988 | 0.035977 | 0.281720 | 8.502% | 0.469% | 0.0230% | 0.89723–0.90194 | 0.78145–0.78616 |
| traditional | 1.612209 | 0.101058 | 0.282964 | 8.502% | 0.469% | 0.0230% | 0.88979–0.89451 | 0.76924–0.77395 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.869021 | 0.125377 | 0.015885 | 10.028% | 0.012023 | 0.77395–0.78375 |
| bnwiki/train | traditional | 2.028272 | 0.115718 | 0.046548 | 8.906% | 0.031621 | 0.74381–0.75362 |
| newspaper/train | model-optimal | 1.830351 | 0.111204 | 0.019963 | 8.963% | 0.015025 | 0.75550–0.76275 |
| newspaper/train | traditional | 1.964190 | 0.102961 | 0.042055 | 8.080% | 0.029929 | 0.73971–0.74696 |
| bnwiki/heldout | model-optimal | 1.868918 | 0.125620 | 0.015906 | 10.048% | 0.012050 | 0.77307–0.78300 |
| bnwiki/heldout | traditional | 2.028508 | 0.116187 | 0.046645 | 8.942% | 0.031687 | 0.74301–0.75294 |
| newspaper/heldout | model-optimal | 1.830018 | 0.111095 | 0.019894 | 8.957% | 0.014978 | 0.75588–0.76306 |
| newspaper/heldout | traditional | 1.963833 | 0.102930 | 0.042024 | 8.080% | 0.029916 | 0.73999–0.74717 |
| bard-novel/heldout | model-optimal | 1.830752 | 0.111413 | 0.019756 | 8.913% | 0.014890 | 0.75543–0.76234 |
| bard-novel/heldout | traditional | 1.965560 | 0.102816 | 0.041916 | 8.022% | 0.029809 | 0.74064–0.74755 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-18fe73cb912ae3f1.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | O/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | D/shift |
| গ | U+0997 | Q/base | Y/base | Q/base |
| ঙ | U+0999 | P/shift | A/shift | P/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | H/base |
| ঝ | U+099D | W/shift | B/shift | W/shift |
| ঞ | U+099E | B/shift | R/shift | B/shift |
| ট | U+099F | Z/base | T/base | Z/base |
| ঠ | U+09A0 | E/shift | V/shift | E/shift |
| ড | U+09A1 | H/shift | U/shift | H/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ণ | U+09A3 | S/shift | O/shift | S/shift |
| ত | U+09A4 | M/base | A/base | M/base |
| থ | U+09A5 | M/shift | L/shift | M/shift |
| দ | U+09A6 | W/base | O/base | W/base |
| ধ | U+09A7 | N/shift | F/shift | N/shift |
| ন | U+09A8 | S/base | L/base | S/base |
| প | U+09AA | O/base | N/base | O/base |
| ফ | U+09AB | A/shift | H/shift | A/shift |
| ব | U+09AC | A/base | M/base | A/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | X/base |
| য | U+09AF | N/base | R/base | N/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | E/base |
| শ | U+09B6 | Y/base | G/base | Y/base |
| ষ | U+09B7 | U/shift | J/shift | U/shift |
| স | U+09B8 | U/base | C/base | U/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | X/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-a280bdc4ca72c6c7 — experimental candidate

**Balance v1:** eligible rank 1, R=0.072759785. Primary changes versus its published reference: effort +0.288%, cross distance +18.81%, within distance -14.63%.

Assignment changes versus A-18fe73cb912ae3f1: 45 symbols; 45 change physical key; 2 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 0 symbols, 0 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 15 retained records. First record: `{"file": "results/mix-search/search/A.json", "kind": "runs", "seed": 20261164, "origin": null}`. Duplicate appearances and inserted references are not independent rediscoveries.

**What controls its Balance v1 result:** at setting A-19 (weights [6, 1, 1.25, 0.75], rho 0.025), within-word distance is the largest weighted deviation. B+ is 0.868077469, the frozen optimistic calibration cost is 0.795317685, and their shortfall is R=0.072759785. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

**Accepted cross-space cost:** primary X rises 18.81%. Within-word distance changes -14.63%; order-credit lower endpoint changes +0.05826. This states the traded quantities without converting them into human comfort.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.325%, X +29.44%, W -3.52%. Order-credit superiority over the reference survives every observed coverage interval: **yes**. Engram pair superiority survives every interval: **yes**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.538960 | 0.035214 | 0.280833 | 8.541% | 0.638% | 0.0230% | 0.91054–0.91525 | 0.79659–0.80130 |
| traditional | 1.586553 | 0.084814 | 0.281285 | 8.541% | 0.638% | 0.0230% | 0.90212–0.90684 | 0.78476–0.78948 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.875040 | 0.143232 | 0.015326 | 10.777% | 0.011473 | 0.82146–0.83127 |
| bnwiki/train | traditional | 1.978104 | 0.137434 | 0.036466 | 9.776% | 0.026158 | 0.79520–0.80500 |
| newspaper/train | model-optimal | 1.834976 | 0.137844 | 0.015278 | 10.690% | 0.011690 | 0.82450–0.83175 |
| newspaper/train | traditional | 1.927201 | 0.133031 | 0.033183 | 9.670% | 0.024042 | 0.79833–0.80558 |
| bnwiki/heldout | model-optimal | 1.875000 | 0.142993 | 0.015323 | 10.768% | 0.011466 | 0.82149–0.83142 |
| bnwiki/heldout | traditional | 1.977861 | 0.137160 | 0.036397 | 9.761% | 0.026108 | 0.79547–0.80540 |
| newspaper/heldout | model-optimal | 1.834853 | 0.138061 | 0.015273 | 10.704% | 0.011690 | 0.82454–0.83172 |
| newspaper/heldout | traditional | 1.927009 | 0.133229 | 0.033220 | 9.685% | 0.024058 | 0.79836–0.80554 |
| bard-novel/heldout | model-optimal | 1.836516 | 0.137760 | 0.015599 | 10.649% | 0.012003 | 0.82363–0.83054 |
| bard-novel/heldout | traditional | 1.928230 | 0.131756 | 0.033323 | 9.518% | 0.024062 | 0.79768–0.80460 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-a280bdc4ca72c6c7.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | H/base |
| ◌ঁ | U+0981 | O/shift | P/shift | P/shift |
| ◌ং | U+0982 | K/shift | I/shift | I/shift |
| অ | U+0985 | F/shift | D/shift | D/shift |
| খ | U+0996 | D/shift | N/shift | N/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | A/shift |
| চ | U+099A | J/shift | B/base | B/base |
| ছ | U+099B | B/base | K/shift | K/shift |
| জ | U+099C | H/base | Q/base | Q/base |
| ঝ | U+099D | W/shift | B/shift | B/shift |
| ঞ | U+099E | B/shift | R/shift | R/shift |
| ট | U+099F | Z/base | T/base | T/base |
| ঠ | U+09A0 | E/shift | V/shift | V/shift |
| ড | U+09A1 | H/shift | U/shift | U/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | C/shift |
| ঢ | U+09A2 | Z/shift | T/shift | T/shift |
| ণ | U+09A3 | S/shift | O/shift | O/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | L/shift |
| দ | U+09A6 | W/base | O/base | O/base |
| ধ | U+09A7 | N/shift | F/shift | F/shift |
| ন | U+09A8 | S/base | L/base | L/base |
| প | U+09AA | O/base | N/base | N/base |
| ফ | U+09AB | A/shift | H/shift | H/shift |
| ব | U+09AC | A/base | M/base | M/base |
| ভ | U+09AD | L/shift | M/shift | M/shift |
| ম | U+09AE | X/base | U/base | U/base |
| য | U+09AF | N/base | R/base | R/base |
| র | U+09B0 | D/base | F/base | F/base |
| ল | U+09B2 | E/base | V/base | V/base |
| শ | U+09B6 | Y/base | G/base | G/base |
| ষ | U+09B7 | U/shift | J/shift | J/shift |
| স | U+09B8 | U/base | C/base | C/base |
| ◌া | U+09BE | F/base | D/base | D/base |
| ◌ি | U+09BF | C/base | E/base | E/base |
| ◌ী | U+09C0 | T/base | Z/base | Z/base |
| ◌ু | U+09C1 | V/base | X/base | X/base |
| ◌ূ | U+09C2 | C/shift | S/shift | S/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | E/shift |
| ◌ে | U+09C7 | L/base | S/base | S/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | X/shift |
| ◌ো | U+09CB | R/base | W/base | W/base |
| ◌ৌ | U+09CC | T/shift | W/shift | W/shift |
| ৎ | U+09CE | X/shift | Z/shift | Z/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-36f3428c3f344a54 — experimental candidate

**Balance v1:** eligible rank 2, R=0.182291295. Primary changes versus its published reference: effort +0.371%, cross distance -21.15%, within distance -16.74%.

Assignment changes versus A-18fe73cb912ae3f1: 25 symbols; 25 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 44 symbols, 44 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 13 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101320.json", "seed": 2026101320, "archive_index": 35, "direction": 0.25, "start": "published-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.083%, X -33.64%, and W -2.47%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.06245, -0.04539]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.692864030, the frozen optimistic calibration cost is 0.510572735, and their shortfall is R=0.182291295. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +2.200%, X -3.42%, W +25.93%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.544103 | 0.028596 | 0.283845 | 8.502% | 0.470% | 0.0230% | 0.89509–0.89980 | 0.77878–0.78349 |
| traditional | 1.628967 | 0.117481 | 0.284297 | 8.502% | 0.470% | 0.0230% | 0.88413–0.88884 | 0.76366–0.76837 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.875948 | 0.099382 | 0.013801 | 7.607% | 0.010228 | 0.77287–0.78267 |
| bnwiki/train | traditional | 2.054986 | 0.109019 | 0.052183 | 7.806% | 0.034372 | 0.74127–0.75107 |
| newspaper/train | model-optimal | 1.837141 | 0.087151 | 0.016048 | 6.922% | 0.011868 | 0.76526–0.77251 |
| newspaper/train | traditional | 2.006504 | 0.099442 | 0.052961 | 7.438% | 0.035124 | 0.74024–0.74749 |
| bnwiki/heldout | model-optimal | 1.875816 | 0.099884 | 0.013793 | 7.645% | 0.010214 | 0.77248–0.78241 |
| bnwiki/heldout | traditional | 2.055513 | 0.109299 | 0.052479 | 7.827% | 0.034507 | 0.74080–0.75073 |
| newspaper/heldout | model-optimal | 1.836988 | 0.087027 | 0.016042 | 6.918% | 0.011872 | 0.76550–0.77268 |
| newspaper/heldout | traditional | 2.006167 | 0.099236 | 0.052909 | 7.428% | 0.035119 | 0.74050–0.74768 |
| bard-novel/heldout | model-optimal | 1.837762 | 0.087044 | 0.015821 | 6.908% | 0.011688 | 0.76634–0.77325 |
| bard-novel/heldout | traditional | 2.008812 | 0.098876 | 0.052561 | 7.389% | 0.034934 | 0.74261–0.74952 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-36f3428c3f344a54.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | O/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| ◌ঃ | U+0983 | Q/shift | Q/shift | G/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | U/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | E/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | P/base |
| ঝ | U+099D | W/shift | B/shift | B/shift |
| ঞ | U+099E | B/shift | R/shift | X/shift |
| ট | U+099F | Z/base | T/base | Q/base |
| ঠ | U+09A0 | E/shift | V/shift | P/shift |
| ড | U+09A1 | H/shift | U/shift | H/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | Q/shift |
| ণ | U+09A3 | S/shift | O/shift | A/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | M/shift |
| দ | U+09A6 | W/base | O/base | Z/base |
| ধ | U+09A7 | N/shift | F/shift | N/shift |
| ন | U+09A8 | S/base | L/base | E/base |
| প | U+09AA | O/base | N/base | N/base |
| ফ | U+09AB | A/shift | H/shift | S/shift |
| ব | U+09AC | A/base | M/base | S/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | W/base |
| য | U+09AF | N/base | R/base | U/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | X/base |
| শ | U+09B6 | Y/base | G/base | H/base |
| ষ | U+09B7 | U/shift | J/shift | D/shift |
| স | U+09B8 | U/base | C/base | M/base |
| হ | U+09B9 | P/base | P/base | O/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | W/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-3270b803ada27b63 — experimental candidate

**Balance v1:** eligible rank 3, R=0.184446613. Primary changes versus its published reference: effort +0.372%, cross distance -21.18%, within distance -16.85%.

Assignment changes versus A-18fe73cb912ae3f1: 24 symbols; 24 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 44 symbols, 44 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101477.json", "seed": 2026101477, "archive_index": 20, "direction": 0.5, "start": "perturbed-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.084%, X -33.66%, and W -2.61%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.06244, -0.04538]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.695019348, the frozen optimistic calibration cost is 0.510572735, and their shortfall is R=0.184446613. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +2.187%, X -3.37%, W +25.78%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.544150 | 0.028574 | 0.283845 | 8.502% | 0.473% | 0.0230% | 0.89520–0.89992 | 0.77875–0.78347 |
| traditional | 1.628771 | 0.117424 | 0.284297 | 8.502% | 0.473% | 0.0230% | 0.88425–0.88896 | 0.76374–0.76846 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.875977 | 0.099347 | 0.013777 | 7.603% | 0.010203 | 0.77288–0.78269 |
| bnwiki/train | traditional | 2.054710 | 0.109079 | 0.052124 | 7.808% | 0.034344 | 0.74127–0.75107 |
| newspaper/train | model-optimal | 1.837162 | 0.087129 | 0.016029 | 6.919% | 0.011849 | 0.76527–0.77252 |
| newspaper/train | traditional | 2.006273 | 0.099488 | 0.052898 | 7.439% | 0.035095 | 0.74024–0.74749 |
| bnwiki/heldout | model-optimal | 1.875822 | 0.099829 | 0.013764 | 7.639% | 0.010185 | 0.77252–0.78245 |
| bnwiki/heldout | traditional | 2.055249 | 0.109357 | 0.052422 | 7.829% | 0.034480 | 0.74080–0.75073 |
| newspaper/heldout | model-optimal | 1.837008 | 0.087003 | 0.016026 | 6.914% | 0.011856 | 0.76551–0.77269 |
| newspaper/heldout | traditional | 2.005943 | 0.099280 | 0.052848 | 7.429% | 0.035090 | 0.74050–0.74768 |
| bard-novel/heldout | model-optimal | 1.837824 | 0.087075 | 0.015819 | 6.907% | 0.011680 | 0.76631–0.77323 |
| bard-novel/heldout | traditional | 2.008553 | 0.098916 | 0.052489 | 7.390% | 0.034901 | 0.74261–0.74952 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-3270b803ada27b63.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | O/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| ◌ঃ | U+0983 | Q/shift | Q/shift | G/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | U/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | E/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | P/base |
| ঝ | U+099D | W/shift | B/shift | B/shift |
| ঞ | U+099E | B/shift | R/shift | W/shift |
| ট | U+099F | Z/base | T/base | Q/base |
| ঠ | U+09A0 | E/shift | V/shift | P/shift |
| ড | U+09A1 | H/shift | U/shift | H/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | Q/shift |
| ণ | U+09A3 | S/shift | O/shift | A/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | M/shift |
| দ | U+09A6 | W/base | O/base | Z/base |
| ধ | U+09A7 | N/shift | F/shift | N/shift |
| ন | U+09A8 | S/base | L/base | E/base |
| প | U+09AA | O/base | N/base | N/base |
| ফ | U+09AB | A/shift | H/shift | S/shift |
| ব | U+09AC | A/base | M/base | S/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | W/base |
| য | U+09AF | N/base | R/base | U/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | X/base |
| শ | U+09B6 | Y/base | G/base | H/base |
| ষ | U+09B7 | U/shift | J/shift | D/shift |
| স | U+09B8 | U/base | C/base | M/base |
| হ | U+09B9 | P/base | P/base | O/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | X/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-cd1cedf0ef5f7fe3 — experimental candidate

**Balance v1:** eligible rank 4, R=0.185457466. Primary changes versus its published reference: effort +0.373%, cross distance -21.17%, within distance -16.97%.

Assignment changes versus A-18fe73cb912ae3f1: 22 symbols; 22 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 42 symbols, 42 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 11 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101320.json", "seed": 2026101320, "archive_index": 36, "direction": 0.25, "start": "published-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.085%, X -33.65%, and W -2.74%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.06239, -0.04534]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.696030201, the frozen optimistic calibration cost is 0.510572735, and their shortfall is R=0.185457466. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +2.186%, X -3.37%, W +25.76%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.544162 | 0.028574 | 0.283845 | 8.502% | 0.473% | 0.0230% | 0.89521–0.89992 | 0.77873–0.78344 |
| traditional | 1.628783 | 0.117489 | 0.284297 | 8.502% | 0.473% | 0.0230% | 0.88424–0.88895 | 0.76371–0.76842 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.876056 | 0.099353 | 0.013769 | 7.604% | 0.010218 | 0.77292–0.78272 |
| bnwiki/train | traditional | 2.054879 | 0.109099 | 0.052166 | 7.810% | 0.034387 | 0.74124–0.75104 |
| newspaper/train | model-optimal | 1.837107 | 0.087137 | 0.015997 | 6.919% | 0.011829 | 0.76532–0.77257 |
| newspaper/train | traditional | 2.006259 | 0.099496 | 0.052889 | 7.440% | 0.035088 | 0.74026–0.74751 |
| bnwiki/heldout | model-optimal | 1.875895 | 0.099836 | 0.013755 | 7.640% | 0.010198 | 0.77255–0.78248 |
| bnwiki/heldout | traditional | 2.055405 | 0.109378 | 0.052460 | 7.831% | 0.034520 | 0.74077–0.75070 |
| newspaper/heldout | model-optimal | 1.836955 | 0.087010 | 0.015994 | 6.915% | 0.011836 | 0.76556–0.77274 |
| newspaper/heldout | traditional | 2.005927 | 0.099288 | 0.052839 | 7.430% | 0.035083 | 0.74052–0.74770 |
| bard-novel/heldout | model-optimal | 1.837765 | 0.087090 | 0.015788 | 6.908% | 0.011659 | 0.76637–0.77329 |
| bard-novel/heldout | traditional | 2.008524 | 0.098934 | 0.052476 | 7.392% | 0.034890 | 0.74265–0.74956 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-cd1cedf0ef5f7fe3.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | O/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | U/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | E/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | P/base |
| ঝ | U+099D | W/shift | B/shift | B/shift |
| ঞ | U+099E | B/shift | R/shift | W/shift |
| ট | U+099F | Z/base | T/base | Q/base |
| ঠ | U+09A0 | E/shift | V/shift | P/shift |
| ড | U+09A1 | H/shift | U/shift | H/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ণ | U+09A3 | S/shift | O/shift | A/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | M/shift |
| দ | U+09A6 | W/base | O/base | Z/base |
| ধ | U+09A7 | N/shift | F/shift | N/shift |
| ন | U+09A8 | S/base | L/base | E/base |
| প | U+09AA | O/base | N/base | N/base |
| ফ | U+09AB | A/shift | H/shift | S/shift |
| ব | U+09AC | A/base | M/base | S/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | W/base |
| য | U+09AF | N/base | R/base | U/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | X/base |
| শ | U+09B6 | Y/base | G/base | H/base |
| ষ | U+09B7 | U/shift | J/shift | D/shift |
| স | U+09B8 | U/base | C/base | M/base |
| হ | U+09B9 | P/base | P/base | O/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | X/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-70dc91ce76c7391e — experimental candidate

**Balance v1:** eligible rank 5, R=0.189785627. Primary changes versus its published reference: effort +0.375%, cross distance -21.18%, within distance -17.26%.

Assignment changes versus A-18fe73cb912ae3f1: 22 symbols; 22 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 42 symbols, 42 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101328.json", "seed": 2026101328, "archive_index": 42, "direction": 0.75, "start": "random"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.087%, X -33.66%, and W -3.08%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.06236, -0.04530]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.700358362, the frozen optimistic calibration cost is 0.510572735, and their shortfall is R=0.189785627. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +2.205%, X -3.37%, W +25.80%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.544306 | 0.028479 | 0.283845 | 8.502% | 0.473% | 0.0230% | 0.89521–0.89992 | 0.77865–0.78336 |
| traditional | 1.628927 | 0.117496 | 0.284297 | 8.502% | 0.473% | 0.0230% | 0.88423–0.88894 | 0.76362–0.76833 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.875856 | 0.099356 | 0.013699 | 7.604% | 0.010193 | 0.77301–0.78282 |
| bnwiki/train | traditional | 2.054789 | 0.109096 | 0.052156 | 7.809% | 0.034392 | 0.74122–0.75102 |
| newspaper/train | model-optimal | 1.837405 | 0.087120 | 0.015963 | 6.918% | 0.011832 | 0.76530–0.77255 |
| newspaper/train | traditional | 2.006651 | 0.099487 | 0.052906 | 7.439% | 0.035117 | 0.74018–0.74743 |
| bnwiki/heldout | model-optimal | 1.875683 | 0.099839 | 0.013673 | 7.640% | 0.010167 | 0.77266–0.78259 |
| bnwiki/heldout | traditional | 2.055334 | 0.109375 | 0.052456 | 7.831% | 0.034527 | 0.74075–0.75068 |
| newspaper/heldout | model-optimal | 1.837239 | 0.086996 | 0.015956 | 6.914% | 0.011835 | 0.76555–0.77273 |
| newspaper/heldout | traditional | 2.006321 | 0.099279 | 0.052859 | 7.429% | 0.035111 | 0.74044–0.74762 |
| bard-novel/heldout | model-optimal | 1.838060 | 0.087031 | 0.015767 | 6.905% | 0.011666 | 0.76632–0.77324 |
| bard-novel/heldout | traditional | 2.008910 | 0.098917 | 0.052506 | 7.390% | 0.034922 | 0.74252–0.74944 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-70dc91ce76c7391e.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | O/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | U/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | W/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | P/base |
| ঝ | U+099D | W/shift | B/shift | B/shift |
| ঞ | U+099E | B/shift | R/shift | E/shift |
| ট | U+099F | Z/base | T/base | Q/base |
| ঠ | U+09A0 | E/shift | V/shift | P/shift |
| ড | U+09A1 | H/shift | U/shift | H/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ণ | U+09A3 | S/shift | O/shift | A/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | M/shift |
| দ | U+09A6 | W/base | O/base | Z/base |
| ধ | U+09A7 | N/shift | F/shift | N/shift |
| ন | U+09A8 | S/base | L/base | E/base |
| প | U+09AA | O/base | N/base | N/base |
| ফ | U+09AB | A/shift | H/shift | S/shift |
| ব | U+09AC | A/base | M/base | S/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | W/base |
| য | U+09AF | N/base | R/base | U/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | X/base |
| শ | U+09B6 | Y/base | G/base | H/base |
| ষ | U+09B7 | U/shift | J/shift | D/shift |
| স | U+09B8 | U/base | C/base | M/base |
| হ | U+09B9 | P/base | P/base | O/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | X/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-4dfc1837861ac886 — experimental candidate

**Balance v1:** eligible rank 376, R=0.491678626. Primary changes versus its published reference: effort +0.351%, cross distance -25.69%, within distance -0.63%.

Assignment changes versus A-18fe73cb912ae3f1: 22 symbols; 22 change physical key; 0 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 42 symbols, 42 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101787.json", "seed": 2026101787, "archive_index": 36, "direction": 0.1, "start": "perturbed-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.063%, X -37.45%, and W +16.40%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.05185, -0.03479]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting A-21 (weights [6, 1, 1.25, 0.75], rho 0.075), within-word distance is the largest weighted deviation. B+ is 1.375801365, the frozen optimistic calibration cost is 0.884122739, and their shortfall is R=0.491678626. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.378%, X -13.10%, W +2.34%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.533686 | 0.037370 | 0.285122 | 8.502% | 0.469% | 0.0230% | 0.89906–0.90378 | 0.78063–0.78535 |
| traditional | 1.609077 | 0.100470 | 0.285266 | 8.502% | 0.469% | 0.0230% | 0.89196–0.89667 | 0.76938–0.77409 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.875439 | 0.092204 | 0.016232 | 7.294% | 0.011984 | 0.77588–0.78569 |
| bnwiki/train | traditional | 2.029177 | 0.098337 | 0.045838 | 7.462% | 0.031263 | 0.74396–0.75376 |
| newspaper/train | model-optimal | 1.836917 | 0.083596 | 0.019392 | 6.819% | 0.014416 | 0.78344–0.79069 |
| newspaper/train | traditional | 1.960450 | 0.089354 | 0.040220 | 6.993% | 0.028648 | 0.76689–0.77415 |
| bnwiki/heldout | model-optimal | 1.875326 | 0.091955 | 0.016278 | 7.280% | 0.012009 | 0.77571–0.78564 |
| bnwiki/heldout | traditional | 2.029452 | 0.098181 | 0.045966 | 7.456% | 0.031323 | 0.74389–0.75382 |
| newspaper/heldout | model-optimal | 1.836829 | 0.083694 | 0.019417 | 6.826% | 0.014446 | 0.78353–0.79071 |
| newspaper/heldout | traditional | 1.960378 | 0.089446 | 0.040251 | 7.002% | 0.028692 | 0.76697–0.77415 |
| bard-novel/heldout | model-optimal | 1.837675 | 0.083919 | 0.019290 | 6.826% | 0.014378 | 0.78414–0.79106 |
| bard-novel/heldout | traditional | 1.962032 | 0.089132 | 0.040270 | 6.956% | 0.028734 | 0.76824–0.77515 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-4dfc1837861ac886.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | G/base |
| ◌ঁ | U+0981 | O/shift | P/shift | P/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| ◌ঃ | U+0983 | Q/shift | Q/shift | B/shift |
| অ | U+0985 | F/shift | D/shift | F/shift |
| খ | U+0996 | D/shift | N/shift | N/shift |
| গ | U+0997 | Q/base | Y/base | Y/base |
| ঙ | U+0999 | P/shift | A/shift | H/shift |
| চ | U+099A | J/shift | B/base | J/shift |
| ছ | U+099B | B/base | K/shift | B/base |
| জ | U+099C | H/base | Q/base | P/base |
| ঝ | U+099D | W/shift | B/shift | W/shift |
| ঞ | U+099E | B/shift | R/shift | X/shift |
| ট | U+099F | Z/base | T/base | Z/base |
| ঠ | U+09A0 | E/shift | V/shift | E/shift |
| ড | U+09A1 | H/shift | U/shift | D/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | I/shift |
| ঢ | U+09A2 | Z/shift | T/shift | Z/shift |
| ণ | U+09A3 | S/shift | O/shift | S/shift |
| ত | U+09A4 | M/base | A/base | A/base |
| থ | U+09A5 | M/shift | L/shift | A/shift |
| দ | U+09A6 | W/base | O/base | Q/base |
| ধ | U+09A7 | N/shift | F/shift | O/shift |
| ন | U+09A8 | S/base | L/base | S/base |
| প | U+09AA | O/base | N/base | U/base |
| ফ | U+09AB | A/shift | H/shift | U/shift |
| ব | U+09AC | A/base | M/base | M/base |
| ভ | U+09AD | L/shift | M/shift | L/shift |
| ম | U+09AE | X/base | U/base | N/base |
| য | U+09AF | N/base | R/base | X/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | E/base |
| শ | U+09B6 | Y/base | G/base | H/base |
| ষ | U+09B7 | U/shift | J/shift | M/shift |
| স | U+09B8 | U/base | C/base | W/base |
| হ | U+09B9 | P/base | P/base | O/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | C/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | V/base |
| ◌ূ | U+09C2 | C/shift | S/shift | C/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | V/shift |
| ◌ে | U+09C7 | L/base | S/base | L/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | R/base |
| ◌ৌ | U+09CC | T/shift | W/shift | T/shift |
| ৎ | U+09CE | X/shift | Z/shift | Q/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### A-7c36e8f26e6c7142 — requested diagnostic; ineligible under the adopted effort cap

**Balance v1:** ineligible; no eligible R/rank. Primary changes versus its published reference: effort +3.396%, cross distance -46.78%, within distance -26.08%.

Assignment changes versus A-18fe73cb912ae3f1: 41 symbols; 41 change physical key; 2 change base/Shift layer. Versus Balance leader A-a280bdc4ca72c6c7: 47 symbols, 47 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/A-2026101779.json", "seed": 2026101779, "archive_index": 46, "direction": 0.9, "start": "greedy-J1"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +3.099%, X -55.21%, and W -13.41%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.08884, -0.07178]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

Across individual training/held-out sources and both fingerings, worst observed changes are E +7.221%, X -30.14%, W +30.68%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.603852 | 0.022823 | 0.285826 | 8.541% | 0.579% | 0.0230% | 0.89341–0.89812 | 0.77586–0.78057 |
| traditional | 1.704069 | 0.128438 | 0.285970 | 8.541% | 0.579% | 0.0230% | 0.87690–0.88161 | 0.75519–0.75991 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.930908 | 0.065950 | 0.013161 | 4.604% | 0.009994 | 0.74648–0.75628 |
| bnwiki/train | traditional | 2.131175 | 0.078397 | 0.052211 | 5.237% | 0.038817 | 0.70605–0.71586 |
| newspaper/train | model-optimal | 1.894095 | 0.059950 | 0.013339 | 4.292% | 0.010405 | 0.73887–0.74612 |
| newspaper/train | traditional | 2.105780 | 0.071901 | 0.054703 | 5.048% | 0.040207 | 0.69891–0.70617 |
| bnwiki/heldout | model-optimal | 1.931127 | 0.065937 | 0.013156 | 4.604% | 0.009993 | 0.74637–0.75631 |
| bnwiki/heldout | traditional | 2.130761 | 0.078190 | 0.051944 | 5.233% | 0.038644 | 0.70615–0.71608 |
| newspaper/heldout | model-optimal | 1.893950 | 0.059812 | 0.013357 | 4.289% | 0.010420 | 0.73891–0.74610 |
| newspaper/heldout | traditional | 2.105644 | 0.071907 | 0.054757 | 5.045% | 0.040245 | 0.69897–0.70615 |
| bard-novel/heldout | model-optimal | 1.893609 | 0.060330 | 0.013257 | 4.286% | 0.010311 | 0.73819–0.74510 |
| bard-novel/heldout | traditional | 2.106935 | 0.070976 | 0.054777 | 4.945% | 0.040283 | 0.69828–0.70520 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/A-7c36e8f26e6c7142.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | G/base | H/base | E/base |
| ◌ঁ | U+0981 | O/shift | P/shift | Y/shift |
| ◌ং | U+0982 | K/shift | I/shift | K/shift |
| ◌ঃ | U+0983 | Q/shift | Q/shift | B/shift |
| অ | U+0985 | F/shift | D/shift | L/shift |
| ক | U+0995 | J/base | J/base | A/base |
| খ | U+0996 | D/shift | N/shift | P/shift |
| গ | U+0997 | Q/base | Y/base | Q/base |
| ঘ | U+0998 | Y/shift | Y/shift | Q/shift |
| ঙ | U+0999 | P/shift | A/shift | A/shift |
| চ | U+099A | J/shift | B/base | B/base |
| ছ | U+099B | B/base | K/shift | I/shift |
| জ | U+099C | H/base | Q/base | U/base |
| ঝ | U+099D | W/shift | B/shift | G/shift |
| ঞ | U+099E | B/shift | R/shift | F/shift |
| ট | U+099F | Z/base | T/base | N/base |
| ঠ | U+09A0 | E/shift | V/shift | O/shift |
| ড | U+09A1 | H/shift | U/shift | U/shift |
| ড় | U+09A1 U+09BC | I/shift | C/shift | X/shift |
| ঢ | U+09A2 | Z/shift | T/shift | H/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | W/shift |
| ণ | U+09A3 | S/shift | O/shift | S/shift |
| ত | U+09A4 | M/base | A/base | J/base |
| থ | U+09A5 | M/shift | L/shift | J/shift |
| দ | U+09A6 | W/base | O/base | Z/base |
| ধ | U+09A7 | N/shift | F/shift | E/shift |
| ন | U+09A8 | S/base | L/base | S/base |
| প | U+09AA | O/base | N/base | O/base |
| ফ | U+09AB | A/shift | H/shift | N/shift |
| ব | U+09AC | A/base | M/base | L/base |
| ভ | U+09AD | L/shift | M/shift | D/shift |
| ম | U+09AE | X/base | U/base | P/base |
| য | U+09AF | N/base | R/base | H/base |
| য় | U+09AF U+09BC | I/base | I/base | W/base |
| র | U+09B0 | D/base | F/base | D/base |
| ল | U+09B2 | E/base | V/base | X/base |
| শ | U+09B6 | Y/base | G/base | Y/base |
| ষ | U+09B7 | U/shift | J/shift | M/shift |
| স | U+09B8 | U/base | C/base | M/base |
| হ | U+09B9 | P/base | P/base | I/base |
| ◌া | U+09BE | F/base | D/base | F/base |
| ◌ি | U+09BF | C/base | E/base | R/base |
| ◌ী | U+09C0 | T/base | Z/base | T/base |
| ◌ু | U+09C1 | V/base | X/base | G/base |
| ◌ূ | U+09C2 | C/shift | S/shift | V/shift |
| ◌ৃ | U+09C3 | V/shift | E/shift | T/shift |
| ◌ে | U+09C7 | L/base | S/base | C/base |
| ◌ৈ | U+09C8 | R/shift | X/shift | R/shift |
| ◌ো | U+09CB | R/base | W/base | V/base |
| ◌ৌ | U+09CC | T/shift | W/shift | C/shift |
| ৎ | U+09CE | X/shift | Z/shift | Z/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-e4a6be48881da590 — published reference, retained

**Balance v1:** eligible rank 110, R=0.240273932. Primary changes versus its published reference: effort +0.000%, cross distance +0.00%, within distance +0.00%.

Assignment changes versus D-e4a6be48881da590: 0 symbols; 0 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 3 symbols, 3 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 4808 retained records. First record: `{"file": "results/mix-search/search/D.json", "kind": "published", "seed": 20261126}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.272%, X +14.69%, and W +8.98%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.01838, -0.00079]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-21 (weights [6, 1, 1.25, 0.75], rho 0.075), within-word distance is the largest weighted deviation. B+ is 0.776106453, the frozen optimistic calibration cost is 0.535832521, and their shortfall is R=0.240273932. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.000%, X +0.00%, W +0.00%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.493596 | 0.037302 | 0.277898 | 8.865% | 0.803% | 0.0254% | 0.89402–0.89895 | 0.77788–0.78281 |
| traditional | 1.572358 | 0.138550 | 0.278349 | 8.865% | 0.803% | 0.0254% | 0.87683–0.88176 | 0.75842–0.76335 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.835055 | 0.136000 | 0.018381 | 10.539% | 0.014691 | 0.75472–0.76478 |
| bnwiki/train | traditional | 2.030340 | 0.124334 | 0.059701 | 9.302% | 0.047038 | 0.67844–0.68850 |
| newspaper/train | model-optimal | 1.782537 | 0.132053 | 0.020090 | 10.207% | 0.016075 | 0.74441–0.75194 |
| newspaper/train | traditional | 1.948174 | 0.122856 | 0.055826 | 9.188% | 0.043890 | 0.67830–0.68582 |
| bnwiki/heldout | model-optimal | 1.834823 | 0.136201 | 0.018379 | 10.561% | 0.014729 | 0.75484–0.76503 |
| bnwiki/heldout | traditional | 2.029837 | 0.124551 | 0.059625 | 9.331% | 0.047029 | 0.67879–0.68898 |
| newspaper/heldout | model-optimal | 1.782223 | 0.132072 | 0.020032 | 10.208% | 0.016036 | 0.74493–0.75239 |
| newspaper/heldout | traditional | 1.948095 | 0.122945 | 0.055911 | 9.191% | 0.043938 | 0.67854–0.68599 |
| bard-novel/heldout | model-optimal | 1.783031 | 0.131240 | 0.019925 | 10.080% | 0.015946 | 0.74373–0.75090 |
| bard-novel/heldout | traditional | 1.951118 | 0.122314 | 0.056131 | 9.093% | 0.044083 | 0.67781–0.68498 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-e4a6be48881da590.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| গ | U+0997 | P/base | Q/base | P/base |
| ট | U+099F | Q/base | X/base | Q/base |
| ম | U+09AE | X/base | P/base | X/base |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-9ad5412603069cd6 — experimental candidate

**Balance v1:** eligible rank 1, R=0.139415963. Primary changes versus its published reference: effort +0.273%, cross distance -12.81%, within distance -8.24%.

Assignment changes versus D-e4a6be48881da590: 3 symbols; 3 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 0 symbols, 0 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 3 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026101949.json", "seed": 2026101949, "archive_index": 29, "direction": 0.9, "start": "perturbed-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**What controls its Balance v1 result:** at setting D-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.521179273, the frozen optimistic calibration cost is 0.381763310, and their shortfall is R=0.139415963. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.296%, X -3.41%, W -1.32%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.499622 | 0.036212 | 0.277898 | 8.865% | 0.795% | 0.0254% | 0.89568–0.90061 | 0.77744–0.78237 |
| traditional | 1.571986 | 0.137346 | 0.278349 | 8.865% | 0.795% | 0.0254% | 0.87846–0.88339 | 0.75930–0.76423 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.840484 | 0.118268 | 0.017397 | 9.024% | 0.013894 | 0.76142–0.77148 |
| bnwiki/train | traditional | 2.029896 | 0.120093 | 0.058914 | 9.003% | 0.046440 | 0.68473–0.69479 |
| newspaper/train | model-optimal | 1.786978 | 0.115455 | 0.017905 | 8.825% | 0.014505 | 0.75688–0.76441 |
| newspaper/train | traditional | 1.945467 | 0.118044 | 0.054131 | 8.836% | 0.042601 | 0.68907–0.69660 |
| bnwiki/heldout | model-optimal | 1.840036 | 0.118530 | 0.017303 | 9.051% | 0.013872 | 0.76147–0.77167 |
| bnwiki/heldout | traditional | 2.029339 | 0.119998 | 0.058818 | 9.010% | 0.046410 | 0.68494–0.69513 |
| newspaper/heldout | model-optimal | 1.786651 | 0.115544 | 0.017880 | 8.830% | 0.014480 | 0.75724–0.76470 |
| newspaper/heldout | traditional | 1.945347 | 0.118179 | 0.054205 | 8.843% | 0.042640 | 0.68924–0.69669 |
| bard-novel/heldout | model-optimal | 1.787419 | 0.114582 | 0.017656 | 8.714% | 0.014298 | 0.75675–0.76392 |
| bard-novel/heldout | traditional | 1.948214 | 0.116961 | 0.054297 | 8.715% | 0.042700 | 0.68879–0.69596 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-9ad5412603069cd6.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| গ | U+0997 | P/base | Q/base | Q/base |
| ট | U+099F | Q/base | X/base | X/base |
| ম | U+09AE | X/base | P/base | P/base |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-eb3bf7d2da4f048e — experimental candidate

**Balance v1:** eligible rank 2, R=0.161369564. Primary changes versus its published reference: effort +0.286%, cross distance -12.84%, within distance -8.25%.

Assignment changes versus D-e4a6be48881da590: 5 symbols; 5 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 2 symbols, 2 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026102214.json", "seed": 2026102214, "archive_index": 34, "direction": 0.0, "start": "perturbed-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.013%, X -0.04%, and W -0.01%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.00879, +0.00879]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.543132875, the frozen optimistic calibration cost is 0.381763310, and their shortfall is R=0.161369564. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.311%, X -3.48%, W -1.35%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.499853 | 0.036212 | 0.277898 | 8.865% | 0.796% | 0.0254% | 0.89560–0.90053 | 0.77730–0.78223 |
| traditional | 1.572217 | 0.137346 | 0.278349 | 8.865% | 0.796% | 0.0254% | 0.87838–0.88331 | 0.75916–0.76408 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.840761 | 0.118178 | 0.017390 | 9.015% | 0.013888 | 0.76142–0.77148 |
| bnwiki/train | traditional | 2.030172 | 0.120002 | 0.058893 | 8.994% | 0.046434 | 0.68473–0.69479 |
| newspaper/train | model-optimal | 1.787164 | 0.115451 | 0.017908 | 8.825% | 0.014505 | 0.75688–0.76441 |
| newspaper/train | traditional | 1.945652 | 0.118039 | 0.054129 | 8.836% | 0.042601 | 0.68907–0.69660 |
| bnwiki/heldout | model-optimal | 1.840314 | 0.118431 | 0.017296 | 9.041% | 0.013866 | 0.76147–0.77167 |
| bnwiki/heldout | traditional | 2.029617 | 0.119896 | 0.058798 | 9.001% | 0.046404 | 0.68494–0.69513 |
| newspaper/heldout | model-optimal | 1.786837 | 0.115542 | 0.017884 | 8.830% | 0.014480 | 0.75724–0.76470 |
| newspaper/heldout | traditional | 1.945532 | 0.118177 | 0.054203 | 8.843% | 0.042640 | 0.68924–0.69669 |
| bard-novel/heldout | model-optimal | 1.787590 | 0.114593 | 0.017659 | 8.715% | 0.014298 | 0.75675–0.76392 |
| bard-novel/heldout | traditional | 1.948384 | 0.116972 | 0.054294 | 8.716% | 0.042700 | 0.68879–0.69596 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-eb3bf7d2da4f048e.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| ◌ঃ | U+0983 | T/shift | T/shift | R/shift |
| গ | U+0997 | P/base | Q/base | Q/base |
| ট | U+099F | Q/base | X/base | X/base |
| ম | U+09AE | X/base | P/base | P/base |
| ◌ৈ | U+09C8 | R/shift | R/shift | T/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-a3a1484044fb8d5e — experimental candidate

**Balance v1:** eligible rank 3, R=0.161652545. Primary changes versus its published reference: effort +0.260%, cross distance -11.72%, within distance -9.22%.

Assignment changes versus D-e4a6be48881da590: 2 symbols; 2 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 2 symbols, 2 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 7 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026101932.json", "seed": 2026101932, "archive_index": 30, "direction": 0.0, "start": "published-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.013%, X +1.24%, and W -1.07%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.01468, +0.00291]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-07 (weights [6, 1, 0.75, 1.25], rho 0.025), order deficit is the largest weighted deviation. B+ is 0.813835232, the frozen optimistic calibration cost is 0.652182688, and their shortfall is R=0.161652545. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.284%, X -1.38%, W -0.06%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.500359 | 0.035242 | 0.277898 | 8.865% | 0.795% | 0.0254% | 0.89438–0.89931 | 0.77707–0.78200 |
| traditional | 1.572723 | 0.137682 | 0.278349 | 8.865% | 0.795% | 0.0254% | 0.87677–0.88170 | 0.75876–0.76369 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.839603 | 0.119694 | 0.017141 | 9.162% | 0.013677 | 0.75768–0.76774 |
| bnwiki/train | traditional | 2.030198 | 0.122620 | 0.059667 | 9.172% | 0.046684 | 0.67901–0.68907 |
| newspaper/train | model-optimal | 1.787394 | 0.116935 | 0.017783 | 8.976% | 0.014414 | 0.74886–0.75638 |
| newspaper/train | traditional | 1.947311 | 0.120166 | 0.055495 | 8.996% | 0.043201 | 0.67910–0.68663 |
| bnwiki/heldout | model-optimal | 1.839133 | 0.119978 | 0.017036 | 9.190% | 0.013646 | 0.75791–0.76810 |
| bnwiki/heldout | traditional | 2.029623 | 0.122469 | 0.059563 | 9.176% | 0.046646 | 0.67940–0.68959 |
| newspaper/heldout | model-optimal | 1.787089 | 0.116941 | 0.017766 | 8.973% | 0.014396 | 0.74931–0.75676 |
| newspaper/heldout | traditional | 1.947211 | 0.120157 | 0.055567 | 8.993% | 0.043242 | 0.67938–0.68683 |
| bard-novel/heldout | model-optimal | 1.788099 | 0.116162 | 0.017606 | 8.874% | 0.014273 | 0.74853–0.75570 |
| bard-novel/heldout | traditional | 1.950541 | 0.119136 | 0.056006 | 8.879% | 0.043491 | 0.67853–0.68570 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-a3a1484044fb8d5e.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| গ | U+0997 | P/base | Q/base | P/base |
| ট | U+099F | Q/base | X/base | X/base |
| ম | U+09AE | X/base | P/base | Q/base |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-c4028c28dc54b209 — experimental candidate

**Balance v1:** eligible rank 4, R=0.164988475. Primary changes versus its published reference: effort +0.287%, cross distance -11.71%, within distance -9.20%.

Assignment changes versus D-e4a6be48881da590: 4 symbols; 4 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 4 symbols, 4 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026102202.json", "seed": 2026102202, "archive_index": 25, "direction": 0.0, "start": "published-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.014%, X +1.26%, and W -1.05%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.01468, +0.00291]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.546751785, the frozen optimistic calibration cost is 0.381763310, and their shortfall is R=0.164988475. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.304%, X -1.35%, W -0.12%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.500856 | 0.035238 | 0.277898 | 8.865% | 0.795% | 0.0254% | 0.89440–0.89933 | 0.77712–0.78205 |
| traditional | 1.573220 | 0.137651 | 0.278349 | 8.865% | 0.795% | 0.0254% | 0.87679–0.88172 | 0.75881–0.76374 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.840208 | 0.119728 | 0.017146 | 9.166% | 0.013678 | 0.75768–0.76774 |
| bnwiki/train | traditional | 2.030765 | 0.122650 | 0.059629 | 9.175% | 0.046685 | 0.67901–0.68907 |
| newspaper/train | model-optimal | 1.787776 | 0.116941 | 0.017785 | 8.977% | 0.014415 | 0.74886–0.75638 |
| newspaper/train | traditional | 1.947675 | 0.120172 | 0.055479 | 8.997% | 0.043201 | 0.67910–0.68663 |
| bnwiki/heldout | model-optimal | 1.839739 | 0.120007 | 0.017040 | 9.193% | 0.013647 | 0.75791–0.76810 |
| bnwiki/heldout | traditional | 2.030192 | 0.122495 | 0.059526 | 9.179% | 0.046647 | 0.67940–0.68959 |
| newspaper/heldout | model-optimal | 1.787471 | 0.116949 | 0.017768 | 8.974% | 0.014396 | 0.74931–0.75676 |
| newspaper/heldout | traditional | 1.947575 | 0.120165 | 0.055551 | 8.993% | 0.043242 | 0.67938–0.68683 |
| bard-novel/heldout | model-optimal | 1.788452 | 0.116175 | 0.017607 | 8.875% | 0.014273 | 0.74853–0.75570 |
| bard-novel/heldout | traditional | 1.950877 | 0.119150 | 0.055989 | 8.880% | 0.043491 | 0.67853–0.68570 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-c4028c28dc54b209.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| গ | U+0997 | P/base | Q/base | P/base |
| ট | U+099F | Q/base | X/base | X/base |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | R/shift |
| ম | U+09AE | X/base | P/base | Q/base |
| ◌ৈ | U+09C8 | R/shift | R/shift | G/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-f4e1710b3ec62eb8 — experimental candidate

**Balance v1:** eligible rank 5, R=0.182134413. Primary changes versus its published reference: effort +0.056%, cross distance -1.06%, within distance -2.19%.

Assignment changes versus D-e4a6be48881da590: 6 symbols; 6 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 9 symbols, 9 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 4 retained records. First record: `{"file": "results/phase3/search/D.json", "kind": "earlier"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.216%, X +13.47%, and W +6.59%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.01789, -0.00030]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-07 (weights [6, 1, 0.75, 1.25], rho 0.025), order deficit is the largest weighted deviation. B+ is 0.834317101, the frozen optimistic calibration cost is 0.652182688, and their shortfall is R=0.182134413. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.139%, X -0.61%, W -0.82%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.490961 | 0.037224 | 0.281631 | 8.865% | 0.829% | 0.0254% | 0.89431–0.89924 | 0.77791–0.78283 |
| traditional | 1.569722 | 0.135718 | 0.282082 | 8.865% | 0.829% | 0.0254% | 0.87749–0.88241 | 0.75859–0.76352 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.834624 | 0.134280 | 0.017889 | 10.379% | 0.014305 | 0.75549–0.76555 |
| bnwiki/train | traditional | 2.027015 | 0.122621 | 0.057606 | 9.168% | 0.045915 | 0.67875–0.68881 |
| newspaper/train | model-optimal | 1.785007 | 0.130934 | 0.019741 | 10.108% | 0.015766 | 0.74463–0.75215 |
| newspaper/train | traditional | 1.948030 | 0.121846 | 0.054048 | 9.113% | 0.042896 | 0.67787–0.68540 |
| bnwiki/heldout | model-optimal | 1.834310 | 0.134494 | 0.017882 | 10.401% | 0.014338 | 0.75563–0.76583 |
| bnwiki/heldout | traditional | 2.026525 | 0.122786 | 0.057574 | 9.192% | 0.045925 | 0.67909–0.68928 |
| newspaper/heldout | model-optimal | 1.784671 | 0.130977 | 0.019673 | 10.112% | 0.015719 | 0.74514–0.75260 |
| newspaper/heldout | traditional | 1.947937 | 0.121978 | 0.054128 | 9.119% | 0.042939 | 0.67811–0.68557 |
| bard-novel/heldout | model-optimal | 1.785394 | 0.130280 | 0.019762 | 9.997% | 0.015797 | 0.74359–0.75076 |
| bard-novel/heldout | traditional | 1.950747 | 0.121564 | 0.054479 | 9.041% | 0.043220 | 0.67704–0.68421 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-f4e1710b3ec62eb8.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| খ | U+0996 | N/shift | N/shift | A/shift |
| গ | U+0997 | P/base | Q/base | P/base |
| ট | U+099F | Q/base | X/base | Q/base |
| ঠ | U+09A0 | E/shift | E/shift | H/shift |
| ড | U+09A1 | H/shift | H/shift | U/shift |
| ড় | U+09A1 U+09BC | S/shift | S/shift | E/shift |
| ধ | U+09A7 | U/shift | U/shift | N/shift |
| ফ | U+09AB | A/shift | A/shift | S/shift |
| ম | U+09AE | X/base | P/base | X/base |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-48319b4b30582e8c — experimental candidate

**Balance v1:** eligible rank 37, R=0.201139299. Primary changes versus its published reference: effort +0.083%, cross distance -2.64%, within distance -4.95%.

Assignment changes versus D-e4a6be48881da590: 14 symbols; 14 change physical key; 2 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 17 symbols, 17 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026101940.json", "seed": 2026101940, "archive_index": 31, "direction": 0.25, "start": "random"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.189%, X +11.66%, and W +3.58%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.02063, -0.00304]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-07 (weights [6, 1, 0.75, 1.25], rho 0.025), order deficit is the largest weighted deviation. B+ is 0.853321986, the frozen optimistic calibration cost is 0.652182688, and their shortfall is R=0.201139299. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.099%, X -2.28%, W -4.84%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.490244 | 0.036784 | 0.283271 | 8.824% | 0.834% | 0.0254% | 0.89160–0.89652 | 0.77620–0.78112 |
| traditional | 1.568633 | 0.133574 | 0.283723 | 8.824% | 0.834% | 0.0254% | 0.87841–0.88334 | 0.76009–0.76501 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.836866 | 0.132862 | 0.017469 | 10.312% | 0.014138 | 0.75252–0.76258 |
| bnwiki/train | traditional | 2.027181 | 0.119827 | 0.055653 | 9.049% | 0.044998 | 0.69020–0.70026 |
| newspaper/train | model-optimal | 1.783733 | 0.128123 | 0.019097 | 9.976% | 0.015380 | 0.74212–0.74965 |
| newspaper/train | traditional | 1.944679 | 0.117235 | 0.051134 | 8.894% | 0.041466 | 0.69288–0.70041 |
| bnwiki/heldout | model-optimal | 1.836476 | 0.133094 | 0.017461 | 10.331% | 0.014172 | 0.75266–0.76286 |
| bnwiki/heldout | traditional | 2.026790 | 0.120080 | 0.055685 | 9.075% | 0.045046 | 0.69041–0.70060 |
| newspaper/heldout | model-optimal | 1.783412 | 0.128034 | 0.019047 | 9.973% | 0.015349 | 0.74274–0.75019 |
| newspaper/heldout | traditional | 1.944520 | 0.117221 | 0.051191 | 8.896% | 0.041497 | 0.69323–0.70069 |
| bard-novel/heldout | model-optimal | 1.784059 | 0.127593 | 0.018961 | 9.861% | 0.015302 | 0.74144–0.74861 |
| bard-novel/heldout | traditional | 1.946702 | 0.116696 | 0.050976 | 8.803% | 0.041451 | 0.69328–0.70045 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-48319b4b30582e8c.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| ◌ঃ | U+0983 | T/shift | T/shift | G/shift |
| গ | U+0997 | P/base | Q/base | P/base |
| ঘ | U+0998 | Y/shift | Y/shift | H/shift |
| চ | U+099A | B/base | B/base | J/shift |
| ছ | U+099B | J/shift | J/shift | B/base |
| ঞ | U+099E | X/shift | X/shift | Y/shift |
| ট | U+099F | Q/base | X/base | Q/base |
| ঠ | U+09A0 | E/shift | E/shift | X/shift |
| ড | U+09A1 | H/shift | H/shift | U/shift |
| ড় | U+09A1 U+09BC | S/shift | S/shift | E/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | T/shift |
| থ | U+09A5 | M/shift | M/shift | S/shift |
| ধ | U+09A7 | U/shift | U/shift | M/shift |
| ম | U+09AE | X/base | P/base | X/base |
| ◌ৃ | U+09C3 | C/shift | C/shift | R/shift |
| ◌ৈ | U+09C8 | R/shift | R/shift | V/shift |
| ◌ৌ | U+09CC | V/shift | V/shift | C/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-8e3f1abe1434b3ea — experimental candidate

**Balance v1:** eligible rank 464, R=0.533368651. Primary changes versus its published reference: effort +0.500%, cross distance -21.38%, within distance +0.16%.

Assignment changes versus D-e4a6be48881da590: 44 symbols; 44 change physical key; 2 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 43 symbols, 43 physical-key changes, 2 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026102229.json", "seed": 2026102229, "archive_index": 29, "direction": 0.5, "start": "perturbed-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.226%, X -9.84%, and W +9.15%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.00375, +0.01383]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

**What controls its Balance v1 result:** at setting D-57 (weights [10, 1, 0.75, 0.75], rho 0.075), effort is the largest weighted deviation. B+ is 0.915131961, the frozen optimistic calibration cost is 0.381763310, and their shortfall is R=0.533368651. This is the candidate's worst setting, not a weight choice fitted specifically to favor or reject it.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.596%, X -16.06%, W +2.29%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.499909 | 0.034797 | 0.283128 | 8.931% | 0.759% | 0.0254% | 0.89681–0.90174 | 0.77894–0.78387 |
| traditional | 1.552146 | 0.076955 | 0.283152 | 8.931% | 0.759% | 0.0254% | 0.88886–0.89379 | 0.77094–0.77587 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.845988 | 0.108831 | 0.018801 | 8.095% | 0.014367 | 0.75805–0.76811 |
| bnwiki/train | traditional | 1.936920 | 0.104363 | 0.034347 | 7.845% | 0.025731 | 0.72823–0.73829 |
| newspaper/train | model-optimal | 1.789679 | 0.101905 | 0.019731 | 7.740% | 0.015041 | 0.77033–0.77786 |
| newspaper/train | traditional | 1.887588 | 0.092765 | 0.039124 | 7.044% | 0.029244 | 0.73485–0.74237 |
| bnwiki/heldout | model-optimal | 1.845513 | 0.108780 | 0.018634 | 8.090% | 0.014249 | 0.75865–0.76884 |
| bnwiki/heldout | traditional | 1.936545 | 0.103953 | 0.034255 | 7.823% | 0.025661 | 0.72864–0.73883 |
| newspaper/heldout | model-optimal | 1.789303 | 0.101820 | 0.019651 | 7.737% | 0.015008 | 0.77056–0.77802 |
| newspaper/heldout | traditional | 1.886906 | 0.092675 | 0.038946 | 7.041% | 0.029162 | 0.73516–0.74261 |
| bard-novel/heldout | model-optimal | 1.791427 | 0.104073 | 0.020258 | 7.850% | 0.015382 | 0.76969–0.77686 |
| bard-novel/heldout | traditional | 1.892423 | 0.094564 | 0.040396 | 7.142% | 0.030158 | 0.73245–0.73962 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-8e3f1abe1434b3ea.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | T/base | T/base | P/base |
| ◌ং | U+0982 | I/shift | I/shift | D/shift |
| ◌ঃ | U+0983 | T/shift | T/shift | G/shift |
| ক | U+0995 | J/base | J/base | A/base |
| খ | U+0996 | N/shift | N/shift | F/shift |
| গ | U+0997 | P/base | Q/base | Q/base |
| ঘ | U+0998 | Y/shift | Y/shift | W/shift |
| ঙ | U+0999 | W/shift | W/shift | A/shift |
| চ | U+099A | B/base | B/base | Y/base |
| ছ | U+099B | J/shift | J/shift | B/base |
| জ | U+099C | H/base | H/base | T/base |
| ঝ | U+099D | B/shift | B/shift | Q/shift |
| ঞ | U+099E | X/shift | X/shift | Y/shift |
| ট | U+099F | Q/base | X/base | H/base |
| ঠ | U+09A0 | E/shift | E/shift | V/shift |
| ড় | U+09A1 U+09BC | S/shift | S/shift | C/shift |
| ঢ | U+09A2 | Q/shift | Q/shift | Z/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | B/shift |
| দ | U+09A6 | W/base | W/base | N/base |
| ধ | U+09A7 | U/shift | U/shift | N/shift |
| ন | U+09A8 | S/base | S/base | J/base |
| প | U+09AA | I/base | I/base | Z/base |
| ফ | U+09AB | A/shift | A/shift | S/shift |
| ব | U+09AC | A/base | A/base | S/base |
| ভ | U+09AD | K/shift | K/shift | J/shift |
| ম | U+09AE | X/base | P/base | W/base |
| য | U+09AF | O/base | O/base | R/base |
| য় | U+09AF U+09BC | N/base | N/base | V/base |
| র | U+09B0 | D/base | D/base | F/base |
| ল | U+09B2 | E/base | E/base | C/base |
| শ | U+09B6 | Y/base | Y/base | G/base |
| ষ | U+09B7 | D/shift | D/shift | U/shift |
| হ | U+09B9 | Z/base | Z/base | X/base |
| ◌া | U+09BE | F/base | F/base | K/base |
| ◌ী | U+09C0 | G/base | G/base | K/shift |
| ◌ু | U+09C1 | V/base | V/base | E/base |
| ◌ূ | U+09C2 | F/shift | F/shift | I/shift |
| ◌ৃ | U+09C3 | C/shift | C/shift | R/shift |
| ◌ে | U+09C7 | K/base | K/base | D/base |
| ◌ৈ | U+09C8 | R/shift | R/shift | E/shift |
| ◌ো | U+09CB | R/base | R/base | O/base |
| ◌ৌ | U+09CC | V/shift | V/shift | X/shift |
| ◌্ | U+09CD | C/base | C/base | I/base |
| ৎ | U+09CE | Z/shift | Z/shift | T/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-8ed0c088f68ad80a — experimental candidate

**Balance v1:** ineligible; no eligible R/rank. Primary changes versus its published reference: effort +0.957%, cross distance -33.42%, within distance -5.53%.

Assignment changes versus D-e4a6be48881da590: 49 symbols; 49 change physical key; 4 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 49 symbols, 49 physical-key changes, 4 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026101996.json", "seed": 2026101996, "archive_index": 37, "direction": 0.75, "start": "greedy-J1"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E +0.682%, X -23.64%, and W +2.95%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [+0.00595, +0.02353]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

Across individual training/held-out sources and both fingerings, worst observed changes are E +1.076%, X -20.27%, W +0.16%. Order-credit superiority over the reference survives every observed coverage interval: **yes**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.497172 | 0.039748 | 0.289180 | 9.090% | 0.947% | 0.0254% | 0.89714–0.90206 | 0.77886–0.78378 |
| traditional | 1.553954 | 0.090436 | 0.289632 | 9.090% | 0.947% | 0.0254% | 0.89162–0.89655 | 0.77143–0.77636 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.854798 | 0.094880 | 0.017026 | 6.905% | 0.013630 | 0.76858–0.77863 |
| bnwiki/train | traditional | 1.961073 | 0.099137 | 0.035293 | 7.085% | 0.026467 | 0.74643–0.75649 |
| newspaper/train | model-optimal | 1.797403 | 0.083586 | 0.019317 | 6.389% | 0.015617 | 0.77921–0.78674 |
| newspaper/train | traditional | 1.906971 | 0.086866 | 0.039346 | 6.518% | 0.030182 | 0.75318–0.76071 |
| bnwiki/heldout | model-optimal | 1.854397 | 0.094848 | 0.016865 | 6.899% | 0.013496 | 0.76936–0.77956 |
| bnwiki/heldout | traditional | 1.960838 | 0.098802 | 0.035244 | 7.064% | 0.026377 | 0.74696–0.75716 |
| newspaper/heldout | model-optimal | 1.797149 | 0.083440 | 0.019275 | 6.387% | 0.015586 | 0.77939–0.78684 |
| newspaper/heldout | traditional | 1.906563 | 0.086873 | 0.039281 | 6.521% | 0.030152 | 0.75334–0.76080 |
| bard-novel/heldout | model-optimal | 1.799829 | 0.084675 | 0.019956 | 6.458% | 0.016085 | 0.77902–0.78619 |
| bard-novel/heldout | traditional | 1.912121 | 0.086449 | 0.040566 | 6.493% | 0.031172 | 0.75168–0.75885 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-8ed0c088f68ad80a.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| । | U+0964 | T/base | T/base | O/base |
| ◌ঁ | U+0981 | P/shift | P/shift | Z/shift |
| ◌ং | U+0982 | I/shift | I/shift | D/shift |
| ◌ঃ | U+0983 | T/shift | T/shift | Q/shift |
| অ | U+0985 | L/shift | L/shift | I/shift |
| ক | U+0995 | J/base | J/base | A/base |
| খ | U+0996 | N/shift | N/shift | S/shift |
| গ | U+0997 | P/base | Q/base | H/base |
| ঘ | U+0998 | Y/shift | Y/shift | H/shift |
| ঙ | U+0999 | W/shift | W/shift | C/shift |
| চ | U+099A | B/base | B/base | J/shift |
| ছ | U+099B | J/shift | J/shift | Y/base |
| জ | U+099C | H/base | H/base | Q/base |
| ঞ | U+099E | X/shift | X/shift | Y/shift |
| ট | U+099F | Q/base | X/base | T/base |
| ঠ | U+09A0 | E/shift | E/shift | V/shift |
| ড | U+09A1 | H/shift | H/shift | N/shift |
| ড় | U+09A1 U+09BC | S/shift | S/shift | F/shift |
| ঢ | U+09A2 | Q/shift | Q/shift | W/shift |
| ঢ় | U+09A2 U+09BC | G/shift | G/shift | R/shift |
| ণ | U+09A3 | O/shift | O/shift | A/shift |
| ত | U+09A4 | M/base | M/base | U/base |
| থ | U+09A5 | M/shift | M/shift | L/shift |
| দ | U+09A6 | W/base | W/base | N/base |
| ন | U+09A8 | S/base | S/base | J/base |
| প | U+09AA | I/base | I/base | Z/base |
| ফ | U+09AB | A/shift | A/shift | P/shift |
| ব | U+09AC | A/base | A/base | S/base |
| ভ | U+09AD | K/shift | K/shift | B/base |
| ম | U+09AE | X/base | P/base | W/base |
| য | U+09AF | O/base | O/base | R/base |
| য় | U+09AF U+09BC | N/base | N/base | V/base |
| র | U+09B0 | D/base | D/base | F/base |
| ল | U+09B2 | E/base | E/base | C/base |
| শ | U+09B6 | Y/base | Y/base | G/base |
| ষ | U+09B7 | D/shift | D/shift | M/shift |
| স | U+09B8 | U/base | U/base | M/base |
| হ | U+09B9 | Z/base | Z/base | P/base |
| ◌া | U+09BE | F/base | F/base | K/base |
| ◌ী | U+09C0 | G/base | G/base | K/shift |
| ◌ু | U+09C1 | V/base | V/base | X/base |
| ◌ূ | U+09C2 | F/shift | F/shift | X/shift |
| ◌ৃ | U+09C3 | C/shift | C/shift | O/shift |
| ◌ে | U+09C7 | K/base | K/base | D/base |
| ◌ৈ | U+09C8 | R/shift | R/shift | E/shift |
| ◌ো | U+09CB | R/base | R/base | E/base |
| ◌ৌ | U+09CC | V/shift | V/shift | G/shift |
| ◌্ | U+09CD | C/base | C/base | I/base |
| ৎ | U+09CE | Z/shift | Z/shift | T/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

### D-072c558b633d1019 — experimental candidate

**Balance v1:** ineligible; no eligible R/rank. Primary changes versus its published reference: effort +0.185%, cross distance -15.81%, within distance +6.40%.

Assignment changes versus D-e4a6be48881da590: 11 symbols; 11 change physical key; 0 change base/Shift layer. Versus Balance leader D-9ad5412603069cd6: 10 symbols, 10 physical-key changes, 0 layer changes. These count edits, not learned switching difficulty.

Provenance: 1 retained records. First record: `{"file": "results/evaluator-e4/rigorous-v1/runs/D-2026102252.json", "seed": 2026102252, "archive_index": 22, "direction": 0.25, "start": "published-reference"}`. Duplicate appearances and inserted references are not independent rediscoveries.

**Against the same-style Balance leader:** this map has E -0.088%, X -3.45%, and W +15.95%. Its order-credit difference, allowing both maps' unsupported-event bounds, is [-0.04090, -0.02331]. These differences explain which component benefits are exchanged; R determines the ordering across all 81 settings rather than declaring a single component sufficient.

Across individual training/held-out sources and both fingerings, worst observed changes are E +0.260%, X -2.78%, W +7.30%. Order-credit superiority over the reference survives every observed coverage interval: **no**. Engram pair superiority survives every interval: **no**. A 'no' includes overlap or reversal; it does not automatically imply inferiority.

#### Effort components and secondary diagnostics on the training mix

| Fingering | Key effort | Pair effort | Shift effort | Shift share | Repeated-pair share | Escapes | Engram pair credit | Dvorak-7 credit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-optimal | 1.491461 | 0.040824 | 0.279857 | 8.865% | 0.799% | 0.0254% | 0.89162–0.89655 | 0.77316–0.77809 |
| traditional | 1.566181 | 0.143635 | 0.280308 | 8.865% | 0.799% | 0.0254% | 0.87488–0.87981 | 0.75500–0.75993 |

#### Individual-source scores

| Source | Fingering | J1 | X (u/window) | W (u/unit) | Cross SF rate | Within SF/unit | Order credit bounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | 1.839047 | 0.115944 | 0.019723 | 8.757% | 0.016228 | 0.72752–0.73757 |
| bnwiki/train | traditional | 2.035506 | 0.120883 | 0.061489 | 9.036% | 0.048720 | 0.65593–0.66599 |
| newspaper/train | model-optimal | 1.785236 | 0.109718 | 0.021210 | 8.325% | 0.017628 | 0.72658–0.73411 |
| newspaper/train | traditional | 1.944743 | 0.114600 | 0.056500 | 8.489% | 0.044536 | 0.66554–0.67306 |
| bnwiki/heldout | model-optimal | 1.838775 | 0.116121 | 0.019694 | 8.773% | 0.016267 | 0.72756–0.73775 |
| bnwiki/heldout | traditional | 2.035121 | 0.120785 | 0.061414 | 9.041% | 0.048709 | 0.65625–0.66644 |
| newspaper/heldout | model-optimal | 1.784949 | 0.109645 | 0.021166 | 8.317% | 0.017590 | 0.72674–0.73420 |
| newspaper/heldout | traditional | 1.944766 | 0.114711 | 0.056578 | 8.494% | 0.044581 | 0.66547–0.67292 |
| bard-novel/heldout | model-optimal | 1.785612 | 0.109988 | 0.020964 | 8.313% | 0.017424 | 0.72737–0.73454 |
| bard-novel/heldout | traditional | 1.947031 | 0.115096 | 0.056821 | 8.478% | 0.044768 | 0.66588–0.67305 |

#### Key map and symbol relocations

[Full base/Shift keyboard diagram](layouts/D-072c558b633d1019.svg). Orange keys differ from the published same-style reference.

| Symbol | NFC code points | Published reference | Balance leader | This candidate |
| --- | --- | --- | --- | --- |
| ◌ঁ | U+0981 | P/shift | P/shift | O/shift |
| গ | U+0997 | P/base | Q/base | Q/base |
| ঙ | U+0999 | W/shift | W/shift | Z/shift |
| ট | U+099F | Q/base | X/base | Z/base |
| ড় | U+09A1 U+09BC | S/shift | S/shift | P/shift |
| ণ | U+09A3 | O/shift | O/shift | S/shift |
| প | U+09AA | I/base | I/base | O/base |
| ম | U+09AE | X/base | P/base | I/base |
| য | U+09AF | O/base | O/base | X/base |
| হ | U+09B9 | Z/base | Z/base | P/base |
| ৎ | U+09CE | Z/shift | Z/shift | W/shift |

Only the 52 searched symbol assignments differ. Fixed digits/punctuation and the style grammar remain unchanged. A layer change on the same physical key can change J1/Shift without changing projected physical-key movement. Full differences against every other reported same-style candidate are in layout-differences.csv.

## 4. Differences between candidates of the same style

Each cell is changed symbol assignments. Zero means identical complete searched assignments. Physical-key and layer-change counts, and the individual symbols, are in the companion CSVs. A and D are not mixed in this comparison.

### Style A

| Alias | Candidate |
| --- | --- |
| A1 | A-18fe73cb912ae3f1 |
| A2 | A-a280bdc4ca72c6c7 |
| A3 | A-36f3428c3f344a54 |
| A4 | A-3270b803ada27b63 |
| A5 | A-cd1cedf0ef5f7fe3 |
| A6 | A-70dc91ce76c7391e |
| A7 | A-4dfc1837861ac886 |
| A8 | A-7c36e8f26e6c7142 |

| From / to | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 0 | 45 | 25 | 24 | 22 | 22 | 22 | 41 |
| A2 | 45 | 0 | 44 | 44 | 42 | 42 | 42 | 47 |
| A3 | 25 | 44 | 0 | 2 | 4 | 5 | 23 | 43 |
| A4 | 24 | 44 | 2 | 0 | 2 | 4 | 24 | 43 |
| A5 | 22 | 42 | 4 | 2 | 0 | 2 | 23 | 43 |
| A6 | 22 | 42 | 5 | 4 | 2 | 0 | 23 | 43 |
| A7 | 22 | 42 | 23 | 24 | 23 | 23 | 0 | 42 |
| A8 | 41 | 47 | 43 | 43 | 43 | 43 | 42 | 0 |

### Style D

| Alias | Candidate |
| --- | --- |
| D1 | D-e4a6be48881da590 |
| D2 | D-9ad5412603069cd6 |
| D3 | D-eb3bf7d2da4f048e |
| D4 | D-a3a1484044fb8d5e |
| D5 | D-c4028c28dc54b209 |
| D6 | D-f4e1710b3ec62eb8 |
| D7 | D-48319b4b30582e8c |
| D8 | D-8e3f1abe1434b3ea |
| D9 | D-8ed0c088f68ad80a |
| D10 | D-072c558b633d1019 |

| From / to | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 0 | 3 | 5 | 2 | 4 | 6 | 14 | 44 | 49 | 11 |
| D2 | 3 | 0 | 2 | 2 | 4 | 9 | 17 | 43 | 49 | 10 |
| D3 | 5 | 2 | 0 | 4 | 5 | 11 | 17 | 43 | 49 | 12 |
| D4 | 2 | 2 | 4 | 0 | 2 | 8 | 16 | 44 | 49 | 11 |
| D5 | 4 | 4 | 5 | 2 | 0 | 10 | 16 | 44 | 48 | 13 |
| D6 | 6 | 9 | 11 | 8 | 10 | 0 | 14 | 43 | 50 | 16 |
| D7 | 14 | 17 | 17 | 16 | 16 | 14 | 0 | 42 | 47 | 24 |
| D8 | 44 | 43 | 43 | 44 | 44 | 43 | 42 | 0 | 31 | 45 |
| D9 | 49 | 49 | 49 | 49 | 48 | 50 | 47 | 31 | 0 | 48 |
| D10 | 11 | 10 | 12 | 11 | 13 | 16 | 24 | 45 | 48 | 0 |

## 5. Public fixed Bangla layouts: a matched held-out comparison

The six registered fixed-layout baselines are UniJoy, National (Jatiya), Bornona, Probhat, Windows Default and Munir Optima (uni). Their frozen maps/provenance are under data/baselines/; UniJoy uses the vendored Kala file. This is the registry’s fixed-layout comparison set, not a claim to cover every publicly available Bangla keyboard version. Phonetic layouts are excluded by the repository’s owner decision. No new baseline has been added.

Baseline action encodings use minimum presses with traditional-grid tie-breaks fixed across fingerings, including their supported formatting and vowel rules. The tables below score every layout under the same fingering and the same equal-weight three-source held-out average. They do not combine per-metric best-of-grid numbers into one fictitious scenario. Historical official baseline tables may differ slightly because their optimal-grid encoder was not fixed in the same way.

No baseline receives a Balance v1 R/rank: the formula’s frozen A/D symbol problem, reference, training calibration and coverage rules are not defined for these different layout grammars. Ranking their held-out J1 or credit diagnostics is a separate comparison.

### model-optimal: effort and movement

| Layout | J1 | X (u/window) | W (u/unit) | Cross SF rate | Shift share | Escaped units |
| --- | --- | --- | --- | --- | --- | --- |
| D-e4a6be48881da590 | 1.800026 | 0.133171 | 0.019445 | 10.283% | 8.694% | 0.0244% |
| D-48319b4b30582e8c | 1.801316 | 0.129574 | 0.018490 | 10.055% | 8.621% | 0.0244% |
| D-f4e1710b3ec62eb8 | 1.801458 | 0.131917 | 0.019106 | 10.170% | 8.694% | 0.0244% |
| D-072c558b633d1019 | 1.803112 | 0.111918 | 0.020608 | 8.467% | 8.694% | 0.0244% |
| D-9ad5412603069cd6 | 1.804702 | 0.116219 | 0.017613 | 8.865% | 8.694% | 0.0244% |
| D-a3a1484044fb8d5e | 1.804774 | 0.117694 | 0.017469 | 9.012% | 8.694% | 0.0244% |
| D-eb3bf7d2da4f048e | 1.804913 | 0.116188 | 0.017613 | 8.862% | 8.694% | 0.0244% |
| D-c4028c28dc54b209 | 1.805221 | 0.117711 | 0.017472 | 9.014% | 8.694% | 0.0244% |
| D-8e3f1abe1434b3ea | 1.808747 | 0.104891 | 0.019514 | 7.893% | 8.703% | 0.0244% |
| D-8ed0c088f68ad80a | 1.817125 | 0.087654 | 0.018699 | 6.581% | 8.902% | 0.0244% |
| A-18fe73cb912ae3f1 | 1.843229 | 0.116043 | 0.018519 | 9.306% | 8.302% | 0.0209% |
| A-a280bdc4ca72c6c7 | 1.848790 | 0.139605 | 0.015398 | 10.707% | 8.373% | 0.0209% |
| A-4dfc1837861ac886 | 1.849943 | 0.086522 | 0.018329 | 6.977% | 8.302% | 0.0209% |
| A-36f3428c3f344a54 | 1.850189 | 0.091318 | 0.015219 | 7.157% | 8.302% | 0.0209% |
| A-cd1cedf0ef5f7fe3 | 1.850205 | 0.091312 | 0.015179 | 7.154% | 8.302% | 0.0209% |
| A-3270b803ada27b63 | 1.850218 | 0.091302 | 0.015203 | 7.153% | 8.302% | 0.0209% |
| A-70dc91ce76c7391e | 1.850327 | 0.091289 | 0.015132 | 7.153% | 8.302% | 0.0209% |
| A-7c36e8f26e6c7142 | 1.906229 | 0.062027 | 0.013257 | 4.393% | 8.373% | 0.0209% |
| baseline:Windows Default | 2.154327 | 0.171891 | 0.073726 | 13.262% | 13.244% | 2.5715% |
| baseline:Probhat | 2.561472 | 0.135470 | 0.078067 | 10.055% | 9.901% | 0.0160% |
| baseline:Munir Optima (uni) | 2.590847 | 0.179446 | 0.139010 | 12.288% | 12.884% | 0.0974% |
| baseline:Bornona | 2.618413 | 0.124641 | 0.096431 | 8.897% | 18.106% | 0.0166% |
| baseline:UniJoy | 2.808219 | 0.334545 | 0.182938 | 22.250% | 17.728% | 0.0128% |
| baseline:National (Jatiya) | 2.912252 | 0.327629 | 0.218022 | 22.275% | 16.040% | 0.0702% |

| Layout | Engram pair credit | Engram order credit | Dvorak-7 credit | Pair coverage | Triple coverage |
| --- | --- | --- | --- | --- | --- |
| D-e4a6be48881da590 | 0.89386–0.89849 | 0.74783–0.75610 | 0.77833–0.78296 | 99.537% | 99.173% |
| D-48319b4b30582e8c | 0.89127–0.89590 | 0.74561–0.75389 | 0.77648–0.78111 | 99.537% | 99.173% |
| D-f4e1710b3ec62eb8 | 0.89404–0.89867 | 0.74812–0.75639 | 0.77831–0.78293 | 99.537% | 99.173% |
| D-072c558b633d1019 | 0.89189–0.89652 | 0.72723–0.73550 | 0.77391–0.77854 | 99.537% | 99.173% |
| D-9ad5412603069cd6 | 0.89586–0.90049 | 0.75849–0.76676 | 0.77808–0.78271 | 99.537% | 99.173% |
| D-a3a1484044fb8d5e | 0.89425–0.89888 | 0.75192–0.76019 | 0.77745–0.78208 | 99.537% | 99.173% |
| D-eb3bf7d2da4f048e | 0.89579–0.90042 | 0.75849–0.76676 | 0.77795–0.78258 | 99.537% | 99.173% |
| D-c4028c28dc54b209 | 0.89426–0.89889 | 0.75192–0.76019 | 0.77749–0.78212 | 99.537% | 99.173% |
| D-8e3f1abe1434b3ea | 0.89704–0.90166 | 0.76630–0.77457 | 0.77961–0.78424 | 99.537% | 99.173% |
| D-8ed0c088f68ad80a | 0.89746–0.90209 | 0.77593–0.78420 | 0.77992–0.78455 | 99.537% | 99.173% |
| A-18fe73cb912ae3f1 | 0.89683–0.90126 | 0.76146–0.76947 | 0.78123–0.78565 | 99.558% | 99.199% |
| A-a280bdc4ca72c6c7 | 0.91133–0.91575 | 0.82322–0.83123 | 0.79773–0.80215 | 99.558% | 99.199% |
| A-4dfc1837861ac886 | 0.89954–0.90396 | 0.78113–0.78914 | 0.78120–0.78562 | 99.558% | 99.199% |
| A-36f3428c3f344a54 | 0.89515–0.89957 | 0.76811–0.77611 | 0.77882–0.78324 | 99.558% | 99.199% |
| A-cd1cedf0ef5f7fe3 | 0.89527–0.89969 | 0.76816–0.77617 | 0.77878–0.78320 | 99.558% | 99.199% |
| A-3270b803ada27b63 | 0.89527–0.89969 | 0.76811–0.77612 | 0.77879–0.78322 | 99.558% | 99.199% |
| A-70dc91ce76c7391e | 0.89527–0.89969 | 0.76818–0.77619 | 0.77868–0.78310 | 99.558% | 99.199% |
| A-7c36e8f26e6c7142 | 0.89341–0.89783 | 0.74116–0.74917 | 0.77567–0.78009 | 99.558% | 99.199% |
| baseline:Windows Default | 0.87510–0.89446 | 0.78968–0.82152 | 0.76199–0.78135 | 98.064% | 96.816% |
| baseline:Probhat | 0.81950–0.85430 | 0.69278–0.74339 | 0.64699–0.68179 | 96.520% | 94.939% |
| baseline:Munir Optima (uni) | 0.80862–0.81409 | 0.57363–0.58011 | 0.69085–0.69632 | 99.453% | 99.352% |
| baseline:Bornona | 0.82793–0.83287 | 0.65694–0.66584 | 0.68839–0.69333 | 99.506% | 99.111% |
| baseline:UniJoy | 0.80972–0.81457 | 0.60221–0.61101 | 0.72489–0.72974 | 99.514% | 99.119% |
| baseline:National (Jatiya) | 0.77970–0.78450 | 0.52597–0.53449 | 0.69516–0.69996 | 99.520% | 99.149% |

#### A-a280bdc4ca72c6c7 against each public baseline

| Baseline | Candidate J1 change | Candidate X change | Candidate W change | Pair-credit relation | Order-credit relation |
| --- | --- | --- | --- | --- | --- |
| Windows Default | -14.18% | -18.78% | -79.11% | candidate higher, bounds separated | candidate higher, bounds separated |
| Probhat | -27.82% | +3.05% | -80.28% | candidate higher, bounds separated | candidate higher, bounds separated |
| Munir Optima (uni) | -28.64% | -22.20% | -88.92% | candidate higher, bounds separated | candidate higher, bounds separated |
| Bornona | -29.39% | +12.01% | -84.03% | candidate higher, bounds separated | candidate higher, bounds separated |
| UniJoy | -34.17% | -58.27% | -91.58% | candidate higher, bounds separated | candidate higher, bounds separated |
| National (Jatiya) | -36.52% | -57.39% | -92.94% | candidate higher, bounds separated | candidate higher, bounds separated |

**Reading this comparison:** under model-optimal, A-a280bdc4ca72c6c7 has lower held-out modeled J1 than 6 of the six registered baselines. Its cross-space distance is higher than: Probhat, Bornona. Its order credit is conclusively lower, allowing coverage bounds, than: none of these six. These are scope-specific modeled comparisons; escapes and encoding differences remain relevant.

#### D-9ad5412603069cd6 against each public baseline

| Baseline | Candidate J1 change | Candidate X change | Candidate W change | Pair-credit relation | Order-credit relation |
| --- | --- | --- | --- | --- | --- |
| Windows Default | -16.23% | -32.39% | -76.11% | candidate higher, bounds separated | candidate lower, bounds separated |
| Probhat | -29.54% | -14.21% | -77.44% | candidate higher, bounds separated | candidate higher, bounds separated |
| Munir Optima (uni) | -30.34% | -35.23% | -87.33% | candidate higher, bounds separated | candidate higher, bounds separated |
| Bornona | -31.08% | -6.76% | -81.73% | candidate higher, bounds separated | candidate higher, bounds separated |
| UniJoy | -35.74% | -65.26% | -90.37% | candidate higher, bounds separated | candidate higher, bounds separated |
| National (Jatiya) | -38.03% | -64.53% | -91.92% | candidate higher, bounds separated | candidate higher, bounds separated |

**Reading this comparison:** under model-optimal, D-9ad5412603069cd6 has lower held-out modeled J1 than 6 of the six registered baselines. Its cross-space distance is higher than: none of these six. Its order credit is conclusively lower, allowing coverage bounds, than: Windows Default. These are scope-specific modeled comparisons; escapes and encoding differences remain relevant.

### traditional: effort and movement

| Layout | J1 | X (u/window) | W (u/unit) | Cross SF rate | Shift share | Escaped units |
| --- | --- | --- | --- | --- | --- | --- |
| D-8e3f1abe1434b3ea | 1.905291 | 0.097064 | 0.037866 | 7.335% | 8.703% | 0.0244% |
| D-8ed0c088f68ad80a | 1.926507 | 0.090708 | 0.038364 | 6.693% | 8.902% | 0.0244% |
| A-a280bdc4ca72c6c7 | 1.944367 | 0.134048 | 0.034313 | 9.655% | 8.373% | 0.0209% |
| D-48319b4b30582e8c | 1.972671 | 0.117999 | 0.052617 | 8.925% | 8.621% | 0.0244% |
| D-9ad5412603069cd6 | 1.974300 | 0.118380 | 0.055773 | 8.856% | 8.694% | 0.0244% |
| D-eb3bf7d2da4f048e | 1.974511 | 0.118349 | 0.055765 | 8.853% | 8.694% | 0.0244% |
| D-f4e1710b3ec62eb8 | 1.975069 | 0.122109 | 0.055394 | 9.117% | 8.694% | 0.0244% |
| D-072c558b633d1019 | 1.975639 | 0.116864 | 0.058271 | 8.671% | 8.694% | 0.0244% |
| D-a3a1484044fb8d5e | 1.975792 | 0.120587 | 0.057045 | 9.016% | 8.694% | 0.0244% |
| D-c4028c28dc54b209 | 1.976215 | 0.120603 | 0.057022 | 9.018% | 8.694% | 0.0244% |
| D-e4a6be48881da590 | 1.976350 | 0.123270 | 0.057222 | 9.205% | 8.694% | 0.0244% |
| A-4dfc1837861ac886 | 1.983954 | 0.092253 | 0.042162 | 7.138% | 8.302% | 0.0209% |
| A-18fe73cb912ae3f1 | 1.985967 | 0.107311 | 0.043528 | 8.348% | 8.302% | 0.0209% |
| A-3270b803ada27b63 | 2.023248 | 0.102518 | 0.052587 | 7.550% | 8.302% | 0.0209% |
| A-cd1cedf0ef5f7fe3 | 2.023285 | 0.102533 | 0.052592 | 7.551% | 8.302% | 0.0209% |
| A-36f3428c3f344a54 | 2.023497 | 0.102470 | 0.052650 | 7.548% | 8.302% | 0.0209% |
| A-70dc91ce76c7391e | 2.023522 | 0.102524 | 0.052607 | 7.550% | 8.302% | 0.0209% |
| A-7c36e8f26e6c7142 | 2.114447 | 0.073691 | 0.053826 | 5.074% | 8.373% | 0.0209% |
| baseline:Windows Default | 2.210507 | 0.171994 | 0.086572 | 12.776% | 13.244% | 2.5715% |
| baseline:Munir Optima (uni) | 2.586298 | 0.186330 | 0.104855 | 13.069% | 12.884% | 0.0974% |
| baseline:Probhat | 2.637441 | 0.168799 | 0.089727 | 10.859% | 9.901% | 0.0160% |
| baseline:Bornona | 2.684508 | 0.157260 | 0.107819 | 9.799% | 18.106% | 0.0166% |
| baseline:UniJoy | 2.839467 | 0.240791 | 0.152890 | 16.907% | 17.728% | 0.0128% |
| baseline:National (Jatiya) | 2.865663 | 0.232841 | 0.162277 | 15.827% | 16.040% | 0.0702% |

| Layout | Engram pair credit | Engram order credit | Dvorak-7 credit | Pair coverage | Triple coverage |
| --- | --- | --- | --- | --- | --- |
| D-8e3f1abe1434b3ea | 0.88849–0.89312 | 0.73208–0.74036 | 0.77105–0.77568 | 99.537% | 99.173% |
| D-8ed0c088f68ad80a | 0.89164–0.89627 | 0.75066–0.75893 | 0.77227–0.77689 | 99.537% | 99.173% |
| A-a280bdc4ca72c6c7 | 0.90314–0.90756 | 0.79717–0.80518 | 0.78605–0.79047 | 99.558% | 99.199% |
| D-48319b4b30582e8c | 0.87854–0.88317 | 0.69231–0.70058 | 0.76085–0.76548 | 99.537% | 99.173% |
| D-9ad5412603069cd6 | 0.87897–0.88359 | 0.68765–0.69593 | 0.76034–0.76497 | 99.537% | 99.173% |
| D-eb3bf7d2da4f048e | 0.87889–0.88352 | 0.68765–0.69593 | 0.76021–0.76484 | 99.537% | 99.173% |
| D-f4e1710b3ec62eb8 | 0.87752–0.88215 | 0.67808–0.68635 | 0.75932–0.76395 | 99.537% | 99.173% |
| D-072c558b633d1019 | 0.87559–0.88022 | 0.66253–0.67081 | 0.75631–0.76094 | 99.537% | 99.173% |
| D-a3a1484044fb8d5e | 0.87691–0.88154 | 0.67910–0.68737 | 0.75955–0.76418 | 99.537% | 99.173% |
| D-c4028c28dc54b209 | 0.87693–0.88156 | 0.67910–0.68737 | 0.75959–0.76422 | 99.537% | 99.173% |
| D-e4a6be48881da590 | 0.87698–0.88161 | 0.67838–0.68665 | 0.75919–0.76382 | 99.537% | 99.173% |
| A-4dfc1837861ac886 | 0.89305–0.89747 | 0.75970–0.76771 | 0.77072–0.77514 | 99.558% | 99.199% |
| A-18fe73cb912ae3f1 | 0.88998–0.89441 | 0.74121–0.74922 | 0.76958–0.77401 | 99.558% | 99.199% |
| A-3270b803ada27b63 | 0.88459–0.88902 | 0.74130–0.74931 | 0.76410–0.76852 | 99.558% | 99.199% |
| A-cd1cedf0ef5f7fe3 | 0.88459–0.88901 | 0.74131–0.74932 | 0.76407–0.76849 | 99.558% | 99.199% |
| A-36f3428c3f344a54 | 0.88447–0.88889 | 0.74130–0.74931 | 0.76401–0.76843 | 99.558% | 99.199% |
| A-70dc91ce76c7391e | 0.88457–0.88900 | 0.74124–0.74925 | 0.76397–0.76839 | 99.558% | 99.199% |
| A-7c36e8f26e6c7142 | 0.87683–0.88126 | 0.70113–0.70914 | 0.75480–0.75922 | 99.558% | 99.199% |
| baseline:Windows Default | 0.87305–0.89240 | 0.78661–0.81845 | 0.75995–0.77931 | 98.064% | 96.816% |
| baseline:Munir Optima (uni) | 0.82229–0.82775 | 0.62407–0.63055 | 0.69385–0.69932 | 99.453% | 99.352% |
| baseline:Probhat | 0.81874–0.85354 | 0.67129–0.72189 | 0.64784–0.68264 | 96.520% | 94.939% |
| baseline:Bornona | 0.82348–0.82842 | 0.63573–0.64462 | 0.68237–0.68731 | 99.506% | 99.111% |
| baseline:UniJoy | 0.81477–0.81962 | 0.58940–0.59820 | 0.71198–0.71683 | 99.514% | 99.119% |
| baseline:National (Jatiya) | 0.80602–0.81082 | 0.56132–0.56984 | 0.70006–0.70486 | 99.520% | 99.149% |

#### A-a280bdc4ca72c6c7 against each public baseline

| Baseline | Candidate J1 change | Candidate X change | Candidate W change | Pair-credit relation | Order-credit relation |
| --- | --- | --- | --- | --- | --- |
| Windows Default | -12.04% | -22.06% | -60.36% | candidate higher, bounds separated | unresolved: bounds overlap |
| Munir Optima (uni) | -24.82% | -28.06% | -67.28% | candidate higher, bounds separated | candidate higher, bounds separated |
| Probhat | -26.28% | -20.59% | -61.76% | candidate higher, bounds separated | candidate higher, bounds separated |
| Bornona | -27.57% | -14.76% | -68.17% | candidate higher, bounds separated | candidate higher, bounds separated |
| UniJoy | -31.52% | -44.33% | -77.56% | candidate higher, bounds separated | candidate higher, bounds separated |
| National (Jatiya) | -32.15% | -42.43% | -78.85% | candidate higher, bounds separated | candidate higher, bounds separated |

**Reading this comparison:** under traditional, A-a280bdc4ca72c6c7 has lower held-out modeled J1 than 6 of the six registered baselines. Its cross-space distance is higher than: none of these six. Its order credit is conclusively lower, allowing coverage bounds, than: none of these six. These are scope-specific modeled comparisons; escapes and encoding differences remain relevant.

#### D-9ad5412603069cd6 against each public baseline

| Baseline | Candidate J1 change | Candidate X change | Candidate W change | Pair-credit relation | Order-credit relation |
| --- | --- | --- | --- | --- | --- |
| Windows Default | -10.69% | -31.17% | -35.58% | unresolved: bounds overlap | candidate lower, bounds separated |
| Munir Optima (uni) | -23.66% | -36.47% | -46.81% | candidate higher, bounds separated | candidate higher, bounds separated |
| Probhat | -25.14% | -29.87% | -37.84% | candidate higher, bounds separated | unresolved: bounds overlap |
| Bornona | -26.46% | -24.72% | -48.27% | candidate higher, bounds separated | candidate higher, bounds separated |
| UniJoy | -30.47% | -50.84% | -63.52% | candidate higher, bounds separated | candidate higher, bounds separated |
| National (Jatiya) | -31.10% | -49.16% | -65.63% | candidate higher, bounds separated | candidate higher, bounds separated |

**Reading this comparison:** under traditional, D-9ad5412603069cd6 has lower held-out modeled J1 than 6 of the six registered baselines. Its cross-space distance is higher than: none of these six. Its order credit is conclusively lower, allowing coverage bounds, than: Windows Default. These are scope-specific modeled comparisons; escapes and encoding differences remain relevant.

## 6. Interpreting the public comparison

Lower J1, lower SF distances and higher movement credit are distinct modeled findings; no one table establishes overall comfort. Interval-separated credit superiority is stated explicitly; overlapping intervals remain unresolved. Escaped text is outside the scored movement domain and contributes no modeled key effort: Windows Default’s larger escape share is a material comparison limitation. Extra presses, Shift use and vowel formatting differ between grammars.

Pair models share finger/row/home features with J1 and with the SF diagnostics. Agreement is robustness to some modeled assumptions, not independent human validation. Engram repeated-key credit differs from J1’s identical-action pair treatment. Distance uses key centers, not measured finger travel. Source/fingering changes can reverse individual diagnostics even for a primary balance winner.

## 7. Decision status

Keep Goti and Jhor as published. Balance v1 is the adopted experimental formula with frozen constants; its two leaders are research candidates for comparison. Eligibility applies to the primary training mix, not an automatic promise that every corpus/fingering stays within the same caps. The full per-source CSVs expose these limits. The next validation is independent new text and Bangla human preference/sustained typing studies, with priorities preregistered before examining those outcomes.

Both reports and their datasets were generated without changing model constants, official search, challenge scoring, reproduction locks, the website or existing results. run-manifest.json records hashes; validation.json records checks.
