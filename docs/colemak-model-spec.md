# Colemak Mod-DH model — frozen Phase 1 specification

This is the regression-tested mathematical specification of the original
Colemak Mod-DH analysis, as reproduced by `bangla_dh.colemak` and
`bangla_dh.geometry`. Every statement here is checked by `tests/` or by
`bangla-dh reproduce-colemak`; the reproduction record is
[results/phase1/REPORT.md](../results/phase1/REPORT.md).

It also lists where the Bangla-DH research specification (v1.0) differs from
what the original actually computes (section 7). Later phases build on this
document, not on the summary in the research specification.

## 1. Pinned sources

| Source | Pin | Use |
| --- | --- | --- |
| [stevep99/keyboard-layout-analysis-tool](https://github.com/stevep99/keyboard-layout-analysis-tool) | commit `5e7e869` (2024-01-21, Kotlin) | Reference implementation. No license is declared, so it is fetched (`bangla-dh fetch-upstream`), not copied. 107 files pinned by SHA-256. |
| [colemakmods/mod-dh](https://github.com/colemakmods/mod-dh) `gh-pages` | commit `1d23c82` (2026-10-03), CC0 | Published pages and the analyzer resources, vendored in `reference/colemak-dh-resources` (59 files; 57 byte-identical to the analyzer repository, plus `colemak_dhm.keyb`). |

`reference/sources.lock.json` holds every hash. `bangla-dh verify-reference`
checks them.

## 2. Analyzer inputs

**Layout** (`*.keyb`): one keyboard row per non-empty line, keys separated by
spaces, `#` starts a comment. A single-character key also receives its
default shifted character: the other case for a cased letter, the US-shift
symbol for `1-0 ' - = [ ] ; , . /`. Keys listing several characters keep them
as written. Default fingers by column: 0-3 → 0-3, 4 → 3, 5 → 6, 6-9 → 6-9,
≥10 → 9. Fingers are numbered 0 (left pinky) to 9 (right pinky); 4-5 are thumbs
and never used.

**Configuration** (`effort_*_config.dat`): sections `effort: n`,
`fingers: n`, `penalties:` and `type:`. Grid sections are aligned to the
bottom of the layout (a 4-row grid applied to a 3-row layout skips its first
row). Penalty rows: same finger, then pinky-ring, ring-middle, middle-index,
each for row differences 0, 1, ≥2.

| Pair | Same row | 1 row apart | 2+ rows apart | In configs |
| --- | --- | --- | --- | --- |
| same finger | 2.5 | 3.0 | 4.0 | all |
| pinky–ring | 0.5 | 1.0 | 1.5 | all |
| ring–middle | 0.1 | 0.2 | 0.3 | all |
| middle–index | **−0.2** | **−0.1** | **0.0** | ergonomic, traditional, matrix (not alternative) |

**Frequencies** (`*.freq`): lines `token count`; lines *beginning* with `#`
are skipped (so the `#` character never has a frequency). Tokens are
upper-cased. Only single characters in the layout alphabet and bigrams of two
alphabet characters are kept. Each list is normalized separately in binary32:
`freq = float32(count) / float32(Σ counts)`. Characters outside the layout,
including space, carry no effort and break no bigram; bigrams across a space
are not counted (`FreqAnalysis` never forms them).

## 3. Effort

Let `u_c` be the character frequency, `v_ab` the bigram frequency, `K(k)` the
configured effort of key `k`, `f(k)` its finger and `r(k)` its row.

    E_base = Σ_c u_c · K(key(c))                       (both characters of a key share K)
    E_sfb  = Σ_{a≠b, f(a)=f(b)} v_ab · S[min(2, |r(a)−r(b)|)]
    E_nfb  = Σ_{|f(a)−f(b)|=1} v_ab · N[outer(a,b)][min(2, |r(a)−r(b)|)]
    E      = E_base + E_sfb + E_nfb

* Same-finger pairs need two *different characters*: `ee` is free, but `;:`
  (same key, different characters) is a same-finger pair with row difference 0.
* `outer` is the finger farther from the index (pinky over ring over middle);
  right-hand fingers are mirrored onto the left-hand table.
* Shift has no cost: `:` costs exactly what `;` costs.
* Per finger, components are summed in binary64; the totals include only
  fingers whose base effort is positive.

Published table values: `base = E_base`, `bigram = E_sfb + E_nfb`,
`total = E`, `SFB% = 100 · Σ v_ab` over same-finger pairs. Values are printed
with Java `%.3f` (half-up on the shortest decimal representation).

**Reproduced:** all 60 values of the compare.html table (15 layouts) exactly,
using `layout_full`, `en_books.freq` and the configuration each layout is
assigned in the upstream `keyboard_analysis_all.sh`.

## 4. Key effort grid (model.html)

The analyzer does not compute key efforts; it reads the one-decimal grid in
the config file. The grid comes from a separate, unpublished generator
described on model.html:

    K(k, f) = P_f + sqrt( (P_f · F_y)² + (P_x · F_x)² ),   F = log2(1 + P_d · D)

| Constant | Value | Status |
| --- | --- | --- |
| P_f index / middle / ring / pinky | 1.0 / 1.1 / 1.3 / 1.6 | published |
| P_x (lateral multiplier) | 2.0 | published |
| Approach angle | 10° staggered, 0° split matrix | published |
| Activation area | key footprint inset by 0.3u on each side | published |
| Resting point (dx, dy↑) index / middle / ring / pinky | (−0.04, −0.32) / (0.03, 0.16) / (0.00, 0.08) / (0.01, 0.09); x mirrored for the right hand | published |
| **P_d** | **1.12** | recovered (section 4.1) |
| Contact point | Euclidean nearest point of the activation area to the resting point, on the keyboard plane | recovered |
| Own home key | costs exactly P_f | recovered |
| Finger | the cheapest finger ("optimal"), or the traditional assignment | published |

D_x, D_y are the components of (contact point − resting point) across and
along the forearm: on the left hand the forearm points up and to the right by
the approach angle, on the right hand up and to the left.

### 4.1 Recovering P_d

Scanning P_d from 0.9 to 1.3 (step 0.0005) and counting the one-unit keys
whose model value rounds half-up to the published value over all three
published grids (142 keys) gives a maximum of 138, reached only for
P_d ∈ [1.1195, 1.1220]. 1.12 is the round value inside that interval.
At P_d = 1.12 the largest one-unit deviation is 0.073 (`]` and `'` on ISO),
so every one-unit key is within rounding noise of the published grid, and
the split-matrix grid matches on all 46 one-unit keys. The other choices
were selected the same way; each rejected alternative, at its own best P_d,
matches fewer keys: an activation box of half-width 0.3 (margin 0.2) 82/142,
unmirrored right-hand resting offsets 119/142, no home-key rule 132/142.

### 4.2 Effect of the grid's rounding

Re-running the comparison on unrounded model grids instead of the published
one-decimal grids moves totals by +0.001 to +0.007 and keeps the ranking
(report section 5). The published `effort_traditional_config.dat` gives `]`
5.6 where model.html's grid shows 4.7; the model agrees with 4.7.

### 4.3 ANSI

The 30 main keys and the number row of ANSI and ISO boards have the same
positions, so their model efforts are identical. Only the ANSI-specific keys
(1.5u `\`, 2.25u Enter, 2.25u left Shift) are model-only values with no
published counterpart. The generated grids are in
`results/phase1/effort-grids/`.

## 5. Switching difficulty (learn.html)

For each primary key of the old layout:

    m = 0 unchanged | 0.25 same finger | 0.5 other finger, same hand
        | 0.75 mirrored finger, other hand | 1.0 other finger, other hand
        | per-key override (Colemak-DH: Z X C = 0.25, V = 0)
    C(f) = f^(1+p) / (1+p),   p = log2 0.8 = −0.3219280949…,   f = float32(100 · u_c)
    d = Σ m · C(f) · S2 / S1

S1/S2 are the configured efforts of the old and new key. The implementation
includes the S2/S1 ratio; learn.html's closing formula omits it.

**Reproduced:** keys moved, new-finger moves and Σm for all 11 layouts; d (an
integer on the page) for 10 of 11. Qwpr is published as 18; the model gives
14.41 with S2/S1 and 17.58 without it, so that cell predates the 2021-03-27
update that added the ratio. The experience-curve examples (1, 2, 5, 10 % →
1.47, 2.36, 4.39, 7.03) reproduce exactly.

## 6. The original analyzer and Bangla

The original cannot score Bangla unmodified. `Character.isAlphabetic` is
true for Bangla consonants, independent vowels and vowel signs, none of
which have case, so the default-shift rule pairs each character with itself:
every key holds its character twice, the alphabet reports duplicates and
`E_base` is counted twice. Phase 2 therefore uses its own Bangla symbol
inventory and loaders and keeps this port for English regression only.

Other properties that matter for Bangla:

* No space key, no Shift or AltGr cost and no layer transitions: the model
  covers one character per key position and treats all characters on a key
  as equally easy.
* Frequencies are normalized over the characters present on the layout, so
  scores of layouts with different character sets are not comparable.
* Characters are UTF-16 code units in the original; all of Bangla is in the
  Basic Multilingual Plane, so code units and code points coincide.

## 7. Differences from the Bangla-DH research specification v1.0

| Spec section | Specification says | The original actually does |
| --- | --- | --- |
| 2.3, 6.4 | Pairs other than same-finger, pinky-ring and ring-middle carry no penalty. | Middle–index pairs get −0.2 / −0.1 / 0.0 in the ergonomic, traditional and matrix configs. For Colemak-DH ergonomic this benefit is −0.017 of the 0.065 bigram score; without it 1.735 cannot be reproduced. |
| 2.2, 6.2 | The analyzer computes key effort from the Fitts formula. | It reads a precomputed one-decimal grid; the formula belongs to an unpublished generator. P_d is not published (recovered: 1.12). |
| 6.2 | Contact point to be chosen. | Euclidean nearest point of the inset area; a finger's own home key costs P_f even though the index rests 0.32u below its key centre. |
| 6.4 | B depends on the row difference. | The row difference is capped at 2; repeated characters are excluded; neighbour penalties apply to adjacent fingers only and are booked to the outer finger. |
| 6.3, 6.5 | u_i, v_ij are corpus frequencies. | They are re-normalized over the layout's own characters and pairs (binary32). Space and cross-space bigrams are absent. |
| 2.4 | Two versions of the switching formula; choose by implementation. | The implementation uses S2/S1 and f in percent (binary32). One published cell (Qwpr) still uses the older formula. |
| 4 | ANSI keyboard. | The published grids are ISO. The main block is identical on ANSI; ANSI-only keys are model values. |

## 8. Reproducing

```bash
pip install -e .
bangla-dh fetch-upstream
bangla-dh reproduce-colemak
python -m unittest discover -s tests
```

`reproduce-colemak` exits non-zero unless every acceptance check passes and
writes `results/phase1/` (report, full-precision record, calibration curve,
model grids and configs, Kala data inventory, run manifest with SHA-256 of
inputs and outputs).
