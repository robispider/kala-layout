# Interpretation of the requested layout candidates

**For a balanced style D test candidate, I would prioritize the earlier D-8ed0c088f68ad80a. For style A, A-14557e4aab2f81f6 offers the smallest J1 cost; A-013e60b38d2caf28 is the stronger primary-fingering movement candidate below 1.9.** These are priorities for exploratory typing tests, not measured comfort rankings or replacement decisions.

Every percentage in the next table compares equal-weight held-out means with Jhor under model-optimal fingering. Negative distance changes mean less distance. Training and held-out scores are kept separate.

| Candidate | Training J1 | Held-out J1 | Cross-space SF rate | Cross-space distance change | Within-word SF-distance change |
| --- | ---: | ---: | ---: | ---: | ---: |
| D-8ed0c088f68ad80a | 1.826100 | 1.817125 | 6.5811% | -34.18% | -3.84% |
| A-14557e4aab2f81f6 | 1.855874 | 1.849279 | 6.7849% | -34.36% | +3.38% |
| D-fb0954976e8c5a32 | 1.860799 | 1.852390 | 6.1760% | -38.04% | +47.55% |
| A-b4106689d404415b | 1.871801 | 1.863444 | 5.9251% | -37.73% | +6.62% |
| D-7af0f238d12d0b4a | 1.880604 | 1.873831 | 5.6058% | -44.42% | +18.06% |
| D-29a057973f8e46f1 | 1.881102 | 1.874246 | 5.5530% | -44.84% | +16.92% |
| A-013e60b38d2caf28 | 1.891982 | 1.887465 | 4.8508% | -50.77% | -25.09% |
| A-7c36e8f26e6c7142 | 1.912502 | 1.906229 | 4.3932% | -53.42% | -31.83% |

## Candidate-by-candidate assessment

* **D-8ed0c088f68ad80a, earlier anchor:** the best low-cost broad compromise among the options examined here. Held-out J1 rises 0.95% versus Jhor, cross-space SF rate falls 36.00%, cross-space SF distance falls 34.18%, and within-word SF distance falls 3.84%. Engram order credit is conclusively higher given its coverage bounds; pair credit improves in its lower bound but intervals overlap. Under traditional fingering, J1 and both SF-distance measures fall relative to traditional Jhor, and all three credit measures separate favorably. Shift share rises by about 0.208 percentage points; most of the primary J1 increase comes from the model’s Shift-effort component. This map changes 49 of Jhor’s 52 symbol positions, so its learning cost needs assessment.
* **A-14557e4aab2f81f6:** strongest low-J1-cost A option. Its training J1 rises only 0.335% versus Goti, while cross-space SF rate falls 26.92% and cross-space SF distance falls 24.38% versus Goti. It preserves the A vowel-entry recipe. Held-out Engram order improves conclusively over Goti under both fingerings, but primary within-word SF distance increases. Relative to Jhor it has nearly the same cross-space distance as D-8ed, at a higher J1; there is no reason to call it universally better than that D anchor.
* **D-fb0954976e8c5a32:** strongly fingering-dependent. Primary held-out cross-space SF distance falls 38.04%, but within-word SF distance rises 47.55%; J1 rises 2.91%, and Dvorak-7 credit is conclusively lower than Jhor. Traditional fingering gives a much more favorable result: J1 falls 2.84%, within-word SF distance falls 36.24%, and the credit bounds separate favorably. It is worth considering for a separately specified traditional-fingering study, not as a robust primary-grid winner.
* **A-b4106689d404415b:** a middle A trade-off. Held-out cross-space SF rate is 5.9251%, with 37.73% less cross-space distance than Jhor; within-word SF distance rises 6.62%. It has the highest primary held-out Engram order credit among the requested candidates. Its pair-credit comparison with Jhor remains unresolved. Training J1 is 1.196% above Goti. It reduces cross-space event frequency more than D-fb, but its cross-space distance is slightly greater: event count and distance are not interchangeable.
* **D-7af0f238d12d0b4a and D-29a057973f8e46f1:** close alternatives. Moving to D-29 costs only 0.0265% additional training J1 and reduces both cross-space SF rate and distance slightly; primary within-word SF distance is also lower than D-7af. D-29 still has 16.92% more primary held-out within-word SF distance than Jhor and conclusively lower Dvorak-7 credit; its Engram order improves, and its pair-credit interval overlaps Jhor. Both look more favorable under traditional fingering. I would investigate D-29 rather than keep both as distinct primary test priorities, while retaining their records.
* **A-013e60b38d2caf28:** the strongest below-1.9 primary-fingering movement option in this selected group. Held-out cross-space SF rate is 4.8508%; distance falls 50.77% across spaces and 25.09% within words versus Jhor. Engram order is conclusively above Jhor; pair-credit intervals overlap. The cost is 4.86% higher held-out J1 than Jhor, or 2.29% higher training J1 than Goti. Its reduction in pair effort is outweighed by higher single-key effort. Under traditional fingering, within-word SF distance rises 10.39% versus traditional Jhor and J1 rises 6.28%, so the broad primary benefit is fingering-specific.
* **A-7c36e8f26e6c7142:** the most aggressive cross-space reduction in the selected group, but outside the 1.9 cutoff. Its held-out J1 is 1.906229 and training J1 1.912502. Cross-space distance falls 53.42% and primary within-word distance falls 31.83% versus Jhor. Against same-style Goti, however, its primary Engram order credit is conclusively lower. The lower credit-bound values relative to Jhor have overlapping intervals, so do not overstate those comparisons. Extra single-key effort is the main reason its J1 rises. The added movement reduction over A-013 comes with a meaningful extra effort cost. **Retain it on the shortlist at the owner’s explicit request**, as a movement-focused option above the 1.9 threshold.

