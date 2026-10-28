# Expanded 100-million pilot: findings

**The expanded pilot did not improve either known 4-billion alternative in both mode scores.** The scoring model and per-start setup are unchanged.

The 100-million annealing budget is divided equally between control and enhanced: 50 million each, 100 paired starts per variant, 500,000 proposals per start and 32 workers. Both variants use the same initial maps/seeds and common final refinement. The first ten pairs repeat the smaller pilot; 90 pairs are additional. This is a nested expansion, not an independent fresh replication.

## Results

| Measure | Control | Enhanced |
| --- | --- | --- |
| Annealing proposals | 50000000 | 50000000 |
| Mechanical maps saved | 756 | 6183 |
| Qualifying distinct maps fully scored | 55 | 425 |
| Qualifying maps outside common starts | 52 | 422 |
| Retained non-dominated alternatives | 2 | 2 |
| Non-start frontier alternatives | 0 | 0 |

The enhanced variant fully scored **7.73 times** as many distinct qualifying arrangements. Its summed per-seed wall durations were **15.1% lower**. Equal proposal budget is not equal compute cost; the two variants ran concurrently and final reporting/scoring adds serial work. More saved maps alone is expected from the larger archive and does not establish better quality.

## Compared with the 10-million pilot

| Budget | Control qualifying | Enhanced qualifying | Control frontier | Enhanced frontier |
| --- | --- | --- | --- | --- |
| 10 million | 47 | 137 | 2 | 2 |
| 100 million | 55 | 425 | 2 | 2 |

## Final score alternatives

| Variant | Candidate | Goti R | Jhor R |
| --- | --- | --- | --- |
| control | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| control | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |
| enhanced | shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| enhanced | shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |

Lower R is better only within the same mode. A score improvement in this report means no worse in either mode-specific score and strictly better in at least one; the two R values are never added. A trade-off can be a useful new alternative without dominating an old point. Qualifying under the caps is not evidence of measured speed or comfort.

All evaluated points are covered by the retained frontier: {'control': True, 'enhanced': True}. Unbounded non-dominated counts among fully scored points are {'control': 2, 'enhanced': 2}. These checks distinguish a small bounded output from the actual evaluated score set; neither describes an exhaustive frontier over all possible layouts.

Fully scored qualifying maps absent from the old 4-billion retained pool: {'control': 46, 'enhanced': 394}. Absence means not saved there, not proof that the old search never visited them.

## Model, setup and validation

Frozen J1, Balance components, calibration, aspirations, scales, all 81 settings, typing rules, geometry and +0.75% effort/+7.5% within-word limits are reused unchanged. The input hash maps match the smaller pilot exactly. Per-start search settings also match exactly; only pair count and total proposal budget differ. All 20 saved prefix runs reproduce the earlier scientific outputs, excluding timing and the settings digest.

Both variants receive the current 4-billion finalists as common starts/comparisons. The enhanced method retains diverse mechanical candidates and performs bounded full-score local work before completion. The final routine, including its budget, is shared. This combined pilot cannot isolate diversity from earlier scoring or make an equal-wall-time claim.

Every run-manifest input/output/protected hash matched after completion. The source run already checked paired starts, budget, independent final scores and exact challenge J1. Known held-out data were scored after training selection and did not guide this comparison. Existing results, source model and published layouts are preserved. The engine-generated report title inherits the original 10-million harness label; its actual settings and proposal counts, and this interpretation, describe the 100-million run.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_explore --out work/evaluator-experiments/shared-explore-100m-repeat --pairs 100 --steps 500000 --workers 32
```
