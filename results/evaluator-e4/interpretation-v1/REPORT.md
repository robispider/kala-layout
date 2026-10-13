# Interpreting the completed e4 search

**The search did not meet the stated goal of lower J1 plus better modeled movement.** It found no lower-J1 layout in the saved archives and no strict joint improvement. Kala Goti and Kala Jhor remain the preferred maps for that goal. The new evaluator does expose meaningful movement/effort trade-offs, including useful candidates omitted by the small final summary. Those trade-offs do not qualify as replacements under the owner’s objective.

This interpretation reads the completed [run](../rigorous-v1/REPORT.md) and all 1,024 saved per-seed archives. It writes a separate analysis directory; every original layout, run result and manifest remains unchanged.

## What was run

The run used 512 seeds for each style, 1,000,000 annealing proposals and 1,000 ILS trials per seed: 1.024 billion proposals and 1.024 million ILS trials in total. Wikipedia and newspaper training each receive half the weight after independent normalization. The primary fingering is the frozen model-optimal grid; held-out scores do not guide search.

Per style, 86 seeds use J1 alone, 86 use direction 0.1, and 85 each use 0.25, 0.5, 0.75 and 0.9. There are 103 published-reference starts, 103 retained-map starts, and 102 each from perturbed references, random permutations and the greedy J1 map.

The filesystem timestamps indicate approximately 131.5 minutes from the saved plan to the final manifest, including final verification. This is an approximate duration, not a persisted wall-time measurement. Summed per-seed elapsed time is 58.13 worker-hours; that is not measured CPU time. The final invocation used 28 workers.

## Result against the objective

| Reference | Training J1 | Cross-space SF movement rate | Distinct saved maps | Reconstructed frontier | Final summary points |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kala Goti (A) | 1.849686030715 | 9.495762% | 12,622 | 93 | 32 |
| Kala Jhor (D) | 1.808795894870 | 10.372783% | 14,270 | 153 | 32 |

All 64 final-summary points comprise two unchanged reference maps and 62 higher-J1 movement trade-offs. None improves both training objectives; none is marked as improving both objectives on all three held-out sources under the primary fingering. Scanning the per-seed archives did not uncover a missed joint success.

Both references appear in all their style’s archives because the implementation inserts them explicitly. They must not be described as 512 independent rediscoveries. Every run’s attained exploration energy is zero to floating-point precision: the reference remains the best retained energy when no joint win is found. That behavior follows from including the reference as an incumbent, and does not establish global optimality.

## Movement means a specific event

The new objective counts **different physical keys assigned to the same finger on the two sides of one space**. It skips the intervening thumb press when classifying the endpoints. Same-key repeats, Shift effort, distance, within-word pair costs and Engram order remain separate. A lower value is evidence of fewer such modeled movements; it is not a claim that all movement, human comfort or typing speed improves.

Rates use all valid key–space–key windows in each source, not all keystrokes or all trigrams. For these style maps endpoint coverage is complete. Percentage changes below are relative; percentage-point changes describe the absolute change in this event rate.

## Trade-offs recovered from the saved archives

The caps below are analytical comparison bands, not a relaxation of the accepted goal. Each row selects the lowest movement rate within that J1-increase cap from the stored training frontier. Selection uses training data only. Zero cap recovers the reference.

| Style | Allowed J1 increase | Actual J1 increase | SF movement reduction | Rate decrease (percentage points) | Source seed |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 0% | +0.000000% | -0.0000% | -0.000000 | A-2026101300 |
| A | 0.01% | +0.009926% | 0.1174% | 0.011149 | A-2026101307 |
| A | 0.03% | +0.029104% | 1.0281% | 0.097631 | A-2026101303 |
| A | 0.1% | +0.098842% | 13.9210% | 1.321903 | A-2026101661 |
| A | 0.5% | +0.481113% | 29.9120% | 2.840369 | A-2026101652 |
| A | 1% | +0.737156% | 35.4766% | 3.368777 | A-2026101449 |
| D | 0% | +0.000000% | -0.0000% | -0.000000 | D-2026101812 |
| D | 0.01% | +0.005759% | 0.0297% | 0.003085 | D-2026101821 |
| D | 0.03% | +0.029811% | 1.1586% | 0.120177 | D-2026101823 |
| D | 0.1% | +0.071558% | 3.9934% | 0.414228 | D-2026102167 |
| D | 0.5% | +0.482235% | 26.7098% | 2.770545 | D-2026102147 |
| D | 1% | +0.956689% | 35.9206% | 3.725969 | D-2026101996 |

