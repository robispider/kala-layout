# Four-billion shared-layout experiment: interpretation

**Primary typing-test candidate: shared-76c9b9dbfc689d0b.** The larger run found a better shared arrangement than either 100-million alternative under both mode-specific Balance scores. Retain shared-7083b1ebfa5aa3a7 as the small Jhor-score trade-off. These are experimental choices for testing, not a replacement release or a proven optimum.

## What completed and what was checked

The configured run completed **4 billion annealing proposals**, split equally between two tracks, on **32 workers**: 10,000 starts per track and 200,000 proposals per start, plus 30 ILS trials per start. File timestamps indicate approximately **6.58 hours** from the frozen plan to final manifest. This includes final scoring; it is an elapsed-time diagnostic, not a universal benchmark.

There are **113,550 distinct retained assignments**. **961** qualifying shared maps received the full frozen-expression score during final selection/refinement, including order; the final bounded score frontier retains **two alternatives**. Four billion proposals can repeat arrangements and are not four billion unique maps or full Balance evaluations.

Verified 180 input hashes, 20015 output hashes, 2916 protected-artifact hashes, every seed identity/signature/progress entry, and all retained maps' 52-slot bijections. Both finalists independently reproduce direct mechanics, full scores and the official exact challenge J1 under A and D. The 100-million output hashes also match.

## Primary training result

Changes are versus each mode's original published map on the original independently normalized 50/50 Wikipedia/newspaper mix and model-optimal fingering. E is J1 per text unit. W is within-word SF different-key distance per text unit. X is cross-space SF different-key endpoint distance per spanning window. X and W have different denominators.

| Candidate | Mode | E change | W change | X change | Experimental R | Original v1 eligible |
| --- | --- | --- | --- | --- | --- | --- |
| shared-76c9b9dbfc689d0b | A | +0.689% | +4.79% | +25.59% | 0.761312 | False |
| shared-76c9b9dbfc689d0b | D | +0.439% | +3.77% | +5.89% | 0.441365 | True |
| shared-7083b1ebfa5aa3a7 | A | +0.703% | +5.38% | +25.59% | 0.785849 | False |
| shared-7083b1ebfa5aa3a7 | D | +0.438% | +3.77% | +5.96% | 0.438747 | True |

Both finalists satisfy the requested **+0.75% E / +7.5% W** limits in both modes on this primary mix. The first candidate's movement also satisfies the original +5% W cap in both modes. Its Jhor mode satisfies original Balance v1 eligibility; its Goti mode still exceeds the original +0.5% effort cap. Neither is an original-policy two-mode success.

The remaining physical trade-off is clear: **cross-space distance rises about 25.6% in Goti and 5.9% in Jhor** for the primary candidate. X has no hard cap in this experiment, but remains positively penalized in the full score. Passing the E/W caps is not an all-movement improvement.

## Why keep the first candidate as the primary test

shared-76c9b9dbfc689d0b has the lower Goti R, lower Goti effort and within-word distance, and lower Jhor cross-space distance. shared-7083b1ebfa5aa3a7 has a slightly lower Jhor R. The Goti R difference is 0.024536, whereas the Jhor R gain of the alternative is 0.002619. These are separate same-mode score differences; they are not combined into one winner or interpreted as comfort percentages.

The maps differ only by swapping the vowel-sign labels **ৈ and ৌ between Shift+X and Shift+W**. This offers a narrow, concrete preference test without learning a second complete arrangement. The first-map recommendation is a practical testing priority, not a formal shared scalar-score optimum.

## Improvement over the smaller experiment

| Candidate | Goti R | Jhor R |
| --- | --- | --- |
| shared-65cdcd9b9364f827 | 0.795110 | 0.476769 |
| shared-bd53cdb670b32e32 | 0.816328 | 0.470757 |
| shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |

Each 4-billion alternative has a strictly lower Goti R and a strictly lower Jhor R than each of the two 100-million frontier alternatives under the same frozen expression and revised eligibility. Thus the larger run improves both score endpoints, rather than merely moving the old trade-off. These R changes are modeled shortfalls against fixed calibration, not measured speed or comfort improvements.

The lowest-effort retained map reduces the worst relative effort loss to **0.6230%**, from **0.6402%** in the 100-million run. Its within-word movement rises about 33%/30%, so it fails the movement cap and should not be treated as the balanced result.

