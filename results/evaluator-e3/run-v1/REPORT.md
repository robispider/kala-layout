# Continuous-text mechanics: evaluation season e3

Exact consecutive action windows, including spaces, for all eight public fixed layouts and the retained A/D maps. These are movement frequencies, not measured speed, comfort, a new search objective or an optimality claim.

## Counting rules

Words use their own layout encoder and the frozen e2 canonical policy. Space is an explicit action. Escapes, paragraph ends and document ends break windows. Supported punctuation remains a key action; escaped punctuation breaks the stream. Base/Shift layers are retained; separate modifier presses are excluded. Short words, repeated keys, empty tokens and multiple spaces are preserved.

Canonical baseline encoding minimizes actions with traditional-grid effort tie-breaking, held fixed across both fingerings, as in e2. Adapted baseline J1 can therefore differ from the published scoreboard's independently chosen encoding/fingering; no scoreboard score is replaced.

Within-word windows retain the existing Engram order score. Edge-space windows and windows containing multiple spaces are counted without assigning a thumb or scoring them. For key–space–key, only the two endpoint keys define hand/finger relationships. The intervening space is not removed from the action stream. No upstream Engram formula or constant was changed.

## Exact window coverage

Counts are independent of fingering, but depend on the encoder. Shares use all valid windows after escape resets. They do not estimate windows inside unmodeled escape keystrokes or an error in J1. Escaped text may bias layout comparisons.

| Layout | Corpus | Within word | Edge space | Spanning space | Multiple spaces | Within-word share |
| --- | --- | --- | --- | --- | --- | --- |
| Kala Goti | bard-novel/heldout | 4185173 | 2160297 | 1083133 | 3673 | 56.311% |
| Kala Goti | bnwiki/heldout | 26194712 | 12807604 | 6414406 | 20085 | 57.651% |
| Kala Goti | newspaper/heldout | 46099365 | 24311755 | 12183241 | 41351 | 55.786% |
| Kala Jhor | bard-novel/heldout | 3965333 | 2115059 | 1083055 | 26014 | 55.155% |
| Kala Jhor | bnwiki/heldout | 24886239 | 12654701 | 6414145 | 95656 | 56.494% |
| Kala Jhor | newspaper/heldout | 43645104 | 23840027 | 12182971 | 275887 | 54.595% |
| Bornona | bard-novel/heldout | 3789280 | 2118017 | 1085181 | 26022 | 53.990% |
| Bornona | bnwiki/heldout | 23520649 | 12681138 | 6431054 | 97046 | 55.045% |
| Bornona | newspaper/heldout | 41725930 | 23908528 | 12227402 | 277036 | 53.400% |
| Munir Optima (uni) | bard-novel/heldout | 3738361 | 2115612 | 1082893 | 26016 | 53.690% |
| Munir Optima (uni) | bnwiki/heldout | 23176845 | 12622408 | 6375598 | 95324 | 54.830% |
| Munir Optima (uni) | newspaper/heldout | 41149893 | 23868215 | 12186937 | 276143 | 53.110% |
| National (Jatiya) | bard-novel/heldout | 3961717 | 2115927 | 1084359 | 26021 | 55.116% |
| National (Jatiya) | bnwiki/heldout | 24896756 | 12662279 | 6425784 | 97120 | 56.478% |
| National (Jatiya) | newspaper/heldout | 43618033 | 23883156 | 12217412 | 277028 | 54.526% |
| Probhat | bard-novel/heldout | 3948694 | 2115338 | 1083079 | 26015 | 55.048% |
| Probhat | bnwiki/heldout | 24822407 | 12664098 | 6420230 | 96212 | 56.411% |
| Probhat | newspaper/heldout | 43462744 | 23844147 | 12185658 | 276876 | 54.485% |
| UniJoy | bard-novel/heldout | 4010336 | 2163225 | 1085259 | 3681 | 55.220% |
| UniJoy | bnwiki/heldout | 24837104 | 12833557 | 6431286 | 21471 | 56.290% |
| UniJoy | newspaper/heldout | 44194191 | 24380081 | 12227738 | 42502 | 54.666% |
| Windows Default | bard-novel/heldout | 3697779 | 1990051 | 959115 | 22743 | 55.442% |
| Windows Default | bnwiki/heldout | 22836873 | 11905871 | 5715155 | 81117 | 56.333% |
| Windows Default | newspaper/heldout | 40644641 | 22370377 | 10717364 | 241067 | 54.945% |

