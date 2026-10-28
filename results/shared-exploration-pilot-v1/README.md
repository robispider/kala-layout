# Matched 10-million pilot: diversity and earlier full Balance

Requested on 28 October 2026 to test whether proposed search changes 1 and 2 produce additional useful shared arrangements. The owner explicitly requires **the same model**. No scoring constant, model parameter, typing rule, corpus, calibration, score expression, published result or website number changes.

## Unchanged model

Reuse the original J1 effort and the frozen Balance v1 expression with its four components, order-coverage bounds, 81 priority settings, aspirations, scales and calibration minima. Retain the already adopted experimental eligibility: exact J1 no more than +0.75%, and within-word SF different-key distance no more than +7.5%, separately against original Goti/Jhor. Cross-space distance remains scored without a new hard cap. The two mode-specific R numbers are never added or compared across styles.

Search and selection use only the original independently normalized 50/50 training mix and model-optimal fingering. The known held-out sources and alternative fingering remain post-selection exploratory diagnostics.

## Paired budget and controls

**10 million total annealing proposals** are divided equally: 5 million control and 5 million enhanced. Each variant has ten paired starts, 500,000 proposals per start, 30 ILS trials, identical starting permutations and identical seed values (first seed 2026113082). The effort/movement proposal objectives and temperature policy are unchanged. Even ordinals use the original-effort objective; odd ordinals use constraint restoration with the existing three cross/within priorities.

Both variants share original Goti/Jhor, their Balance leaders, the initial shared candidate, and both 4-billion finalists as available initial/comparison maps. Remaining starts perturb the 4-billion map or start randomly. Thus rediscovering the 4-billion finalists does not count as a new result. The older results are warm starts, not an independent test set.

The control is a mechanical-only seed search with a small top-proposal-energy archive, followed by full scoring. It reproduces the previous exploration objective and archive rule in this paired harness; this is not a bitwise replay of the earlier differently seeded/budgeted run.

## Search changes under test

1. **Diverse archive.** Enhanced runs retain 64 mechanical candidates rather than eight, protect the best proposal energy and each mechanical component's representative, and prune near-duplicate symbol assignments using Hamming distance. Periodic samples are retained independently of improvement in proposal energy. Full-score discoveries are stored separately so that later mechanical pruning cannot erase them.
2. **Earlier full Balance.** Every 50,000 proposals, enhanced runs fully score up to eight archived candidates passing the unchanged mechanical screen. Full scores are computed from the unchanged independent training-count evaluator and exact eligibility. A maximum of 256 unique full evaluations per enhanced seed bounds cost. The three known feasible shared starts initialize that score archive. They are also included in control's final candidate pool.

At these checkpoints, 64 additional local proposals explore one swap (60%), a three-cycle expressed as two swaps (20%) or two disjoint swaps (20%). Full-score dominance/trade-offs decide acceptance, and the result can restart the mechanical trajectory. A dominating-worse move is rejected; incomparable same-style trade-offs remain admissible. This is full R guiding actual local decisions before seed completion, not just a final rescore. Three additional checkpoints follow ILS iterations 10/20/30. Separate random streams keep this extra work from directly consuming the mechanical RNG stream, but the changed states intentionally alter later paths.

Both variants receive the same final 2,048-proposal full-score local walk, with the same move mixture, so the pilot compares retention and *earlier* scoring on a common postprocessing foundation. This shared final routine differs from the old one-swap-only final routine. Early local checks and final checks are additional to the 10-million annealing total and are recorded separately. Equal proposal budget is not equal runtime or number of full-score calls.

## What counts as more useful results

Report saved mechanical maps, distinct eligible full-scored maps, non-start eligible discoveries, number of non-dominated alternatives, changes in Goti/Jhor R, assignment diversity and compute cost. In particular, check whether new points dominate control points or the known 4-billion incumbents. Increasing the archive size trivially saves more maps; that alone is not success. A trade-off is not a joint improvement. Small counts do not justify a statistical superiority claim.

Full-score caches deduplicate within each seed and final variant pool. Scores of selected candidates are independently checked against direct counts and the exact public challenge scorer. Selection is frozen before held-out evaluation. New outputs have a fresh directory, frozen plan, code/data hashes, seed results, complete score/refinement counts, final layouts and a manifest protecting prior artifacts.

The protocol combines changes 1 and 2; it does not isolate which change caused a gain. A later ablation or equal-wall-time comparison could answer that. Bounded archives and pilot size do not prove optimality, completeness or absence of better maps. These are model scores, not measured typing speed, comfort or learning benefit.

## Run

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_explore --out results/shared-exploration-pilot-v1/run-v1 --workers 32
```

A smoke check uses `--pairs 1 --steps 100` and a fresh path under `work/evaluator-experiments/`. Repeats require a new output directory. This short paired harness saves each completed seed atomically but does not support automatic resume.

```powershell
python -m unittest discover -s tests -p test_shared_explore.py
```
