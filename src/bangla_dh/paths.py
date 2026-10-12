"""Project paths and the write guard.

Everything the pipeline reads or writes lives inside this repository: frozen
inputs in ``data/`` (Kala's small Bangla inputs are vendored under
``data/kala/``, the large public datasets are downloaded into ``data/`` and
ignored by Git), phase outputs in ``results/``. Writers call ``output_path``
so that a wrong path fails loudly instead of writing elsewhere.
"""
from __future__ import annotations

import contextlib
import gzip
import io
import json
from pathlib import Path

from .reference import PROJECT_ROOT, sha256_file

DATA = PROJECT_ROOT / "data"
KALA_INPUTS = DATA / "kala"  # small Bangla inputs taken from the Kala application, pinned by SHA-256
CORPUS_DATA = DATA / "corpus"  # large generated corpora and token tables, ignored by Git
RESULTS_ROOT = PROJECT_ROOT / "results"


class WriteOutsideProject(PermissionError):
    pass


def output_path(path: str | Path) -> Path:
    """Resolve ``path`` for writing; refuse anything outside this project."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT.resolve()):
        raise WriteOutsideProject(f"refusing to write outside {PROJECT_ROOT}: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def kala_path(relative: str) -> Path:
    """A vendored Kala input (``data/kala/<path in the Kala repository>``), for reading only."""
    return KALA_INPUTS / relative


def repo_state() -> tuple[str, bool]:
    """(commit, working tree clean) of this repository, for run manifests."""
    import subprocess

    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", "-C", str(PROJECT_ROOT), *args], capture_output=True, text=True,
                                  check=False).stdout
        except OSError:
            return ""

    return git("rev-parse", "HEAD").strip(), not git("status", "--porcelain")


def write_json(path: str | Path, data, *, indent: int | None = 2) -> Path:
    target = output_path(path)
    target.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return target


def write_text(path: str | Path, text: str) -> Path:
    target = output_path(path)
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


@contextlib.contextmanager
def gzip_text_writer(path: str | Path):
    """Write UTF-8 text to a gzip file whose bytes depend only on the text."""
    with open(output_path(path), "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz:
            with io.TextIOWrapper(gz, encoding="utf-8", newline="\n") as text:
                yield text


def gzip_text_lines(path: str | Path):
    with gzip.open(path, "rt", encoding="utf-8", newline="\n") as stream:
        for line in stream:
            yield line.rstrip("\n")


def relative_to_project(path: Path) -> str:
    return Path(path).resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def hash_outputs(paths: list[Path]) -> dict[str, str]:
    return {relative_to_project(p): sha256_file(p) for p in sorted(paths)}