## model-optimal: equal-weight held-out endpoint rates

Each source contributes one third. Lower same-finger movement frequency describes fewer same-finger moves across a space; hand switching is descriptive and is not assumed better. Same-key repeats are separate. Every interval retains unsupported endpoint mass with possible values 0 to 1. These are coverage bounds, not confidence intervals. Supported conditional rates and distance bounds are in the machine data.

| Layout | Within-word share | Same key bounds | Same-finger different-key bounds | Opposite-hand bounds | Endpoint coverage |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 55.415% | 3.639–3.639% | 10.283–10.283% | 50.285–50.285% | 100.000% |
| Kala Goti | 56.583% | 2.407–2.407% | 9.306–9.306% | 53.875–53.875% | 100.000% |
| Windows Default | 55.573% | 3.473–3.473% | 13.262–13.262% | 52.165–52.165% | 100.000% |
| Probhat | 55.315% | 2.356–2.356% | 10.055–10.055% | 50.668–50.668% | 100.000% |
| Munir Optima (uni) | 53.877% | 2.058–2.058% | 12.288–12.288% | 44.895–44.895% | 100.000% |
| Bornona | 54.145% | 3.564–3.564% | 8.897–8.897% | 51.406–51.406% | 100.000% |
| UniJoy | 55.392% | 3.815–3.815% | 22.250–22.250% | 55.388–55.388% | 100.000% |
| National (Jatiya) | 55.373% | 3.664–3.664% | 22.275–22.275% | 52.293–52.293% | 100.000% |

Kala Goti has a lower same-finger different-key endpoint rate than the other Kala map, with intervals separated. This does not decide overall comfort. All pairwise comparisons are in public-summary.json.

## traditional: equal-weight held-out endpoint rates

Each source contributes one third. Lower same-finger movement frequency describes fewer same-finger moves across a space; hand switching is descriptive and is not assumed better. Same-key repeats are separate. Every interval retains unsupported endpoint mass with possible values 0 to 1. These are coverage bounds, not confidence intervals. Supported conditional rates and distance bounds are in the machine data.

| Layout | Within-word share | Same key bounds | Same-finger different-key bounds | Opposite-hand bounds | Endpoint coverage |
| --- | --- | --- | --- | --- | --- |
| Kala Jhor | 55.415% | 3.639–3.639% | 9.205–9.205% | 50.139–50.139% | 100.000% |
| Kala Goti | 56.583% | 2.407–2.407% | 8.348–8.348% | 53.679–53.679% | 100.000% |
| Windows Default | 55.573% | 3.473–3.473% | 12.776–12.776% | 52.164–52.164% | 100.000% |
| Munir Optima (uni) | 53.877% | 2.058–2.058% | 13.069–13.069% | 46.515–46.515% | 100.000% |
| Probhat | 55.315% | 2.356–2.356% | 10.859–10.859% | 52.569–52.569% | 100.000% |
| Bornona | 54.145% | 3.564–3.564% | 9.799–9.799% | 50.219–50.219% | 100.000% |
| UniJoy | 55.392% | 3.815–3.815% | 16.907–16.907% | 54.953–54.953% | 100.000% |
| National (Jatiya) | 55.373% | 3.664–3.664% | 15.827–15.827% | 52.272–52.272% | 100.000% |

Kala Goti has a lower same-finger different-key endpoint rate than the other Kala map, with intervals separated. This does not decide overall comfort. All pairwise comparisons are in public-summary.json.

## Benchmark and verification

Encoding includes token counting and comparison with frozen e2 counts. Scan time covers the full running-text boundary pass. Memory is process-lifetime peak working set/RSS and can include an earlier job in a reused worker.

