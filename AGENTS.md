# kala-layout — instructions for agents and new contributors

**Current publication (28 October 2026): one shared provisional Kala Layout arrangement (research identifier B01), with Goti (A) and Jhor (D) as typing styles.** Read `docs/SHARED_LAYOUT.md`. Active descriptor: `data/layout-publications/shared-v1.json`; outputs: `results/shared-publication-v1/`. Original separate-layout research, exports and challenge remain historical. CLI challenge/export/board commands default to shared-v1; use `--season legacy-v1` explicitly for the original season. Never globally repoint `mix.mixed_best_layout` or rewrite old model evidence. Run `challenge-kit`, `publish-shared`, `leaderboard`, then `check-results`; the shared portable scorer includes frozen mechanics and both styles. Current claims must name the relaxed shared eligibility policy, separate R calibration and provisional status.

This repository is the public, repeatable record of how the **Kala Jhor** and **Kala Goti** Bangla keyboard layouts were found (Bangla-DH Pure: Colemak Mod-DH effort model applied to Bangla, searched under an explicit objective). It is the research only: the Kala Windows application is a separate project, and nothing here changes how Kala types.

The pipeline began inside the Kala repository (`colemak-bangla/`). This repository carries it forward so that outsiders can rerun it: Kala's small Bangla inputs are vendored, and the large texts come from the public `ban-dataset-collection` at run time.

## Read first

1. [README.md](README.md) and [docs/HOW_WE_FOUND_THEM.md](docs/HOW_WE_FOUND_THEM.md): what the project claims and how.
2. [docs/REPRODUCE.md](docs/REPRODUCE.md): the three ways to run it and what each checks.
3. [docs/RESEARCH_SPEC.md](docs/RESEARCH_SPEC.md): the full plan, decisions D1–D6 and the changelog (written inside the Kala repository; paths to Kala files now mean the copies under `data/kala/`).
4. [docs/colemak-model-spec.md](docs/colemak-model-spec.md): the frozen, tested mathematics of the original model.
5. The phase reports under `results/`, in order: `phase1`, `phase2`, `phase3`, `phase3-crosscheck`, `phase4`, `mix-search`, `kala-keyboards`.

## Commands (run from the repository root)

```bash
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m bangla_dh --help
```

In PowerShell set `$env:PYTHONPATH = "src"` first; `pip install -e .` provides a `bangla-dh` command instead. Run multiprocessing commands from the command line, not from stdin (Windows spawn re-imports the main module).

