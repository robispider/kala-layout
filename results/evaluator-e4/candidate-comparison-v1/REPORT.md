# Requested candidate comparison against earlier run evidence

[Candidate-by-candidate interpretation and shortlist](INTERPRETATION.md)

This report compares the seven requested A/D placements with Kala Jhor, Kala Goti, three earlier experimental D candidates, and the six fixed-layout baselines scored in e2/e3. The completed run and every original layout/result remain unchanged.

**Evidence scope:** exact corpus-derived modeled scores, not measured typing speed or comfort. Training uses the original independently normalized 50/50 Wikipedia/newspaper mix. Held-out comparisons use one third each of Wikipedia, newspaper and BARD novel news. All layouts use their own frozen encoder; baselines retain the e2/e3 canonical encoder across fingerings. These already examined held-out sources support exploratory comparisons.

**Directions:** lower J1, cross-space SF rate and SF distance are favorable. Higher Engram pair, Engram order and Dvorak-7 credit are favorable. Their coverage bounds are not statistical confidence intervals. Interval-overlap comparisons remain unresolved.

## Requested candidates: training comparison

| Candidate | Style | J1 | J1 change from Jhor | J1 change from same-style published map | Cross-space SF rate | Cross-space SF distance change from Jhor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [A-14557e4aab2f81f6](layouts/A-14557e4aab2f81f6.json) | A | 1.855874426 | +2.60276% | +0.33456% | 6.93950% | -33.25523% |
| [D-fb0954976e8c5a32](layouts/D-fb0954976e8c5a32.json) | D | 1.860798951 | +2.87501% | +2.87501% | 6.14667% | -38.27768% |
| [A-b4106689d404415b](layouts/A-b4106689d404415b.json) | A | 1.871801294 | +3.48328% | +1.19562% | 5.97726% | -37.18606% |
| [D-7af0f238d12d0b4a](layouts/D-7af0f238d12d0b4a.json) | D | 1.880603674 | +3.96992% | +3.96992% | 5.63313% | -44.19097% |
| [D-29a057973f8e46f1](layouts/D-29a057973f8e46f1.json) | D | 1.881102430 | +3.99750% | +3.99750% | 5.58511% | -44.56892% |
| [A-013e60b38d2caf28](layouts/A-013e60b38d2caf28.json) | A | 1.891981548 | +4.59895% | +2.28663% | 4.91097% | -50.24376% |
| [A-7c36e8f26e6c7142](layouts/A-7c36e8f26e6c7142.json) | A | 1.912501586 | +5.73341% | +3.39601% | 4.44772% | -53.03180% |

For style A, the same-style reference is Goti; for D it is Jhor. The same-style column avoids attributing A’s vowel-entry recipe cost to placement alone. None of these candidates has lower primary training J1 than its same-style published map.

## Held-out comparison with earlier layouts: primary fingering

Every row below uses the same three held-out sources and model-optimal fingering. It does not mix a candidate’s training score with a baseline’s held-out score. Within-word SF distance has a different denominator from cross-space distance and is shown separately.

