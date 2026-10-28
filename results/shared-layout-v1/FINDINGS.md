# Shared-layout v1 findings

Completed 32 seeds per track, 64 total, with 12.8 million annealing proposals and 30 ILS trials per seed. The bounded retained pool contains 486 distinct shared assignments. The selected candidate was found by the Balance constraint-restoration track and also has the lowest exact worst relative effort increase in the combined retained pool.

Candidate: **shared-65cdcd9b9364f827**. Its physical assignment is identical under Goti and Jhor vowel entry.

| Measurement | Goti mode | Jhor mode |
| --- | ---: | ---: |
| Training J1 | 1.862789 (+0.708%) | 1.817115 (+0.460%) |
| Training cross-space SF distance | 0.154369 (+30.499%) | 0.147734 (+10.227%) |
| Training within-word SF distance | 0.019103 (+6.578%) | 0.020280 (+5.432%) |
| Engram order-credit coverage interval | 0.788137–0.796666 | 0.775412–0.784204 |
| Existing held-out mean J1 | 1.854916 | 1.808578 |

Percentages compare with the original same-mode published arrangement on the primary training mix. Held-out means are the equal average of three known benchmarks and do not drive selection.

**No retained map passes Balance v1 in both modes.** Goti effort is above the +0.5% cap; both within-word distances exceed +5%. Jhor effort passes its cap. The candidate therefore receives no eligible R in either mode. Full Balance Pareto refinement could not start: zero mechanically eligible retained shared maps were available. Full order diagnostics were still computed for the selected candidate.

The result is substantially closer than reusing either existing original or Balance leader. It does not establish feasibility under the strict current limits, a full Balance optimum, or impossibility. The finite seeds and bounded proposal archives can miss better or eligible shared maps. Further search must keep these results and limits visible; changing caps or scoring rules would be a separately declared experiment.

| Compared with | Changed assignments / 52 | Changed physical keys |
| --- | ---: | ---: |
| A-18fe73cb912ae3f1 | 47 | 47 |
| D-e4a6be48881da590 | 39 | 39 |
| A-a280bdc4ca72c6c7 | 32 | 32 |
| D-9ad5412603069cd6 | 39 | 39 |

The new shared arrangement still requires learning new positions. This experiment measures neither learning cost nor typing speed or comfort. Layout JSON files remain research artifacts; no Kala application feature was changed.

Validation: all 267 repository tests passed; all eight published reproduction groups matched. Additional checks reproduced the Balance-arm seeded run, refused completed-run resume, and verified every manifest input/output/protected hash.
