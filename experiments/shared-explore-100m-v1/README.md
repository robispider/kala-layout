# Matched 100-million shared-search pilot

This extends the completed 10-million pilot using the same unchanged engine and scoring model. Total annealing budget is 100 million: 50 million control and 50 million enhanced, plus separately recorded local/refinement checks. There are 100 paired starts per variant, 500,000 proposals per start and 32 workers.

The fixed seed sequence is nested: the first ten pairs reproduce the smaller pilot, and 90 pairs are additional. This is an expanded experiment, not 100 million independent new proposals. The paired comparison remains within this run. Starting-map policy, archive limits (8/64), early full-score policy/caps, final refinement, +0.75% effort/+7.5% within-word eligibility and all frozen model/calibration constants are unchanged.

The engine freezes settings and code/data hashes before launch, pairs start maps/seeds, and freezes selection before existing held-out diagnostics. It does not support resume. A failed/interrupted run must remain preserved; any repeat uses a new output directory. At this size, complete archive-diversity reporting and full-score evaluation add serial work after parallel seed searches.

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_explore --out results/shared-exploration-pilot-v1/run-100m-v1 --pairs 100 --steps 500000 --workers 32
```

Interpretation will compare qualifying unique layouts, new non-dominated alternatives, separate Goti/Jhor scores and timing. Larger saved counts alone do not establish better layout quality. Existing layouts, scores and artifacts are preserved; no published layout or application feature changes.
