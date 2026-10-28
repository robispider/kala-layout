# Shared arrangement: movement and trade-offs

## Current Kala Layout results

One arrangement serves Goti (A) and Jhor (D). Below are equal means of the three previously examined held-out sources, normalized separately. Within-word same-finger different-key distance is per text unit; cross-space distance is per spanning window. They cannot be added as raw distances. Effort and distance are lower-is-better; order credit is higher-is-better. Order bounds retain unsupported mass and are not confidence intervals. Shift effort is part of J1; physical-key order projects layers and excludes modifier movement.

| Style | Fingering | J1 | Within distance | Cross-space distance | Order bounds | Escaped share |
| --- | --- | --- | --- | --- | --- | --- |
| Goti (A) | model-optimal | 1.854428 | 0.018499 | 0.145923 | 0.777256–0.785263 | 0.021% |
| Goti (A) | traditional | 2.003928 | 0.050533 | 0.120883 | 0.743621–0.751629 | 0.021% |
| Jhor (D) | model-optimal | 1.808080 | 0.019708 | 0.138395 | 0.764513–0.772786 | 0.024% |
| Jhor (D) | traditional | 1.938823 | 0.043834 | 0.126911 | 0.740875–0.749147 | 0.024% |

The main cost of sharing is Goti's cross-space regression; [the transition rationale](SHARED_LAYOUT.md) compares with the original separate maps. Traditional fingering is a separate scenario, not an eligibility guarantee. All five source scopes, both fingerings, repeated keys, Shift and coverage are in the [publication summary](../results/shared-publication-v1/public-summary.json) and [score table](../results/shared-publication-v1/scores.csv). [The full fixed-baseline comparison](../results/shared-top10-comparison-v1/REPORT.md) retains favorable canonical mechanical envelopes; it is not a single overall ranking. Bornona/Probhat win some cross-space comparisons and Windows Default has stronger order credit with more escapes. No measured comfort or speed is established.

## Original separate-arrangement diagnostics (historical)

The tables below retain the original e2/e3 results and original names. They do not score B01. Their numerical provenance continues to be checked separately.

<!-- historical-mechanics -->


Dvorak-7 and Engram criteria add a useful check of which priorities favor Kala Jhor or Kala Goti. We adapted the original upstream scoring code, verified its calculations, and evaluated all eight fixed layouts and 101 retained search maps. The results describe modeled movement, not measured comfort or speed.

## What we learned

With the upstream model's traditional fingering, Goti earns more Dvorak-7 and Engram pair credit than Jhor, even after allowing for missing coverage. Jhor still has lower J1 effort. Goti receives more credit for hand/finger distribution, home-row use and inward movement; Jhor receives more finger-strength credit. Engram's largest pair-component difference is its same-finger criterion, which counts repeated keys as well as changes between keys.

With Kala's model-optimal fingering, the two layouts' pair-score bounds overlap. Neither pair model conclusively orders them there. Goti has higher Engram triple-order credit under both fingerings. Windows Default has higher triple-order credit than both Kala layouts, but escapes about 2.6% of text units. The order diagnostic also excludes Shift effort. This is a trade-off worth investigating, not an overall comfort ranking.

Both Kala layouts earn more pair credit than the five other baselines under traditional fingering, allowing for missing-pair bounds. Their pair comparison with Windows Default remains unresolved. The models share features with J1, so agreement supports robustness to some assumptions; it is not independent scientific validation.

## All eight fixed layouts

Higher movement scores are better within their scope. Each interval retains unsupported events, assigning their possible values from 0 to 1. These are coverage bounds, not statistical confidence intervals or comfort percentages. Each source contributes one third: held-out Wikipedia, newspaper and BARD novel news.

Traditional fingering preserves the upstream rules:

