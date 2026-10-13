# Additional evaluation season e2

Source-verified Dvorak-7 and Engram movement comparison, 13 October 2026.

See [run-v1/REPORT.md](run-v1/REPORT.md) for all eight public fixed layouts, both
fingerings, all three held-out sources, individual components, frequent pair
deficits, ranking reversals, coverage limits and the 101 retained search maps.

The published J1 layout season is preserved. Results are mechanics diagnostics,
not measured comfort, speed or new optimality certificates. The optional challenge
report includes them; official scoring is unchanged.

Machine data: public-summary.json, scores.csv, scores.json.gz, candidates.json,
source-fidelity.json, compressed derived counts and run-manifest.json. Gzip outputs
are deterministic (mtime 0), standard-library readable and contain no corpus text.

Reproduction from committed counts:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.mechanics_run --out work/evaluator-experiments/mechanics-repeat --workers 4
```

Add --rebuild-counts to verify the independent token-to-action/triple extraction;
all local token-table hashes must match the frozen frequency records. Every output
directory must be new. Code and third-party source hashes are recorded in the manifest.

The paired website explanation is docs/MECHANICS.md and translations/bn/docs/MECHANICS.md.
The Bangla meaning changes await native-speaker review before publication.
