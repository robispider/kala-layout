# Constrained near-best stability methods

The complete configuration, including inherited numerical aspirations/scales, was saved before any selection. Source metrics and their hashes come from balance-study-v2. Existing published results, model constants, challenge scoring, locks and prior experimental artifacts are preserved.

Eligibility uses exact rational J1 and binary64 within-distance comparisons with absolute tolerance 1e-14. Cross and within distances retain distinct denominators; only their normalized components enter the score. References and rankings remain per style. The primary 5% guardrail is declared rather than selected from outcomes.

For each setting, let candidate score lie in [l_i,u_i]. Its regret against the unknown best is bounded by [max(0,l_i-min_j u_j), u_i-min_j l_j]. Maxima across settings/scenarios bound its worst regret. Endpoint regret uses all optimistic or all pessimistic credits and is saved separately; it is not substituted for the conservative bound. A positive fixed 0.05 score-unit normalizer avoids division by zero, negative scores and reference-dependent percentage interpretations.

Weights are normalized by their total before score calculation. This positive common multiplier preserves each setting's winner, but makes regret magnitudes insensitive to multiplying the entire weight vector by a constant. The weight ranges represent a narrow, declared design region. No prior optimum or held-out result fits them.

Every primary eligible saved map is evaluated on all six existing training scenarios. The same primary eligible pool and frozen primary anchors are used throughout. Primary and training-robust minimax choices are reported separately; training/held-out cap violations are diagnostics, not silently ignored or used to retune the primary selection.

Reproduce from the root with PYTHONPATH=src: `python -m bangla_dh.experimental.balance_stability --out work/balance-stability-repeat`. Repeated runs require new directories. Finite grids do not prove continuous weight-region competitiveness; coverage bounds do not supply statistical confidence; existing Phase 4 certificates do not certify this score.

Fixed acceptable-change scales and explicit eligibility limits were used before scoring. This is an exploratory follow-up on already examined data; no layout search or official selection occurred.

Effort caps: 0.5% and 1%. Primary within-word-distance cap: 5%, with 0%/10% sensitivity checks. Priorities vary narrowly: effort weight 6/8/10, cross weight 1, within/order weights 0.75/1/1.25, augmentation 0.025/0.05/0.075. These are declared choices, not ergonomic constants.

Worst regret means the largest score difference from the best eligible saved map across the declared settings. We divide by a fixed positive tolerance of 0.05 score units, rather than by the winning score. Whole weight vectors sum to one, keeping the score scale interpretable across settings. Three-component comparisons use point values; four-component minimax rankings use conservative coverage-regret upper bounds.

| Style | Effort cap | Components | Ranking | Candidate | Worst regret bound | Near-best maps |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| A | 0.5% | 3 | primary | A-a280bdc4ca72c6c7 | 0.094242 | 0 |
| A | 0.5% | 3 | training-robust | A-3dc21f6cf21dcbc3 | 1.120955 | 0 |
| A | 0.5% | 4 | primary | A-a280bdc4ca72c6c7 | 0.072760 | 0 |
| A | 0.5% | 4 | training-robust | A-3dc21f6cf21dcbc3 | 1.063620 | 0 |
| A | 1% | 3 | primary | A-a280bdc4ca72c6c7 | 0.104897 | 0 |
| A | 1% | 3 | training-robust | A-3dc21f6cf21dcbc3 | 1.120955 | 0 |
| A | 1% | 4 | primary | A-a280bdc4ca72c6c7 | 0.091730 | 0 |
| A | 1% | 4 | training-robust | A-3dc21f6cf21dcbc3 | 1.063620 | 0 |
| D | 0.5% | 3 | primary | D-48319b4b30582e8c | 0.137943 | 0 |
| D | 0.5% | 3 | training-robust | D-5f8a124fb6380369 | 1.016897 | 0 |
| D | 0.5% | 4 | primary | D-9ad5412603069cd6 | 0.139416 | 0 |
| D | 0.5% | 4 | training-robust | D-5f8a124fb6380369 | 0.955643 | 0 |
| D | 1% | 3 | primary | D-48319b4b30582e8c | 0.137943 | 0 |
| D | 1% | 3 | training-robust | D-b2bf1b9bb62fd09d | 1.318982 | 0 |
| D | 1% | 4 | primary | D-9ad5412603069cd6 | 0.139416 | 0 |
| D | 1% | 4 | training-robust | D-b2bf1b9bb62fd09d | 1.244243 | 0 |

Near-best counts require worst regret ≤0.05 across the finite grid; they are neither probabilities nor a continuous-region proof. Primary and six-training-scope rankings remain separate. The eligible set is fixed using the primary mix; a sensitivity winner can violate the same cap on another source/fingering. shortlist.csv discloses those violations and actual worst observed effort/movement regressions.

44 distinct shortlisted/reference/named maps have complete training and exploratory held-out diagnostics; 174 held-out rows were newly recovered from existing derived counts after selection. The requested A-7c36e8f26e6c7142 is included diagnostically, but the effort caps exclude it.

Keep three questions separate: eligibility, score regret within the declared priorities, and actual movement regressions across sources/fingerings. A small regret alone does not establish ergonomic superiority. A four-component coverage envelope can be too conservative because it permits adversarial unknown credits; it remains a bound, not a statistical confidence interval.

Review the primary minimax candidates that also retain small observed regressions. If their order changes between component sets, guardrails or training scenarios, report the alternatives and their explicit priorities rather than selecting one natural balance. New independent text and Bangla human trials remain necessary to test generalization and comfort.

## What the primary 5% guardrail results mean

The A minimax candidate is unchanged across the two effort caps and both component sets, but its cross-space distance worsens. The declared constraints limit J1 and within-word distance only: this candidate is eligible by construction, not an all-movement improvement. The D minimax choice changes when order enters the score.

| Candidate | J1 change | Cross distance change | Within distance change | Worst observed cross change |
| --- | ---: | ---: | ---: | ---: |
| A-a280bdc4ca72c6c7 | +0.288% | +18.81% | -14.63% | +29.44% |
| D-48319b4b30582e8c | +0.083% | -2.64% | -4.95% | -2.28% |
| D-9ad5412603069cd6 | +0.273% | -12.81% | -8.24% | -3.41% |

No candidate meets the declared worst-regret tolerance of 0.05 under the primary 5% guardrail, even in this narrower finite grid. This is an outcome under an exploratory threshold, not proof that no dependable compromise exists. Rankings and numerical regrets remain useful without labeling a candidate near-best.

Before launching another search, decide whether cross-space distance may worsen, must stay no worse than the reference, or must improve by a declared amount. That constraint is absent from the critic's proposed region and was not silently added here. Also decide whether improvements in within-word movement may compensate for cross-space regressions. The result above provides a concrete trade-off for that decision.
