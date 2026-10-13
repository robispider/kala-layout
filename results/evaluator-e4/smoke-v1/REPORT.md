# Joint J1/movement search: experimental season e4

A success requires strictly lower exact training J1 AND strictly fewer same-finger different-key endpoint moves across a space than the published map of the same vowel style. Higher-J1 movement trade-offs are reported separately and never labeled a success. All existing layouts/results are preserved.

Completed 12 deterministic runs. Verified joint improvements: **0**.

## Training comparison

| Candidate | Style | J1 change | Movement change | Joint improvement | All held-out primary scores improve |
| --- | --- | --- | --- | --- | --- |
| A-18fe73cb912ae3f1 | A | +0.000000% | +0.0000% | False | False |
| A-bfe96c3b2907c43e | A | +0.003975% | -0.0040% | False | False |
| A-44f9108b6803b121 | A | +87.267280% | -49.9595% | False | False |
| A-ce2afa6edf5c4d08 | A | +90.009027% | -51.1873% | False | False |
| D-e4a6be48881da590 | D | +0.000000% | +0.0000% | False | False |
| D-841a9b84244e2457 | D | +0.008749% | -0.0137% | False | False |
| D-02b98dd44dba58ec | D | +49.337269% | -41.2370% | False | False |
| D-bf128e0d74dfe6a8 | D | +49.394009% | -41.3264% | False | False |

References: style A is Kala Goti; style D is Kala Jhor. Both objectives use the original 50/50 Wikipedia/newspaper training mix, each source normalized independently. Primary fingering is the frozen model-optimal grid. J1 retains Shift and extra-action effort; movement excludes separate modifier presses and keeps same-key repeats separate. Exact J1 uses the existing integer/challenge model; exact movement uses rational endpoint counts. No ergonomic weights or Colemak constants are changed.

## Corpus and fingering changes

