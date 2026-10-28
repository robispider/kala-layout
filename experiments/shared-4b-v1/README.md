# Four-billion-proposal shared-layout experiment

Prepared at the owner's request on 28 October 2026. The long run is **not started by setup**. The owner will run it in a terminal and request interpretation afterward.

## Frozen budget

| Parameter | Value |
| --- | --- |
| Total annealing proposals | **4,000,000,000**, plus local-search checks |
| Workers | **32** |
| Tracks | Original-effort and Balance constraint restoration |
| Starts per track | 10,000; 20,000 total |
| Annealing proposals per start | 200,000 |
| ILS trials per start | 30 |
| First seed | 2026103082; balance-track offset 100000 |
| Per-run archive | 8 low proposal-energy maps plus protected endpoint |
| Full-score frontier limit | 8 |
| Full-score refinement proposals | 2,048 |
| Effort cap | +0.75% versus the original layout of each mode |
| Within-word SF distance cap | +7.5% versus the original layout of each mode |
| Output | `results/shared-layout-relaxed-v1/run-4b-v1/` |

This scales the 100-million experiment by adding starts, while retaining its per-start search settings, caps and score calibration. The seed ranges follow the completed 100-million experiment without overlapping its ranges. Trials can repeat arrangements: four billion proposals does not mean four billion distinct maps or four billion full Balance scores.

The engine is unchanged. Starts include original Goti/Jhor, their Balance-v1 leaders, the earlier shared candidate, perturbed shared candidates and random maps. Effort uses the unchanged original J1. The Balance proposal track checks effort, within-word movement and cross-space movement. Qualifying retained maps then receive the **full frozen Balance score expression**, including order, followed by bounded Pareto refinement. Full R is not evaluated for every annealing proposal. A and D score calibration remains separate; no cross-style R sum is used. Cross-space movement retains no additional hard cap.

The independently normalized 50/50 training mix alone guides search and selection. Existing held-out sources are evaluated after selection and remain exploratory. The engine automatically writes a technical report, scores, research layout maps, checkpoints and a manifest. Human-readable interpretation can be prepared afterward. No application feature, published layout, challenge score or website number changes.

## Start in PowerShell

The runner locates the repository itself, verifies this setup and its engine inputs, and logs terminal output under ignored `work/shared-4b-v1-logs/`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\git repo\kala-layout\experiments\shared-4b-v1\run.ps1"
```

`-ExecutionPolicy Bypass` applies only to this PowerShell process; the command changes no saved execution-policy setting. Alternatively invoke the script from an already configured PowerShell session.

Preflight only, without starting the search:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\git repo\kala-layout\experiments\shared-4b-v1\run.ps1" -CheckOnly
```

After interruption, repeat with explicit resume:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\git repo\kala-layout\experiments\shared-4b-v1\run.ps1" -Resume
```

Completed seed checkpoints are verified before reuse. Resume requires the same code, inputs, settings and Python/platform. A completed run cannot be overwritten. Keep the terminal open and prevent sleep during the run. Avoid editing research code or inputs while it runs, because the engine checks their hashes again before completion. Do not run two instances against the same output directory.

For reference, the exact underlying command from the repository root is:

```powershell
$env:PYTHONPATH = "src"
python -u -m bangla_dh.experimental.shared_relaxed --out results/shared-layout-relaxed-v1/run-4b-v1 --seeds 10000 --steps 200000 --ils-iterations 30 --workers 32 --first-seed 2026103082 --archive-limit 8 --frontier-limit 8 --balance-refine-steps 2048
```

Budget roughly **6–8 hours plus any extended final scoring**, extrapolated from the measured 100-million run; 32-worker performance has not been benchmarked for this budget. Claims remain best found, with bounded archives. These are modeled effort/mechanical trade-offs, not measured comfort or speed.
