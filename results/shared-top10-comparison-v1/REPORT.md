# Top ten shared layouts: 4-billion search, 100-million pilot and fixed baselines

**The pilot keeps the same two leading shared layouts.** Two requested top-ten lists are selected from the experiments' fully scored, jointly eligible maps using training alone. Goti (A) and Jhor (D) R values remain separately calibrated. Additional top-ten lists for each mode are exported, so the report ordering does not invent one combined Balance score.

## Main findings

**The 100-million pilot did not improve the leading two-mode trade-off.** The 4-billion, pilot and combined fully scored pools all have exactly the same two non-dominated maps. Each ten-map list therefore contains two finalists and eight dominated backups. Six maps occur in both lists. More retained or fully scored maps did not translate into a better frontier in this pilot.

| Experiment | Eligible fully scored maps | Non-dominated maps | Symbol changes vs B01 across its top ten |
| --- | --- | --- | --- |
| 4b | 961 | 2 | 0–7 |
| pilot100m | 434 | 2 | 0–5 |

The complete fully scored pools share 76 maps. The pilot contributes 358 maps absent from the recovered 4-billion full-score collection. Absence there does not prove the earlier search never visited or mechanically retained a map. The leading maps were supplied to the pilot as common starts, so matching them is not an independent rediscovery.

**For a shared-layout prototype, B01/P01 is my preferred starting point.** This is a judgment favoring the better Goti score while retaining the leading Jhor trade-off, not a numerical overall winner. Keep B02/P02 as the Jhor-favoring alternative. Their only position difference is swapping the rare vowel signs ৈ and ৌ between Shift+X and Shift+W. No measured speed or learning advantage is established.

| Finalist | Full ID | Goti R (lower) | Jhor R (lower) |
| --- | --- | --- | --- |
| B01/P01 | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| B02/P02 | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |

The pilot-specific backups offer small local alternatives, not an improved leading arrangement. The top ten differ from B01 by at most seven symbol positions in the 4-billion pool and five in the pilot; all share the same entry-rule choice and frozen problem. Exact changes and control/enhanced origins are in candidate-map-differences.csv and shortlist-overview.csv.

## What the shared arrangement costs against separate Kala layouts

Changes below compare B01/B02 with the original independently optimized layout for the same mode, using model-optimal fingering. Negative E/W/X means improvement; positive means additional cost. Order change is the difference in lower credit bounds in percentage points; it is a diagnostic, not an interval-separated win claim. Training is the fixed 50/50 training-source mixture; held-out is the equal mean of the three held-out sources.

| Finalist | Mode | Source scope | Effort change | Within change | Cross change | Order lower change (pp) |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | A | training | +0.689% | +4.790% | +25.589% | +1.031 |
| B01 | A | held-out | +0.608% | -0.107% | +25.750% | +1.580 |
| B01 | D | training | +0.439% | +3.766% | +5.893% | +1.258 |
| B01 | D | held-out | +0.447% | +1.351% | +3.923% | +1.668 |
| B02 | A | training | +0.703% | +5.378% | +25.587% | +1.017 |
| B02 | A | held-out | +0.617% | +0.346% | +25.746% | +1.570 |
| B02 | D | training | +0.438% | +3.767% | +5.962% | +1.260 |
| B02 | D | held-out | +0.445% | +1.354% | +3.973% | +1.671 |

For B01 on the held-out mean, sharing costs about **0.61% effort in Goti and 0.45% in Jhor** versus the original layouts. Its Goti within-word distance is essentially unchanged there, but cross-space distance increases about **25.75%**; Jhor within/cross increases are about **1.35% / 3.92%**. The low effort cost should not obscure the Goti cross-space trade-off. Training movement changes and held-out changes differ.

The separately optimized Balance leaders are another relevant target. B01 versus each same-mode leader on the held-out mean, model-optimal fingering:

| Mode | Separate Balance reference | Effort change | Within change | Cross change | Order lower change (pp) |
| --- | --- | --- | --- | --- | --- |
| A | A-a280bdc4ca72c6c7 | +0.305% | +20.136% | +4.526% | -4.597 |
| D | D-9ad5412603069cd6 | +0.187% | +11.893% | +19.082% | +0.602 |

These values do not establish that sharing improves the separate Balance designs. Its intended benefit is one remembered arrangement; that benefit is outside the frozen mechanical formula.

Fingering sensitivity also matters. B01 versus the original same-mode layout under traditional fingering on the held-out mean:

