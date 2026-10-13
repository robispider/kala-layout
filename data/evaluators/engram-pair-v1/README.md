# Engram pair source v1

Author: Arno Klein. The pair table and LICENSE are distributed under the source repository's MIT license, copied verbatim from commit 179e1c08b220ae1b02f6c425a7d1cbd1150c1db2 of binarybottle/keyboard_layout_scorers. source-lock.json pins source URLs and SHA-256 values; ordinary evaluation never downloads or regenerates them.

pair-scores.csv is the source input prep/input/comfort_keypair_scores_24keys.csv, **not** the rule-generated complete table. It contains predicted latent pair preference scores and source uncertainties. Scores are neither percentages nor milliseconds. Higher values express greater source-model preference. The learning pipeline is documented in binarybottle/typing_preferences_to_comfort_scores, associated with the Engram Study (DOI 10.1080/10447318.2026.2665409).

The original fitting output named estimated_bigram_scores.csv and independent held-out prediction artifacts are not reproduced here. A source-distributed input does not itself prove its derivation. Right-hand values reflect a symmetry assumption; cross-hand pairs, central keys, modifiers, digits and spaces are unsupported. Only base-layer pairs matching traditional fingering are counted as supported by the experimental adapter. The full-layout admission gate remains closed.

lookup-benchmark.json uses independent decimal arithmetic for FF (weight 2), DF and RF (weight 1 each). It tests lookup, directionality and aggregation, not human predictive validity. No source uncertainty is promoted to a layout confidence interval. Do not normalize or impute missing cells silently.

These are derived coefficients, not source corpus texts or participant records. Read source-lock.json and the experimental report for the evidence limits and verification outcomes.
