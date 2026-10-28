# Kala Layout: one arrangement, two typing styles

**Kala Layout is the public name of the provisional shared key arrangement; Goti and Jhor are its typing styles.** B01 is its technical research identifier. Every symbol keeps its position when styles change. Goti uses hasant/sign vowel entry; Jhor uses context vowels. [Why transition?](docs/SHARED_LAYOUT.md) explains the intended benefit of one remembered map, the mechanical costs and the relearning required.

**Found through four billion search proposals:** 20,000 starts, 200,000 proposals each, plus local search; 113,550 distinct retained arrangements, 961 full qualifying evaluations and two leading trade-offs. Proposals can revisit maps; this is not four billion unique combinations or a proof of optimality. [Search provenance](results/shared-layout-relaxed-v1/interpretation-4b-v1/REPORT.md). Goti builds on the modern fixed-layout tradition of Ekushey UniJoy and Avro/OmicronLab; see [typing-style heritage and credits](docs/TYPING_STYLES.md), including earlier Avro context-vowel automation and the limited scope of Jhor's originality claim.

Previously examined held-out mean modeled effort is **1.854428 (Goti)** and **1.808080 (Jhor)**. Sharing adds about **0.61% / 0.45% effort** versus the original same-style arrangements, with **25.75% / 3.92% more cross-space same-finger distance**. These are model comparisons, not measured learning, speed or comfort. [Current map and rules](docs/LAYOUTS.md), [report](results/shared-publication-v1/REPORT.md), [reproduction](docs/REPRODUCE.md).

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh challenge-verify challenge/shared-v1/reference.json
python challenge/shared-v1/score.py --template my-shared.json
python challenge/shared-v1/score.py my-shared.json
```

The [shared challenge](docs/CHALLENGE.md) accepts one map evaluated in both styles. Its joint eligibility and separate R values are a new season; the original J1 challenge remains legacy. [Shared board](submissions/shared-v1/LEADERBOARD.md). Research exports do not change the installed Kala app; existing installations may retain the original maps. The shared map/exports use MIT; original separate maps retain CC0.

The [shared local certificate](docs/SHARED_CERTIFICATION.md) exhaustively checks all 45,526 alternatives moving two or three symbols. None is jointly eligible and improves one style's R without worsening the other. This is a local non-dominance result, not global optimality.

## Historical original separate-arrangement release

The original description, numbers and commands below describe the original separate-arrangement season. For current reproduction and challenge commands use the links above. In historical commands, use `--season legacy-v1` for builders/verifiers/boards. The old maps, sources, reports and embedded scorer are preserved.

How the **Kala Jhor** (কালা ঝড়) and **Kala Goti** (কালা গতি) Bangla keyboard layouts were found, with everything needed to **run the search yourself, compare the result with ours, and try to beat it**.

[Kala](https://robispider.github.io/kala-releases/en/) is a Windows Bangla typing application. Its two original fixed layouts were not drawn by hand: a computer searched for them under an explicit ergonomic model (the Colemak Mod-DH effort model, extended to Bangla) on large Bangla texts. This repository is the research, cleaned up so that anyone can repeat it.

> **What the numbers mean.** The scores are *modeled finger effort* per typed character, not measured typing speed or comfort. Typing tests with people are the next research step. Our layouts are the **best found** by the search; they are not proven optimal.

## Result in one table

Held-out effort (J1, lower is better) on texts that no search has seen. Recorded comparison with every fixed layout installed in Kala when the research ran.

| Rank | Layout | Wikipedia | Newspaper | Unseen news | Average | Less effort than UniJoy |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Kala Jhor** | 1.8348 | 1.7822 | 1.7830 | 1.8000 | 35.7 % |
| 2 | **Kala Goti** | 1.8689 | 1.8300 | 1.8308 | 1.8432 | 34.1 % |
| 3 | Windows Default | 2.1435 | 2.1510 | 2.1549 | 2.1498 | 23.2 % |
| 4 | Probhat | 2.6022 | 2.5337 | 2.5299 | 2.5553 | 8.7 % |
| 5 | Munir Optima (uni) | 2.5898 | 2.5783 | 2.5885 | 2.5855 | 7.6 % |
| 6 | Bornona | 2.6534 | 2.5923 | 2.5900 | 2.6119 | 6.6 % |
| 7 | UniJoy | 2.7976 | 2.7948 | 2.7998 | 2.7974 | 0.0 % |
| 8 | National (Jatiya) | 2.8913 | 2.8503 | 2.8554 | 2.8657 | -2.4 % |

## Try it

You need Python 3.10 or newer and nothing else (the standard library only). No dataset download is needed for the first three steps.

```bash
git clone https://github.com/robispider/kala-layout
cd kala-layout
```

**1. Check the repository works** (about 5 seconds):

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

**2. Score a layout** against ours and the public layouts (a single file, no setup):

```bash
python challenge/bangla_dh_challenge.py --reference
python challenge/bangla_dh_challenge.py --template D --out my-layout.json
python challenge/bangla_dh_challenge.py my-layout.json
```

**3. Run the search yourself** and see whether you find the same layout as Kala Jhor, or a different one:

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --seeds 32
```