| Layout | Dvorak-7 bounds | Engram pair bounds | Engram order bounds | Pair coverage | Escaped text units |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 0.759194–0.763823 | 0.876980–0.881609 | 0.678379–0.686651 | 99.537% | 0.024% |
| Kala Goti | 0.769583–0.774007 | 0.889982–0.894406 | 0.741212–0.749220 | 99.558% | 0.021% |
| Windows Default | 0.759952–0.779309 | 0.873047–0.892405 | 0.786608–0.818445 | 98.064% | 2.572% |
| Probhat | 0.647842–0.682642 | 0.818740–0.853540 | 0.671286–0.721894 | 96.520% | 0.016% |
| Munir Optima (uni) | 0.693853–0.699321 | 0.822285–0.827753 | 0.624074–0.630554 | 99.453% | 0.097% |
| Bornona | 0.682367–0.687310 | 0.823476–0.828420 | 0.635725–0.644620 | 99.506% | 0.017% |
| UniJoy | 0.711979–0.716834 | 0.814766–0.819621 | 0.589398–0.598203 | 99.514% | 0.013% |
| National (Jatiya) | 0.700064–0.704862 | 0.806023–0.810821 | 0.561324–0.569839 | 99.520% | 0.070% |

The adapted model-optimal scenario changes fingers to Kala's frozen grid while retaining the source's physical rows, columns and inside/outside key set:

| Layout | Dvorak-7 bounds | Engram pair bounds | Engram order bounds | Pair coverage | Escaped text units |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 0.778331–0.782960 | 0.893861–0.898490 | 0.747832–0.756104 | 99.537% | 0.024% |
| Kala Goti | 0.781226–0.785650 | 0.896832–0.901255 | 0.761458–0.769466 | 99.558% | 0.021% |
| Windows Default | 0.761988–0.781345 | 0.875103–0.894460 | 0.789681–0.821518 | 98.064% | 2.572% |
| Probhat | 0.646987–0.681787 | 0.819497–0.854297 | 0.692782–0.743389 | 96.520% | 0.016% |
| Munir Optima (uni) | 0.690848–0.696316 | 0.808623–0.814091 | 0.573627–0.580107 | 99.453% | 0.097% |
| Bornona | 0.688388–0.693331 | 0.827930–0.832874 | 0.656942–0.665837 | 99.506% | 0.017% |
| UniJoy | 0.724888–0.729743 | 0.809718–0.814573 | 0.602206–0.611011 | 99.514% | 0.013% |
| National (Jatiya) | 0.695163–0.699961 | 0.779703–0.784501 | 0.525972–0.534487 | 99.520% | 0.070% |

## What each model counts

Dvorak-7 awards credit for distribution across hands/fingers, stronger fingers, home-row use, small row separation, finger columns, remote-finger patterns and inward movement. Its score is the seven-criterion sum divided by seven.

The Engram pair score uses the upstream generator's explicit average of four criteria: row separation, same-row direction/column separation, same-finger movement and outside reach. Key preference, scissor and half-scissor values appear separately in the full report. The upstream table-combination code can average extra columns under the same score name; we use the explicit four-criterion formula and document that choice.

J1 adds no pair penalty for repeating the identical action, while Engram gives a same-finger pair zero credit even when the physical key repeats. The pair mean measures credit per transition; J1 measures effort per text unit and prices extra presses and Shift. These different priorities help explain the reversal.

Engram order examines three consecutive keys. It awards credit for the source's hand changes and monotonic finger sequences, and withholds credit for its mixed/repeated-finger cases. It is a separate diagnostic, not part of a new combined comfort score.

All three project base and Shift actions onto physical keys; they exclude modifier effort and chords. Pairs preserve direction and repeated keys. Triples stay within a word/token and never cross a space or escape. Number-row values come from rules already present in the source functions. Unsupported keys and AltGr remain unsupported. Escaped text is outside the scored movement domain and may bias comparisons; it is disclosed rather than assigned an invented movement score.

The learned Engram preference table examined earlier remains a separate, partial evidence audit. These source-defined movement rules do not fill its missing empirical evidence.

## Verification and reproduction

