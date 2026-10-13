# Feedback: full-archive balance study

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
