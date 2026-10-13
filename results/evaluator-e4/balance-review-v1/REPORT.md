# A candidate that balances low J1 with cross-space movement

**D-072c558b633d1019 is a useful modeled compromise for comparison. It does not meet the strict goal of lowering both values relative to Kala Jhor under the primary model.** Its training J1 is 1.812141562086, versus 1.808795894870 for Kala Jhor: an increase of 0.184967%. Cross-space same-finger different-key movement falls by 17.6600%.

The candidate was selected from the stored training frontier by allowing at most a 0.2% J1 increase, then minimizing cross-space SF movement. This comparison band is not an approved change to the owner’s strict objective. No new search was run; the placement already occurs in seed D-2026102252. Held-out scores did not guide this selection.

[Layout JSON](D-072c558b633d1019.json) · [Complete comparison](comparison.json)

| Training diagnostic | Change versus Kala Jhor, primary fingering |
| --- | ---: |
| J1 | +0.184967% |
| Cross-space SF movement rate | -17.6600% |
| SF distance per spanning window | -15.8144% |
| Cross-space repeat rate | -0.002575 percentage points |
| Shift share | +0.000000 percentage points |
| Engram pair lower bound | -0.002404 |
| Engram order lower bound | -0.022518 |

All these movement diagnostics improve in the 50/50 training mix, with Shift share unchanged. Engram values are descriptive coverage-bound changes, not a combined comfort score. The candidate changes 11 symbol placements. Individual held-out repeat rates can rise slightly, so the aggregate improvement does not apply to every event on every source.

| Held-out source | J1 change | Cross-space SF movement change | SF distance change |
| --- | ---: | ---: | ---: |
| bnwiki/heldout | +0.215403% | -16.9322% | -14.7426% |
| newspaper/heldout | +0.152948% | -18.5240% | -16.9812% |
| bard-novel/heldout | +0.144704% | -17.5336% | -16.1932% |

Under traditional fingering, training J1 changes by +0.043621%, cross-space SF movement by -5.2183% and distance by -4.7363%. Both Engram lower bounds also fall. Thus the SF benefit does not reverse with fingering, although its size depends on fingering.

Relative to the reviewed candidates, this offers more cross-space improvement than the conservative D candidate at +0.071558% J1, while avoiding the Engram regressions of the D candidate at +0.482235% J1. This is a reason to prioritize it for comparison, not a mathematical definition or proof of the best balance.

If the requirement remains strictly lower J1 than Kala Jhor, keep Kala Jhor: this candidate raises that score. If the requirement is to retain a low J1 while improving several movement diagnostics, this is a credible candidate for exploratory typing tests. Modeled scores are not measured speed or comfort. Existing layouts and reports remain unchanged.

## Position between the published layouts

| Layout | Training J1 | Cross-space SF movement rate |
| --- | ---: | ---: |
| Kala Goti (A) | 1.849686030715 | 9.495762% |
| Kala Jhor (D) | 1.808795894870 | 10.372783% |
| Candidate D-072c558b633d1019 (D) | 1.812141562086 | 8.540954% |

Against Kala Goti, this candidate has 2.029775% lower J1 and 10.055100% lower cross-space SF movement. Against Kala Jhor, J1 rises by 0.184967% while movement falls by 17.659960%. This is a concrete way to retain low modeled effort while improving this movement rate. The Goti comparison crosses vowel styles: this candidate uses Jhor’s style D, so it does not preserve Goti’s UniJoy-style vowel recipe. Each style uses its own encoder and its own valid spanning-window denominator.

## Symbol changes

| Symbol | Kala Jhor slot | Candidate slot |
| --- | --- | --- |
| ঁ | P/shift | O/shift |
| গ | P/base | Q/base |
| ঙ | W/shift | Z/shift |
| ট | Q/base | Z/base |
| ড় | S/shift | P/shift |
| ণ | O/shift | S/shift |
| প | I/base | O/base |
| ম | X/base | I/base |
| য | O/base | X/base |
| হ | Z/base | P/base |
| ৎ | Z/shift | W/shift |