| Mode | Effort change | Within change | Cross change | Order lower change (pp) |
| --- | --- | --- | --- | --- |
| A | +0.904% | +16.093% | +12.647% | +0.241 |
| D | -1.899% | -23.398% | +2.954% | +6.250 |

The experimental +0.75%/+7.5% caps apply to the model-optimal training mix, so they do not promise those bounds on each source or on traditional fingering.

## B01 against known fixed layouts

Conservative percentage reductions on the equal held-out mean: take B01's worse value over the two fingerings and the baseline's better value. Effort uses the extra favorable published effort benchmark; movement uses the canonical action metrics. Positive favors B01. The UniJoy row also represents the explicitly stated Bijoy-positions / UniJoy-rule proxy.

| Fixed layout | Goti effort reduction | Jhor effort reduction | Goti within reduction | Jhor within reduction |
| --- | --- | --- | --- | --- |
| UniJoy / Bijoy positions proxy | 28.37% | 30.69% | 66.95% | 71.33% |
| National (Jatiya) | 30.07% | 32.34% | 68.86% | 72.99% |
| Windows Default | 6.79% | 9.81% | 31.46% | 40.54% |
| Munir Optima (uni) | 22.49% | 25.01% | 51.81% | 58.20% |
| Probhat | 21.58% | 24.12% | 35.27% | 43.85% |
| Bornona | 23.28% | 25.77% | 47.60% | 54.54% |

All twenty shortlist entries in both modes improve these aggregate effort and within-word metrics against all six fixed maps under this conservative check. This is not a win on every dimension: **Bornona and Probhat have less cross-space same-finger distance**, and **Windows Default has a higher key-order credit interval** across both fingerings. Goti clears Probhat's order interval; many Jhor comparisons with Probhat remain unresolved. Windows Default also escapes about 2.57% of corpus units, versus roughly 0.02% for the shared candidates, which favors its zero-cost escape scores.

I would carry the two existing finalists into direct typing evaluation before scaling this same search much further. The enhanced pilot expands candidate coverage but supplies no evidence yet that another order of magnitude will improve the leading compromise. This is a recommendation from the observed search behavior, not a probability estimate or proof that a better layout does not exist.

## Selection and provenance

Replayed the original 4-billion final filter/refinement, recovering **961** eligible full-score records and reproducing its saved bounded frontier. The pilot pool is the deduplicated union of control and enhanced fully scored maps: **434** layouts. Origins remain explicit. Only these evaluated/saved scopes are ranked; this is not a ranking of every proposal.

The report takes the first non-dominated layer, then the next layer, until ten slots are filled. Within each layer, ascending Goti and Jhor lists are interleaved, starting with Goti, and duplicate maps are removed. Companion R and layout ID break exact ties only. This is a declared display/shortlist rule, not a fitted ergonomic score. Backups below layer 1 are dominated and should not be presented as equally competitive finalists.

The joint lists share **6 of ten maps**. The combined joint lists contain 14 distinct maps; joint and extra mode lists together contain 24. Existing held-out sources and both fingerings are scored only after this selection was frozen.

## 4-billion top ten

| Slot | Layer | Candidate | Goti R | Jhor R | Goti held-out J1 | Jhor held-out J1 |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | 1 | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 | 1.854428 | 1.808080 |
| B02 | 1 | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 | 1.854607 | 1.808032 |
| B03 | 2 | shared-1c797d59289ce714 | 0.761640 | 0.441693 | 1.854444 | 1.808096 |
| B04 | 3 | shared-cf127cbaa5e759a4 | 0.764126 | 0.444589 | 1.854416 | 1.808071 |
| B05 | 3 | shared-e53aefc6bbbdd4d3 | 0.795612 | 0.443173 | 1.854658 | 1.808008 |
| B06 | 4 | shared-4575308306443d09 | 0.764939 | 0.445456 | 1.854427 | 1.808081 |
| B07 | 5 | shared-01af8ede4511bd23 | 0.767413 | 0.447952 | 1.854458 | 1.808112 |
| B08 | 5 | shared-29bdf903c92fbbba | 0.793653 | 0.446221 | 1.854447 | 1.807880 |
| B09 | 5 | shared-bfff27b14751bd04 | 0.767562 | 0.447750 | 1.854506 | 1.808157 |
| B10 | 6 | shared-a9b744054e24213b | 0.767522 | 0.448076 | 1.854480 | 1.808135 |

Held-out J1 is the equal mean of Wikipedia, newspaper and BARD novels under model-optimal fingering; lower is better. It does not determine the slots. Complete per-source and traditional-fingering values are in per-source-metrics.csv.

