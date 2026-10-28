# Kala Layout: one arrangement, Goti and Jhor styles

**Kala Layout** is the public name; **B01/P01** is its research shortlist identifier. The underlying map, encoders and scores are unchanged by this naming update of 29 October 2026.

Owner decision, 28 October 2026: provisionally use `shared-76c9b9dbfc689d0b` (B01/P01), with Goti (A) and Jhor (D) as typing styles. Changing style preserves every symbol position. Selection is a practical compromise, not a new scalar-score optimum or a measured learning benefit.

## Why share

The original arrangements differ at 31/52 assignments. Using the original Goti arrangement for Jhor costs +1.218% training effort and +24.83% within-word distance; using original Jhor for Goti costs +4.421%/+159.56%. B01 instead costs +0.689%/+4.790% in Goti and +0.439%/+3.766% in Jhor. These pass the shared experiment's +0.75%/+7.5% limits against each original on the independently normalized 50/50 training mix and model-optimal fingering. B01 Goti fails the original strict +0.5% effort policy. Calibration is unchanged; the expanded eligible domain is explicitly a new shared challenge season.

Sharing means one arrangement to remember and maintain across styles. It still requires learning a new arrangement: 43 Goti and 39 Jhor symbols move from the originals. Entry recipes remain different. Learning time, error rate, speed and comfort have not been measured.

## Four-billion search provenance

The source run completed 20,000 starts across two tracks, with 200,000 annealing proposals per start: 4,000,000,000 proposals, plus local search. It retained 113,550 distinct assignments; final screening/refinement fully scored 961 qualifying maps and retained two leading trade-offs. Proposals may revisit maps. This was not an exhaustive test of four billion unique combinations, and is not a proof of optimality. The selected B01 map became the provisional Kala Layout. See the original source-run and interpretation manifests for the exact saved scope.

## Typing-style heritage and credit

Goti preserves the modern fixed-layout consonant-then-sign and hasant-plus-sign core: the original Goti search explicitly used the UniJoy-style grammar. Credit [Ekushey's UniJoy contributors](https://ekushey.org/keyboard-layout/ekusheyr-shadhinota-unijoy-layout/) and [Avro/OmicronLab's fixed-layout documentation](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf), including Mehdi Hasan Khan and the Avro team. These entry conventions are not a Kala invention; the key arrangement was searched separately.

Avro also documents Automatic Vowel Forming, so context-sensitive vowel entry predates Jhor. Jhor's exact timing-free repeated-key rule is specified by this project; the reviewed primary documentation did not establish an identical complete recipe or invention priority. [Typing-style credits and source-review scope](../../docs/TYPING_STYLES.md) explain the distinction. This attribution correction changes no grammar, benchmark or score.

## Trade-offs and alternatives

Training cross-space same-finger distance rises +25.59% in Goti and +5.89% in Jhor. On previously examined held-out sources, effort rises +0.608%/+0.447%, within-word distance changes -0.107%/+1.351%, and cross-space distance rises +25.750%/+3.923%. These caps apply only to primary training/fingering. Separate Balance leaders have lower same-style R than B01; one remembered map is outside that formula.

B01 has Goti R 0.761312 and Jhor R 0.441365. These are separately calibrated; they are never added or compared across styles. B02 (`shared-7083b1ebfa5aa3a7`) exchanges ৈ/ৌ between Shift+X/Shift+W and trades a slightly better Jhor R for worse Goti R. Both are non-dominated in the evaluated full-score pools. B01 is the provisional practical preference. The enhanced pilot used shared starts and is not independent rediscovery. Four billion counts proposals, not unique maps/full R evaluations; no optimality proof transfers.

## Previously examined held-out effort

| Configuration | Wikipedia | Newspaper | BARD news | Mean J1 |
| --- | --- | --- | --- | --- |
| Kala Layout · Jhor style | 1.842057 | 1.790535 | 1.791648 | 1.808080 |
| Kala Layout · Goti style | 1.886133 | 1.837932 | 1.839221 | 1.854428 |
| Windows Default | 2.143500 | 2.151000 | 2.154900 | 2.149800 |
| Probhat | 2.602200 | 2.533700 | 2.529900 | 2.555300 |
| Munir Optima (uni) | 2.589800 | 2.578300 | 2.588500 | 2.585500 |
| Bornona | 2.653400 | 2.592300 | 2.590000 | 2.611900 |
| UniJoy | 2.797600 | 2.794800 | 2.799800 | 2.797400 |
| National (Jatiya) | 2.891300 | 2.850300 | 2.855400 | 2.865700 |

Two style configurations of one shared map plus six fixed baselines: seven physical arrangements, eight evaluations. Fixed baselines retain their favorable recorded original effort scores; canonical mechanical envelopes are separate and are not an overall score. All five sources and both fingerings are in scores.csv; exact training effort and separate R are in public-summary.json. All six maps and conservative mechanical/coverage comparisons are documented in [the top-ten comparison](../shared-top10-comparison-v1/REPORT.md). Bijoy positions use the explicitly borrowed UniJoy-rule proxy, not a separately verified commercial implementation. Bornona and Probhat beat B01 on some cross-space metrics; Windows Default has better order credit with greater escapes. No phonetic layouts are compared.

## Evidence, history and availability

The chain is [existing-map check](../shared-style-check-v1/REPORT.md), [strict shared search](../shared-layout-v1/run-v1/REPORT.md), [relaxed four-billion experiment](../shared-layout-relaxed-v1/run-4b-v1/REPORT.md), [interpretation](../shared-layout-relaxed-v1/interpretation-4b-v1/REPORT.md), then [top-ten/pilot comparison](../shared-top10-comparison-v1/REPORT.md). Original mixed-search results, phase reports, exports and legacy challenge remain unchanged. Known held-out results are exploratory reuse, not fresh confirmation. The token `bard-novel` means non-overlapping BARD news documents, not literary novels; references to BARD novels in the historical comparison prose are a naming error, with no numerical effect.

The new map/exports use the repository MIT license; the original separate maps retain their CC0 dedication. Exports are research artifacts, not an installed application update. Goti uses hasant/sign sequences; Jhor requires the application's context-vowel engine. Confirm compatible support before importing; older installations may retain original arrangements. No companion application was modified.

## Rebuild

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh challenge-kit
python -m bangla_dh publish-shared
python -m bangla_dh challenge-verify challenge/shared-v1/reference.json
python -m bangla_dh check-results
```

This rebuild reuses frozen derived counts; no new search/text download. Full source search settings/seeds remain in the original run manifest. run-manifest.json pins the descriptor, evidence, scorer, calibration, inputs and outputs. The new portable shared scorer independently agrees with the integer/direct evaluators under both styles. Model constants, text and typing grammars are unchanged. Best found; no claim of proven optimum, measured speed or comfort.