| Encoder | Corpus | Cached word types | Encoding seconds | Scan seconds | Peak process bytes |
| --- | --- | --- | --- | --- | --- |
| Bornona | bard-novel/heldout | 100254 | 30.65 | 2.951 | 532955136 |
| Bornona | bnwiki/heldout | 515824 | 173.761 | 18.697 | 544038912 |
| Bornona | newspaper/heldout | 501020 | 181.466 | 34.908 | 540090368 |
| Munir Optima (uni) | bard-novel/heldout | 100254 | 30.145 | 2.901 | 529604608 |
| Munir Optima (uni) | bnwiki/heldout | 515824 | 171.829 | 18.476 | 539660288 |
| Munir Optima (uni) | newspaper/heldout | 501020 | 184.879 | 36.147 | 539521024 |
| National (Jatiya) | bard-novel/heldout | 100254 | 28.211 | 3.09 | 535142400 |
| National (Jatiya) | bnwiki/heldout | 515824 | 158.439 | 18.142 | 534925312 |
| National (Jatiya) | newspaper/heldout | 501020 | 169.955 | 34.829 | 532303872 |
| Probhat | bard-novel/heldout | 100254 | 28.386 | 3.019 | 539013120 |
| Probhat | bnwiki/heldout | 515824 | 158.107 | 18.051 | 534654976 |
| Probhat | newspaper/heldout | 501020 | 167.743 | 35.034 | 530083840 |
| UniJoy | bard-novel/heldout | 100254 | 5.879 | 2.995 | 532955136 |
| UniJoy | bnwiki/heldout | 515824 | 30.298 | 18.311 | 539013120 |
| UniJoy | newspaper/heldout | 501020 | 30.635 | 34.431 | 533815296 |
| Windows Default | bard-novel/heldout | 100254 | 29.106 | 2.813 | 528527360 |
| Windows Default | bnwiki/heldout | 515824 | 166.298 | 17.686 | 516001792 |
| Windows Default | newspaper/heldout | 501020 | 167.534 | 34.084 | 502575104 |
| A | bard-novel/heldout | 100254 | 2.39 | 2.878 | 161112064 |
| A | bnwiki/heldout | 515824 | 17.223 | 18.066 | 532955136 |
| A | bnwiki/train | 2458519 | 86.816 | 160.631 | 2060255232 |
| A | newspaper/heldout | 501020 | 17.662 | 34.717 | 528527360 |
| A | newspaper/train | 2052203 | 77.42 | 310.011 | 1790652416 |
| D | bard-novel/heldout | 100254 | 2.132 | 3.072 | 162308096 |
| D | bnwiki/heldout | 515824 | 18.105 | 18.306 | 535142400 |
| D | bnwiki/train | 2458519 | 88.578 | 161.959 | 2068209664 |
| D | newspaper/heldout | 501020 | 18.316 | 34.758 | 529604608 |
| D | newspaper/train | 2052203 | 78.591 | 311.662 | 1795510272 |

Every rebuilt job matches e2 unigrams, pairs and within-word triples exactly. Running word frequencies and first/last-paragraph counts match the token table. Edge windows match the word-table formulas. A full-action scanner checks the first 50 paragraphs of each corpus. The full-run window total independently equals the sum of max(run length − 2, 0) over uninterrupted action runs. Synthetic randomized tests cover the optimized scanner and separate full-action scanner.

## Retained candidates and scope

101 retained A/D maps reuse style-specific label windows. All three held-out sources and both fingerings are reported. Training diagnostics use the original 50/50 Wikipedia/newspaper mix, separately for each style. No candidates are selected and no new layouts are searched. Existing held-out comparisons are exploratory; future selection would need independent confirmatory validation.

Original J1, published layouts, challenge DATA_VERSION, acceptance and leaderboard ordering are unchanged. The optional challenge diagnostics can read the hashed committed style windows without running-text downloads.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.continuous_run --out work/evaluator-experiments/continuous-repeat --workers 4
```

Add --rebuild-counts to scan the pinned local corpus/token files. All writers use the repository guard and require a new output directory. Deterministic compressed counts contain no corpus text. Code/input/output hashes, policies, timings and preservation checks are in run-manifest.json. Rescoring preserves original counting benchmarks; it does not claim to repeat those timings.