| Layout | J1 | Cross-space SF rate | Cross-space SF distance (u/window) | Within-word SF distance (u/text unit) | Engram pair credit bounds ↑ | Engram order credit bounds ↑ | Escaped units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kala Jhor | 1.800026 | 10.2830% | 0.133171 | 0.019445 | 0.893861–0.898490 | 0.747832–0.756104 | 0.0244% |
| D-072c558b633d1019 | 1.803112 | 8.4675% | 0.111918 | 0.020608 | 0.891892–0.896521 | 0.727226–0.735498 | 0.0244% |
| D-57ae5853f15edfec | 1.809322 | 7.4849% | 0.097974 | 0.023743 | 0.898221–0.902851 | 0.760104–0.768376 | 0.0244% |
| D-8ed0c088f68ad80a | 1.817125 | 6.5811% | 0.087654 | 0.018699 | 0.897462–0.902091 | 0.775926–0.784199 | 0.0244% |
| Kala Goti | 1.843229 | 9.3062% | 0.116043 | 0.018519 | 0.896832–0.901255 | 0.761458–0.769466 | 0.0209% |
| A-14557e4aab2f81f6 | 1.849279 | 6.7849% | 0.087412 | 0.020103 | 0.899739–0.904163 | 0.776163–0.784170 | 0.0209% |
| D-fb0954976e8c5a32 | 1.852390 | 6.1760% | 0.082513 | 0.028692 | 0.890265–0.894895 | 0.766607–0.774879 | 0.0244% |
| A-b4106689d404415b | 1.863444 | 5.9251% | 0.082928 | 0.020732 | 0.897982–0.902406 | 0.790856–0.798863 | 0.0209% |
| D-7af0f238d12d0b4a | 1.873831 | 5.6058% | 0.074014 | 0.022957 | 0.893635–0.898264 | 0.779068–0.787341 | 0.0244% |
| D-29a057973f8e46f1 | 1.874246 | 5.5530% | 0.073458 | 0.022736 | 0.893131–0.897761 | 0.778651–0.786924 | 0.0244% |
| A-013e60b38d2caf28 | 1.887465 | 4.8508% | 0.065559 | 0.014566 | 0.897274–0.901697 | 0.767382–0.775389 | 0.0209% |
| A-7c36e8f26e6c7142 | 1.906229 | 4.3932% | 0.062027 | 0.013257 | 0.893407–0.897831 | 0.741161–0.749168 | 0.0209% |
| Windows Default | 2.154327 | 13.2617% | 0.171891 | 0.073726 | 0.875103–0.894460 | 0.789681–0.821518 | 2.5715% |
| Probhat | 2.561472 | 10.0553% | 0.135470 | 0.078067 | 0.819497–0.854297 | 0.692782–0.743389 | 0.0160% |
| Munir Optima (uni) | 2.590847 | 12.2877% | 0.179446 | 0.139010 | 0.808623–0.814091 | 0.573627–0.580107 | 0.0974% |
| Bornona | 2.618413 | 8.8975% | 0.124641 | 0.096431 | 0.827930–0.832874 | 0.656942–0.665837 | 0.0166% |
| UniJoy | 2.808219 | 22.2504% | 0.334545 | 0.182938 | 0.809718–0.814573 | 0.602206–0.611011 | 0.0128% |
| National (Jatiya) | 2.912252 | 22.2749% | 0.327629 | 0.218022 | 0.779703–0.784501 | 0.525972–0.534487 | 0.0702% |

The baseline J1 here is the e2/e3 canonical-encoder score. It can differ from the original published scoreboard, which independently selects the best encoder/grid result. The next section also checks the candidates against that more favorable original J1 benchmark.

## Favorable baseline benchmarks

| Fixed baseline | Published best J1 (held-out mean) | Lowest cross-space SF rate across the two fingerings | Lowest cross-space SF distance across the two fingerings |
| --- | ---: | ---: | ---: |
| Windows Default | 2.149828 | 12.7759% | 0.171891 |
| Probhat | 2.555256 | 10.0553% | 0.135470 |
| Munir Optima (uni) | 2.585521 | 12.2877% | 0.179446 |
| Bornona | 2.611886 | 8.8975% | 0.124641 |
| UniJoy | 2.797422 | 16.9069% | 0.240791 |
| National (Jatiya) | 2.865663 | 15.8268% | 0.232841 |

Each column is a favorable benchmark for that baseline, not a claim that all those minima occur under one encoder/fingering. Published J1 takes the best original grid score per corpus, then averages the three sources. SF rate/distance take the better equal-weight e3 average across model-optimal and traditional fingerings. No phonetic layout is compared.

The registry covers Windows Default, Probhat, Munir Optima (uni), Bornona, UniJoy and National (Jatiya), plus Jhor/Goti as research references. This does not establish a ranking against every publicly available Bangla layout, alternative typing system or human typist.

## Candidate-by-candidate held-out changes from Jhor

