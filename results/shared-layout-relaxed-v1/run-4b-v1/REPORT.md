# Shared-layout experiment: relaxed eligibility

**Owner-requested limits: +0.75% J1 effort and +7.5% within-word SF distance, separately for Goti and Jhor.** This is a new experimental eligibility policy chosen after examining v1; it is not independent confirmation or an official Balance v1 ranking. Frozen Balance v1 aspirations, scales, settings, order bounds and calibration constants remain unchanged.

Completed 20000 seed runs on 32 workers, 4,000,000,000 annealing proposals plus local search; 113550 distinct retained shared maps. Full score refinement: {'initial_frontier': 1, 'refine_proposals': 2048, 'full_R_evaluations': 961, 'jointly_eligible_evaluations': 961}.

**2 retained jointly eligible relaxed-score Pareto alternatives.** A and D R values retain separate calibration and are never added or compared across styles. No single Balance winner is asserted.

## Training-selected maps

Changes compare with each mode's original published map on the independently normalized 50/50 training mix and model-optimal fingering. R below means the unchanged frozen expression evaluated under this experiment's relaxed eligibility. Separate original Balance v1 flags are saved in results.json.

| Assignment | Role | A effort | A within | A cross | A R | D effort | D within | D cross | D R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shared-f9096b7bb25243ef | lowest retained exact worst relative J1 | +0.600% | +32.79% | +42.14% | ineligible | +0.623% | +30.02% | +20.49% | ineligible |
| shared-76c9b9dbfc689d0b | relaxed-eligibility R_A/R_D Pareto alternative | +0.689% | +4.79% | +25.59% | 0.761312 | +0.439% | +3.77% | +5.89% | 0.441365 |
| shared-7083b1ebfa5aa3a7 | relaxed-eligibility R_A/R_D Pareto alternative | +0.703% | +5.38% | +25.59% | 0.785849 | +0.438% | +3.77% | +5.96% | 0.438747 |
| shared-8cab7309b3311430 | comparison: A-18fe73cb912ae3f1 | +0.000% | +0.00% | +0.00% | 0.490656 | +1.218% | +24.83% | +1.25% | ineligible |
| shared-b2c5b3f8b2196605 | comparison: D-e4a6be48881da590 | +4.421% | +159.56% | +49.93% | ineligible | +0.000% | +0.00% | +0.00% | 0.240274 |
| shared-de3178d2ceb5108b | comparison: A-a280bdc4ca72c6c7 | +0.288% | -14.63% | +18.81% | 0.072760 | +1.625% | +11.61% | +6.14% | ineligible |
| shared-39dccebe0bb8d6ca | comparison: D-9ad5412603069cd6 | +4.687% | +150.72% | +35.42% | ineligible | +0.273% | -8.24% | -12.81% | 0.139416 |
| shared-65cdcd9b9364f827 | comparison: shared-65cdcd9b9364f827 | +0.708% | +6.58% | +30.50% | 0.795110 | +0.460% | +5.43% | +10.23% | 0.476769 |

The lowest retained worst relative J1 loss is 0.6230%. This is a finite best-found result; it carries no optimality or comfort proof.

## Protocol, reproducibility and limits

The original-effort objective is unchanged. Mechanical proposal energy replaces allowances 0.005/0.05 by 0.0075/0.075 in the separately recorded v1 exploration formula. Actual relaxed eligibility uses exact rational effort and direct-distance comparisons with tolerance 1e-14. Full R scoring/refinement follows proposal generation; it does not occur in every annealing step.

Both original maps, both original Balance leaders and the earlier shared best are retained as starting/comparison maps. Per-run archives and the R frontier are bounded and may miss improvements. The full-score frontier uses componentwise same-style dominance. Known held-out data never tune limits, search parameters or selection. Selection is frozen before all held-out/fingering diagnostics. Scores are modeled mechanics, not measured speed, learning or comfort.

Research assignment files are not Kala app imports. Published layouts, frozen scoring, challenge acceptance and website numbers remain unchanged.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_relaxed --out work/evaluator-experiments/shared-relaxed-repeat --seeds 10000 --steps 200000 --ils-iterations 30 --workers 32 --first-seed 2026103082 --archive-limit 8 --frontier-limit 8 --balance-refine-steps 2048
```

Use --resume after interruption with identical settings. Completed runs cannot be overwritten.
