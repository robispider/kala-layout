# Historical research: shared Kala Layout

**Historical shared-map research.** This record retains the decision and scope at the time. See the current [selection criterion](PUBLICATION_DECISION.md) and [maps](LAYOUTS.md). Select shared CLI operations explicitly with `--season shared-v1`.

We are moving from two independently positioned layouts to **one shared arrangement with two typing styles: Goti and Jhor**. The public name is **Kala Layout**; B01 is the technical research identifier of the arrangement provisionally selected on 28 October 2026. Switching styles changes the vowel-entry recipe; every symbol stays on the same key and layer. See the [shared map and typing rules](LAYOUTS.md).

## Why change?

The original Goti and Jhor arrangements differ at 31 of 52 symbol positions. Choosing a different vowel-entry style therefore also meant changing positions. One shared arrangement gives both styles the same positional memory and a common map for guides and practice. The styles remain different ways to type vowels. Easier switching, learning and maintenance are intended benefits, not measured improvements in learning time, speed or comfort.

Simply using one original arrangement for both styles is a poor compromise. On the original 50/50 Wikipedia/newspaper training mix, with model-optimal fingering:

| Arrangement used for both styles | Goti effort change | Jhor effort change | Goti within-word distance change | Jhor within-word distance change |
| --- | --- | --- | --- | --- |
| Original Goti | 0.000% | +1.218% | 0.00% | +24.83% |
| Original Jhor | +4.421% | 0.000% | +159.56% | 0.00% |
| Kala Layout | +0.689% | +0.439% | +4.79% | +3.77% |

Each change compares with that style's own original arrangement. B01 satisfies the shared experiment's +0.75% effort and +7.5% within-word distance limits in both styles. These limits apply to that training mixture and fingering, not every source or person. The Goti result exceeds the earlier strict +0.5% effort limit; this is explicitly a relaxed shared policy, with unchanged scoring calibration.

## What we give up

Sharing has a mechanical cost. The following numbers are equal means of three previously examined held-out sources, using model-optimal fingering:

| Kala Layout versus original same-style arrangement | Goti style | Jhor style |
| --- | --- | --- |
| Mean modeled effort J1 | 1.854428 | 1.808080 |
| Effort change | +0.608% | +0.447% |
| Within-word same-finger distance change | -0.107% | +1.351% |
| Cross-space same-finger distance change | +25.750% | +3.923% |

Goti's larger cross-space movement cost deserves attention. Both styles also have higher modeled Balance cost than keeping their separate Balance leaders. The reason to share is one remembered arrangement, a benefit outside the mechanical formula. [Movement checks](MECHANICS.md) retain both fingerings and coverage limits.

Existing users must relearn positions: B01 moves 43 of 52 Goti symbols and 39 of 52 Jhor symbols from the originals. All change physical key; two Jhor symbols also change layer. These counts do not predict learning time. [Original maps and exports](../results/kala-keyboards/README.md) remain available, and [relocation data](../results/shared-publication-v1/RELOCATIONS.md) records every move.

## Why this arrangement provisionally?

B01 is `shared-76c9b9dbfc689d0b` (also P01). The four-billion search and enhanced pilot have the same two leading non-dominated maps in their fully scored pools. B01 has Goti R 0.761312 and Jhor R 0.441365. B02 has Goti R 0.785849 and Jhor R 0.438747. Their only difference swaps ৈ and ৌ between Shift+X and Shift+W.

B01 favors Goti's score while retaining the leading Jhor trade-off. This is a practical preference, not a numerical overall winner. R is calibrated separately by style and must never be added, averaged or compared across styles. The pilot used shared starts, so matching its leaders is not independent rediscovery. Four billion means search proposals, not unique maps or full Balance evaluations.

A [new exhaustive local certificate](SHARED_CERTIFICATION.md) rules out eligible Pareto improvements moving at most three symbols, covering 45,526 alternatives with no unresolved comparisons. It does not prove global optimality or resolve trade-offs such as B01 versus B02.

## Evidence and next checks

The [transition report](../results/shared-publication-v1/REPORT.md) connects the [existing-map check](../results/shared-style-check-v1/REPORT.md), [strict search](../results/shared-layout-v1/run-v1/REPORT.md), [relaxed search](../results/shared-layout-relaxed-v1/run-4b-v1/REPORT.md) and [top-ten comparison](../results/shared-top10-comparison-v1/REPORT.md). The original results remain history; this is a new publication and [shared challenge season](SHARED_CHALLENGE.md).

The searches are finite and bounded; no old optimality certificate transfers. Known held-out sources are exploratory reuse, not fresh confirmation. New independent text and typing studies should test learning, errors and sustained performance before stronger claims. B01 is provisional. Research exports do not update the installed Kala application; check [availability](LAYOUTS.md).