| Task | Commands |
| --- | --- |
| Data | `fetch-data`, `prepare-data`, `verify-data` (`lock-datasets` is the maintainer's) |
| Phase 2 | `build-inventory`, `build-corpus`, `compute-frequency`, `evaluate-phase2` |
| Phase 3 | `build-problem`, `style-frequency`, `optimize`, `evaluate-phase3` |
| News cross-check | `crosscheck-build`, `crosscheck-optimize`, `evaluate-crosscheck` |
| Proofs (optional, OR-Tools) | `certify-lp`, `certify`, `sensitivity`, `evaluate-phase4` |
| Final layouts | `mix-optimize --styles A D --seeds 512`, `kala-export` |
| Challenge | `challenge-kit`, `challenge-verify FILE`, `leaderboard [--check FILES]` |
| Run it yourself | `generate-layout --style D [--seeds N] [--reproduce]` |
| Did it reproduce? | `check-results` (compares with `results/reproduction.lock.json`) |
| Shared local certificate | `certify-shared --radius 3 --out EMPTY_DIR`, `verify-shared-certificate` (all 45,526 two/three-symbol alternatives; no global claim) |
| Model check (optional) | `fetch-upstream`, `reproduce-colemak` |

Timings on 32 cores are in [docs/REPRODUCE.md](docs/REPRODUCE.md). Everything is deterministic for its seeds.

## Rules

* **No texts in Git.** `data/ban-dataset-collection/` and `data/corpus/` are downloads and build products, ignored by Git. The repository may contain counts and tables derived from these search corpora, never the corpus texts. **Owner exception, 26 October 2026:** `data/usage-metric-dataset/` may contain full original predefined-prompt typing-study packages, including text and events, published by the usage-metric receiver. Withdrawal removes packages from the current dataset; earlier Git history and other copies may retain them. See `data/usage-metric-dataset/README.md`. This dataset does not change frozen search inputs or published scores. The lock `data/datasets.lock.json` pins the collection commit and every SHA-256; do not edit it by hand (use `lock-datasets`).
* **Standard library only**, Python ≥ 3.10, with one approved exception: OR-Tools (`ortools==9.14.6206`, optional extra `phase4`), used only by the Phase 4 solver modules. Ask before adding any other dependency.
* **Writers go through `bangla_dh.paths.output_path`**, which refuses any path outside the repository.
* **Never edit `reference/colemak-dh-resources/`.** The files are pinned by SHA-256 in `reference/sources.lock.json` and are byte-identical to the upstream files (`.gitattributes` disables line-ending conversion). **Never commit `reference/upstream/`**: the original analyzer has no licence; `fetch-upstream` downloads it at the pinned commit.
* **`bangla_dh.colemak` is a faithful port, quirks included** (binary32 frequencies, Java rounding, the caseless-script double count). Do not "fix" it. Bangla scoring belongs in new modules (`bangla/`, `corpus/`, `scoring/`, ...).
* **`results/phase1/` is the frozen baseline.** Tests compare against `reproduction.json` bit for bit. Regenerate it only with `reproduce-colemak`, and only for a deliberate model change; explain the change in the spec changelog.
* **Do not change model constants silently.** P_d, finger factors, penalties and geometry are frozen in `docs/colemak-model-spec.md`. A new phase may add parameters, but they must be recorded in its run manifest and reported separately from J0.
* **Bangla text is NFC Unicode code points.** Never key on drawn glyphs. ড় ঢ় য় decompose under NFC. Validate Kala's data rather than trust it (its conjunct list contains a Devanagari entry).
* **Every phase writes `results/<phase>/`** with a report, machine-readable results and a `run-manifest.json` (input and output SHA-256, parameters, seeds).
* **A change to the search, the model, the texts or the symbol problem changes the published layouts.** It must be a new season: update `results/reproduction.lock.json` (`check-results --lock`), the challenge `DATA_VERSION`, the docs and the website numbers together, and say so in the spec changelog.
* **Claims follow RESEARCH_SPEC section 14:** "best found", "bounded near-optimum" or "proven optimal". Use "proven" only for the exact stated scope. Scores are modeled effort, never measured typing speed.
* **Baselines are fixed layouts only; never compare with phonetic layouts** (owner decision, 10 October 2026). Add a layout by registry entry; see [data/baselines/README.md](data/baselines/README.md).
* **The website is bilingual and built from the Markdown.** Edit `docs/*.md` and its Bangla pair in `translations/bn/docs/`; never the generated `site/src/content/`. `npm run build` in `site/` fails when a pair drifts. Bangla needs a native-speaker review when its meaning changes.

## Where things are

| Need | Location |
| --- | --- |
| Original analyzer port, effort-grid model | `src/bangla_dh/colemak/`, `src/bangla_dh/geometry/` |
| Symbol inventory, normalization, typing grammar, vowel styles | `src/bangla_dh/bangla/`, `data/bangla-symbols-v1.json` |
| Dataset fetch, assemble, verify | `src/bangla_dh/datasets.py`, `data/datasets.lock.json` |
| Corpus and frequencies | `src/bangla_dh/corpus/`, `data/corpus-v1.json`, `data/crosscheck-v1.json` |
| Scorers and baselines | `src/bangla_dh/scoring/`, `data/baselines/` |
| Search problem and search | `data/problem-v1.json`, `src/bangla_dh/search/`, `phase3.py`, `mix.py` |
| Run-it-yourself search | `src/bangla_dh/generate.py` |
| Proofs | `src/bangla_dh/phase4.py`, `search/integer.py`, `search/bounds.py`, `search/lp_bound.py`, `search/cpsat.py` |
| Kala layout files | `src/bangla_dh/kala_export.py`, `results/kala-keyboards/` |
| Challenge scorer and leaderboard | `src/bangla_dh/challenge*.py`, `leaderboard.py`, `challenge/`, `submissions/` |
| Reproduction check | `src/bangla_dh/reproduction.py`, `results/reproduction.lock.json` |
| Vendored Kala inputs | `data/kala/` (hashes in `data/kala/SOURCES.json`) |
| Website | `site/`, `docs/`, `translations/bn/docs/` |
