# Evaluation season e1

This additional experimental track preserves the original published layout season. It scores existing layouts and retained candidates; it runs no optimizer and changes no challenge/website results.

The [run-v1 report](run-v1/REPORT.md), [evidence audit](run-v1/evidence.json) and [manifest](run-v1/run-manifest.json) describe the executed Stage 1/2 experiment. [Candidate maps](run-v1/candidates.json) retain seed provenance and training-only descriptive frontier membership. [Scores](run-v1/scores.csv) keep J0/J1 separate from the conditional preference diagnostic.

The source evidence and condition coverage do not admit a full-layout comfort evaluator. No comfort winner or replacement shortlist is selected. The conditional preference mean uses layout-dependent supported pairs and is not an overall comfort ranking. There is no claim of human speed or comfort validation.

Implementation, commands and scope: [experimental package](../../src/bangla_dh/experimental/README.md). The formal run uses all three existing held-out benchmarks and all six fixed market baselines, with no corpus text exported. Source files are pinned under data/evaluators/engram-pair-v1 with attribution and byte-preserving line-ending rules.

## Challenge connection

The full-repository challenge verifier and leaderboard checks can now request an optional report. The PR workflow includes it in the job summary for accepted entries; official validation, exact J1 and sorting stay independent of report generation. The one-file scorer and challenge season are unchanged.

Executed local examples: [reference verification](challenge-reference-v1/REPORT.md) and [a deliberately Q/W-swapped submission](challenge-submission-v1/REPORT.md). The swapped map is an integration example, not a replacement recommendation. Both reports retain the closed comfort-ranking gate and compare each map with its same-style reference. New runs must use a new output directory.
