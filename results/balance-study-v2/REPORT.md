# Balance study v2: saved-candidate experiment

Protocol was persisted and hashed before metric evaluation and formula selection. No search ran. A and D are analyzed separately, with same-style references. All published outputs and pre-existing edits are hash-preserved. Standard library only.

## Methods

See experiment-config.json for the immutable protocol, metric-definitions.json for scope/units, candidate-provenance.json.gz for complete assignments and every origin, and frozen-scales-3/4.json for realized training-only anchors. The primary three components use the complete union, including candidates dominated on the earlier J1/rate frontier. Within-word distances and cross-space distances retain their distinct denominators and are never added in raw units. Each source is normalized independently before equal averaging. Mix count columns average raw counts only for audit, not pooled-rate reconstruction.

J1 and effort components are integer sums over the official six-decimal grids, stored as exact fractions. Directed/repeated pairs remain intact. SF different-key distance uses binary64 Euclidean key centers. Distance assertions use absolute tolerance 1e-12; official J1 checks are rational equality. Pair credit uses source-derived binary64 functions; unsupported events retain full denominator 0..1 coverage bounds. Order credit is 0/1 integer counting. Escapes break event chains and remain disclosed in N. Shift effort is included in J1; separate modifier motion is excluded from movement.

Every saved union map receives all requested training metrics under both fingerings. A pilot staged run failed while producing its shortlist because some sensitivity-scenario winners lacked order metrics. The final v2 protocol was frozen in a new directory before v2 selection, expanding the order scope to all 27,019 maps without changing formulas or parameter grids. The incomplete pilot is retained separately under results/balance-study-v1 and is not final evidence.

Two scaling schemes use fixed per-style primary training component minima: explicit acceptable changes (0.5% J1, 20% cross distance, 5% within distance, 0.02 order deficit) and q90-q10 across the full training union. A constant percentile component uses its positive acceptable-change fallback. Negative deviations are allowed. Order aspirations use the full saved collection and the lower deficit endpoint. Optimistic/pessimistic endpoint rankings retain uncertainty; interval certification requires the winner upper score to be below every other lower score. This is conservative and does not assume unknown-event covariance.

Full primary candidate scores/ranks for every setting are compressed in formula-all-candidates-3/4.csv.gz. formula-sweep.csv records every declared scenario/grid/bound outcome, winner, runner-up, tie count and coverage certification. Candidate metrics plus frozen scales/grid suffice to recreate all scenario scores. Worst-scenario means max across both source-specific and mixed training results under both fingerings; it is not merged with primary ranking.

Budget eligibility uses exact J1 fractions; distance guardrails use binary64 + 1e-14 absolute tolerance. Marginal gain is relative movement percentage points saved per additional J1 percentage point, between distinct selected points; zero intervals have no slope. Chord knees normalize endpoints for each condition. Slope knees require both adjacent intervals ≥0.03 effort percentage points and a positive slope drop. These methods depend on range, discrete archive gaps and guardrails.

## Algebraic checks and proof limits

If y is componentwise no worse than x with at least one strict improvement, every w_k r_k(y) ≤ w_k r_k(x), so the max cannot rise and the positive augmented sum strictly falls. Thus B(y)<B(x). This property also holds for the weighted sum. Translation by fixed aspirations does not alter dominance. Unit changes cancel when x,a,t change together. Constant components have positive fallback scales; zero scales and missing metrics are rejected.

Legacy e4 regression: reference (J/Jref−1,S/Sref−1)=(0,0) scores zero. At direction 0.5, a trade-off with J=1.001 Jref and S=0.8 Sref scores max(0.0005,−0.1)=0.0005>0; the reference wins. At direction zero it also loses. New aspirations at component minima remove that structural zero-reference barrier, while still exposing chosen priorities.

Existing Phase 4 proofs cover only their original scope/corpus/objective. Neither augmented-score optimality nor mixed-layout optimality nor a continuous parameter winner region follows from this experiment.

## Verification and reproducibility

Reproduce from the repository root into a new directory: `python -m bangla_dh.experimental.balance_study --out work/balance-study-repeat --workers 16; python -m bangla_dh.experimental.balance_feedback --out work/balance-study-repeat` with PYTHONPATH=src. Worker count changes timing only. Run tests with `python -m unittest discover -s tests`, `python -m bangla_dh check-results`, and site `npm run build`. Actual check output is recorded separately in validation.json.

Deterministic replay checks full-row equality on eight maps. Every rigorous-e4 legacy J1/rate agrees exactly and every legacy distance agrees within 1e-12. All shortlisted candidates are independently checked against official exact training J1 and established action/window/pair/order evaluators on their evaluated sources. Baselines are six fixed registered layouts, not phonetic: their saved held-out canonical rows are separate because no committed baseline training counts exist. Historical best-of-grid baseline numbers are not treated as one scenario.

Benchmark (single-process, includes four pair scenarios and two mixes per map): {"pair_seconds_8_candidates_6_scopes": 0.04575219999242108, "order_first_source_seconds_including_table": 0.21433600000455044, "order_warm_source_seconds": 0.016298899994581006, "full_order_4_scopes_serial_estimate_seconds": 1761.5199158143369, "order_staging_rule": "all saved union maps: complete training evaluation under both fingerings; expensive order diagnostics parallelized after measured pilot benchmark"}. The measured cost supported a parallel full-archive order pass. Selection remains archive-biased: e4 was designed around J1/rate, pruned its archives and is not representative of every feasible map. No human comfort, speed, statistical confidence or unbiased generalization claim is supported.

