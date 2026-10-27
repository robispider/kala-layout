# One key arrangement with Goti and Jhor vowel styles: existing-map check

This diagnostic cross-scores the two published maps, the adopted four-component Balance v1 leaders, and the earlier three-component D alternative. It runs no search and changes no published layout, formula, threshold, calibration or website number.

A means Goti vowel entry; D means Jhor context vowels. Each arrangement retains exactly the same 52 symbol positions in both modes. Counts are from each mode's own frozen encoder, including repeats, Shift, punctuation and boundary policy.

## Primary training effort

Original 50/50 Wikipedia/newspaper training mix; model-optimal fingering. Changes compare with the original layout of the SAME mode, not with the other mode. Lower J1 is better.

| Arrangement | Goti J1 | Change | Jhor J1 | Change | Balance eligibility A / D |
| --- | --- | --- | --- | --- | --- |
| Original Goti | 1.849686 | +0.000% | 1.830818 | +1.218% | True / False |
| Original Jhor | 1.931457 | +4.421% | 1.808796 | +0.000% | False / True |
| Balance v1 Goti leader | 1.855008 | +0.288% | 1.838184 | +1.625% | True / False |
| Balance v1 Jhor leader | 1.936388 | +4.687% | 1.813731 | +0.273% | False / True |
| Earlier three-component Jhor alternative | 1.932847 | +4.496% | 1.810300 | +0.083% | False / True |

## Frozen Balance v1

Eligibility requires J1 no more than 0.5% above the original same-style layout and within-word same-finger distance no more than 5% above that reference. Cross-space regressions remain permitted and penalized. R is evaluated only for eligible maps on primary training. A and D have separate calibration: their R numbers must not be compared, averaged or combined into a shared score.

| Arrangement | Mode | Effort cap | Within cap | Cross distance change | Within distance change | Order credit bounds | R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Original Goti | A | True | True | +0.00% | +0.00% | 0.764724–0.773253 | 0.490656484 |
| Original Goti | D | False | False | +1.25% | +24.83% | 0.740886–0.749677 | ineligible |
| Original Jhor | A | False | False | +49.93% | +159.56% | 0.729270–0.737799 | ineligible |
| Original Jhor | D | True | True | +0.00% | +0.00% | 0.749568–0.758360 | 0.240273932 |
| Balance v1 Goti leader | A | True | True | +18.81% | -14.63% | 0.822983–0.831511 | 0.072759785 |
| Balance v1 Goti leader | D | False | False | +6.14% | +11.61% | 0.791684–0.800475 | ineligible |
| Balance v1 Jhor leader | A | False | False | +35.42% | +150.72% | 0.738497–0.747026 | ineligible |
| Balance v1 Jhor leader | D | True | True | -12.81% | -8.24% | 0.759154–0.767946 | 0.139415963 |
| Earlier three-component Jhor alternative | A | False | False | +46.85% | +153.96% | 0.727134–0.735662 | ineligible |
| Earlier three-component Jhor alternative | D | True | True | -2.64% | -4.95% | 0.747320–0.756112 | 0.201139299 |

## Previously examined held-out texts

Equal mean of Wikipedia, newspaper and unseen-news benchmark scores under model-optimal fingering. These are exploratory reused benchmarks, not fresh confirmation; they select no shared arrangement.

| Arrangement | Goti held-out J1 | Jhor held-out J1 |
| --- | --- | --- |
| Original Goti | 1.843229 | 1.824390 |
| Original Jhor | 1.926601 | 1.800026 |
| Balance v1 Goti leader | 1.848790 | 1.832242 |
| Balance v1 Jhor leader | 1.931271 | 1.804702 |
| Earlier three-component Jhor alternative | 1.927815 | 1.801316 |

## Arrangement differences

| Pair | Changed assignments / 52 | Changed physical keys | Changed layer |
| --- | --- | --- | --- |
| A-18fe73cb912ae3f1 vs D-e4a6be48881da590 | 31 | 31 | 2 |
| A-a280bdc4ca72c6c7 vs D-9ad5412603069cd6 | 42 | 42 | 0 |

## Interpretation and scope

0 of these 5 existing arrangements pass the adopted Balance v1 eligibility limits in both modes. This finite cross-check does not prove that a jointly eligible shared arrangement is impossible. The original searches optimized styles separately; Balance v1 selected separate style candidates from a saved archive, and no Balance v1 layout search was performed by that report.

A shared-map search would be a separate experimental objective, using both original effort references and frozen Balance v1 eligibility limits. Combining A/D R values requires an explicitly defined new rule because their calibration differs. Evaluate both modes separately and retain all movement/order trade-offs. Original J1 scores and published maps remain the reference.

scores.csv and scores.json include all five text sets under both fingerings, plus separately normalized training mixes. Only model-optimal training mixes carry Balance v1 R; other rows are sensitivity diagnostics. Order intervals retain unsupported-event coverage bounds. Scores model mechanics and effort, not measured speed or comfort.

## Reproduction

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python results/shared-style-check-v1/analyze.py --out work/shared-style-repeat
```
