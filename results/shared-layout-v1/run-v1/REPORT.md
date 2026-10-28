# Shared-layout v1 experiment

One identical 52-symbol assignment serves Goti (A) and Jhor (D). This is an experimental search; all published layouts and frozen scores remain the references. Results are best found, not proven optimal.

Run: 32 seeds per arm, 64 total; 200,000 annealing proposals and 30 ILS trials per seed. The bounded retained pool has 486 distinct assignments. Full Balance refinement: {'initial_frontier': 0, 'refine_proposals': 0, 'full_R_evaluations': 0, 'jointly_eligible_evaluations': 0}.

## Training-selected candidates

Changes are against the original layout of each mode on the original 50/50 training mix and model-optimal fingering. Effort and within-word distance caps remain +0.5% and +5%. R values have separate style calibration and are never added or compared across styles.

| Assignment | Role | A effort | A within distance | A R | D effort | D within distance | D R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shared-65cdcd9b9364f827 | lowest retained exact worst relative J1; closest retained Balance constraint-restoration candidate; ineligible | +0.708% | +6.58% | ineligible | +0.460% | +5.43% | ineligible |
| shared-8cab7309b3311430 | existing comparison: A-18fe73cb912ae3f1 | +0.000% | +0.00% | 0.490656 | +1.218% | +24.83% | ineligible |
| shared-b2c5b3f8b2196605 | existing comparison: D-e4a6be48881da590 | +4.421% | +159.56% | ineligible | +0.000% | +0.00% | 0.240274 |
| shared-de3178d2ceb5108b | existing comparison: A-a280bdc4ca72c6c7 | +0.288% | -14.63% | 0.072760 | +1.625% | +11.61% | ineligible |
| shared-39dccebe0bb8d6ca | existing comparison: D-9ad5412603069cd6 | +4.687% | +150.72% | ineligible | +0.273% | -8.24% | 0.139416 |

**0 retained jointly eligible Balance frontier maps.** Finding none is not proof of impossibility. The lowest retained worst relative effort increase is 0.7084%. It is selected with exact rational scores; a sum of the two effort ratios breaks ties only.

## Best retained effort arrangement

Upper rows are Shift; lower rows are base. Vowel symbols identify the shared key; the selected mode determines their behavior.

| Layer | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঢ় | ৌ | ৃ | ঠ | ৎ | ঘ | ড | ং | ণ | ঙ |
| base | ী | হ | ু | য | ট | চ | স | প | ব | দ |

| Layer | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঁ | ূ | অ | ষ | ঢ | ফ | ছ | ভ | থ |
| base | ি | ্ | া | র | জ | শ | ক | ে | ন |

| Layer | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shift | ঃ | ৈ | ড় | ঞ | ঝ | খ | ধ |
| base | । | ো | ল | ম | গ | য় | ত |

## Protocol and interpretation

The effort arm minimizes max(E_A/E_Aref, E_D/E_Dref)−1. The balance arm explores the largest normalized violation of the two effort and two within-word caps, with a declared small movement guidance term and three cross/within priorities. That proposal objective is not Balance v1 R. Every retained mechanically feasible candidate is rescored using full frozen four-component Balance v1, including order-coverage bounds. Further seeded pair-swap proposals refine a bounded R_A/R_D Pareto archive using training only. See the frozen search-plan.json and protocol README for exact formulas and limits.

No raw A/D R sum, shared comfort score or transferred optimality certificate is introduced. Archive bounds and finite stochastic search can miss eligible candidates and Pareto improvements. Starting maps include the original and Balance leaders; original-arm and balance-arm proposals share the final training-only candidate pool. Full Balance scoring follows mechanical exploration rather than entering every annealing proposal.

selection.json was frozen before held-out evaluation. scores.csv includes every selected assignment under both modes, all five existing text sets and both fingerings. The three known held-out sets remain exploratory diagnostics; no held-out value changes selection or parameters. These metrics are modeled effort and mechanics, not measured speed, learning or comfort.

Layout files are research assignments with both supported styles; they are not application-ready Kala imports. Switching modes also changes vowel-entry rules, even though all physical positions stay fixed.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_search --out work/evaluator-experiments/shared-repeat --seeds 32 --steps 200000 --ils-iterations 30 --workers 8 --first-seed 2026102800 --archive-limit 8 --frontier-limit 8 --balance-refine-steps 2048
```

For interruption recovery repeat with --resume. Completed outputs cannot be overwritten.
