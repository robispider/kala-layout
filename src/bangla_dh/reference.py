"""Pinned reference inputs: the original analyzer source and the published
Colemak Mod-DH resources, identified by commit and SHA-256.

* The analyzer repository has no license file, so its source is not copied
  into this project; ``fetch_upstream`` clones it at the pinned commit into
  ``reference/upstream`` (ignored by Git) and verifies every pinned file.
* The analyzer resources (layouts, configs, frequency tables) are vendored
  from the CC0 ``colemakmods/mod-dh`` site branch, where they are
  byte-identical to the analyzer repository's copies.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REFERENCE = PROJECT_ROOT / "reference"
LOCK_FILE = REFERENCE / "sources.lock.json"
RESOURCES = REFERENCE / "colemak-dh-resources"
PUBLISHED = REFERENCE / "published" / "colemak_dh_published.json"
UPSTREAM = REFERENCE / "upstream"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def hash_tree(root: Path, patterns: tuple[str, ...] = ("**/*",)) -> dict[str, str]:
    files = sorted({p for pattern in patterns for p in root.glob(pattern) if p.is_file() and ".git" not in p.parts})
    return {p.relative_to(root).as_posix(): sha256_file(p) for p in files}


def load_lock() -> dict:
    return json.loads(LOCK_FILE.read_text(encoding="utf-8"))


def load_published() -> dict:
    return json.loads(PUBLISHED.read_text(encoding="utf-8"))


def resource(relative: str) -> Path:
    return RESOURCES / relative


def _diff(expected: dict[str, str], actual: dict[str, str]) -> list[str]:
    problems = [f"missing: {name}" for name in expected if name not in actual]
    problems += [f"hash mismatch: {name}" for name in expected if name in actual and actual[name] != expected[name]]
    problems += [f"unpinned file: {name}" for name in actual if name not in expected]
    return problems


def verify_vendored() -> list[str]:
    """Problems with the vendored resources (empty when they match the lock)."""
    return _diff(load_lock()["vendored_resources"]["files"], hash_tree(RESOURCES))


def verify_upstream(path: Path = UPSTREAM) -> list[str]:
    lock = load_lock()["analyzer"]
    if not path.exists():
        return [f"not fetched: {path} (run: bangla-dh fetch-upstream)"]
    actual = {name: sha256_file(path / name) for name in lock["files"] if (path / name).is_file()}
    head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    problems = [] if head == lock["commit"] else [f"checked-out commit {head or '?'} != pinned {lock['commit']}"]
    return problems + [p for p in _diff(lock["files"], actual) if not p.startswith("unpinned")]


def fetch_upstream(path: Path = UPSTREAM) -> list[str]:
    lock = load_lock()["analyzer"]
    if not path.exists():
        subprocess.run(["git", "clone", "--quiet", lock["repository"], str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "fetch", "--quiet", "origin", lock["commit"]], check=False)
    subprocess.run(["git", "-C", str(path), "checkout", "--quiet", lock["commit"]], check=True)
    return verify_upstream(path)


def build_lock(upstream_checkout: Path, site_checkout: Path, site_commit: str) -> dict:
    """Maintainer helper: pin a reviewed analyzer checkout and the vendored resources."""
    head = subprocess.run(["git", "-C", str(upstream_checkout), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    upstream_files = hash_tree(upstream_checkout, ("analyzer/src/**/*", "analyzer/resources/**/*", "analyzer/*.sh",
                                                   "analyzer/*.bat", "analyzer/build.gradle", "README.md", "data/README.md"))
    site_resources = hash_tree(site_checkout / "webapp" / "resources")
    vendored = hash_tree(RESOURCES)
    identical = sorted(name for name, digest in vendored.items()
                       if upstream_files.get("analyzer/resources/" + name) == digest)
    return {
        "description": "Pinned Phase 1 reference inputs. Verify with: bangla-dh verify-reference",
        "analyzer": {
            "repository": "https://github.com/stevep99/keyboard-layout-analysis-tool",
            "commit": head,
            "license": "none declared (source is fetched, not vendored)",
            "files": upstream_files,
        },
        "site": {
            "repository": "https://github.com/colemakmods/mod-dh",
            "branch": "gh-pages",
            "commit": site_commit,
            "license": "CC0 1.0",
            "pages": ["compare.html", "learn.html", "model.html", "analyze.html"],
        },
        "vendored_resources": {
            "source": "mod-dh gh-pages webapp/resources",
            "path": "reference/colemak-dh-resources",
            "files": vendored,
            "matches_site": vendored == site_resources,
            "identical_in_analyzer_repository": identical,
        },
    }
