# Diverse/earlier-Balance search: matched 10-million pilot

**The model is unchanged.** This pilot changes search retention and the timing/use of full Balance scores. Frozen J1, Balance components, 81 settings, calibration, geometry, encoders and +0.75% effort/+7.5% within-word caps are reused exactly.

Total budget: **10,000,000 annealing proposals**, half control and half enhanced, plus separately recorded local/full-score neighbor checks. Each variant has 10 paired starts with identical initial maps and seed values. Both have the same current 4-billion incumbents available. Equal proposal budget is not equal compute time.

## Results

| Measure | Control | Enhanced |
| --- | --- | --- |
| annealing_proposals | 5000000 | 5000000 |
| mechanical_saved_unique | 64 | 625 |
| early_full_saved_unique | 0 | 126 |
| retained_union | 68 | 740 |
| eligible_full_scored_unique | 47 | 137 |
| non_start_eligible_unique | 44 | 134 |
| frontier_count | 2 | 2 |
| non_start_frontier_count | 0 | 0 |
| mean_mechanical_pair_hamming | 35.552 | 48.447 |
| summed_seed_seconds | 551.629 | 642.407 |

## Full Balance alternatives

| Variant | Candidate | Goti R | Jhor R | New vs starts | Beats other frontier point | Beats a 4b incumbent |
| --- | --- | --- | --- | --- | --- | --- |
| control | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 | False | False | False |
| control | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 | False | False | False |
| enhanced | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 | False | False | False |
| enhanced | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 | False | False | False |

Lower R is better only within the same mode. Dominance means no worse in both mode-specific scores and strictly better in at least one. More saved layouts alone is not evidence of better layouts: the enhanced retention limit is intentionally larger. Eligible discoveries, non-dominated discoveries, score improvements and compute cost must be considered together. A small paired pilot supplies exploratory evidence, not a probability or proof of superiority.

## What changed in the search

Control uses the existing effort/movement proposal objective with a small top-energy archive and full scoring after seed completion. Enhanced protects per-metric representatives and removes near-duplicate assignments from a larger archive. Periodic full-score evaluations seed interleaved one-swap, three-cycle and double-swap exploration; full R controls local acceptance/restarts. The two R numbers are never added. Full-score points are protected from later mechanical pruning.

Both variants receive the same final full-score neighbor-proposal budget. Enhanced also has additional early full-score work, recorded separately in results.json. Thus any observed gain is a return on extra scoring/retention, not a claim of equal runtime. Controls share initial maps/seeds, but enhanced restarts intentionally change subsequent paths. This combines changes 1 and 2 and does not isolate their individual contributions.

The common 4-billion candidates are warm starts/comparisons, not new discoveries. Full scoring is still gated by unchanged eligibility, and is bounded per enhanced seed. Known held-out diagnostics run only after training selection is frozen. No held-out outcome tunes the pilot. No published result, layout, challenge score or website number changes. Findings are best found; these metrics are not measured typing speed or comfort.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_explore --out work/evaluator-experiments/shared-explore-repeat --pairs 10 --steps 500000 --workers 32
```
