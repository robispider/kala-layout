# Git-safe storage for large experimental results

Two derived artifacts exceeded GitHub's file-size limit. Their byte-identical `.gz` versions are committed; their original local CSV/JSON copies are ignored by Git and retained for inspection. No counts, layouts, scores, official locks or original run manifests were changed. Git LFS and extra dependencies are unnecessary.

- `results/balance-study-v2/candidate-metrics.csv.gz`
- `results/evaluator-e4/rigorous-v1/results.json.gz`

The gzip files contain the exact original UTF-8 bytes, including CSV CRLF endings. `storage-manifest.json` records both physical and decompressed SHA-256 hashes. Historical run manifests retain the logical `.csv`/`.json` names and their original hashes. The experimental artifact readers fall back to `.gz` when the logical file is absent; hash verification uses decompressed bytes for that logical path, and compressed bytes for an explicit `.gz` path. Official dataset/reference verification is unchanged.

New joint-search summaries are written as `results.json.gz`; experimental CSV writers compress tables of at least 50 MiB. Smaller CSV reports remain plain. New manifests can record physical `.gz` paths; readers accept either manifest form. Original code hashes remain historical run provenance and are not rewritten to claim the code is unchanged.

To inspect a compressed artifact, use Python's standard-library gzip module, an archive tool, or the experimental readers. Decompressing the two named files back to their original paths creates only ignored local copies. There is no need to restore them to run the reports from a fresh checkout.