| Slot | Mode | Within SF distance | Cross-space SF distance | Order credit bounds | Shift share | Escaped share |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | A | 0.018499 | 0.145923 | 0.77726–0.78526 | 8.30% | 0.021% |
| B01 | D | 0.019708 | 0.138395 | 0.76451–0.77279 | 8.62% | 0.024% |
| B02 | A | 0.018583 | 0.145919 | 0.77716–0.78517 | 8.30% | 0.021% |
| B02 | D | 0.019709 | 0.138462 | 0.76454–0.77281 | 8.62% | 0.024% |
| B03 | A | 0.018524 | 0.145866 | 0.77726–0.78526 | 8.30% | 0.021% |
| B03 | D | 0.019733 | 0.138338 | 0.76451–0.77279 | 8.62% | 0.024% |
| B04 | A | 0.018447 | 0.145612 | 0.77733–0.78534 | 8.30% | 0.021% |
| B04 | D | 0.019658 | 0.138107 | 0.76459–0.77287 | 8.62% | 0.024% |
| B05 | A | 0.018530 | 0.145922 | 0.77727–0.78528 | 8.30% | 0.021% |
| B05 | D | 0.019656 | 0.138453 | 0.76474–0.77301 | 8.62% | 0.024% |
| B06 | A | 0.018436 | 0.145609 | 0.77731–0.78532 | 8.30% | 0.021% |
| B06 | D | 0.019647 | 0.138106 | 0.76458–0.77285 | 8.62% | 0.024% |
| B07 | A | 0.018452 | 0.145488 | 0.77733–0.78534 | 8.30% | 0.021% |
| B07 | D | 0.019662 | 0.137983 | 0.76459–0.77287 | 8.62% | 0.024% |
| B08 | A | 0.018266 | 0.145891 | 0.77841–0.78642 | 8.30% | 0.021% |
| B08 | D | 0.019379 | 0.138437 | 0.76607–0.77434 | 8.62% | 0.024% |
| B09 | A | 0.018523 | 0.145823 | 0.77726–0.78526 | 8.30% | 0.021% |
| B09 | D | 0.019732 | 0.138295 | 0.76451–0.77279 | 8.62% | 0.024% |
| B10 | A | 0.018515 | 0.145902 | 0.77723–0.78524 | 8.30% | 0.021% |
| B10 | D | 0.019726 | 0.138394 | 0.76448–0.77275 | 8.62% | 0.024% |

## 100-million pilot top ten

| Slot | Layer | Candidate | Goti R | Jhor R | Goti held-out J1 | Jhor held-out J1 |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | 1 | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 | 1.854428 | 1.808080 |
| P02 | 1 | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 | 1.854607 | 1.808032 |
| P03 | 2 | shared-1c797d59289ce714 | 0.761640 | 0.441693 | 1.854444 | 1.808096 |
| P04 | 2 | shared-51a8e6183208a069 | 0.786179 | 0.439077 | 1.854623 | 1.808048 |
| P05 | 3 | shared-cf127cbaa5e759a4 | 0.764126 | 0.444589 | 1.854416 | 1.808071 |
| P06 | 3 | shared-84290f3dbadf04fb | 0.788435 | 0.441761 | 1.854592 | 1.808020 |
| P07 | 4 | shared-4575308306443d09 | 0.764939 | 0.445456 | 1.854427 | 1.808081 |
| P08 | 4 | shared-e53aefc6bbbdd4d3 | 0.795612 | 0.443173 | 1.854658 | 1.808008 |
| P09 | 4 | shared-e47e49a39082ae28 | 0.791927 | 0.445345 | 1.854657 | 1.808085 |
| P10 | 4 | shared-8f1adf7385fb8290 | 0.792100 | 0.445133 | 1.854684 | 1.808109 |

Held-out J1 is the equal mean of Wikipedia, newspaper and BARD novels under model-optimal fingering; lower is better. It does not determine the slots. Complete per-source and traditional-fingering values are in per-source-metrics.csv.

