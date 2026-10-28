# Kala Layout: shared neighbourhood certificate

Research identifier B01; `shared-76c9b9dbfc689d0b`. Result: **certified neighbourhood non-dominance**.

All 45,526 alternatives moving two through 3 symbols were checked. Every symbol may move across base/Shift layers; all other positions stay fixed. Both styles always share the same map.

| Symbols moved | Exact effort failures | Within-distance failures | Cannot dominate | Dominators | Unresolved |
| --- | --- | --- | --- | --- | --- |
| 2 | 1268 | 3 | 55 | 0 | 0 |
| 3 | 44100 | 3 | 97 | 0 | 0 |

## Exact scope

Frozen shared challenge season, 52 searched symbols, model-optimal ANSI fingering, equal Wikipedia/newspaper training weights, original same-style effort cap +0.75%, within-word distance cap +7.5% (including the existing 1e-14 tolerance), and frozen style-specific Balance calibration. A dominator must be eligible in both styles, no worse in either R, and strictly better in at least one. R values are never added.

Reference R: Goti 0.761312297133290; Jhor 0.441365109131921.

## Numerical safeguards

Effort uses exact integers and rational source normalization. Stored binary64 distance coefficients are lifted to exact integers with a common power-of-two denominator. Order credit uses exact integer triple counts. These exact totals are centres of conservative intervals enclosing the public scorer: nonnegative movement sums use gamma_(m+6), u=2^-53, where m is the maximum source pair count; source ratios and equal means use gamma_4. Balance arithmetic is enclosed outward with nextafter; term sums additionally allow gamma_(4n+16) times their absolute magnitudes for sequential or compensated summation. Counts must convert exactly to binary64; the pinned tables have no underflow/overflow. Only an exact effort failure, a lower within bound above its cap, or a lower R bound above the reference can exclude a candidate. Any undecided boundary is saved as unresolved and prevents certification. No scoring tolerance or calibration is changed.

## Reproduce and inspect

Use an empty destination; existing runs are never overwritten. No corpus text or extra dependency is needed.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh certify-shared --radius 3 --out work/shared-certificate-repeat
python -m bangla_dh verify-shared-certificate results/shared-certification-v1
```

[Certificate](certificate.json), [all candidate decisions](evaluations.jsonl.gz), [input/output hashes](run-manifest.json). The verifier checks hashes, replays the conservative checker and independently recomputes every exclusion witness from the raw source counts or direct portable scorer. Python-source hashes normalize CRLF to LF so Windows/Linux checkouts agree; all other input/output hashes are byte-exact. Small exhaustive tests check the delta mathematics independently. This is executable computational evidence, not a standalone solver proof.

## Limits

This does not prove global Pareto optimality, minimum per-style effort, a global optimality gap, or superiority to another non-dominated trade-off such as B02. It says nothing about measured speed, comfort or learning. Original Phase 4 certificates remain separate and unchanged. The selected map, public scores, challenge season and installed Kala application are unchanged.