At a 0.1% J1 budget, the stored search can cut cross-space SF movement by about 13.92% for A and 3.99% for D. At a 0.5% budget, the reductions are about 29.91% and 26.71%. These are material changes in this narrow metric, but their J1 costs are positive. The owner’s strict goal rejects all of them.

## Why the automatic summary understates the trade-offs

The final report keeps only 32 points per style. Its archive prunes repeatedly using evenly spaced indices in J1 order. That can remove useful intermediate points and cannot be treated as an exhaustive frontier. The per-seed archives retain additional candidates, so this interpretation reconstructs their union before selecting comparison bands. Per-seed pruning still applies: this is the frontier of stored points, not every layout visited or every feasible layout.

| Style | J1 cap | SF reduction shown by 32-point report | SF reduction in stored union |
| --- | ---: | ---: | ---: |
| A | 0.1% | 1.0281% | 13.9210% |
| A | 0.5% | 1.0281% | 29.9120% |
| A | 1% | 1.0281% | 35.4766% |
| D | 0.1% | 0.3589% | 3.9934% |
| D | 0.5% | 0.3589% | 26.7098% |
| D | 1% | 0.3589% | 35.9206% |

This summary loss affects how much movement improvement appears available at a cost; it does not conceal a strict joint win. The run also protects observed joint-goal points during pruning, and the stored-union audit independently found none.

## Do the useful trade-offs carry over?

The following candidates were selected only by the training caps of 0.1%, 0.5% and 1%, then rescored on all sources under both fingerings. Held-out changes below use the primary model-optimal fingering. A negative J1 change is favorable; a positive movement reduction is favorable. These already examined benchmarks provide exploratory checks, not new confirmatory validation.

| Candidate | Held-out source | J1 change | SF movement reduction | Distance reduction |
| --- | --- | ---: | ---: | ---: |
| A, cap 0.1% | bnwiki/heldout | +0.074864% | 11.5938% | 10.6443% |
| A, cap 0.1% | newspaper/heldout | +0.136838% | 16.7667% | 16.0792% |
| A, cap 0.1% | bard-novel/heldout | +0.170809% | 16.9372% | 16.2768% |
| A, cap 0.5% | bnwiki/heldout | +0.656276% | 28.0295% | 21.3570% |
| A, cap 0.5% | newspaper/heldout | +0.305121% | 32.0926% | 26.4233% |
| A, cap 0.5% | bard-novel/heldout | +0.311965% | 30.3349% | 24.7990% |
| A, cap 1% | bnwiki/heldout | +0.664982% | 36.0419% | 31.4496% |
| A, cap 1% | newspaper/heldout | +0.810028% | 34.8307% | 32.2791% |
| A, cap 1% | bard-novel/heldout | +0.838965% | 33.1856% | 30.9881% |
| D, cap 0.1% | bnwiki/heldout | +0.046873% | 3.8945% | 3.3604% |
| D, cap 0.1% | newspaper/heldout | +0.085940% | 4.2225% | 4.2512% |
| D, cap 0.1% | bard-novel/heldout | +0.083526% | 3.8077% | 3.8268% |
| D, cap 0.5% | bnwiki/heldout | +0.455391% | 25.6974% | 24.6997% |
| D, cap 0.5% | newspaper/heldout | +0.505994% | 27.9940% | 27.2819% |
| D, cap 0.5% | bard-novel/heldout | +0.589745% | 28.0033% | 27.3689% |
| D, cap 1% | bnwiki/heldout | +1.066779% | 34.6765% | 30.3619% |
| D, cap 1% | newspaper/heldout | +0.837493% | 37.4337% | 36.8222% |
| D, cap 1% | bard-novel/heldout | +0.942061% | 35.9347% | 35.4803% |

