# Challenge the shared arrangement

Submit **one map used unchanged by both Goti and Jhor typing styles**. Kala Layout is the provisional reference. The season is `bangla-dh-shared-challenge-v1`. [Why sharing?](SHARED_LAYOUT.md) explains the goal and its costs.

## Run the scorer

Python 3.10 or newer, standard library only. Keep the [scoring bundle](../challenge/shared-v1/) together: script, compressed derived counts and mechanics licence. No corpus download or package installation is needed. The package is about 3 MB; scoring both training styles normally takes less than a second on the development machine, not a performance guarantee.

```bash
python challenge/shared-v1/score.py --reference
python challenge/shared-v1/score.py --template my-shared.json
python challenge/shared-v1/score.py my-shared.json --diagnostics
```

Edit the template's 26 letter keys, each with base and Shift symbols. Keep its season; do not supply a style or alternative per-style maps. Every frozen symbol must appear once. Digits, punctuation, encoders and model constants stay fixed. Dotted-circle marks and canonically equivalent Bangla labels are normalized to NFC.

## Eligibility and comparison

Both styles must pass, on the original independently normalized 50/50 training mixture with model-optimal fingering:

* Exact rational J1 at most 403/400 of that style's **original separate-arrangement** effort (+0.75%).
* Within-word same-finger different-key distance at most 1.075 of that original reference (+7.5%), with the existing absolute allowance of 1e-14.

These are the relaxed shared policy, not the original strict Balance policy. Limits are not rebased on Kala Layout. Cross-space movement can regress but remains positively penalized. The frozen four-component expression, all 81 priority settings per style, scales, aspirations, calibration minima and unsupported-order bounds are unchanged.

Eligible maps receive separate Goti and Jhor R values; lower is better within each style. R values are never summed, averaged or compared across styles. An improvement on Kala Layout is no worse in both R values and strictly better in at least one. A lower one-style J1 is insufficient. B02 is a trade-off, not a winner on both scores. Comparisons use unrounded results.

The [shared board](../submissions/shared-v1/LEADERBOARD.md) shows frontier entries first, then dominated and ineligible arrangements. Frontier status compares with Kala Layout and all eligible submissions. Within groups, filenames determine display order, not an overall rank. The same normalized map counts once across both styles; the first processed filename keeps the entry. Equal score vectors remain tied. Reference copies and duplicate submissions are reported separately. Maintainers can use Git history to resolve authorship disputes without changing scores.

## Submit and verify

Add the JSON file to [submissions/shared-v1/](../submissions/shared-v1/) in a pull request. The check recalculates scores; embedded score claims are ignored. Malformed or cross-season files fail validation. Valid but ineligible maps are visibly labeled and receive no joint rank. A valid submission never automatically replaces Kala Layout.

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh challenge-verify my-shared.json
python -m bangla_dh leaderboard --check my-shared.json
```

The first command checks the portable score against the independent integer/direct evaluators. The standalone diagnostics option reports five source scopes under both fingerings, including effort, within/cross movement, order bounds, Shift, repeated keys and escapes. Only training controls eligibility and ranking; already examined held-out results are exploratory diagnostics. Unsupported order mass is bounded, not imputed. Scores are modeled mechanics, not measured speed or comfort.

## Original effort challenge

The [original independent-style J1 scorer](../challenge/bangla_dh_challenge.py), [guide](../challenge/USER_GUIDE.md) and [board](../submissions/LEADERBOARD.md) remain a separate legacy season. They compare the original separate arrangements and do not solve the shared task.

```powershell
python -m bangla_dh challenge-verify --season legacy-v1 challenge/D-reference.json
python -m bangla_dh leaderboard --season legacy-v1 --check challenge/D-reference.json
```

The legacy board refuses a reference copy as a submission; the independent verifier accepts it as a scoring check. [Reproduction instructions](REPRODUCE.md) distinguish both seasons. Changing inputs, policy or calibration requires a new season; never mix boards.