## Comparison with the fixed layouts in the earlier results

All seven requested candidates have lower **held-out mean J1, cross-space SF rate and cross-space SF distance** than each of the six previously scored fixed baselines. This remains true for either candidate fingering when compared with the favorable baseline benchmarks. Against the strongest old fixed baseline in J1, Windows Default’s published best mean of 2.149828, their primary means are 11.33%–13.98% lower. Against the smallest old fixed-baseline cross-space SF rate, Bornona’s 8.8975%, their primary rates are 23.74%–50.62% lower. Their within-word SF distances are also below all six old fixed baselines under the primary grid.

This is a strong modeled comparison with the registry, not proof of superiority to every publicly available Bangla keyboard. The six are Windows Default, Probhat, Munir Optima (uni), Bornona, UniJoy and National (Jatiya). Phonetic layouts are excluded by the research rules. Encoder/escape differences are reported: Windows Default escapes about 2.57% of units in this diagnostic pass, while these A/D candidates escape about 0.02%.

Mechanical superiority is not universal. Windows Default’s primary Engram order-credit bounds are 0.789681–0.821518. All requested candidates except A-b410 have upper bounds below Windows Default’s lower bound, so Windows Default wins that narrow diagnostic; A-b410 overlaps it. A layout can reduce effort and SF-distance measures while earning less triple-order credit.

## Research decision

Keep Jhor as the low-J1 reference. For an exploratory comparison, prioritize **D-8ed** as the low-cost broad D option, **A-14557** if the A vowel recipe is important, and **A-013** if a larger primary J1 budget is accepted to reduce SF movement strongly. Consider **D-29** for a stronger cross-space emphasis within style D; the within-word penalty remains explicit. Reserve **D-fb** for a predefined traditional-fingering comparison. **Keep A-7c on the shortlist by owner request as an explicit exception to the 1.9 threshold**, with its J1 cost and Engram trade-offs visible. No official layout, objective or reproduction lock is changed.

The complete numeric tables and interval comparisons are in [REPORT.md](REPORT.md), [comparison.json](comparison.json) and [metrics.csv](metrics.csv). The [126 D frontier rows below 1.9](D-under-1.9-frontier.md) include Jhor, and the full saved D cutoff collection contains 6,584 maps.