A reduction in event count should also be assessed against distance, repeat frequency and movement within words. The next table is the 50/50 training comparison under the primary fingering. Engram values are changes in lower coverage bounds, so they are descriptive differences rather than complete comfort rankings.

| Candidate | Labels moved | Shift change (pp) | Repeats change (pp) | Distance reduction | Engram pair lower change | Engram order lower change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A, cap 0.1% | 29 | +0.000000 | -0.003122 | 13.0865% | +0.003770 | +0.001733 |
| A, cap 0.5% | 17 | +0.000000 | -0.506082 | 23.7145% | +0.003373 | +0.028167 |
| A, cap 1% | 24 | +0.000000 | -0.411602 | 31.8585% | -0.001205 | +0.009129 |
| D, cap 0.1% | 8 | +0.000000 | +0.066998 | 3.7282% | -0.001322 | -0.010762 |
| D, cap 0.5% | 11 | +0.000000 | +0.009455 | 25.8569% | +0.004040 | +0.011417 |
| D, cap 1% | 49 | +0.224532 | -0.074297 | 33.4215% | +0.003113 | +0.024325 |

All scores for traditional fingering, per-source coverage, and symbol moves are in [analysis.json](analysis.json); the CSV provides the complete per-source comparison for these candidates. The copies in [layouts/](layouts/) identify experimental trade-offs, not replacements for the published layouts.

## What the new evaluator contributed

It contributed an independently measurable cross-word movement criterion and found alternative layouts that improve it at an explicit J1 cost. Reconstructing the stored archives is necessary to see that benefit. It did not find a lower-J1 layout or deliver the strict joint improvement sought here.

The exploration function itself favors the reference when J1 cannot improve: for nonzero directions, a J1 increase makes the relative Chebyshev energy positive even if SF movement drops substantially. This explains why trade-offs live mainly in the archives rather than winning the per-run energy. There is no evidence here that adding this movement criterion makes the unchanged J1 optimum easier to beat.

## Research decision and next work

Keep Kala Goti and Kala Jhor for the current objective. Retain the e3/e4 movement evaluators as diagnostic evidence and preserve the recovered frontier for comparisons. Do not update the official layouts, challenge version, reproduction lock or website layout scores on the basis of this run.

Before another joint search, improve archive reporting so useful low-cost trade-offs survive into the final summary, for example by retaining the nondominated union after the runs and explicitly preserving points within declared J1 bands. That addresses report completeness; it would not turn these trade-offs into joint successes.

If the objective stays strict, the unresolved task is finding a lower-J1 layout first or alongside the movement gate. Additional J1-focused starts or a separately scoped mixed-corpus bound/certificate would investigate that bottleneck. This run supplies no promise that more seeds will help and no proof that a joint improvement is impossible. If a J1 budget is later accepted, that is an explicit owner decision; it is not assumed in this report.

## Evidence and reproducibility

The analysis checked every run-manifest output hash, pinned input hash, protected original-file hash, checkpoint digest and expected seed identity. The reconstructed frontier and all near-reference saved maps were rescored with exact rational J1 and movement. Each reviewed trade-off additionally agrees exactly with the independent official challenge scorer. All source-run and original-layout hashes were rechecked after writing the interpretation.

This directory contains its own manifest, exact reconstructed frontier, selected comparison bands, compact secondary scores, layout copies and the analysis script. Reproduce into a new directory from the repository root:

```powershell
$env:PYTHONPATH = "src"
python results/evaluator-e4/interpretation-v1/analysis.py --source results/evaluator-e4/rigorous-v1 --out work/evaluator-experiments/e4-interpretation-repeat
```

Claims concern best found layouts under the stated search and modeled scores. They are neither optimality proofs nor measured typing-speed or comfort results.
