# Kala Goti: eight-billion-proposal J1 search report

**Result: the search rediscovered the exact original published Kala Goti arrangement. No lower-J1 layout was found.** All 52 symbol positions are identical to the original separate Goti map, `A-18fe73cb912ae3f1`; this is not the shared B01 arrangement.

Run-manifest completion time: **29 October 2026, 15:46:19 Asia/Dhaka**. Classification: **best found**, strengthened by reproduction from fresh seeds. This run produces no new optimality certificate.

## Search scope and budget

| Item | Recorded configuration |
| --- | --- |
| Style | Goti / A only; original UniJoy-style hasant-plus-sign vowel grammar |
| Objective | J_mix = 0.5 J1(Wikipedia training) + 0.5 J1(newspaper training) |
| Model | Frozen J1 key + pair + Shift effort; model-optimal ANSI fingering; middle-index benefit retained |
| Search space | Same 52 symbols on the original 52 base/Shift positions; fixed digits and punctuation |
| Seed range | 20270001–20278000; disjoint from the original mixed-search range |
| Starts | 8,000: one greedy start and 7,999 random starts |
| Annealing proposals | 1,000,000 per start; **8,000,000,000 total** |
| Local search | Steepest descent and 1,000 ILS iterations per start; perturbation strengths 2–6 |
| Confirmation | Three 5,000-iteration ILS runs from the best result, strengths 2–6, 4–10 and 8–16 |
| Earlier-layout polish | None; the terminal reported 0 polish runs |
| Parallel workers | 28, from the executed command |
| Elapsed search time | 12,746 s = **3 h 32 min 26 s**, from completed-search terminal output |
| Run revision | `010ee328d92f8a0f066b89dadfeb89090b0ab877`; run manifest records a clean working tree |

The 8 billion count covers annealing proposals only. Local descent, ILS and confirmation add further work. Revisited proposals are possible; the total number of unique visited arrangements was not recorded. Timing is not a controlled performance benchmark: a process-level Windows performance preference was applied during this run.

## Dataset

| Training source | Documents | Word tokens | Objective weight |
| --- | ---: | ---: | ---: |
| Bangla Wikipedia | 171,685 | 58,136,180 | 50% |
| Bangla newspaper | 386,205 | 110,175,696 | 50% |
| Total | **557,890** | **168,311,876** | **100%** |

The run reused the original frozen style-A frequency tables. Each source is normalized separately before the equal-weight mean; this is not pooling counts by corpus size. All nine inputs listed in this run manifest have identical hashes to the corresponding original publication inputs. Held-out Wikipedia, newspaper and non-overlapping BARD news were scored after selection. They are previously examined benchmarks, so this repeat provides no fresh independent text validation. The historical key `bard-novel` denotes BARD news, not literary novels.

## Findings

| Measurement | Verified result |
| --- | ---: |
| Best training J1 | **1.8496860307151324** |
| Exact frozen-grid mixed score | `1036279711123197914729669/560246276349152954000000` |
| Change from original published Goti | **0** |
| Search starts reaching that exact arrangement | **514 / 8,000 = 6.425%** |
| Successful start types | All 514 successes came from random starts; the greedy start did not reach the best |
| Distinct layouts tied at the lowest exact score among retained endpoints | **1** |
| Distinct retained final search layouts | **241** |
| Symbol assignments differing from published Goti | **0 / 52** |
| Confirmation improvement | None in all three runs |
| Median final J1 across the 8,000 starts | 1.855008031951 (+0.287725%) |
| Worst final J1 across the 8,000 starts | 1.871338577482 (+1.170607%) |

**241 counts distinct saved final layouts, not every layout visited during annealing and local search.** The hit rate describes these particular seeded runs; it is not a probability that Goti is globally optimal. Integer-coefficient verification rules out a hidden rounding tie or a better saved endpoint.

### Ten lowest-scoring distinct saved endpoints

| Rank | Candidate ID | Mixed training J1 | Above published | Runs ending here | Changed assignments |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | `A-18fe73cb912ae3f1` | 1.849686030715 | +0.000000% | 514 | 0 |
| 2 | `A-4e1cd3423a58a451` | 1.849702170455 | +0.000873% | 40 | 7 |
| 3 | `A-3e662797b599457a` | 1.849806115444 | +0.006492% | 2 | 12 |
| 4 | `A-699f547d9ee6d551` | 1.849982598605 | +0.016033% | 1 | 12 |
| 5 | `A-edc1ed137d208156` | 1.850034722880 | +0.018851% | 1 | 5 |
| 6 | `A-44969124f5a18faa` | 1.850155624954 | +0.025388% | 1 | 8 |
| 7 | `A-958d51adad195692` | 1.850224365642 | +0.029104% | 1 | 11 |
| 8 | `A-a3c5a5babf48c0dd` | 1.850271029988 | +0.031627% | 4 | 14 |
| 9 | `A-b80684ffcffa53d9` | 1.850297046434 | +0.033033% | 10 | 9 |
| 10 | `A-8d84fff46f3ffcc7` | 1.850320353476 | +0.034294% | 3 | 7 |