| Candidate | J1 change | Cross-space SF change | Cross-space SF-distance change | Within-word SF-distance change | Engram pair credit lower change | Engram order credit lower change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D-072c558b633d1019 | +0.1714% | -17.6555% | -15.9591% | +5.9803% | -0.001969 | -0.020606 |
| D-57ae5853f15edfec | +0.5165% | -27.2108% | -26.4301% | +22.1028% | +0.004361 | +0.012272 |
| D-8ed0c088f68ad80a | +0.9499% | -36.0000% | -34.1789% | -3.8403% | +0.003601 | +0.028095 |
| A-14557e4aab2f81f6 | +2.7362% | -34.0184% | -34.3610% | +3.3807% | +0.005878 | +0.028331 |
| D-fb0954976e8c5a32 | +2.9091% | -39.9400% | -38.0395% | +47.5516% | -0.003595 | +0.018775 |
| A-b4106689d404415b | +3.5232% | -42.3795% | -37.7281% | +6.6188% | +0.004122 | +0.043024 |
| D-7af0f238d12d0b4a | +4.1002% | -45.4844% | -44.4217% | +18.0583% | -0.000226 | +0.031237 |
| D-29a057973f8e46f1 | +4.1233% | -45.9983% | -44.8390% | +16.9221% | -0.000729 | +0.030820 |
| A-013e60b38d2caf28 | +4.8577% | -52.8270% | -50.7704% | -25.0918% | +0.003413 | +0.019550 |
| A-7c36e8f26e6c7142 | +5.9001% | -57.2766% | -53.4233% | -31.8267% | -0.000453 | -0.006671 |

Credit lower-bound changes are descriptive. The JSON separately records whether full candidate/reference intervals separate or overlap; a favorable change in a bound is not automatically a conclusive full-score ranking.

## Fingering sensitivity

| Candidate | Traditional held-out J1 | Traditional cross-space SF rate | Traditional SF distance | Traditional Engram pair bounds ↑ | Traditional Engram order bounds ↑ |
| --- | ---: | ---: | ---: | ---: | ---: |
| D-fb0954976e8c5a32 | 1.920236 | 5.6365% | 0.079784 | 0.889830–0.894459 | 0.764051–0.772323 |
| D-8ed0c088f68ad80a | 1.926507 | 6.6926% | 0.090708 | 0.891639–0.896268 | 0.750661–0.758933 |
| D-29a057973f8e46f1 | 1.946688 | 5.9493% | 0.081902 | 0.890381–0.895010 | 0.767627–0.775899 |
| D-7af0f238d12d0b4a | 1.948237 | 5.9942% | 0.082321 | 0.890727–0.895357 | 0.767884–0.776156 |
| A-b4106689d404415b | 1.973416 | 6.0141% | 0.084438 | 0.889259–0.893683 | 0.751903–0.759910 |
| D-57ae5853f15edfec | 1.974059 | 7.8405% | 0.104313 | 0.883032–0.887662 | 0.697075–0.705347 |
| D-072c558b633d1019 | 1.975639 | 8.6714% | 0.116864 | 0.875592–0.880221 | 0.662533–0.670805 |
| A-14557e4aab2f81f6 | 1.985440 | 7.2718% | 0.095761 | 0.892904–0.897328 | 0.753980–0.761988 |
| A-013e60b38d2caf28 | 2.100504 | 5.4480% | 0.075267 | 0.879335–0.883759 | 0.725091–0.733099 |
| A-7c36e8f26e6c7142 | 2.114447 | 5.0744% | 0.073691 | 0.876834–0.881258 | 0.701133–0.709140 |

## Evidence checks and downloadable data

* [Complete source/candidate comparison JSON](comparison.json)
* [Training and held-out metrics for both fingerings](metrics.csv)
* [Per-source candidate scores](per-source.csv)
* [All 126 saved-frontier D layouts below J1 1.9](D-under-1.9-frontier.md)
* [All 6,584 distinct saved D maps below J1 1.9](D-under-1.9-all-saved.csv)

The D cutoff is exact and applies to training J1. The frontier list includes Jhor; its running J1 differences are recomputed within the filtered D list. These are saved maps, not all possible layouts. A-7c36e8f26e6c7142 is above 1.9 training J1 and therefore does not meet that cutoff. It remains in the seven-candidate review and on the shortlist at the owner’s explicit request, as an exception to the 1.9 threshold.

Every selected map agrees exactly with the independent official challenge scorer. Existing e2/e3 stored-output and completed-run hashes are verified. Some e2/e3 historical Python input hashes differ after later phases; those differences are disclosed in the JSON, rather than claiming the current checkout reproduces their historical code snapshots. Current e4 scoring-code and data hashes match. Baseline J1 and continuous/Engram rows are joined by identity, corpus and fingering, and their reference J1 values must agree. Original layout and scientific-file preservation hashes are checked after writing the new analysis.