This takes a few minutes. Our published run used 512 seeds per style (about 7.5 hours of processor time per style, 40 minutes for both on 32 cores); `--reproduce` repeats it exactly. See [docs/REPRODUCE.md](docs/REPRODUCE.md).

**4. Rebuild everything from the public texts** (about 1 GB download, then about 1.5 hours of computing on 32 cores) and check that every table equals the one committed here:

```bash
PYTHONPATH=src python -m bangla_dh fetch-data
PYTHONPATH=src python -m bangla_dh prepare-data
```

then the stages in [docs/REPRODUCE.md](docs/REPRODUCE.md).

On Windows PowerShell set `$env:PYTHONPATH = "src"` first, or run `pip install -e .` and use the `bangla-dh` command.

## The challenge

Can you place the 52 Bangla symbols on the keyboard with less modeled effort than Kala Jhor or Kala Goti? Score your layout with the one-file scorer, then add it to [`submissions/`](submissions/) in a pull request. A workflow re-scores it and the [leaderboard](submissions/LEADERBOARD.md) is rebuilt. Rules, scoring and the submission format: [docs/CHALLENGE.md](docs/CHALLENGE.md).

## The data

The texts behind the search are **not stored here**. They are the public [ban-dataset-collection](https://github.com/robispider/ban-dataset-collection): Bangla Wikipedia, a Bangla newspaper collection and BARD news articles, in hash-listed ZIP chunks. `fetch-data` downloads the chunks at a pinned commit into `data/ban-dataset-collection/` (ignored by Git) and checks every SHA-256 against [`data/datasets.lock.json`](data/datasets.lock.json). Sources, attributions and reuse notes: [docs/DATASETS.md](docs/DATASETS.md).

## How the layouts were found

[docs/HOW_WE_FOUND_THEM.md](docs/HOW_WE_FOUND_THEM.md) explains the whole chain in plain language: the effort model, the Bangla typing rules, the texts, the four vowel-entry styles, the search, the optimality bounds, and why Kala Goti and Kala Jhor were chosen. The full plan and every decision are in [docs/RESEARCH_SPEC.md](docs/RESEARCH_SPEC.md), and each phase has a report under [`results/`](results/).

| Folder | Contents |
| --- | --- |
| [`challenge/`](challenge) | The one-file public scorer, reference layouts, challengers' guide |
| [`submissions/`](submissions) | Layout files from challengers and the generated leaderboard |
| [`src/bangla_dh/`](src/bangla_dh) | The pipeline (standard library only; OR-Tools only for the optional proofs) |
| [`data/`](data) | Frozen inputs: symbol inventory, search problem, baselines, vendored Kala files, dataset lock |
| [`results/`](results) | Every phase's report, machine-readable results and run manifest; `kala-keyboards/` holds the layout files for Kala |
| [`reference/`](reference) | The published Colemak Mod-DH resources the model was reproduced from |
| [`tests/`](tests) | Unit and regression tests |
| [`site/`](site) | The bilingual website source |
| [`docs/`](docs) | Explanations, reproduction guide, challenge rules, research specification |

## Use the layouts in Kala

Kala Jhor and Kala Goti are built into Kala. Their layout files are in [`results/kala-keyboards/`](results/kala-keyboards) and can be imported in Kala's layout page.

## Licenses

* Code: [MIT](LICENSE).
* The original Kala Jhor and Kala Goti layout maps are dedicated under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (owner decision, 12 October 2026); see [kala-releases](https://github.com/robispider/kala-releases/blob/main/docs/reference/original-layout-license.md).
* Texts are not part of this repository; each dataset keeps its own terms ([docs/DATASETS.md](docs/DATASETS.md)).
* Other layouts' key maps (`data/baselines/layouts/`) belong to their authors and are kept only as comparison data; see [docs/DATASETS.md](docs/DATASETS.md#third-party-layout-data).