Ranks refer only to the final endpoints retained by these 8,000 runs. The candidate IDs use the existing research identity convention. Complete exact scores and counts for all 241 endpoints are in [report-data.json](report-data.json).

## Comparison with the original separate Goti search

| Measurement | Original published search | New search |
| --- | ---: | ---: |
| Starts | 512 | 8,000 |
| Annealing proposals | 512,000,000 | 8,000,000,000 |
| Starts reaching the winner | 36 / 512 (7.031%) | 514 / 8,000 (6.425%) |
| Best mixed training J1 | 1.849686030715 | 1.849686030715 |
| Winning arrangement | Original published Goti | Identical original Goti |

The new annealing budget is **15.625 times** the original Goti budget. The original search also polished the earlier Wikipedia/news winners; this repeat omitted those seeded polish runs and used three confirmation runs only after its fresh-start searches. Thus it is a larger repeat under the same scoring problem, with the recorded start protocol rather than an exact replay of the original run.

## Source-by-source scores

| Source / scope | New winner J1 | Published Goti J1 | Difference |
| --- | ---: | ---: | ---: |
| 50/50 training mixture | 1.849686030715 | 1.849686030715 | 0 |
| Wikipedia training | 1.869020959311 | 1.869020959311 | 0 |
| Newspaper training | 1.830351102120 | 1.830351102120 | 0 |
| Wikipedia held-out | 1.868918363798 | 1.868918363798 | 0 |
| Newspaper held-out | 1.830017579482 | 1.830017579482 | 0 |
| BARD news held-out | 1.830751738954 | 1.830751738954 | 0 |

The equality follows from identical symbol assignments and was independently checked from the frozen count tables. These are modeled effort scores, not measured typing speed or comfort.

## Verification and interpretation

- Verified all 9 recorded input hashes and both original run output hashes.
- Verified the complete seed range, all 8,000 recorded one-million-step annealing schedules, per-run ILS settings and all three confirmation runs.
- Independently re-scored all 241 distinct saved endpoints with exact integer coefficients and rational source weighting; no endpoint beats the published reference.
- Checked all 8,000 saved floating scores against those exact endpoint scores (maximum difference: 1.55e-15).
- Verified the exported layout and all 52 winner assignments against the original published Goti map.
- Independently checked all five source scores; the saved training-objective/table-scorer agreement check also passes.

**Conclusion:** retain the original separate Goti as the incumbent for its original mixed-training J1 objective. This larger fresh-seed search found no improvement and repeatedly rediscovered its exact arrangement. It strengthens search-stability evidence, while establishing neither global optimality nor a global gap. No new local certificate was computed, and old Wikipedia-only Phase 4 certificates do not transfer to this mixed-corpus run. The result does not decide the Balance objective, Jhor, human typing performance or the practical value of sharing positions.

## Evidence and repeat command

- [Original completed-run manifest](source-run-manifest.json)
- [All search and confirmation records](search/A.json.gz)
- [Saved published-map comparison](comparison.json)
- [Source-score evaluation](mix-search.json)
- [Exported candidate layout](A-layout.json)
- [Report data and verification](report-data.json)
- [Report provenance and hashes](report-manifest.json)

From the repository root, use a new empty output directory:

```powershell
$env:PYTHONPATH = 'src'
python -u -m bangla_dh generate-layout `
  --style A --seeds 8000 --first-seed 20270001 --workers 28 `
  --weights bnwiki/train=0.5 newspaper/train=0.5 `
  --out work/goti-j1-8b-repeat
```

The command has no intermediate checkpoints. Repeating it repeats the recorded seeds; a new research exploration should use a separately recorded seed range. Report generation itself runs no search.


## Durable publication archive

The [byte-identical source report](source-REPORT.md) and source manifests are retained. [Archive manifest](run-manifest.json) records relocation plus compressed/decompressed hashes. See [reading and verification instructions](README.md).
