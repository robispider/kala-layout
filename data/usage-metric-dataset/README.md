# Kala usage-metric research dataset

This directory receives complete typing-study session packages from the
`kala-usage-metric` receiver on Ubuntu. The optional publisher runs immediately
after local receipt, with retries during outages. Historical sessions are
backfilled when publication is first enabled. The live `manifest.json` is created
and maintained by that publisher; an absent manifest means publication has not
initialized this directory. The manifest, rather than this README, records the
currently published sessions.

## Files and contents

* `sessions/<contributor_id>/<session_id>.json.gz`: the **unchanged original gzip
  upload**, using session schema `kala.typing-check.session/1` or `/2`. Packages retain
  predefined prompt text, final text, text edits, physical key events, timing,
  pseudonymous contributor/session IDs, layout and mapping information, protocol
  and text-bank versions, summary values, completion and quality flags.
* `manifest.json`: index schema `kala.usage-metric.dataset/1` (legacy-only) or `/2`
  (per-entry `session_schema` and a top-level `session_schemas` array), identifying every
  currently published package by path, contributor/session IDs, byte count,
  SHA-256 of the original compressed bytes and Git blob SHA. See `schema.json`.
* `schema.json`: JSON Schema for the public manifest. Session admission semantics
  remain in the receiver's `PackageValidator`, not this index schema.

The publisher never copies server owner files, proof hashes, deletion secrets,
server receipts or credentials. No information inside an accepted session package
is removed, normalized, recompressed or recalculated. Existing quality flags are
preserved; an accepted upload is not a finding that its scores are valid research.

## Read and verify before analysis

Clone the current branch and use Python's standard library from the repository
root. This verifies package checksums and preserves all original fields:

```python
import gzip
import hashlib
import json
from pathlib import Path

root = Path("data/usage-metric-dataset").resolve()
index = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
assert index["schema"] in {"kala.usage-metric.dataset/1", "kala.usage-metric.dataset/2"}
for entry in index["sessions"]:
    path = (root / entry["path"]).resolve()
    assert path.is_relative_to(root / "sessions")
    raw = path.read_bytes()
    assert len(raw) == entry["size_bytes"]
    assert hashlib.sha256(raw).hexdigest() == entry["package_sha256"]
    package = json.loads(gzip.decompress(raw))
    expected_schema = entry["session_schema"] if index["schema"].endswith("/2") else index["session_schema"]
    assert package["schema"] == expected_schema
    assert package["session"]["session_id"] == entry["session_id"]
    assert package["session"]["contributor_id"] == entry["contributor_id"]
    # Analyze package here, keeping protocol, bank, mapping and quality flags.
```

Take a consistent checkout at a recorded commit for an analysis run. Treat schema,
protocol, bank version, input family, mapping hash, session ordering, keyboard and
quality/completion information as research variables. Do not silently combine
incompatible protocols or equate client summary values with independently verified
measurements. This directory makes no fixed-versus-phonetic comparison and adds no
new performance claim.

The /2 format additionally preserves task provenance, runtime input snapshots,
engine/delivery observations and physical-key probes, including incomplete attempts.
The received-data audit handles both manifest formats and lists /2 findings in
`collection_sessions`. These provisional records stay outside /1 measurement tables
and model extraction; structural acceptance does not validate engine semantics.
Publish the matching reader/schema changes before enabling /2 collection on the
receiver so the dataset workflow can read the first mixed manifest.

## Repeatable received-data audit

From the repository root, run `PYTHONPATH=src python -m bangla_dh audit-usage-data`.
In PowerShell set `$env:PYTHONPATH = "src"` first, then run
`python -m bangla_dh audit-usage-data`. It reads original packages without changing
them and writes checks, prompt metadata, candidate timing tables and hashes under
`results/usage-metric-audit-v1/`. `--out work/usage-audit` keeps a later run separate
from the initial investigation. Invalid measurements or transport corruption
return a nonzero exit status; review warnings are retained separately. A passing
audit is not recruitment approval or a fitted model.

The [initial findings](../../results/usage-metric-audit-v1/FINDINGS.md) distinguish
received-file evidence from live collection checks. The
[recruitment and modeling plan](../../results/usage-metric-audit-v1/MODELING_PLAN.md)
sets the remaining gates. A dedicated GitHub workflow runs this audit on dataset
changes, including data-only pushes skipped by the main research CI. The portable
command verifies scalar WPM and event-derived counts; its report explicitly marks
grapheme-dependent scores as unverified. A separate, snapshot-specific score
cross-check is recorded with the initial findings.

## Withdrawal and copies

A contributor's existing withdrawal request deletes local sessions and triggers
removal of all their files and index entries from the **current dataset on the
configured branch**. GitHub removal is asynchronous. Offline jobs retry after
recovery, and permanent local deletion markers prevent later republication.

Earlier Git commits, prepared/unreferenced Git objects, GitHub caches, forks and
downloaded copies may retain the packages. This limitation applies even when
nobody downloaded them. Normal synchronization does not rewrite Git history.
Analysts should refresh current data and apply withdrawals before subsequent use;
record a corrected analysis version when its underlying dataset changes.

## Relationship to the published layout research

The owner authorized a narrow exception to the no-texts-in-Git rule on
26 October 2026 for these complete predefined-prompt study packages. The Wikipedia,
newspaper and BARD search corpora remain excluded from Git. Study packages do not
change the frozen model, layout search inputs, reproduction locks or scores. Any
future use to change the published layouts follows the research-season rules.
Prompt attribution and source terms are not replaced by the repository's code
licence. Package fields are kept as supplied; this directory assigns no new
licence to literary works.

Publisher implementation, installation and client compatibility:
[kala-usage-metric GitHub dataset guide](https://github.com/robispider/kala-usage-metric/blob/main/docs/GITHUB_DATASET.md).
