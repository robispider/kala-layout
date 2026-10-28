# Shared-layout relaxed v1

The owner requested **+0.75% effort and +7.5% within-word same-finger different-key movement** on 28 October 2026, after examining the strict v1 experiment. This new experiment applies those limits separately against the original Goti (A) and Jhor (D) layouts. The previously started strict 100-million-proposal run was interrupted with its completed seed checkpoints preserved under `results/shared-layout-v1/run-100m-v1/`. It is not a completed 100-million result.

## What changes

Eligibility is now:

```
E_s <= (403/400) E_sref
W_s <= 1.075 W_sref + 1e-14
s in {A, D}
```

Effort uses exact rational counts and grid coefficients. W uses direct binary64 distance with the same absolute tolerance. E is original J1 per text unit; W is within-word same-finger different-key physical-key distance per text unit. Cross-space endpoint distance X retains its distinct per-spanning-window denominator and remains permitted to regress. The same 52-symbol arrangement serves both original vowel encoders, without moving any symbol when switching modes.

**Frozen Balance v1 is preserved.** Its eligibility remains +0.5%/+5%. This experiment evaluates the same R expression for a larger eligible region and records both original and relaxed eligibility. The existing style-specific aspirations, scales, 81 priority settings, augmentation values, order-coverage bounds and frozen calibration minima are copied unchanged. In particular the normalization scales are not widened with the caps. A newly eligible result is an experimental relaxed-policy score, not an original Balance v1 rank. This policy was chosen after reviewing exploratory results and supplies no independent confirmation.

## Search and selection

The protocol follows [shared-layout v1](../shared-layout-v1/README.md), with these explicit differences:

- The constraint-restoration proposal replaces effort allowance 0.005 by 0.0075 and within-distance allowance 0.05 by 0.075. The remaining proposal priorities and temperatures remain the same. This exploration score is not R.
- The earlier shared candidate `shared-65cdcd9b9364f827` is a fifth declared start/comparison map. It already passes the relaxed policy. Starts cycle through the four original/reference leaders, this shared candidate, a perturbed shared candidate and a random arrangement.
- The search budget is 250 seeds per track, 500 total, with 200,000 annealing proposals and 30 ILS trials per seed: **100 million total annealing proposals**, plus local search. The worker count is 28. The first seed is 2026102832, with a 100000 offset for the balance track.
- Every run retains up to eight proposal-energy candidates plus its protected endpoint. The final full-score Pareto archive is bounded to eight alternatives. Up to 2048 seeded feasible-neighbor proposals refine `(R_A,R_D)`. Same-style componentwise dominance is used; no raw cross-style sum or score winner is introduced.

The original-effort arm still minimizes `max(E_A/E_Aref, E_D/E_Dref)-1`. The two arms share the final training candidate pool. The retained effort winner is selected using exact rational scores, with sum of ratios for exact ties only. All mechanically feasible retained maps receive full frozen-expression scoring, including order. Full R enters refinement after mechanical exploration, not every annealing proposal. Bounds can omit useful trade-offs, and no global or exhaustive-frontier claim is made.

Only the original independently normalized 50/50 Wikipedia/newspaper training mix and model-optimal fingering guide search/selection. Selection is frozen before five-source/two-fingering diagnostics, including the three already examined held-out sets. Those remain exploratory and do not tune caps, weights or ranking.

Each final assignment is checked independently against direct mechanical counts, exact integer J1 and the official challenge scorer under both modes. Outputs include the frozen plan, atomic seed checkpoints, selection, retained training pool, complete primary metrics, original/relaxed eligibility flags, research layout JSONs, exploratory source diagnostics, report and manifest. Manifest hashes protect code, inputs, earlier artifacts and outputs. No texts or new dependencies are added. No app layout is installed or published.

## Run and resume

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_relaxed --out results/shared-layout-relaxed-v1/run-100m-v1 --workers 28
```

For a small end-to-end check, use `--seeds 1 --steps 100 --ils-iterations 1 --balance-refine-steps 8 --workers 1` and a new path under `work/evaluator-experiments/`. After interruption repeat with `--resume`; code, inputs, settings, Python/platform and protected files must match. Worker count may change. Completed outputs cannot be overwritten.

```powershell
python -m unittest discover -s tests -p test_shared_relaxed.py
```

Claims remain best found. Existing optimality certificates do not transfer. Modeled effort/movement and order diagnostics are not measured typing speed, learning benefit or comfort. Original publication locks, challenge versions, website scores and layouts remain unchanged.
