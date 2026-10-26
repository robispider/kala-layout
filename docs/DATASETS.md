# Datasets

The layout search learns from Bangla text, but **this repository contains no text**. The texts are the public [ban-dataset-collection](https://github.com/robispider/ban-dataset-collection), and the scripts in this repository download them to your computer when you ask for them.

## What is used

| Package | Folder in the collection | Chunks | Download | Documents | Used for |
| --- | --- | --- | --- | --- | --- |
| Bangla Wikipedia | `wikidata/` | 21 | 248 MB | 171,685 train and 19,063 held-out | Training (50 %) and held-out evaluation |
| Bangla newspaper | `bangla-newspaper/` | 36 | 455 MB | 429,394 (386,205 train and 43,022 held-out after the split) | Training (50 %) and held-out evaluation |
| BARD news articles | `bard/` | 27 | 313 MB | 372,445 (5,131 held-out documents that share no sentence with the newspaper set) | Held-out evaluation only |

The collection stores every package as ZIP chunks below 100 MB, each with a SHA-256 in the folder's `manifest.json`. Wikipedia text was cleaned with Kala's `bnwiki-prose-v1` rules and normalized with `bangla-dh-text-v1` (NFC, punctuation mapping, invisible characters removed) before it was published. The newspaper and BARD packages were cleaned the same way. Each folder has an `ATTRIBUTION.txt`.

## How this repository uses them

```bash
PYTHONPATH=src python -m bangla_dh fetch-data
PYTHONPATH=src python -m bangla_dh prepare-data
PYTHONPATH=src python -m bangla_dh verify-data
```

* `fetch-data` downloads the chunks from `raw.githubusercontent.com` at the commit pinned in [data/datasets.lock.json](../data/datasets.lock.json) into `data/ban-dataset-collection/downloads/`. Every chunk is checked against its pinned size and SHA-256. Use `--package wikipedia` (or `newspaper`, `bard`) to fetch one package, or `--from PATH` to copy the chunks from a local checkout of the collection.
* `prepare-data` assembles the chunks into the files the pipeline reads under `data/ban-dataset-collection/assembled/` and checks each against the SHA-256 of its content in the lock. Compressed files are pinned by their decompressed content, because compressed bytes depend on the zlib build.
* `verify-data` repeats the checks without changing anything.

Everything under `data/ban-dataset-collection/` and `data/corpus/` is ignored by Git. The lock pins one commit of the collection, so a later change to the collection cannot silently change a result here. To move to a newer commit, run `lock-datasets` (a maintainer command) and treat it as a new research season.

## What the repository does contain

* **Counts, not text.** The committed keystroke and pair tables in `results/` and the data inside the challenge scorer are aggregate counts (how often each key and key pair occurs). The original texts cannot be recovered from them. This is why the search and the challenge scorer run without any download.
* **Small Kala files** in `data/kala/`: the Bangla alphabet and conjunct list, the UniJoy and Bijoy fixed layouts and six word lists used for round-trip checks, pinned in `data/kala/SOURCES.json`. They are copies of files from the Kala application at the paths shown there.
* **Public comparison layouts** in `data/baselines/layouts/`: see below.

## Licences and attribution of the texts

* Bangla Wikipedia is available under CC BY-SA. See Wikipedia's copyright page and the article histories.
* The newspaper package is derived from the Kaggle dataset *Bangla Newspaper Dataset* by furcifer. The articles belong to their publishers. Check the dataset terms and the article rights before you redistribute any of it.
* BARD is the dataset of the BARD Bangla Article Classifier project by Tanvir Alam and Md Mofijul Islam. The collection notes that clear redistribution terms were not found; check the source terms before you redistribute.

This repository does not redistribute these search-corpus texts. You download them from their public location yourself, subject to those terms.

## Third-party layout data

The comparison table includes UniJoy and five fixed layouts that Avro Keyboard publishes as imports: Windows Default, Probhat, Munir Optima (uni), Bornona and National (Jatiya). The key maps are in `data/baselines/layouts/` (and `data/kala/kala/layout/bn/UniJoy.json`) so that anyone can rescore them. They are the work of their authors, named in each file. They are kept here only as benchmark data and are not covered by this repository's licence. If you are a rights holder and want a map removed, please open an issue.

## What is not used

The original Phase 2 run also checked a small second text domain (BanLemma sentences). That text is not part of the public collection, so this repository does not rebuild it. Its archived result `results/phase2/frequencies/banlemma-heldout.json` is kept for the record and is not used by any later step.

## Full typing-study sessions

A separate live research dataset is published under
[data/usage-metric-dataset/](../data/usage-metric-dataset/README.md). It retains the
complete original predefined-prompt session packages, including text, key events,
timing and research metadata, for analysis. This is an owner-authorized exception
to the search-corpus text exclusion. It does not change the frozen search inputs
or published layout scores. Withdrawal removes a contributor from the current
dataset; earlier Git history, GitHub caches, forks and downloads may retain copies.