## Quantified hypotheses and sensitivity

hypotheses.csv records the full-union incidence of transferred movement costs, cross/within correlations and mean effort-component changes in a declared descriptive low-cost subset (J1 increase ≤0.5%, cross-distance reduction ≥10%, within-distance increase ≤5%). relocation-associations.csv counts which symbols relocate in that subset. This subset describes archive associations after formula selection; it does not alter the preregistered ranking.

Style A: cross/within distance correlation -0.6363; 426 low-cost compromises. Mean key/pair/Shift effort changes: +0.003983, +0.000741, +0.000148.

Style D: cross/within distance correlation -0.6654; 200 low-cost compromises. Mean key/pair/Shift effort changes: +0.004388, +0.000694, +0.001377.

winner-sensitivity.csv compares matched finite grid settings while changing one declared factor at a time. shortlist.csv adds primary rank ranges and adverse order-credit differences across every evaluated corpus/fingering. Conservative interval certification compares a candidate upper deficit score against every competitor lower score; shared unsupported events can make this bound too conservative, but cannot make it invalid.

Published-row verification: {'e2': 60, 'e3': 60}, maximum absolute error 9.55e-15. New full-archive order values were independently checked against the established triple evaluator for every shortlisted map/source/fingering; all rigorous-e4 exact J1/rate values match the earlier archive audit.

Full candidate scores/ranks are saved for every primary formula setting. All 2,520 scenario/grid outcomes are saved in formula-sweep.csv; all non-primary candidate scores can be reconstructed deterministically from candidate-metrics.csv, frozen-scales files and configuration. Held-out data do not enter any formula setting. Exact effort values are fractions; Engram order uses exact integer credit counts but its displayed ratios are binary64. No distance or composite score is labeled exact.

## Findings

**No stable single winner or universal knee. Published layouts and existing research are preserved.**

1. **Fully evaluated:** 27,019 distinct A/D maps for every requested training metric, both training sources and both fingerings (plus their 50/50 mixes). Rigorous e4 contributes 26,892: 12,622 A and 14,270 D. Earlier retained and smoke maps expand the union to 27,019. 177 shortlisted maps also have three-source exploratory held-out checks. Six fixed baselines are inventoried separately; their saved movement counts cover held-out data only.
2. **Knee:** primary mixed-source chord knees span 0.226–2.287% extra J1 for A and 0.733–1.084% for D; local-slope knees span 0.099–0.226% for A and 0.185–0.957% for D. Guardrails, fingering and source change the locations. The methods do not support one stable knee.

3. **Strong low-effort compromises:** cross-distance winners with a 5% within-distance guardrail, against their own style reference:

| Candidate | J1 increase | Cross distance gain | Within distance change |
| --- | ---: | ---: | ---: |
| A-b998a43aeb0f7a37 | +0.213% | 22.55% | -2.33% |
| A-4dfc1837861ac886 | +0.351% | 25.69% | -0.63% |
| D-eb516086a03ab608 | +0.206% | 15.63% | +4.57% |
| D-8e3f1abe1434b3ea | +0.500% | 21.38% | +0.16% |

4. **Formula sensitivity:** 79 distinct primary winners. Changing scales changes the winner in 180/180 matched comparisons; changing augmentation in 17/120; changing weights in 36/36. The primary three-component and four-component winners, weighted-sum controls, exact conditions and rank ranges are in the CSVs. These are finite settings, not calibrated ergonomic weights or probabilities.
5. **Concealed regressions:** A: 11,415/12,645 cross-distance improvers increase within-word distance; D: 13,228/14,296 cross-distance improvers increase within-word distance. D-072c558b633d1019 increases primary within-word distance 6.40% and loses Engram credit, reversing the earlier prose claim. A-a280bdc4ca72c6c7 wins 19 four-component endpoint settings by improving within distance/order, while cross distance rises 18.81%. Rates and distances also choose different maps. Relocation/component associations are descriptive, not causal.
6. **Robustness:** 154 shortlisted maps retain cross-distance improvement across all examined sources/fingerings; 18 show a cross-distance reversal. 607/1,008 four-component scenario/grid configurations have a uniquely best winner separated from every competitor's unsupported-credit bounds. Changing source changes winners in 557/720 matched comparisons, and fingering in 1073/1080. Known held-out sets remain exploratory and never tune formulas.
7. **Evidence:** the positive augmented score algebraically respects strict componentwise dominance and unit changes. Exhaustive comparisons verify winners within this fully evaluated saved union for specified settings. Nothing proves global layout optimality, a continuous weight region, human comfort, or statistical confidence. Phase 4 certificates do not cover this score. Small-cost cross-space gains are observed; diminishing returns are uneven and depend on conditions.
8. **Most useful next experiment:** preregister acceptable changes and formulas, then evaluate on genuinely new independent Bangla text. Obtain Bangla pair-preference data and sustained crossover typing trials to test whether modeled trade-offs predict comfort. More archive search cannot establish that relationship.

Requested A-7c36e8f26e6c7142: J1 1.912502; explicitly included as the below-1.9 threshold exception.

Recommendation: retain effort-budget curves with within-word guardrails as the clearest comparison tool. Use the augmented achievement family for transparent sensitivity analysis with frozen aspirations/scales. This evidence does not select one calibrated formula or an official replacement layout.
