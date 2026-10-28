# Shared-search results: compact Git storage and analysis index

This package preserves the shared-layout research while keeping Git files below GitHub's size limit. **No counts, layouts, scores, formula, model parameters, original scientific manifests or reports change.** No LFS or additional dependency is needed.

Reports, candidate maps, full scores, comparisons, experiment plans, manifests, research code and tests remain ordinary Git files. Raw per-seed JSON evidence is stored losslessly in one deterministic `runs.zip` per run. Derived training pools, including the oversized 4-billion pool, are stored as `training-pool.json.gz`. The original local files remain on disk and are ignored by Git; no evidence is deleted. The interrupted strict run remains explicitly marked incomplete.

## Start the next candidate analysis here

| Evidence | Location |
| --- | --- |
| 4-billion interpretation and keyboard map | [Interpretation](../shared-layout-relaxed-v1/interpretation-4b-v1/REPORT.md) |
| Primary shared typing-test candidate | [shared-76c9b9dbfc689d0b](../shared-layout-relaxed-v1/run-4b-v1/layouts/shared-76c9b9dbfc689d0b.json) |
| Two-key vowel alternative | [shared-7083b1ebfa5aa3a7](../shared-layout-relaxed-v1/run-4b-v1/layouts/shared-7083b1ebfa5aa3a7.json) |
| 4-billion primary scores and selection | [Results](../shared-layout-relaxed-v1/run-4b-v1/results.json), [selection](../shared-layout-relaxed-v1/run-4b-v1/selection.json) |
| 4-billion source/fingering metrics | [Scores](../shared-layout-relaxed-v1/run-4b-v1/scores.csv) |
| Enhanced 100-million pilot findings | [Findings](../shared-exploration-pilot-v1/FINDINGS-100m.md) |
| Enhanced pilot full scored points and variant comparison | [Results](../shared-exploration-pilot-v1/run-100m-v1/results.json), [frontier comparison](../shared-exploration-pilot-v1/run-100m-v1/frontier-comparison.csv) |
| Original 100-million relaxed search | [Findings](../shared-layout-relaxed-v1/FINDINGS.md) |
| Initial strict shared search | [Findings](../shared-layout-v1/FINDINGS.md) |

The paired 100-million pilot returned the same two 4-billion finalists. Their mode-specific experimental R values are:

| Candidate | Goti R | Jhor R |
| --- | ---: | ---: |
| shared-76c9b9dbfc689d0b | 0.761312 | 0.441365 |
| shared-7083b1ebfa5aa3a7 | 0.785849 | 0.438747 |

R is comparable only within the same mode. The current experimental limits are +0.75% effort and +7.5% within-word movement on the declared training mix. Cross-space distance is separate; individual sources/fingerings can exceed the cap percentages. No shared candidate replaces the published layouts or establishes measured comfort/learning gains.

## Integrity and storage

`storage-manifest.json` records compressed-file hashes, exact logical-byte hashes, seed-bundle counts and indexes, and retained-file hashes. Each ZIP contains `_members.json` with SHA-256 and byte length for every raw seed record. ZIP timestamps/permissions and gzip headers are deterministic. JSON bytes, Unicode and line endings are preserved exactly.

Historical scientific manifests keep their original logical JSON paths and original SHA-256 values. Their records are **not rewritten** to pretend that compressed containers are the old files. The storage-aware verifier resolves the exact original bytes from ZIP/gzip before checking those hashes. The existing experimental JSON reader already supports the large pool's gzip fallback. Plain final layouts, results and CSVs need no archive reader.

Existing working-file edits are limited to `.gitignore` and `.gitattributes`, to exclude local raw copies and preserve archive and historically pinned checkout bytes. Three legacy JSON inputs with mixed line endings are re-staged under byte-preserving attributes; their working bytes and parsed values are unchanged. `checkout-byte-pins.json` records all checkout-only newline corrections. Exact pre-cleanup copies of these two bookkeeping files are retained in `bookkeeping-before.zip`. Historical protected-file references to those revisions are checked against their snapshots; the updated current versions have separate hashes. This distinguishes historical context from intentional Git-storage changes rather than suppressing a mismatch.

## Verify from a fresh checkout

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bangla_dh.experimental.shared_storage verify
```

This verifies container/member bytes and retained evidence, then follows the original input/output/protected references across the shared experiment manifests. It works without the ignored raw seed directories or the uncompressed large pool. Scientific source/model bytes are checked against their original hashes.

For direct access without restoring 20,000 files:

```python
from bangla_dh.experimental.shared_storage import StoredArtifacts

with StoredArtifacts() as evidence:
    pool = evidence.read_json(
        "results/shared-layout-relaxed-v1/run-4b-v1/training-pool.json"
    )
    seed = evidence.read_json(
        "results/shared-layout-relaxed-v1/run-4b-v1/runs/effort-2026103082.json"
    )
```

## Restore ignored raw evidence when needed

Old analysis scripts that directly enumerate seed files can use materialized raw copies. To restore one run:

```powershell
python -m bangla_dh.experimental.shared_storage restore --run results/shared-layout-relaxed-v1/run-4b-v1
```

The command restores only missing files, verifies exact bytes and refuses to overwrite any changed local file. It never restores old `.gitignore`/`.gitattributes` snapshots into the checkout. Restored files remain ignored by Git. Old scripts with byte-strict historical working-tree checks may flag the intentional bookkeeping edits; use the storage-aware verifier for those archival checks. Source manifests still describe the environment in which each original experiment ran.

New analyses can use the plain candidate maps and score tables directly. Use a new result directory and a new manifest for any additional candidate analysis; keep the completed runs and their archived evidence unchanged.
