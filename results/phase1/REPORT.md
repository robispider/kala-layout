# Phase 1 reproduction report

Generated 2026-10-09T20:23:37+00:00 by bangla-dh 0.1.0 (Python 3.11.9), Kala commit `ca2a1f9befaa` (uncommitted changes).
Overall acceptance: **PASSED**.

| Check | Result |
| --- | --- |
| vendored resources verified | pass |
| comparison table exact | pass |
| switching table exact or explained | pass |
| experience curve exact | pass |
| effort grid one unit keys within 0 1 | pass |

Upstream analyzer source: verified at the pinned commit.

## 1. Layout comparison (compare.html)

60/60 published values reproduced exactly (15/15 rows).

| Layout | Config | Base | SFB % | Bigram | Total | Match |
| --- | --- | --- | --- | --- | --- | --- |
| Colemak-DH | matrix | 1.661 | 1.67% | 0.065 | 1.726 | yes |
| Colemak-DH | ergonomic | 1.670 | 1.67% | 0.065 | 1.735 | yes |
| Soul | alternative | 1.681 | 1.82% | 0.086 | 1.767 | yes |
| MTGAP | traditional | 1.731 | 1.25% | 0.056 | 1.787 | yes |
| Colemak | ergonomic | 1.739 | 1.67% | 0.063 | 1.802 | yes |
| Workman | traditional | 1.710 | 3.15% | 0.107 | 1.817 | yes |
| Colemak | traditional | 1.773 | 1.67% | 0.063 | 1.836 | yes |
| Halmak | traditional | 1.760 | 2.96% | 0.124 | 1.884 | yes |
| Asset | traditional | 1.795 | 3.12% | 0.117 | 1.911 | yes |
| Dvorak | traditional | 1.843 | 2.63% | 0.080 | 1.923 | yes |
| Norman | traditional | 1.711 | 6.42% | 0.215 | 1.926 | yes |
| qgmlwyfub | traditional | 1.793 | 4.66% | 0.143 | 1.936 | yes |
| Qwpr | traditional | 1.830 | 4.06% | 0.157 | 1.987 | yes |
| Minimak-8key | traditional | 1.863 | 4.10% | 0.142 | 2.005 | yes |
| Qwerty | traditional | 2.169 | 6.58% | 0.231 | 2.400 | yes |

## 2. Switching difficulty (learn.html)

10/11 rows reproduced exactly; 1 explained.

| Layout | Keys moved (finger) | Keys moved | Σm | d | d without S2/S1 | Match |
| --- | --- | --- | --- | --- | --- | --- |
| Minimak-8key | 3 | 8 | 3.50 | 12.55 | 15.05 | yes |
| Qwpr | 2 | 11 | 4.25 | 14.41 | 17.58 | published d = 18 |
| Norman | 4 | 15 | 5.75 | 18.90 | 20.34 | yes |
| Asset | 6 | 15 | 6.25 | 20.18 | 19.97 | yes |
| Colemak | 12 | 17 | 8.00 | 28.25 | 30.21 | yes |
| Colemak-DH | 12 | 19 | 9.25 | 28.71 | 32.85 | yes |
| Workman | 13 | 21 | 10.00 | 34.03 | 35.89 | yes |
| qgmlwyfub | 17 | 20 | 12.25 | 42.12 | 44.75 | yes |
| Halmak | 27 | 30 | 19.50 | 58.10 | 57.22 | yes |
| Dvorak | 26 | 33 | 23.25 | 68.21 | 60.99 | yes |
| MTGAP | 26 | 30 | 23.75 | 64.53 | 68.10 | yes |

Qwpr: Published d equals the model without the S2/S1 effort ratio, i.e. this cell predates the 2021-03-27 model update that added the ratio.

## 3. Experience curve

p = log2(0.8) = -0.3219280949.

| f (%) | Published C_f | Reproduced |
| --- | --- | --- |
| 1 | 1.47 | 1.47 |
| 2 | 2.36 | 2.36 |
| 5 | 4.39 | 4.39 |
| 10 | 7.03 | 7.03 |

Specification example (f = 5, m = 0.5, S2/S1 = 1.2): C_f = 4.3921, D_i = 2.6353 with the rounded exponent 0.678; 4.3921 and 2.6353 with the exact exponent.

## 4. Effort grid reconstruction (model.html)

The grid generator is not published and P_d has no published value. With the published constants, the Euclidean nearest point of the inset activation area and a resting finger's own home key costing P_f, scanning P_d over [0.9, 1.3] gives at most 138/142 one-unit keys equal to the published value at one decimal, for P_d in [1.1195, 1.122]. Frozen value: **P_d = 1.12**.

| Grid | 1u keys matched | All keys matched | Max abs deviation (1u) | Mismatches |
| --- | --- | --- | --- | --- |
| iso_optimal_fingers | 46/48 | 51/55 | 0.073 | BACKSPACE 5.855≠5.8, ] 4.763≠4.7, CAPS 3.473≠3.4, ' 3.473≠3.4 |
| iso_traditional_fingers | 46/48 | 51/55 | 0.073 | BACKSPACE 5.855≠5.8, ] 4.763≠4.7, CAPS 3.473≠3.4, ' 3.473≠3.4 |
| matrix_optimal_fingers | 46/46 | 50/54 | 0.049 | CAPS 3.463≠3.4, LSHIFT 4.053≠4.0, H_R0 3.463≠3.4, RSHIFT 4.053≠4.0 |

Modelling choices compared, each at its own best P_d:

- frozen model: 138/142 one-unit keys
- activation box of half-width 0.3 (margin 0.2): 82/142 one-unit keys
- right-hand resting offsets not mirrored: 119/142 one-unit keys
- no home-key rule: 132/142 one-unit keys

Published-source inconsistency: `effort_traditional_config.dat` gives `]` = 5.6 (used by the comparison table) while the model.html grid shows 4.7.

## 5. Sensitivity to grid rounding

Ergonomic and traditional rows recomputed with unrounded model grids (P_d = 1.12) instead of the published one-decimal grids. Ranking preserved.

| Layout | Config | Published total | Model-grid total |
| --- | --- | --- | --- |
| Colemak-DH | ergonomic | 1.735 | 1.741 |
| MTGAP | traditional | 1.787 | 1.790 |
| Colemak | ergonomic | 1.802 | 1.805 |
| Workman | traditional | 1.817 | 1.821 |
| Colemak | traditional | 1.836 | 1.839 |
| Halmak | traditional | 1.884 | 1.889 |
| Asset | traditional | 1.911 | 1.914 |
| Dvorak | traditional | 1.923 | 1.925 |
| Norman | traditional | 1.926 | 1.930 |
| qgmlwyfub | traditional | 1.936 | 1.937 |
| Qwpr | traditional | 1.987 | 1.990 |
| Minimak-8key | traditional | 2.005 | 2.007 |
| Qwerty | traditional | 2.400 | 2.407 |

## 6. Caseless scripts in the original analyzer

Character.isAlphabetic is true for Bangla letters and vowel signs, which are neither upper- nor lower-case, so Key.kt 'shifts' each to itself: every key holds its character twice and base effort is counted twice. The original tool cannot score Bangla unmodified; Phase 2 uses a Bangla-aware loader instead.

Probe layout `ক া ি` holds ['কক', 'াা', 'িি']; with every key effort 1.0 the base effort is 2.000 instead of 1.000.