| Slot | Mode | Within SF distance | Cross-space SF distance | Order credit bounds | Shift share | Escaped share |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | A | 0.018499 | 0.145923 | 0.77726–0.78526 | 8.30% | 0.021% |
| P01 | D | 0.019708 | 0.138395 | 0.76451–0.77279 | 8.62% | 0.024% |
| P02 | A | 0.018583 | 0.145919 | 0.77716–0.78517 | 8.30% | 0.021% |
| P02 | D | 0.019709 | 0.138462 | 0.76454–0.77281 | 8.62% | 0.024% |
| P03 | A | 0.018524 | 0.145866 | 0.77726–0.78526 | 8.30% | 0.021% |
| P03 | D | 0.019733 | 0.138338 | 0.76451–0.77279 | 8.62% | 0.024% |
| P04 | A | 0.018608 | 0.145861 | 0.77716–0.78517 | 8.30% | 0.021% |
| P04 | D | 0.019734 | 0.138404 | 0.76454–0.77281 | 8.62% | 0.024% |
| P05 | A | 0.018447 | 0.145612 | 0.77733–0.78534 | 8.30% | 0.021% |
| P05 | D | 0.019658 | 0.138107 | 0.76459–0.77287 | 8.62% | 0.024% |
| P06 | A | 0.018530 | 0.145607 | 0.77724–0.78524 | 8.30% | 0.021% |
| P06 | D | 0.019657 | 0.138173 | 0.76462–0.77289 | 8.62% | 0.024% |
| P07 | A | 0.018436 | 0.145609 | 0.77731–0.78532 | 8.30% | 0.021% |
| P07 | D | 0.019647 | 0.138106 | 0.76458–0.77285 | 8.62% | 0.024% |
| P08 | A | 0.018530 | 0.145922 | 0.77727–0.78528 | 8.30% | 0.021% |
| P08 | D | 0.019656 | 0.138453 | 0.76474–0.77301 | 8.62% | 0.024% |
| P09 | A | 0.018598 | 0.145897 | 0.77713–0.78514 | 8.30% | 0.021% |
| P09 | D | 0.019726 | 0.138461 | 0.76451–0.77278 | 8.62% | 0.024% |
| P10 | A | 0.018607 | 0.145818 | 0.77716–0.78517 | 8.30% | 0.021% |
| P10 | D | 0.019732 | 0.138361 | 0.76454–0.77281 | 8.62% | 0.024% |

## Fixed-layout benchmarks

All six registered fixed maps are included, including Bornona. Probhat is the registry spelling of the requested Probhats. The vendored Bijoy normal/Shift maps equal UniJoy's positions, but its raw file lacks vowel-conversion rules. The **Bijoy positions / UniJoy-rule proxy** therefore shares the UniJoy row under that explicit rule assumption. This is not an independently verified commercial Bijoy version or a byte-identical file claim. Bijoy is not counted as an extra independent benchmark.

The table gives the favorable value of each metric over model-optimal and traditional fingering after equal per-source normalization. These columns form a conservative envelope, not one physical fingering or one combined score. The extra published J1 column also permits the older scoreboard's recorded grid/encoder choices, including rounded-grid values, making that effort check favorable to each baseline.

| Fixed layout | Canonical best J1 | Published favorable J1 | Best within distance | Best cross distance | Largest order upper bound | Escaped share |
| --- | --- | --- | --- | --- | --- | --- |
| Windows Default | 2.154327 | 2.149828 | 0.073726 | 0.171891 | 0.821518 | 2.572% |
| Probhat | 2.561472 | 2.555256 | 0.078067 | 0.135470 | 0.743389 | 0.016% |
| Munir Optima (uni) | 2.586298 | 2.585521 | 0.104855 | 0.179446 | 0.630554 | 0.097% |
| Bornona | 2.618413 | 2.611886 | 0.096431 | 0.124641 | 0.665837 | 0.017% |
| UniJoy / Bijoy positions proxy | 2.808219 | 2.797422 | 0.152890 | 0.240791 | 0.611011 | 0.013% |
| National (Jatiya) | 2.865663 | 2.865663 | 0.162277 | 0.232841 | 0.569839 | 0.070% |

Baseline actions and metrics come from the hash-verified e2/e3 canonical encoder. Minimum-press encoding uses traditional-effort tie breaks held fixed across both fingerings. No corpus text is rebuilt. Escaped units cost no effort and break movement/order windows, which can flatter layouts with missing coverage; Windows Default's larger escape share must be considered when reading its scores.

## Conservative comparison across both fingerings

Each cell below is the range of percentage reductions over the ten selected maps in that mode, using the candidate's worse fingering against the baseline's better fingering for that metric. Positive favors the shared map; negative favors the baseline. E uses the additional published favorable J1 benchmark. W/X use the verified canonical movement envelope. These are comparisons of normalized modeled metrics, not speed or comfort percentages.

### 4b

