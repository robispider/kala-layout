# Run it yourself

You can repeat the research at three depths. Each depth checks itself and says `PASS` or names what differs. Everything uses Python 3.10 or newer and the standard library; OR-Tools is needed only for the optional proofs.

In PowerShell set `$env:PYTHONPATH = "src"` before the commands below, or run `pip install -e .` once and replace `python -m bangla_dh` with `bangla-dh`. Run the commands from the repository folder. Multiprocessing commands must be started from the command line, not typed into an interactive Python session.

## Which depth do you need

| Depth | What you do | Download | Time | You learn |
| --- | --- | --- | --- | --- |
| 1. Search | Run the layout search and compare with Kala | none | minutes (`--seeds 32`) to about 25 minutes on 32 cores (`--reproduce`) | Do independent searches find Kala Jhor and Kala Goti, or something different or better? |
| 2. Rebuild the tables | Download the public texts and rebuild every keystroke table | about 1 GB | about 30 minutes after the download | Do the texts give exactly the numbers the search used? |
| 3. Everything | Rebuild all stages in order | about 1 GB | about 1.5 hours on 32 cores after the download | Does the whole chain, from text to layout files, reproduce? |

## Depth 1: run the search

The keystroke tables the search needs are committed under `results/`, so no download is needed.

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --seeds 32
PYTHONPATH=src python -m bangla_dh generate-layout --style A --seeds 32
```

A search of 32 seeds takes a few minutes on 8 cores. It starts from random layouts, prints its best layout and the published layout side by side (training J1 and the three held-out J1 values), and says whether it found the same layout, a different one that scores worse, or a better one. It writes its files to `work/generate-<style>/`, never over the published results. The layout file `D-layout.json` or `A-layout.json` can be scored with the [challenge scorer](CHALLENGE.md).

Options:

* `--seeds N`: independent runs. The published layouts were reached from 24 of 512 starts (Jhor) and 36 of 512 starts (Goti), so 32 seeds find them only some of the time.
* `--first-seed N`: shift the seeds to explore other starts.
* `--workers N`: processes to use.
* `--weights bnwiki/train=0.5 newspaper/train=0.5`: change the training mix, for example `bnwiki/train=1` for Wikipedia only.

To repeat the **published** run exactly (512 seeds, the published seed range, and the polishing from the earlier Wikipedia and news layouts):

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --reproduce --workers 28
```

This takes about 25 minutes on 32 cores and prints `the same layout as Kala Jhor` when it matches; the exit code is 0 only if it does.

## Depth 2: rebuild the tables from the texts

```bash
PYTHONPATH=src python -m bangla_dh fetch-data
PYTHONPATH=src python -m bangla_dh prepare-data
PYTHONPATH=src python -m bangla_dh build-inventory
PYTHONPATH=src python -m bangla_dh build-corpus
PYTHONPATH=src python -m bangla_dh compute-frequency
PYTHONPATH=src python -m bangla_dh build-problem
PYTHONPATH=src python -m bangla_dh style-frequency
PYTHONPATH=src python -m bangla_dh crosscheck-build
PYTHONPATH=src python -m bangla_dh check-results --group tables
```

The last command compares every rebuilt frequency and keystroke table with the published one. The data commands are described in [DATASETS.md](DATASETS.md).

## Depth 3: every stage

After depth 2:

```bash
PYTHONPATH=src python -m bangla_dh evaluate-phase2
PYTHONPATH=src python -m bangla_dh optimize
PYTHONPATH=src python -m bangla_dh evaluate-phase3
PYTHONPATH=src python -m bangla_dh crosscheck-optimize
PYTHONPATH=src python -m bangla_dh evaluate-crosscheck
PYTHONPATH=src python -m bangla_dh mix-optimize --styles A D --seeds 512 --workers 28
PYTHONPATH=src python -m bangla_dh kala-export
PYTHONPATH=src python -m bangla_dh challenge-kit
PYTHONPATH=src python -m bangla_dh check-results
```

| Stage | Command | What it does | Ends with |
| --- | --- | --- | --- |
| Phase 2 report | `evaluate-phase2` | Checks the scorer against the original analyzer port and an independent verifier, round-trips 454,000 words, scores UniJoy | three `PASS` lines |
| Phase 3 search | `optimize` | 64 seeds for each of the four styles on Wikipedia | `check-results --group "phase3 search"` |
| Phase 3 report | `evaluate-phase3` | Held-out scores, baselines, independent verification | all checks `PASS` |
| News search | `crosscheck-optimize` | The same search on newspaper text | `check-results --group "news search"` |
| News report | `evaluate-crosscheck` | Scores every baseline layout on the three held-out texts | all checks `PASS` |
| Mixed search | `mix-optimize` | 512 seeds for A and D on the Wikipedia and newspaper mix, then polish | one `PASS` line |
| Kala files | `kala-export` | Writes the layout files and the leaderboard, types 500,000 held-out words with a port of Kala's engine | `Checks: PASS` |
| Challenge kit | `challenge-kit` | Builds the one-file scorer and proves it equals the integer model exactly | twelve `PASS` lines |
| Final check | `check-results` | Compares all tables, searches and layout files with the published ones | eight `PASS` groups |

Each stage rewrites its folder under `results/` (report, results, `run-manifest.json` with the SHA-256 of its inputs and outputs). Use `git diff` to see what changed.

### Optional: the proofs and the model check

```bash
pip install "ortools==9.14.6206"
PYTHONPATH=src python -m bangla_dh certify-lp
PYTHONPATH=src python -m bangla_dh certify
PYTHONPATH=src python -m bangla_dh sensitivity
PYTHONPATH=src python -m bangla_dh evaluate-phase4
PYTHONPATH=src python -m bangla_dh fetch-upstream
PYTHONPATH=src python -m bangla_dh reproduce-colemak
```

The first four produce the certified lower bounds, the scoped proofs and the parameter-sensitivity study of [Phase 4](../results/phase4/REPORT.md) and take several hours. The last two download the original Colemak Mod-DH analyzer at a pinned commit and reproduce its published results (about one minute); every check must end `PASS`.

## Exactness and what to do if it differs

The search is deterministic: the same seed on the same Python gives the same layout. The result also depends on the exp function of your platform's C library, so on a very different platform an annealing run can drift by a last digit and then end somewhere else. The final layouts were reached by many independent seeds, which is why a different platform still finds them. If `check-results` reports `DIFFERS`:

1. Re-run `verify-data` to rule out damaged downloads.
2. Run the unit tests: `PYTHONPATH=src python -m unittest discover -s tests` should end `OK`.
3. Open an issue with your operating system, `python --version` and the names of the differing files.

## Running on a smaller computer

Everything that takes long is parallel. Use `--workers` to limit processes, and `mix-optimize --seeds 64` or `generate-layout --seeds 16` to shorten a search. Keep in mind that fewer seeds find the best layout less often. The assembled texts need about 4 GB of disk space on top of the 1 GB download.