The MIT upstream code is pinned to commit `179e1c08b220ae1b02f6c425a7d1cbd1150c1db2`. Extracted scoring functions match the originals on every defined key pair and every distributed triple; all 49,152 distributed table rows agree to floating-point precision. Traditional baseline J0/J1 agree with the historical results, and triple extraction reproduces the frozen action counts. This verifies the software, not human comfort.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.mechanics_run --out work/evaluator-experiments/mechanics-repeat --workers 4
```

Committed compressed counts allow this comparison without downloading texts. Add `--rebuild-counts` to independently rebuild them from local pinned token tables. Candidate frontiers use the existing training mix only: eight A maps and twelve D maps show conservative trade-offs among J1 and the pair models. These maps came from J1 searches; no new layout or new optimality claim is selected.

The optional [challenge report](CHALLENGE.md) now includes these diagnostics. Official J1 scoring and leaderboard ordering remain unchanged.

[Full explainable report](../results/evaluator-e2/run-v1/REPORT.md) · [Results table](../results/evaluator-e2/run-v1/scores.csv) · [Source verification](../results/evaluator-e2/run-v1/source-fidelity.json) · [Pinned source and licence](../data/evaluators/mechanics-v1/README.md).

<!-- continuous-e3 -->
## Continuous-text windows (e3)

The tables above describe within-word movement. The additional continuous-text study counts every valid three-action window in each paragraph, including spaces. On held-out Wikipedia with Kala Jhor's style D encoder, 56.494% of valid windows stay within a word and 43.506% touch a space. These are exact counts after escape resets; they are not an estimate of error in J1 or of unmodeled escape keystrokes.

Each layout uses its own word encoder, including UniJoy's extra vowel actions and Avro-fixed formatting/reph behavior. Supported punctuation remains a key action; escaped punctuation breaks windows. Escapes, paragraph ends and document ends reset the stream. The four categories are within-word, edge-space, spanning-space and multiple-space; the last includes a one-action word between two spaces. Separate Shift/AltGr presses are excluded, matching the existing action-stream scope.

### Results across spaces

For key–space–key windows, the two endpoints define repeats, same-finger moves, hand relationships and distance. Space remains in the stream. Same-key repeats are separate from moving the same finger to a different key. Edge-space and multiple-space windows are counted without assigning a thumb model or an Engram order score. No new weights or combined comfort score are introduced.

Each held-out source contributes one third. The within-word share below averages source shares rather than pooling their counts. Endpoint rates use all valid key–space–key windows, retaining unsupported mass in coverage bounds. Lower same-finger movement frequency describes fewer such moves; opposite-hand frequency is descriptive and does not establish a comfort winner.

| Layout | Within-word share | Same-finger moves: traditional | Same-finger moves: model-optimal | Opposite hands: traditional | Endpoint coverage |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 55.415% | 9.205% | 10.283% | 50.139% | 100.000% |
| Kala Goti | 56.583% | 8.348% | 9.306% | 53.679% | 100.000% |
| Windows Default | 55.573% | 12.776% | 13.262% | 52.164% | 100.000% |
| Probhat | 55.315% | 10.859% | 10.055% | 52.569% | 100.000% |
| Munir Optima (uni) | 53.877% | 13.069% | 12.288% | 46.515% | 100.000% |
| Bornona | 54.145% | 9.799% | 8.897% | 50.219% | 100.000% |
| UniJoy | 55.392% | 16.907% | 22.250% | 54.953% | 100.000% |
| National (Jatiya) | 55.373% | 15.827% | 22.275% | 52.272% | 100.000% |

All 101 retained A/D maps are also reported. Training diagnostics use the original 50/50 Wikipedia/newspaper mix; no candidates are selected. Existing held-out comparisons are exploratory, and future selection would need independent confirmatory validation. Original layouts, J1, challenge acceptance and leaderboard ordering are unchanged.

### Reproduce and inspect

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.continuous_run --out work/evaluator-experiments/continuous-repeat --workers 4
```

Committed hashed counts allow rescoring without corpus downloads. Add `--rebuild-counts` to scan the pinned local texts; `--heldout-only` runs the smaller stage first. Rebuilt unigrams, pairs and within-word triples must match e2 exactly. Running word frequencies and paragraph boundaries, edge-space formulas, a separate reference sample and the full uninterrupted-run window total are checked. The report records actual encoding/scanning times, cache sizes and process peak memory; rescoring retains the saved benchmarks.

[Continuous-text report](../results/evaluator-e3/run-v1/REPORT.md) · [Continuous results](../results/evaluator-e3/run-v1/scores.csv) · [Continuous provenance](../results/evaluator-e3/run-v1/run-manifest.json).

The new Bangla explanatory copy awaits native-speaker review before publication.
