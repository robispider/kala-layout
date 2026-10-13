# Additional evaluation season e3

Continuous-text action windows and cross-space endpoint mechanics, 13 October 2026.

See [run-v1/REPORT.md](run-v1/REPORT.md) for exact window coverage, all eight fixed
layouts, both frozen fingerings, all three held-out sources, retained A/D maps,
training diagnostics, counting checks and actual timing/memory measurements.

Space remains in the stream. Key–space–key endpoint movement is a descriptive
statistic; edge-space/multiple-space windows are counted without a thumb model.
Modifiers and escape keystrokes remain outside this action-stream scope. This
season changes no published layout, J1, challenge DATA_VERSION or official rank.

The report records hashes and verifies e2 action/interior-triple counts, running
token boundaries, word-table edge formulas, an independent sample scanner and
full uninterrupted-run totals. Compressed counts contain no corpus text.

The saved held-out counting measurements came from a 16-worker stage; the four
A/D training jobs used 4 workers. The full report reuses the verified held-out
counts and their original benchmarks. Encoding time includes correctness checks;
process peak memory can include earlier jobs handled by the same worker.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.continuous_run --out work/evaluator-experiments/continuous-repeat --workers 4
```

Add `--rebuild-counts` to rebuild from the pinned local corpus/token files.
`--heldout-only` runs the initial smaller held-out stage. Output directories
must be new. Rescoring reuses saved counting benchmarks rather than claiming
new counting times. The paired website explanations are docs/MECHANICS.md and
translations/bn/docs/MECHANICS.md; meaning changes await native-speaker review.