| Mode | Fixed baseline | Effort reduction range | Within reduction range | Cross reduction range | Order interval result |
| --- | --- | --- | --- | --- | --- |
| A | Bornona | +23.26% to +23.43% | +47.50% to +49.36% | -17.08% to -16.73% | candidate |
| A | Munir Optima (uni) | +22.48% to +22.65% | +51.72% to +53.43% | +18.68% to +18.92% | candidate |
| A | National (Jatiya) | +30.06% to +30.21% | +68.80% to +69.91% | +37.33% to +37.52% | candidate |
| A | Probhat | +21.56% to +21.73% | +35.15% to +37.45% | -7.72% to -7.39% | candidate |
| A | UniJoy | +28.35% to +28.51% | +66.89% to +68.06% | +39.40% to +39.58% | candidate |
| A | Windows Default | +6.77% to +6.97% | +31.33% to +33.77% | +15.11% to +15.36% | baseline |
| D | Bornona | +25.76% to +25.92% | +54.41% to +56.31% | -11.09% to -10.70% | candidate |
| D | Munir Optima (uni) | +25.00% to +25.16% | +58.07% to +59.82% | +22.84% to +23.11% | candidate |
| D | National (Jatiya) | +32.33% to +32.48% | +72.91% to +74.04% | +40.53% to +40.74% | candidate |
| D | Probhat | +24.11% to +24.28% | +43.68% to +46.04% | -2.21% to -1.86% | candidate, unresolved |
| D | UniJoy | +30.68% to +30.83% | +71.24% to +72.45% | +42.50% to +42.70% | candidate |
| D | Windows Default | +9.80% to +10.00% | +40.37% to +42.86% | +19.45% to +19.73% | baseline |

### pilot100m

| Mode | Fixed baseline | Effort reduction range | Within reduction range | Cross reduction range | Order interval result |
| --- | --- | --- | --- | --- | --- |
| A | Bornona | +23.26% to +23.28% | +47.50% to +47.60% | -17.08% to -16.82% | candidate |
| A | Munir Optima (uni) | +22.48% to +22.50% | +51.72% to +51.81% | +18.68% to +18.86% | candidate |
| A | National (Jatiya) | +30.06% to +30.07% | +68.80% to +68.86% | +37.33% to +37.46% | candidate |
| A | Probhat | +21.56% to +21.58% | +35.15% to +35.27% | -7.72% to -7.48% | candidate |
| A | UniJoy | +28.35% to +28.37% | +66.89% to +66.95% | +39.40% to +39.53% | candidate |
| A | Windows Default | +6.77% to +6.79% | +31.33% to +31.46% | +15.11% to +15.29% | baseline |
| D | Bornona | +25.76% to +25.77% | +54.41% to +54.54% | -11.09% to -10.80% | candidate |
| D | Munir Optima (uni) | +25.00% to +25.01% | +58.07% to +58.20% | +22.84% to +23.04% | candidate |
| D | National (Jatiya) | +32.33% to +32.34% | +72.91% to +72.99% | +40.53% to +40.69% | candidate |
| D | Probhat | +24.11% to +24.13% | +43.68% to +43.85% | -2.21% to -1.95% | unresolved |
| D | UniJoy | +30.68% to +30.69% | +71.24% to +71.33% | +42.50% to +42.64% | candidate |
| D | Windows Default | +9.80% to +9.82% | +40.37% to +40.54% | +19.45% to +19.66% | baseline |

## Interpretation and practical limits

Lower effort does not guarantee every mechanical advantage. Inspect cross-space movement and order bounds explicitly: a layout can have lower J1 and much less within-word SF distance while losing a cross-space or order comparison. Unsupported order-credit mass retains its full coverage interval; interval overlap is unresolved, not a win. Higher credit is better, whereas E/W/X are lower-is-better.

These shared maps are constrained against the original same-mode layouts on the training mix. The +0.75% E / +7.5% W limits do not apply automatically to every held-out source or traditional fingering. Full per-source rows retain those exceptions. Existing benchmark data are exploratory and are not fresh confirmation.

Fixed baselines are not assigned a shared-layout R rank: they have their own encoders, coverage and key domains and generally fail the shared-layout eligibility region. Raw components supply the comparison without inventing a common calibrated comfort total. No phonetic layout is included.

Mode-specific top-ten lists are in mode-top-tens.csv and full training ranks in all-training-ranks.csv. LAYOUTS.md and layouts/ hold the selected key arrangements. All scientific inputs, original results and the published layouts remain unchanged. Claims are best found within the stated scopes, not optimality or measured learning/speed/comfort.
