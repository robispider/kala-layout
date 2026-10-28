# What is certified for Kala Layout?

**No eligible rearrangement moving at most three symbols improves either typing style's Balance score without worsening the other.** This is a completed, exhaustive local check of Kala Layout (research identifier B01), covering every two-symbol swap and every three-symbol cycle across all 52 base/Shift positions.

## The completed check

| Symbols moved | Alternatives checked | Effort-limit failures | Within-distance failures | Ruled out by a worse R | Dominating alternatives | Unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 1,326 | 1,268 | 3 | 55 | 0 | 0 |
| 3 | 44,200 | 44,100 | 3 | 97 | 0 | 0 |

Together these cover 45,526 alternative maps. Moving one symbol alone cannot produce a valid permutation. Other positions stay fixed, and both Goti and Jhor always use the same arrangement. A lower R is better within its own style. A dominating alternative must pass both styles' eligibility limits, have no higher R in either style and have a strictly lower R in at least one. We never add the two R values.

## Which problem does this certify?

The check uses the frozen shared challenge: equal Wikipedia/newspaper training weights, model-optimal ANSI fingering, the same vowel-entry rules, the original same-style effort limit +0.75%, within-word distance limit +7.5% with its existing numerical tolerance, and unchanged style-specific Balance calibration. It does not select a new map or change the challenge season. See the [shared rationale](SHARED_LAYOUT.md) and [challenge rules](CHALLENGE.md).

Effort comparisons use exact integers and fractions. Movement and Balance comparisons use conservative numerical intervals that enclose the portable scorer's floating-point calculations. If a boundary cannot be decided, the checker records it as unresolved and withholds certification. This run had no unresolved comparisons. A separate full-sum verifier checks every effort exclusion directly from source counts and uses the portable scorer to check the remaining exclusions; it also checks hashes and replays every recorded decision. Small exhaustive tests compare the fast method with direct enumeration.

## How does this differ from Phase 4?

The [original Phase 4 certificates](../results/phase4/REPORT.md) concern the earlier, separate, Wikipedia-trained arrangements and the effort-only objective. Their global effort bounds and neighbourhood results do not transfer to Kala Layout. The new shared check concerns eligibility and the two Balance scores together; it supplies no global optimality gap.

This result does **not** prove global Pareto optimality, rule out improvements moving four or more symbols, or establish that B01 is preferable to every other trade-off. B02 can improve Jhor while worsening Goti and is therefore not a dominator. Kala Layout remains provisional. Modeled mechanics do not establish typing speed, comfort or learning benefits.

## Repeat the check

Python 3.10 or newer and the standard library are sufficient. No corpus download or solver is needed. Choose an empty output folder; saved runs are preserved.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh certify-shared --radius 3 --out work/shared-certificate-repeat
python -m bangla_dh verify-shared-certificate results/shared-certification-v1
```

The [report](../results/shared-certification-v1/REPORT.md), [machine-readable certificate](../results/shared-certification-v1/certificate.json), [all candidate decisions](../results/shared-certification-v1/evaluations.jsonl.gz) and [run manifest](../results/shared-certification-v1/run-manifest.json) state the exact scope and preserve the evidence. [Reproduction instructions](REPRODUCE.md) cover the rest of the research.
