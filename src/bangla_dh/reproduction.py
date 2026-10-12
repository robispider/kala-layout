"""Did a rebuild reproduce the published results?

``results/reproduction.lock.json`` records, for the artefacts that carry the
science (frequency and keystroke tables, search results, the Kala layout files and
the challenge data), a SHA-256 of their canonical JSON. ``check-results`` recomputes
those hashes from the files on disk, so after you rebuild (or run the search with
``--reproduce``) it says which artefacts equal the published ones.

Canonical JSON: keys sorted, and fields that only describe the run or the gzip
packaging (timings, ``*_sha256`` of compressed files) removed, because they differ
between computers without changing any result.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .paths import PROJECT_ROOT, RESULTS_ROOT, write_json

LOCK = RESULTS_ROOT / "reproduction.lock.json"
VOLATILE = {"seconds", "seconds_total", "cpuHours", "generated_utc", "corpus_sha256", "token_table_sha256", "sha256"}
GROUPS = {
    "phase2 frequency tables": ["results/phase2/frequencies/bnwiki-train.json", "results/phase2/frequencies/bnwiki-heldout.json",
                                "results/phase2/frequencies/optimization-frequencies.json"],
    "phase3 keystroke tables": ["results/phase3/frequencies/*.json"],
    "news frequency and keystroke tables": ["results/phase3-crosscheck/frequencies/*.json"],
    "phase3 search": ["results/phase3/search/*.json"],
    "news search": ["results/phase3-crosscheck/search/*.json"],
    "mixed search (Kala Goti, Kala Jhor)": ["results/mix-search/search/*.json"],
    "Kala layout files": ["results/kala-keyboards/kala-goti.json", "results/kala-keyboards/kala-jhor.json"],
    "challenge data": ["challenge/challenge-data.json"],
}


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def canonical_sha256(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    text = json.dumps(_strip(data), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _files(patterns: list[str]) -> list[Path]:
    return sorted({p for pattern in patterns for p in PROJECT_ROOT.glob(pattern)})


def lock_results() -> Path:
    groups = {name: {p.relative_to(PROJECT_ROOT).as_posix(): canonical_sha256(p) for p in _files(patterns)}
              for name, patterns in GROUPS.items()}
    return write_json(LOCK, {"note": "SHA-256 of the canonical JSON of the artefacts that carry the results; "
                                     "check with `python -m bangla_dh check-results`.", "groups": groups})


def check_results(groups: list[str] | None = None, log=print) -> bool:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))["groups"]
    ok = True
    for name, files in lock.items():
        if groups and not any(g.lower() in name.lower() for g in groups):
            continue
        same = differ = missing = 0
        for relative, expected in files.items():
            path = PROJECT_ROOT / relative
            if not path.is_file():
                missing += 1
                log(f"  missing  {relative}")
            elif canonical_sha256(path) == expected:
                same += 1
            else:
                differ += 1
                log(f"  DIFFERS  {relative}")
        log(f"{'PASS' if not (differ or missing) else 'FAIL'}  {name}: {same} identical, {differ} differ, {missing} missing")
        ok &= not (differ or missing)
    return ok
