# Post-analysis preference record

This package records the human preference and extracts existing comparison rows. It does not modify frozen scoring, scales, aspirations, metrics, eligibility caps or rankings.

The owner permits cross-space regression when other components improve. The existing stability experiment already used this policy: no numerical rerun or refitting is necessary. This preference was confirmed after reviewing exploratory results, so it is not fresh preregistration or confirmation.

Keep the 0.5%/1% effort caps, the primary 5% within-word-distance cap, fixed acceptable-change scales, positive movement weights and narrow priority grid. Cross-space regression remains a score penalty; it simply does not disqualify a candidate automatically. All real gains and regressions remain visible.

## Primary minimax candidates

| Candidate | Role | J1 change | Cross distance change | Within distance change | Order credit change |
| --- | --- | ---: | ---: | ---: | ---: |
| A-a280bdc4ca72c6c7 | 3 components/4 components | +0.288% | +18.81% | -14.63% | +0.05826 |
| D-48319b4b30582e8c | 3 components | +0.083% | -2.64% | -4.95% | -0.00225 |
| D-9ad5412603069cd6 | 4 components | +0.273% | -12.81% | -8.24% | +0.00959 |

A-a280bdc4ca72c6c7 is a legitimate comparison candidate under the accepted policy. It is the primary minimax choice in both component sets and effort bands. Its primary within-word distance falls 14.63%, while cross-space distance rises 18.81%; the worst observed cross-space increase is 29.44%. Across examined sources/fingerings, within distance still improves by at least 3.52%, effort rises by at most 0.326%, and order improvement survives all observed coverage bounds. These are existing modeled observations, not future guarantees.

For D, keep two priorities visible. D-48319b4b30582e8c is the three-component primary minimax choice with only 0.083% extra effort. D-9ad5412603069cd6 is the order-inclusive minimax choice with 0.273% extra effort and larger primary cross/within reductions. Its positive primary order-credit change does not survive coverage bounds across every examined condition.

The sensitivity-ranking leaders differ from these primary leaders. Some violate the 5% within-word cap or 0.5% effort cap on other sources/fingerings. candidate-comparison.csv retains all observed feasibility flags and worst regressions, along with the previously named cross-space-oriented alternatives. Do not merge the two rankings or promote a sensitivity winner as uniformly feasible.

No candidate meets the exploratory worst-regret tolerance of 0.05 across the primary narrow grid at the 5% guardrail. Accepting cross-space trade-offs makes the comparisons consistent with the owner's priorities; it does not create a universally near-best layout or calibrate the formula.

The next research step is to compare these explicit alternatives under a preregistered fixed formula/priority range on genuinely new independent text. Bangla preference and sustained typing trials are required to test comfort. Keep published layouts unchanged.
