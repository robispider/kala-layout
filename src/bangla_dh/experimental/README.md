# Experimental evaluation season e1

## Source-derived movement checks (e2)

`python -m bangla_dh.experimental.mechanics_run --out work/evaluator-experiments/mechanics-repeat --workers 4`
evaluates all eight fixed layouts and all 101 retained maps from committed compressed counts.
Use `--rebuild-counts` for independent extraction from hash-pinned local token tables.
Reports and manifests are in `results/evaluator-e2/run-v1/`; source snapshots, license
and hashes are in `data/evaluators/mechanics-v1/`. There are no new dependencies.

Dvorak-7 and Engram avg4 preserve original scoring bodies and constants. All source
pairs/triples and distributed tables are exhaustively checked. Engram triple order
is separate. Traditional fingering is faithful upstream; model-optimal is an explicit
finger/hand adaptation. Scores project base/Shift onto physical keys and omit modifier
effort. Unknown keys and AltGr retain 0..1 bounds; escapes are disclosed. Pair means
are movement diagnostics, not total comfort or speed. The learned preference table's
e1 restrictions continue independently.

Optional challenge reports automatically include the pair criteria and committed
style triple order, without changing validity, official J1, DATA_VERSION or ordering.
Their JSON includes component bounds and frequent pair deficits. Source/table or count
integrity failures remain optional-report failures. Both website languages have a
movement-comparison page with numbers verified against the saved run manifest.

The Bangla meaning changes need native-speaker editorial review before publication.

An isolated addition to Kala Layout research. Original source modules, layouts, J0/J1, challenge DATA_VERSION, reproduction lock and website numbers are preserved. This is a distinct diagnostic season; it does not promote a replacement published layout season.

The added evaluator reads 288 source-distributed predicted key-pair preference scores from the Engram research ecosystem. It deliberately excludes generated values for unsupported keys. It reports a **conditional supported-pair diagnostic**, not a full-layout comfort score. Full comfort ranking and preference-based candidate selection are disabled: independent held-out prediction reproduction, complete condition coverage and Bangla human validation have not been established.

Run from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental audit --out work/evaluator-experiments/audit-v1
python -m bangla_dh.experimental evaluate --out work/evaluator-experiments/published-v1 --workers 4
python -m bangla_dh.experimental candidates --out results/evaluator-e1/run-v1 --workers 4
```

Every output directory must be new. Existing runs and original result destinations are rejected; writers also use the repository path guard. The original bangla-dh command is unchanged. Start multiprocessing commands from the command line on Windows.

`evaluate` evaluates Jhor/Goti and all six registered fixed baselines. `candidates` also deduplicates all 1,024 stored A/D run outcomes, earlier bests, polish and confirmation maps. Both score canonical actions under traditional and model-optimal fingerings. Baseline encoding uses minimum presses and fixed traditional-grid key-effort tie-breaks across scenarios. Traditional J scores match historical baselines; model-optimal baseline results are separately labeled because historical optimal-grid encoding was not frozen that way.

Use `--no-baselines` if corpus token tables have not been rebuilt. A/D counts are committed; complete market-layout aggregation requires the local token tables named in the frequency records. The default comparison uses all three held-out benchmark sources, while candidate diagnostic frontiers use only the existing 50/50 training mix. The known benchmark is not fresh confirmatory data.

Outputs: REPORT.md, evidence.json, scores.json/CSV, candidates.json, reference rankings.csv and run-manifest.json. Baseline action tables contain derived counts only. The manifest records source/code/data hashes, encoding/layer/boundary policies, parameters and original-file preservation checks. No word text is exported. No dependencies were added.

Source attribution and frozen metadata are in data/evaluators/engram-pair-v1. `lookup-benchmark.json` independently calculates a weighted average from fixed source rows; passing proves arithmetic fidelity, not model validity. Pair-level uncertainties cannot become a layout confidence interval without their joint covariance.

The conditional mean uses a different supported subset for each layout and must not be treated as a comparable full-layout score. Reports preserve unsupported probability mass by layer, missing pair and mismatched fingering. Shift and cross-hand conditions are never silently filled. The Stage 2 descriptive frontier uses existing J1, existing Shift effort M, and same-finger/different-key count per text unit. It excludes preference scores and selects no comfort shortlist.

Next evidence needed: released independently verifiable held-out predictions, data for missing keys/cross-hand/modifier conditions, and independent Bangla pair preference plus sustained layout trials. No original Phase 4 certificate transfers to this diagnostic.

## Changelog

- e1, 13 October 2026: source-pinned partial preference evaluation, canonical action counts, published/reference verification and retained-candidate diagnostics; no published layout change.

## Optional challenge connection

Challenge-format A/D submissions can now be read directly, including UTF-8/BOM, UTF-16, dotted circles and NFC forms accepted by the official parser:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.submissions my-layout.json --out work/evaluator-experiments/my-file
python -m bangla_dh challenge-verify my-layout.json --diagnostics work/evaluator-experiments/my-check
python -m bangla_dh leaderboard --check my-layout.json --diagnostics work/evaluator-experiments/my-board-check
```

Every directory must be new. Reports compare the submitted map with the same-style published reference on the two training sources and three held-out benchmarks, under both fingering scenarios. They preserve directed/repeated pairs, compare model-optimal J1 with the official scorer on every corpus and verify the exact mixed J1 against the integer scorer. Only committed counts are used; no corpus download is needed.

The official command's exit status, J1 and leaderboard board data do not depend on the optional report. Duplicate/reference/rejected leaderboard entries are excluded from its diagnostics. Direct diagnostic runs return a nonzero status for unreadable/invalid files, with problems in the report. Missing evidence, unsupported source pairs and table coverage never become challenge objectives or rejection rules. The partial preference values are available in JSON/CSV with ranking disabled; the human report shows coverage rather than promoting a partial comfort ranking.

Submission pull-request checks request this report and append it to their job summary, while their pass/fail remains the official check. The standalone one-file scorer and challenge DATA_VERSION are unchanged. No new layout season or leaderboard recalculation is introduced.
