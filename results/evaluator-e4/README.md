# Experimental season e4: lower J1 and better modeled movement

This search preserves Kala Jhor, Kala Goti and every existing research result.
All new layouts, their comparisons, per-seed archives and hashes go into a new
run directory. It refuses an existing directory unless explicitly resuming an
unfinished run with matching code, inputs and settings.

A success must have **strictly lower J1 and strictly lower cross-space
same-finger different-key movement** than the published layout of the same
style. Both objectives use the original 50/50 Wikipedia/newspaper training
mix and the frozen model-optimal fingering. Movement measures the endpoints
of key–space–key windows; repeated physical keys are counted separately.
J1, Shift costs, model constants and the official challenge remain unchanged.

The search cycles through J1-only and relative Chebyshev exploration directions,
using annealing and iterated local search with cached pair-swap deltas. These
directions diversify exploration; they are not calibrated comfort weights.
Final success uses exact rational scores and independently checks J1 against
the official challenge scorer. Trade-offs with higher J1 remain visible and
are never labeled joint improvements.

Run from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.joint_search --styles A D --seeds 512 --steps 1000000 --ils-iterations 1000 --archive-limit 64 --frontier-limit 32 --workers 28 --out results/evaluator-e4/rigorous-v1
```

This dispatches 512 runs per style, 1,024 in total. Use fewer workers on a smaller
computer. The search reads committed derived counts; no corpus download is
needed. Its full runtime has not been measured. The saved smoke run checks the
pipeline only and provides no evidence that a joint improvement exists.

The [smoke report](smoke-v1/REPORT.md) records 12 short runs covering all six
directions and all five starting strategies. No strict joint improvement was
found. Validation passed 162 tests, the eight original reproduction groups and
the bilingual site build. Checkpoint recovery with one worker reproduced the
same scientific results and byte-identical layout exports as two workers;
timings and output paths naturally differ. All manifest input/output hashes
and protected original-file hashes were checked.

After an interruption, repeat the same command with `--resume` appended.
Worker count may change; all other settings, inputs and Python/platform identity
must match. Completed seeds are checkpointed atomically. An already completed
run cannot be resumed or overwritten: choose another output directory instead.

Outputs include `REPORT.md`, `results.json`, `candidates.csv`, challenge-compatible
files in `layouts/`, per-seed archives in `runs/`, `progress.json`, `search-plan.json`
and `run-manifest.json`. The report compares candidates with the original map
on each source under both fingerings, including Shift share, repeats, Engram
pair cost and triple order. Held-out data never guide search or frontier
selection; these previously examined benchmarks support exploratory checks.

Archives are bounded and pruned, with the best observed joint-goal candidate
protected. The reported frontier is not exhaustive. A candidate is **best found**
for this run, never proven optimal. Zero successes does not prove none exist.
This experimental track does not replace the official research season, its
reproduction lock, challenge version, leaderboard or website scores.

## Completed rigorous run

The [interpreted report](interpretation-v2/REPORT.md) audits the 1,024-run result and reconstructs the saved frontier. No strict joint improvement was found under the primary fingering. New movement/effort trade-offs, held-out behavior, fingering sensitivity and the summary’s pruning losses are reported separately. Original layouts and the completed run remain unchanged.

## Complete evidence table and interpretation correction

The [mechanical statistics table](mechanical-stats-v1/REPORT.md) starts with Jhor and contains all 246 saved frontier rows, with a CSV for all 26,892 distinct saved maps. J1 and SF rates were rescored exactly; SF distance was calculated from the frozen geometry.

**Correction:** the earlier interpretation and balance-review prose reversed the direction of Engram scores. Higher Engram credit is better. Negative credit changes are regressions, not improvements; the J1 and cross-space SF/distance measurements remain correct. Read the [score-direction correction](mechanical-stats-v1/CORRECTION.md) before using the earlier qualitative Engram conclusions. Existing found layouts and raw result files remain unchanged.

## Requested candidate review

The [seven-candidate assessment](candidate-comparison-v1/INTERPRETATION.md) compares the requested A/D maps against the previous e2/e3 fixed-layout results, Jhor/Goti and earlier experimental D maps on the same held-out sources and both fingerings. [Complete metrics](candidate-comparison-v1/REPORT.md) include within-word SF distance and coverage-bound credit comparisons. **A-7c36e8f26e6c7142 is retained on the shortlist by owner request as an explicit movement-focused exception to the 1.9 J1 threshold.** Original layouts and scores remain unchanged.
