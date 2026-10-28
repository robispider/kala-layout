# Pilot findings: more exploration, unchanged best layouts

**The enhanced search produced more qualifying arrangements, but no better final Balance alternative in this pilot. The scoring model stayed unchanged.** Both methods returned the same two known 4-billion finalists.

The total budget was 10 million annealing proposals: 5 million control and 5 million enhanced. Both variants used ten paired starts, identical starting maps and seed values, plus the same final full-score neighbor budget. Earlier full scoring and diversity were additional search work, not different model weights.

| Result | Control | Enhanced |
| --- | ---: | ---: |
| Annealing proposals | 5,000,000 | 5,000,000 |
| Distinct mechanically retained maps | 64 | 625 |
| Distinct qualifying maps fully scored, including refinement | 47 | 137 |
| Qualifying maps outside the common start bank | 44 | 134 |
| Fully scored qualifying maps absent from the old 4b retained pool | 39 | 121 |
| New non-dominated alternatives beyond the start bank | 0 | 0 |
| Final non-dominated alternatives, including incumbents | 2 | 2 |
| Aggregate timed seed duration (seconds) | 551.6 | 642.4 |

Enhanced exploration reached **2.91 times as many distinct qualifying full-scored maps**. The aggregate of the timed per-seed wall durations was **16.5% higher**. This is not a separate equal-wall-time benchmark; both methods ran concurrently, and final postprocessing cost is additional. A larger archive naturally retains more maps, so the retained-map count alone is not success.

## Did it improve the result?

No. Both variants retained the same frontier:

| Candidate | Goti R | Jhor R |
| --- | ---: | ---: |
| shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |

No pilot discovery improved or extended this non-dominated frontier. The extra qualifying maps were dominated by existing alternatives. This does not prove that larger runs or other search changes cannot improve it. Ten paired starts are a small exploratory experiment, and warm-starting from a strong 4-billion result makes genuine improvements harder to find.

## What the extra work achieved

Enhanced seed searches made 8,361 early mechanical screens. 8,132 failed the unchanged caps; 229 received full evaluations across seeds, with repeats across seeds. Those early scored maps deduplicated to 126 arrangements. Final per-variant scoring/refinement produced the distinct counts above. Counts of early checks, unique qualifying maps, and annealing proposals are different quantities.

Full R did guide local acceptance and restarts before seed completion. Thus this is a real test of earlier use of the complete formula, not merely a larger final export. The same-score and exact-J1 tests passed. The mechanical archive was more diverse by mean label-assignment Hamming distance, but greater diversity did not translate into a better score frontier here.

Absence from the old retained pool means only that the arrangement was not saved there; it may have been visited and pruned during the 4-billion run. None of these counts is a count of globally new unique layouts.

## Interpretation

This pilot supports the narrow claim that the two search changes broaden qualifying exploration at the tested budget. It does **not** yet justify a claim of better layout quality or a jump to a very large run. Keep the existing finalists as the best retained alternatives. A useful next research question is whether feasible-neighbor generation and a broader full-score neighborhood can find new non-dominated points with less rejected work; that would require a separately frozen experiment. No further search was launched.

The effects of diversity and earlier scoring were combined, so the pilot cannot attribute the count increase to one change alone. A later ablation or equal-wall-time comparison could separate them.

## Validation

All 279 repository tests passed, including frozen-score agreement, exact eligibility, paired starts, seeded reproducibility, archive bounds, and full-score local exploration. All eight published reproduction groups matched. Every pilot input/output/protected hash was checked after completion, and all 180 inputs of the completed 4-billion run still match. The source model, formula, weights, calibration, geometry, text counts, typing rules and existing outputs were preserved.

Eligibility remains +0.75% effort and +7.5% within-word movement on the primary training mix. Cross-space movement remains separate. Known held-out diagnostics were computed after training selection and did not alter the findings. Scores remain modeled effort and mechanics, not measured speed or comfort.