| Candidate | Corpus | Fingering | J1 change | SF movement change (percentage points) | Shift change (percentage points) | Repeat change (percentage points) | Engram pair lower change | Engram order lower change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-18fe73cb912ae3f1 | bnwiki/train | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | bnwiki/train | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | newspaper/train | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | newspaper/train | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | bnwiki/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | bnwiki/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | newspaper/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | newspaper/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | bard-novel/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-18fe73cb912ae3f1 | bard-novel/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| A-bfe96c3b2907c43e | bnwiki/train | model-optimal | +0.003546% | +0.000867 | +0.000000 | -0.001085 | +0.000336 | +0.002254 |
| A-bfe96c3b2907c43e | bnwiki/train | traditional | -0.078649% | +0.007402 | +0.000000 | -0.001085 | +0.000216 | +0.001017 |
| A-bfe96c3b2907c43e | newspaper/train | model-optimal | +0.004412% | -0.001629 | +0.000000 | +0.000049 | +0.000408 | +0.002195 |
| A-bfe96c3b2907c43e | newspaper/train | traditional | -0.008571% | +0.015349 | +0.000000 | +0.000049 | +0.000092 | +0.000302 |
| A-bfe96c3b2907c43e | bnwiki/heldout | model-optimal | +0.003159% | +0.002759 | +0.000000 | -0.001045 | +0.000326 | +0.002192 |
| A-bfe96c3b2907c43e | bnwiki/heldout | traditional | -0.075480% | +0.006501 | +0.000000 | -0.001045 | +0.000213 | +0.000990 |
| A-bfe96c3b2907c43e | newspaper/heldout | model-optimal | +0.004227% | -0.002192 | +0.000000 | +0.000082 | +0.000404 | +0.002181 |
| A-bfe96c3b2907c43e | newspaper/heldout | traditional | -0.009058% | +0.015193 | +0.000000 | +0.000082 | +0.000091 | +0.000311 |
| A-bfe96c3b2907c43e | bard-novel/heldout | model-optimal | +0.005518% | -0.002677 | +0.000000 | +0.001662 | +0.000429 | +0.002169 |
| A-bfe96c3b2907c43e | bard-novel/heldout | traditional | -0.017442% | +0.013479 | +0.000000 | +0.001662 | +0.000143 | +0.000270 |
| A-44f9108b6803b121 | bnwiki/train | model-optimal | +85.281264% | -4.872455 | +38.356767 | +0.454210 | -0.032543 | -0.079749 |
| A-44f9108b6803b121 | bnwiki/train | traditional | +72.663494% | -3.552410 | +38.356767 | +0.454210 | -0.009510 | -0.009970 |
| A-44f9108b6803b121 | newspaper/train | model-optimal | +89.295256% | -4.615617 | +40.924217 | +0.580019 | -0.025228 | -0.059529 |
| A-44f9108b6803b121 | newspaper/train | traditional | +78.004250% | -3.003555 | +40.924217 | +0.580019 | -0.006468 | -0.008304 |
| A-44f9108b6803b121 | bnwiki/heldout | model-optimal | +85.380846% | -4.902340 | +38.391639 | +0.464065 | -0.032267 | -0.078585 |
| A-44f9108b6803b121 | bnwiki/heldout | traditional | +72.713687% | -3.601736 | +38.391639 | +0.464065 | -0.009205 | -0.008848 |
| A-44f9108b6803b121 | newspaper/heldout | model-optimal | +89.360311% | -4.618919 | +40.934247 | +0.585854 | -0.025371 | -0.060048 |
| A-44f9108b6803b121 | newspaper/heldout | traditional | +78.064997% | -3.001763 | +40.934247 | +0.585854 | -0.006606 | -0.008674 |
| A-44f9108b6803b121 | bard-novel/heldout | model-optimal | +89.484895% | -4.464641 | +40.911560 | +0.625962 | -0.024966 | -0.059407 |
| A-44f9108b6803b121 | bard-novel/heldout | traditional | +78.100203% | -2.810920 | +40.911560 | +0.625962 | -0.005989 | -0.008499 |
| A-ce2afa6edf5c4d08 | bnwiki/train | model-optimal | +88.358208% | -5.024919 | +39.828518 | +0.529139 | -0.026281 | -0.064540 |
| A-ce2afa6edf5c4d08 | bnwiki/train | traditional | +76.166646% | -3.388034 | +39.828518 | +0.529139 | -0.003612 | +0.002896 |
| A-ce2afa6edf5c4d08 | newspaper/train | model-optimal | +91.694722% | -4.696335 | +42.141878 | +0.577068 | -0.020447 | -0.047383 |
| A-ce2afa6edf5c4d08 | newspaper/train | traditional | +80.748199% | -2.901445 | +42.141878 | +0.577068 | -0.001943 | +0.002085 |
| A-ce2afa6edf5c4d08 | bnwiki/heldout | model-optimal | +88.483847% | -5.054435 | +39.884118 | +0.538928 | -0.025975 | -0.063438 |
| A-ce2afa6edf5c4d08 | bnwiki/heldout | traditional | +76.248139% | -3.430216 | +39.884118 | +0.538928 | -0.003299 | +0.003870 |
| A-ce2afa6edf5c4d08 | newspaper/heldout | model-optimal | +91.768748% | -4.696172 | +42.155262 | +0.584196 | -0.020574 | -0.047868 |
| A-ce2afa6edf5c4d08 | newspaper/heldout | traditional | +80.818644% | -2.898006 | +42.155262 | +0.584196 | -0.002063 | +0.001757 |
| A-ce2afa6edf5c4d08 | bard-novel/heldout | model-optimal | +91.781885% | -4.551242 | +42.057203 | +0.621900 | -0.020369 | -0.047213 |
| A-ce2afa6edf5c4d08 | bard-novel/heldout | traditional | +80.723922% | -2.725058 | +42.057203 | +0.621900 | -0.001637 | +0.001919 |
| D-e4a6be48881da590 | bnwiki/train | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | bnwiki/train | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | newspaper/train | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | newspaper/train | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | bnwiki/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | bnwiki/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | newspaper/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | newspaper/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | bard-novel/heldout | model-optimal | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-e4a6be48881da590 | bard-novel/heldout | traditional | +0.000000% | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| D-841a9b84244e2457 | bnwiki/train | model-optimal | +0.014412% | -0.001037 | +0.000000 | +0.001037 | -0.000121 | +0.000000 |
| D-841a9b84244e2457 | bnwiki/train | traditional | +0.211157% | +0.000329 | +0.000000 | +0.001037 | -0.000682 | -0.001770 |
| D-841a9b84244e2457 | newspaper/train | model-optimal | +0.002918% | -0.001811 | +0.000000 | +0.001811 | -0.000044 | +0.000000 |
| D-841a9b84244e2457 | newspaper/train | traditional | +0.080783% | +0.003075 | +0.000000 | +0.001811 | -0.000235 | -0.000254 |
| D-841a9b84244e2457 | bnwiki/heldout | model-optimal | +0.016183% | -0.000904 | +0.000000 | +0.000904 | -0.000131 | +0.000000 |
| D-841a9b84244e2457 | bnwiki/heldout | traditional | +0.216427% | +0.000842 | +0.000000 | +0.000904 | -0.000699 | -0.001800 |
| D-841a9b84244e2457 | newspaper/heldout | model-optimal | +0.003097% | -0.001781 | +0.000000 | +0.001781 | -0.000047 | +0.000000 |
| D-841a9b84244e2457 | newspaper/heldout | traditional | +0.083470% | +0.002700 | +0.000000 | +0.001781 | -0.000246 | -0.000289 |
| D-841a9b84244e2457 | bard-novel/heldout | model-optimal | +0.003788% | -0.002124 | +0.000000 | +0.002124 | -0.000042 | +0.000000 |
| D-841a9b84244e2457 | bard-novel/heldout | traditional | +0.076118% | +0.003693 | +0.000000 | +0.002124 | -0.000212 | -0.000186 |
| D-02b98dd44dba58ec | bnwiki/train | model-optimal | +48.570990% | -4.375282 | +12.453663 | +2.322760 | -0.044495 | -0.100860 |
| D-02b98dd44dba58ec | bnwiki/train | traditional | +37.660864% | -3.245466 | +12.453663 | +2.322760 | -0.019353 | -0.007831 |
| D-02b98dd44dba58ec | newspaper/train | model-optimal | +50.126126% | -4.179573 | +13.132692 | +2.362476 | -0.039162 | -0.084132 |
| D-02b98dd44dba58ec | newspaper/train | traditional | +41.453096% | -3.603828 | +13.132692 | +2.362476 | -0.016334 | -0.002705 |
| D-02b98dd44dba58ec | bnwiki/heldout | model-optimal | +48.634242% | -4.410455 | +12.485821 | +2.320075 | -0.044418 | -0.101045 |
| D-02b98dd44dba58ec | bnwiki/heldout | traditional | +37.759203% | -3.284085 | +12.485821 | +2.320075 | -0.019421 | -0.008512 |
| D-02b98dd44dba58ec | newspaper/heldout | model-optimal | +50.169113% | -4.173161 | +13.130845 | +2.354106 | -0.039285 | -0.084704 |
| D-02b98dd44dba58ec | newspaper/heldout | traditional | +41.470741% | -3.607174 | +13.130845 | +2.354106 | -0.016409 | -0.003018 |
| D-02b98dd44dba58ec | bard-novel/heldout | model-optimal | +50.120127% | -4.113088 | +13.066763 | +2.463494 | -0.039400 | -0.084040 |
| D-02b98dd44dba58ec | bard-novel/heldout | traditional | +41.309664% | -3.598802 | +13.066763 | +2.463494 | -0.016507 | -0.003165 |
| D-bf128e0d74dfe6a8 | bnwiki/train | model-optimal | +48.638057% | -4.391754 | +12.453663 | +2.319825 | -0.044669 | -0.101223 |
| D-bf128e0d74dfe6a8 | bnwiki/train | traditional | +37.717400% | -3.257624 | +12.453663 | +2.319825 | -0.019536 | -0.008253 |
| D-bf128e0d74dfe6a8 | newspaper/train | model-optimal | +50.172232% | -4.181645 | +13.132692 | +2.362446 | -0.039272 | -0.084834 |
| D-bf128e0d74dfe6a8 | newspaper/train | traditional | +41.473148% | -3.603606 | +13.132692 | +2.362446 | -0.016398 | -0.003064 |
| D-bf128e0d74dfe6a8 | bnwiki/heldout | model-optimal | +48.700967% | -4.427636 | +12.485821 | +2.317316 | -0.044598 | -0.101409 |
| D-bf128e0d74dfe6a8 | bnwiki/heldout | traditional | +37.812297% | -3.297135 | +12.485821 | +2.317316 | -0.019599 | -0.008890 |
| D-bf128e0d74dfe6a8 | newspaper/heldout | model-optimal | +50.214624% | -4.175369 | +13.130845 | +2.354204 | -0.039389 | -0.085389 |
| D-bf128e0d74dfe6a8 | newspaper/heldout | traditional | +41.491016% | -3.606928 | +13.130845 | +2.354204 | -0.016470 | -0.003383 |
| D-bf128e0d74dfe6a8 | bard-novel/heldout | model-optimal | +50.162626% | -4.113272 | +13.066763 | +2.463310 | -0.039491 | -0.084813 |
| D-bf128e0d74dfe6a8 | bard-novel/heldout | traditional | +41.327623% | -3.597047 | +13.066763 | +2.463310 | -0.016556 | -0.003609 |

