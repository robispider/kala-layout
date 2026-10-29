# Selection criterion for the published layouts

Decision date: 29 October 2026. Published Kala Goti and Kala Jhor use separate arrangements selected under the original modeled-effort objective for their respective typing styles.

| Style | Published map | Training J1 |
| --- | --- | --- |
| Goti (A) | `A-18fe73cb912ae3f1` | 1.8496860307151324 |
| Jhor (D) | `D-e4a6be48881da590` | 1.8087958948695027 |

The objective remains `0.5 J1(Wikipedia training) + 0.5 J1(newspaper training)`. Model, derived counts, native grammars and scoring season are unchanged. The current CLI defaults to `legacy-v1`; use `--season shared-v1` for the historical shared-map experiment.

## Results under other priorities

The shared experiment examined a common positional map across styles. Its intended learning and switching benefit has not been measured. B01 increases training J1 by 0.689% / 0.439% (Goti / Jhor) relative to the original same-style maps; previously examined held-out means increase 0.608% / 0.447%. Selection used the relaxed shared policy (+0.75% effort, +7.5% within-word distance) and separate R calibration. Its [report](../results/shared-publication-v1/REPORT.md) and [scoped local certificate](SHARED_CERTIFICATION.md) remain valid research records.

Balance adds explicit within-word distance, cross-space distance and order priorities. The separate Balance leaders accept higher original training J1 of 0.288% / 0.273%. Their real component gains and regressions remain in the [analysis](../results/balance-v1/CANDIDATE_ANALYSIS.md). Lower Balance R does not establish lower original J1. Original J1 weights are modeling assumptions, not validated measurements of human performance.

## Additional evidence and limits

The [new Goti search](GOTI_8B.md) found no lower original J1 and repeatedly reproduced the published arrangement. Jhor retains its original separate evidence. This decision does not refute the shared certificate, establish superiority on every mechanical metric, or prove a global optimum. See the [maps and rules](LAYOUTS.md).