## Comparison with the separate-mode layouts

| Mode | Original published R | Separate Balance leader R | Primary shared R |
| --- | --- | --- | --- |
| A | 0.490656 | 0.072760 | 0.761312 |
| D | 0.240274 | 0.139416 | 0.441365 |

Within each mode, the shared arrangement has a higher modeled Balance cost than its independently optimized Balance leader and than the original published map. Its potential benefit is one remembered arrangement across vowel modes, a learning/product benefit not included in these scores. It does not establish a new mechanical winner over keeping the separate arrangements.

Primary order-credit coverage intervals follow. Higher is better; non-overlap can establish that narrow diagnostic ranking, while overlap leaves it unresolved. Compared with the published originals, the primary shared map improves order credit in both modes; the Goti Balance leader still has substantially greater credit.

| Mode | Original order bounds | Separate Balance bounds | Shared order bounds |
| --- | --- | --- | --- |
| A | 0.764724–0.773253 | 0.822983–0.831511 | 0.775029–0.783558 |
| D | 0.749568–0.758360 | 0.759154–0.767946 | 0.762152–0.770944 |

## Held-out diagnostics and generalization

The following are equal means of the three already examined held-out sources under model-optimal fingering. Means normalize each source first; they do not pool raw counts. Selection was frozen before these diagnostics.

| Candidate | Mode | Mean held-out J1 | E change | W change | X change |
| --- | --- | --- | --- | --- | --- |
| shared-76c9b9dbfc689d0b | A | 1.854428 | +0.608% | -0.11% | +25.75% |
| shared-76c9b9dbfc689d0b | D | 1.808080 | +0.447% | +1.35% | +3.92% |
| shared-7083b1ebfa5aa3a7 | A | 1.854607 | +0.617% | +0.35% | +25.75% |
| shared-7083b1ebfa5aa3a7 | D | 1.808032 | +0.445% | +1.35% | +3.97% |

The E/W caps apply to the declared training mix and fingering, not every source or alternative fingering. Important observed exceptions include Jhor within-word distance of roughly +11.16% on held-out Wikipedia under model-optimal fingering, and Goti effort/within distance of roughly +1.64%/+26.96% on held-out BARD news with traditional fingering for the primary candidate. These exceed the corresponding cap percentages in those diagnostics. Do not describe the shared layout as uniformly within the caps across domains or fingerings. scenario-changes.csv retains every context.

Known held-out evidence is exploratory, not a fresh confirmation set. Coverage bounds are not statistical confidence intervals. More annealing alone cannot establish actual learning or sustained comfort.

## Primary shared key arrangement

The same 52 positions serve both modes. Only the vowel-entry recipe changes. Shift is above base; digits and punctuation retain their frozen positions. Learning this shared map still requires relocation from the existing maps; layout-differences.csv records those edits, not measured learning difficulty.

| Layer | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঢ় | ৌ | ৃ | ৎ | ঢ | ঘ | ণ | ং | ফ | ঠ |
| base | ী | হ | ু | য | ট | শ | স | প | ম | দ |

| Layer | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঁ | ূ | অ | ষ | ঝ | ড | থ | ভ | চ |
| base | ি | ্ | া | র | গ | জ | ক | ে | ব |

| Layer | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঃ | ৈ | ড় | ঙ | ঞ | খ | ধ |
| base | । | ো | ন | ল | ছ | য় | ত |

## Search limits and next use

The mechanical proposal archive is bounded; full order scoring follows that filter and does not occur at every annealing step. The R archive is bounded as well. Seed recurrences and starting-map provenance are retained in analysis.json; shared starts are not independent rediscoveries. This search does not enumerate the assignment space or prove optimality or impossibility.

Use the first candidate as an exploratory shared-layout typing-test option, with the second as the two-key vowel alternative. Compare learning, errors and sustained performance against keeping each separate-mode layout. Any application integration or replacement publication is a later decision. Original layouts, scoring constants, challenge version, locks and website numbers remain unchanged.

## Reproduce this interpretation

```powershell
$env:PYTHONPATH = "src"
python results/shared-layout-relaxed-v1/interpretation-4b-v1/analyze.py --out work/evaluator-experiments/interpretation-4b-repeat
```
