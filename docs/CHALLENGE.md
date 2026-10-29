# The layout challenge

Current publication: the original separate Goti and Jhor arrangements. [Selection criterion](PUBLICATION_DECISION.md) · [Additional Goti evidence](GOTI_8B.md).

Can you place the Bangla symbols on the keyboard so that they need less modeled effort than Kala Jhor or Kala Goti? This page gives the rules, the steps and the way to enter.

## The rules

* Choose a style. **Style D** (Kala Jhor's): one key for each vowel, and Kala picks the vowel sign or the full vowel from the letter before it. **Style A** (Kala Goti's): every vowel sign has its own key, and a full vowel is hasant followed by its sign, as in UniJoy.
* The style fixes the 52 symbols you place. Place each exactly once on the 26 letter keys Q to M, base and Shift layer. Digits and punctuation keep their places.
* Your score is **J1**, the modeled effort per typed character, averaged over 50 % Wikipedia and 50 % newspaper training text. Lower is better.
* You beat Kala only with a strictly lower J1. Scores are compared exactly as fractions, so there is no rounding.
* As a second check the scorer also types texts that were held out from every search and shows where your layout stands among the public layouts. A real improvement should be lower there too; a win only on the training score may mean fitting to the training counts.

## Enter in five steps

1. Get the scorer. It is one file with no dependencies besides Python 3.10: [challenge/bangla_dh_challenge.py](../challenge/bangla_dh_challenge.py).
2. Start from a reference layout.
3. Change it, or find a layout by running your own search.
4. Score it and read the held-out check.
5. Add the file to [submissions/](../submissions) and open a pull request.

```bash
python challenge/bangla_dh_challenge.py --reference
python challenge/bangla_dh_challenge.py --template D --out my-layout.json
python challenge/bangla_dh_challenge.py my-layout.json
python challenge/bangla_dh_challenge.py --public
```

The layout file is JSON. Each of the 26 letter keys maps to its two symbols, `[base, shift]`:

```json
{
  "style": "D",
  "name": "my layout",
  "author": "your GitHub name",
  "layout": { "Q": ["ট", "ঢ"], "W": ["দ", "ঙ"] }
}
```

The example shows two keys; a real file lists all 26. Vowel signs may be written on a dotted circle (◌া) or alone; the scorer cleans both.

## Find a layout by search

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --seeds 64 --first-seed 7
```

The search starts from random layouts in your seed range, compares its best layout with the published one, and writes `work/generate-D/D-layout.json`, ready to score. Different seeds explore different regions. The published layouts were reached from 24 of 512 starts (Kala Jhor) and 36 of 512 starts (Kala Goti), so a short run often ends on a slightly worse layout. See [REPRODUCE.md](REPRODUCE.md).

## What happens after you submit

A pull request that adds a file to `submissions/` runs a workflow that re-scores the file with the public scorer and fails if it is invalid. The score inside your file is never trusted: only the layout counts. Maintainers merge valid submissions and the [leaderboard](../submissions/LEADERBOARD.md) is rebuilt with `python -m bangla_dh leaderboard`. Two files with the same layout count once; on equal scores the earlier submission keeps its place.

If a submission beats the reference, the maintainers re-check it with the project's own scorers (`python -m bangla_dh challenge-verify FILE`), which compute the exact integer-model J1 and the held-out scores from the full pipeline. A winning layout does not replace Kala Jhor or Kala Goti automatically: the score is modeled effort, and comfort is decided by typing tests with people.

## Optional diagnostic report

With the full repository, you can request a separate report after official verification:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh challenge-verify my-layout.json --diagnostics work/evaluator-experiments/my-check
python -m bangla_dh leaderboard --check my-layout.json --diagnostics work/evaluator-experiments/my-board-check
```

Choose a new output directory for each run. The report compares your layout with its style's reference: same-finger moves between different keys, repeated keys, Shift use, finger load and preference-table coverage. It also shows traditional fingering as a separate scenario. No corpus download is needed; the diagnostic counts are committed.

The preference table covers only part of typing. Its partial values are not whole-layout comfort scores and never affect J1, acceptance, ties or leaderboard ordering. An optional-report failure is reported separately and does not change official verification. Submission pull-request checks include the diagnostic report in their job summary for accepted entries. The standalone scorer is unchanged.

Further details: [experimental evaluation instructions](../src/bangla_dh/experimental/README.md). You can also run the diagnostic reader directly on a challenge-format file.

The optional report also compares source-verified Dvorak-7 and Engram pair movement with your style's reference, including component bounds and frequent transitions that lose credit. Engram triple order is shown from committed counts. These project Shift actions onto physical keys and exclude modifier effort; unsupported events retain coverage bounds. They explain movement trade-offs and do not change the official score. [Read the model comparison](MECHANICS.md).

## Compare with other public layouts

`--public` lists the held-out scores of Kala Jhor, Kala Goti, UniJoy, Windows Default, Probhat, Munir Optima, Bornona and National. To compare another layout under the same model, add its key map as described in [data/baselines/README.md](../data/baselines/README.md) and rerun the comparison.

## How the score is computed

For each training text, every keystroke costs the effort of its key, a Shift-layer symbol adds a press of the other hand's Shift key, and every pair of consecutive keys adds a penalty or a bonus by finger and row. The total is divided by the number of characters. The model is the Colemak Mod-DH effort model on an ANSI keyboard with model-optimal fingering. The keystroke and pair counts for each style are fixed and are built into the scorer, so only the placement changes the score. The generated guide [challenge/USER_GUIDE.md](../challenge/USER_GUIDE.md) lists the effort of every key and the exact penalties.

## For maintainers

* Rebuild the scorer with `python -m bangla_dh challenge-kit`. It refuses to finish unless the standalone scorer reproduces the integer model's J1 exactly for the reference and earlier layouts.
* A change to the guides or the scorer's wording is a new script version. A change to the data, the model or the texts is a new season (raise `DATA_VERSION` in `src/bangla_dh/challenge.py`) with new boards, because old scores are no longer comparable.


[Historical shared-map challenge](SHARED_CHALLENGE.md).