The full JSON retains coverage bounds, individual pair components, repeated-key and distance diagnostics, both fingerings, and every corpus separately. Secondary movement scores are checks for regressions, not additional success gates or a combined comfort ranking. Held-out scores never guide search or selection; these already-examined benchmarks are exploratory, not fresh human validation.

## What the search explored

Each seed cycles among the reference, retained J1 maps, a perturbed reference, a random permutation and the greedy J1 map. Seeds cycle through the recorded relative Chebyshev directions, including J1-only exploration. Negative energy for nonzero directions means both relative objectives improve, but final success is verified using exact fractions. These directions diversify search; they are not ergonomic weights.

Each run keeps a bounded non-dominated training archive, and the final report selects a bounded training archive from their union. Best observed joint-goal candidates and each run's attained-direction endpoint are additionally protected from crowding. Per-run archives, seeds and starts are saved in runs/. Pruning is explicit; the frontier is not exhaustive. Annealing and iterated local search use separately cached O(1) swap deltas for each symmetric pair objective; no corpus text is read in the search loop.

Candidates are best found for the stated search, never proven optimal. A result of zero joint improvements does not prove none exist. Existing optimality certificates do not transfer. The original J1 challenge DATA_VERSION, layout files, reproduction lock and website scores are unchanged. Layout JSON files in layouts/ are compatible with the challenge scorer and remain separate from published layouts.

## Reproduction and interruption

search-plan.json pins settings, code and data before dispatch. Each completed run is saved atomically and hashed in progress.json. Use the same command with --resume after interruption; worker count may change. Resume refuses changed code/data/settings and refuses an already completed run. A fresh output directory is required for another experiment. run-manifest.json records all output hashes and preservation checks.
