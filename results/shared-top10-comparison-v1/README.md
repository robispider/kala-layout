# Top-ten comparison protocol

Requested on 28 October 2026: analyze ten leading shared arrangements from the 4-billion search and ten from the enhanced 100-million paired pilot, compare those groups, and compare them with fixed Bijoy/UniJoy, National, Windows Default, Munir Optima and Probhat maps. This is a new analysis, not a layout search or publication season. The model, weights, source texts, typing rules, frozen Balance calibration and +0.75% effort/+7.5% within-word experimental caps stay unchanged.

## Pools and replay

The 4-billion run saved 113,550 retained mechanical maps but only two final score-frontier maps. Its final fully scored collection was not exported in full. Replay its original final mechanical eligibility filter and 2,048-proposal refinement using exactly its saved permutation order, RNG seed, swap generator and bounded-frontier rule. Capture all full-score records, verify the old 961-evaluation count and reproduced bounded frontier. Early rejection computes the same E/W screen without calculating unused X for failed maps; selected metrics are still independently scored with the original evaluator. No annealing or new candidate-search step is added.

The pilot pool is the deduplicated union of its control and enhanced fully scored qualifying maps. Preserve both origin labels. Re-evaluate their training metrics and verify their saved A/D R values. Do not treat shared warm starts or duplicate appearances as independent discoveries.

## What “top ten” means

Only maps eligible in both modes enter these lists. R values have separate Goti (A) and Jhor (D) calibration and are not summed, averaged or compared across modes.

For a joint ten-map shortlist, take successive non-dominated score layers. Within each layer, interleave ascending A and ascending D lists, beginning with A and deduplicating maps. Companion score and stable layout ID break ties. Layer 1 is the competitive frontier; dominated backups fill any remaining slots. This is a stated report ordering, not an ergonomic scalar score or a new calibration. Rankings use binary64 R as in the frozen expression.

Also export top-ten lists separately by A and by D for each experiment, with complete within-mode ranks for the evaluated pools. Independent positive rescaling of either mode's R must leave the joint-layer ordering unchanged. All lists are selected from training before held-out diagnostics.

## Benchmark rules

Use all six distinct fixed maps in the baseline registry: UniJoy, National (Jatiya), Bornona, Probhat, Windows Default and Munir Optima (uni). The legacy vendored Bijoy file has the same normal/Shift key positions as UniJoy but a different file format and no vowel-conversion rules. Thus the Bijoy row is explicitly a **Bijoy physical-map / UniJoy-rule proxy**, not a separately validated commercial Bijoy layout. Never label the two files byte-identical or generalize to all Bijoy editions. No phonetic layout is compared.

The existing e2/e3 canonical baseline scores are hash-verified and used for the same three held-out sources as the candidate evaluation. Their encoder minimizes key actions with fixed traditional-effort tie breaks across both fingerings. Score candidate metrics from the same saved A/D count tables under model-optimal and traditional fingering. Existing text downloads are unnecessary.

Report J1 and its terms, within-word and cross-space SF different-key rates/distances, Shift share, order-credit bounds, pair/order coverage and escapes. Normalize each source with its own denominator and average the three held-out source values equally. W and X have different denominators and are never added as raw distances. Unsupported order mass retains coverage bounds, not imputed credits.

For conservative claims use the candidate's worse value across both fingerings against each baseline's better value for that metric. The per-metric baseline envelope is not one physical fingering or one combined score. Add the legacy published scoreboard's most favorable recorded J1 over grid/encoder options, including its rounded-grid records, as an additional effort benchmark. Keep this distinct from the coherent canonical action metrics. Report all unaggregated source/fingering rows.

Do not assign old baselines a shared-layout R rank outside the shared eligibility/key-domain problem. Compare the raw components instead. Escaped units cost zero and break mechanical windows; Windows Default's larger escape share can flatter its scores. These are modeled metrics, not measured speed, comfort, errors or learning benefit.

## Evidence and output

Use the compressed/archived evidence directly. Write a frozen analysis plan, compressed recovered score pools, selection, full training ranks, joint and per-mode lists, candidate maps, per-source/held-out comparison tables and a report/manifest in a fresh directory. Verify selected J1 against the independent official challenge scorer, replay agreement, old baseline score hashes and unchanged model/input hashes. Keep original runs and publication locks untouched.

The report also compares both finalists with the original independent Goti/Jhor layouts on training and held-out means, and B01 with the separate Balance leaders and traditional-fingering references. Export symbol-position differences and pool/frontier overlap so extra backups cannot be mistaken for new leading discoveries. The held-out domains are Wikipedia, newspaper and BARD novels (`bard-novel/heldout`).

Existing held-out sources are already examined and remain exploratory. They do not guide this shortlist or change the formula, caps or ranking. A good J1 comparison is not automatically a movement/order win. Layer-2-and-later backups and interval-overlap cases must remain explicit.

```powershell
$env:PYTHONPATH = "src"
python results/shared-top10-comparison-v1/analyze.py
```

Repeat into a new directory with `--out work/evaluator-experiments/shared-top10-repeat`. No result directory can be overwritten.
