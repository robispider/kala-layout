# Optional challenge diagnostics

**Official J1, submission acceptance and leaderboard ordering are unchanged.**

The preference table is incomplete and lacks independently reproduced predictive/Bangla validation. Its supported-pair diagnostic cannot rank whole layouts. No comfort rank or recommendation is produced.

The counts below retain repeats and directed pairs. Shift share excludes space; finger load excludes modifier presses. Same-finger moves count different physical keys. J1 is effort per text unit including space.

## D-reference.json: Bangla-DH D reference

Style D; official training J1 **1.808796**; +0.0000% versus the reference. Beats reference: False.

The exact official score is stored in submissions.json. Numbers here are descriptive, not additional challenge objectives. The model-optimal scenario is the official one; traditional fingering is a separate scenario.

| Text | Fingering | J1 change vs reference | Same-finger moves per unit (yours / reference) | Repeat share of pairs | Shift share of presses | Preference-table support |
| --- | --- | --- | --- | --- | --- | --- |
| bnwiki/train | model-optimal | +0.0000% | 0.014691 / 0.014691 | 0.79% | 9.18% | 21.19% |
| bnwiki/train | traditional | +0.0000% | 0.047038 / 0.047038 | 0.79% | 9.18% | 31.97% |
| newspaper/train | model-optimal | +0.0000% | 0.016075 / 0.016075 | 0.81% | 8.55% | 23.31% |
| newspaper/train | traditional | +0.0000% | 0.043890 / 0.043890 | 0.81% | 8.55% | 33.17% |
| bnwiki/heldout | model-optimal | +0.0000% | 0.014729 / 0.014729 | 0.79% | 9.18% | 21.20% |
| bnwiki/heldout | traditional | +0.0000% | 0.047029 / 0.047029 | 0.79% | 9.18% | 31.98% |
| newspaper/heldout | model-optimal | +0.0000% | 0.016036 / 0.016036 | 0.81% | 8.55% | 23.29% |
| newspaper/heldout | traditional | +0.0000% | 0.043938 / 0.043938 | 0.81% | 8.55% | 33.14% |
| bard-novel/heldout | model-optimal | +0.0000% | 0.015946 / 0.015946 | 0.82% | 8.35% | 23.37% |
| bard-novel/heldout | traditional | +0.0000% | 0.044083 / 0.044083 | 0.82% | 8.35% | 33.31% |

Detailed per-finger counts, coverage gaps and partial preference values are in submissions.json. The partial values refer to different supported subsets and must not be compared as total comfort scores.

## Verification

Each evaluated submission passed the official parser and frozen inventory/bijection check. Its exact mixed-training J1 matches the repository integer scorer; every model-optimal corpus score matches the official scorer. The original scientific inputs and outputs stayed byte-identical.

Source/data/code hashes and policies are in run-manifest.json. The lookup benchmark verifies arithmetic only. Missing preference values are never replaced with zero or generated rules. This report has no effect on official scores, ties, duplicates, acceptance or leaderboard ordering.
