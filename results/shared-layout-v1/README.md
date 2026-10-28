# Shared-layout v1: joint Goti/Jhor experiment

This isolated experimental season searches for **one 52-symbol key arrangement with two vowel-entry modes**: Goti (A) and Jhor (D). Both modes use their original encoders, fixed punctuation/digits, Shift costs, geometry and scoring constants. Published layouts, reproduction locks, challenge scoring and website numbers stay the reference. This protocol adds no application feature or replacement layout.

## Frozen design

Selection uses only the original independently normalized 50/50 Wikipedia/newspaper training mix and model-optimal fingering. The three already examined held-out sources and traditional fingering are diagnostics after training selection. These known benchmarks are exploratory, not fresh confirmation.

The search has two arms, with the same number of seeds per arm:

1. **Original-effort arm.** Minimize `max(E_A/E_Aref, E_D/E_Dref) - 1`. Each reference is the original published layout of that mode. Exact rational scores determine the lowest retained worst relative effort loss; the sum of ratios breaks exact ties only. Neither mode is assigned a popularity weight.
2. **Balance restoration and exploration arm.** Preserve frozen Balance v1 eligibility: `E_s <= 1.005 E_sref` and `W_s <= 1.05 W_sref`, separately for A and D. Cross-space distance remains a positively weighted diagnostic, with regressions allowed under the existing policy. No cap is relaxed after observing results.

Here `E` is J1 effort per text unit, `W` is within-word same-finger different-key distance per text unit, and `X` is cross-space same-finger different-key endpoint distance per valid key–space–key window. Normalize each source using its own denominator, then average sources. X and W are never added as raw distances. Base/Shift actions project onto physical keys for movement; separate Shift motion is excluded from distance but priced in J1. Identical physical-key repeats are not different-key movement.

For proposal generation only, let `r = (E_A/E_Aref, E_D/E_Dref, W_A/W_Aref, W_D/W_Dref, X_A/X_Aref, X_D/X_Dref)` and:

```
v_i = max(0, (r_i - 1)/allowance_i - 1), i = 0..3
allowance = (0.005, 0.005, 0.05, 0.05)
q_d = max(v) + 0.001 sum(v)
      + 0.0001 [(1-d)(r_4+r_5)/2 + d(r_2+r_3)/2 + 0.05(r_0+r_1)/2]
d in {0, 0.5, 1}
```

These declared proposal priorities aid constraint restoration and movement exploration; **q is not Balance v1 R, a measured comfort model, or a strictly lexicographic constraint solver**. Its small secondary term can permit tiny constraint trade-offs. Final eligibility uses exact rational effort and the unchanged direct-distance tolerance, never q or cached floating-point acceptance.

Every retained mechanically feasible candidate is rescored with full four-component frozen Balance v1, including Engram order-coverage bounds. A seeded random pair-swap refinement proposes neighbors of the eligible archive, first checking cheap mechanical constraints, then evaluating both complete R values. A bounded non-dominated `(R_A, R_D)` archive retains the alternatives. Dominance compares A with A and D with D; **raw R values are never summed, averaged, or compared across styles**. No cross-style scalar Balance winner is invented. Full R enters the refinement and final archive, rather than every annealing proposal. No complete cubic-objective optimization is claimed.

Both arms explore the same bijective assignment space. A permutation always specifies the same symbol positions for A and D. Starts cycle through original Goti, original Jhor, the adopted Balance v1 Goti and Jhor leaders, perturbed existing maps and random permutations. Seeds, directions and starts are retained. No corpus text is exported and no new dependency is used.

## Search and storage

Each run uses simulated annealing, swap-local descent and iterated local search. Cached quadratic swap deltas cover E/W/X for both modes; accepted swaps update all relevant states together. Per-run archives retain a bounded set of lowest proposal energies, including the final best endpoint. Both arms and starting maps contribute to the final candidate pool. Archive pruning is explicit: visited maps and Pareto frontiers are not exhaustive. Selection can miss useful order trade-offs filtered out by the proposal archive.

Defaults are 32 seeds per arm (64 total), 200,000 proposals and 30 ILS trials per seed, 8 retained maps per run, at most 8 full-Balance frontier maps and 2,048 Balance refinement proposals. This is a v1 exploratory search budget, substantially smaller than the original published 512-seed searches. A failed feasibility search does not prove that a shared layout is impossible.

The protocol, code/data hashes and settings are saved before worker launch. Each completed seed is saved atomically; explicit resume requires unchanged code, data, environment, parameters and protected artifacts, and verifies completed checkpoint hashes. Worker count can change. Completed runs cannot be overwritten. Incomplete final evaluation can be restarted from verified seed checkpoints; refinement repeats deterministically.

`selection.json` records the training-selected candidates before any held-out evaluation. Each finalist is independently checked against direct count-based mechanics, exact integer J1 and both styles of the official challenge scorer. All selected maps, including the four original comparison maps, receive the five source diagnostics under both fingerings. Outputs include report, layout assignments, training pool, per-source scores and input/output manifests. Layout files are research assignments, not Kala application imports.

## Run

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_search --out results/shared-layout-v1/run-v1 --workers 8
```

A small end-to-end verification uses a separate directory:

```powershell
python -m bangla_dh.experimental.shared_search --out work/evaluator-experiments/shared-smoke --seeds 1 --steps 100 --ils-iterations 1 --balance-refine-steps 8 --workers 1
```

After interruption, repeat the same command with `--resume`. Fresh repeat runs need a new output directory. Standard library tests:

```powershell
python -m unittest discover -s tests -p test_shared_search.py
```

Claims remain **best found**. No Phase 4 certificate transfers to this shared problem, and modeled effort/movement is not measured speed, learning benefit or comfort. Published-layout adoption would require a separately coordinated release season and human validation.
