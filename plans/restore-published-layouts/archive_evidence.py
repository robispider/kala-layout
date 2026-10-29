"""Additive byte-preserving archive of the completed Goti run; no search."""
import gzip
import hashlib
import json
from pathlib import Path
from bangla_dh.paths import PROJECT_ROOT, output_path, write_json, write_text

source = PROJECT_ROOT / 'work/goti-j1-8b-v1'
target = PROJECT_ROOT / 'results/goti-j1-8b-v1'
entries = {}
files = list(source.rglob('*')) + [PROJECT_ROOT / 'work/goti-j1-8b-v1-performance-adjustment.json']
for file in files:
    if not file.is_file():
        continue
    relative = file.relative_to(source).as_posix() if file.is_relative_to(source) else file.name
    destination = target / relative
    raw = file.read_bytes()
    if relative == 'search/A.json':
        destination = destination.with_suffix('.json.gz')
        packed = gzip.compress(raw, mtime=0)
        assert gzip.decompress(packed) == raw
    else:
        packed = raw
    output_path(destination).write_bytes(packed)
    entries[file.relative_to(PROJECT_ROOT).as_posix()] = {
        'archive': destination.relative_to(PROJECT_ROOT).as_posix(),
        'sha256': hashlib.sha256(packed).hexdigest(),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'encoding': 'gzip' if packed != raw else 'identity',
    }
write_json(target / 'run-manifest.json', {'kind': 'Publication archive, original manifest retained as source-run-manifest.json',
    'date': '2026-10-29', 'files': entries})
# The source manifest is immutable; the publication manifest above owns relocation.
original = source / 'run-manifest.json'
output_path(target / 'source-run-manifest.json').write_bytes(original.read_bytes())
entries[original.relative_to(PROJECT_ROOT).as_posix()]['archive'] = 'results/goti-j1-8b-v1/source-run-manifest.json'
write_json(target / 'run-manifest.json', {'kind': 'Publication archive; no source manifests rewritten',
    'date': '2026-10-29', 'files': entries})
write_text(target / 'README.md', '''# Durable Goti J1 evidence

The source search and report manifests are retained byte for byte. Paths in them
name the original `work/` locations; `run-manifest.json` maps those paths to this
archive and records both compressed and decompressed SHA-256 hashes. No corpus
texts are included. `REPORT.md` is the original report; its `search/A.json` link
refers to the lossless `search/A.json.gz` archive here. The complete 8,000 seeded
records, all 241 endpoints, confirmation records, settings and maps are retained.

From the repository root: `PYTHONPATH=src python -m bangla_dh.goti_evidence`.
Verification reads only this archive and tracked frozen inputs, independently
rescores every retained endpoint with exact integer coefficients, and checks the
52 published assignments. It runs no search and certifies no optimum.
To inspect the original JSON use Python's standard-library `gzip.open`.
Search replay uses the command in `REPORT.md` at its recorded source revision
`010ee328d92f8a0f066b89dadfeb89090b0ab877` in a separate checkout.
''')
