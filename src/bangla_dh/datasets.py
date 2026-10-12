"""The public text datasets: fetch, verify and assemble ``ban-dataset-collection``.

The corpora behind the layout search are published as hash-listed ZIP chunks in
https://github.com/robispider/ban-dataset-collection (Bangla Wikipedia,
a Bangla newspaper collection, and BARD news articles). ``data/datasets.lock.json``
pins the repository commit, the SHA-256 of every ZIP chunk and the SHA-256 of
the assembled files, so a rebuild on another computer can be checked byte for
byte.

Commands (see ``cli.py``):

``fetch-data``    download the ZIP chunks into ``data/ban-dataset-collection/downloads``
                  (or copy them from a local checkout with ``--from``), verifying
                  every SHA-256;
``prepare-data``  assemble the chunks into ``data/ban-dataset-collection/assembled``
                  (the layout of the collection's own ``materialize_datasets.py``)
                  and check the assembled content against the lock;
``verify-data``   re-check downloads and assembled files without changing anything;
``lock-datasets`` maintainer command that writes the lock from a checkout.

Everything under ``data/ban-dataset-collection`` is ignored by Git.
"""
from __future__ import annotations

import concurrent.futures
import gzip
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

from .paths import DATA, PROJECT_ROOT, output_path

LOCK_FILE = DATA / "datasets.lock.json"
ROOT = DATA / "ban-dataset-collection"
DOWNLOADS = ROOT / "downloads"
ASSEMBLED = ROOT / "assembled"
REPOSITORY = "robispider/ban-dataset-collection"

# package → (folder in the collection, what the research uses it for)
PACKAGES = {
    "wikipedia": "wikidata",
    "newspaper": "bangla-newspaper",
    "bard": "bard",
}
WIKIPEDIA_SPLITS = ("train", "heldout")
BARD_CATEGORIES = ("economy", "entertainment", "international", "sports", "state")


class DatasetError(RuntimeError):
    pass


def load_lock() -> dict:
    return json.loads(LOCK_FILE.read_text(encoding="utf-8"))


def raw_url(lock: dict, folder: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{REPOSITORY}/{lock['commit']}/{folder}/{path}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_sha256(path: Path) -> str:
    """SHA-256 of the file's bytes, or of its decompressed bytes for ``.gz``.

    Compressed bytes depend on the zlib build, so assembled ``.gz`` files are
    pinned by what they contain."""
    opener = gzip.open if path.suffix == ".gz" else open
    h = hashlib.sha256()
    with opener(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _packages(selected) -> list[str]:
    names = list(PACKAGES) if not selected or "all" in selected else list(selected)
    unknown = [n for n in names if n not in PACKAGES]
    if unknown:
        raise DatasetError(f"unknown package {unknown}; choose from {', '.join(PACKAGES)} or all")
    return names


def chunk_path(package: str, entry: dict) -> Path:
    return DOWNLOADS / PACKAGES[package] / entry["path"]


# --- fetch ------------------------------------------------------------------------

def _download(url: str, target: Path, expected: dict, attempts: int = 4) -> None:
    partial = target.with_name(target.name + ".part")
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            h = hashlib.sha256()
            size = 0
            request = urllib.request.Request(url, headers={"User-Agent": "kala-layout-fetch"})
            with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as out:
                for block in iter(lambda: response.read(1 << 20), b""):
                    out.write(block)
                    h.update(block)
                    size += len(block)
            if size != expected["bytes"] or h.hexdigest() != expected["sha256"]:
                raise DatasetError(f"{target.name}: downloaded {size} bytes with SHA-256 {h.hexdigest()[:16]}…, "
                                   f"expected {expected['bytes']} bytes and {expected['sha256'][:16]}…")
            partial.replace(target)
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError, DatasetError) as error:
            last = error
            partial.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise DatasetError(f"{url}: {last}")


def _copy(source: Path, target: Path, expected: dict) -> None:
    partial = target.with_name(target.name + ".part")
    shutil.copyfile(source, partial)
    if partial.stat().st_size != expected["bytes"] or sha256_file(partial) != expected["sha256"]:
        partial.unlink(missing_ok=True)
        raise DatasetError(f"{source}: size or SHA-256 differs from the lock")
    partial.replace(target)


def _is_good(path: Path, expected: dict) -> bool:
    return path.is_file() and path.stat().st_size == expected["bytes"] and sha256_file(path) == expected["sha256"]


def fetch(packages=None, workers: int = 4, mirror: str | Path | None = None, log=print) -> list[Path]:
    """Download (or copy from ``mirror``, a local checkout of the collection)
    every ZIP chunk of the packages; chunks already present and correct are kept."""
    lock = load_lock()
    jobs = []
    for package in _packages(packages):
        folder = PACKAGES[package]
        for entry in lock["packages"][package]["files"]:
            target = output_path(chunk_path(package, entry))
            jobs.append((package, folder, entry, target))
    done: list[Path] = []

    def work(job):
        package, folder, entry, target = job
        if _is_good(target, entry):
            return target, "kept"
        if mirror:
            _copy(Path(mirror) / folder / entry["path"], target, entry)
            return target, "copied"
        _download(raw_url(lock, folder, entry["path"]), target, entry)
        return target, "downloaded"

    total_bytes = sum(j[2]["bytes"] for j in jobs)
    log(f"{len(jobs)} chunks, {total_bytes / 1e6:,.0f} MB from commit {lock['commit'][:12]} of {REPOSITORY}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for n, (target, how) in enumerate(pool.map(work, jobs), 1):
            done.append(target)
            if how != "kept" or n % 10 == 0 or n == len(jobs):
                log(f"  {n}/{len(jobs)} {target.relative_to(DOWNLOADS).as_posix()} ({how})")
    return done


# --- assemble ------------------------------------------------------------------------

def _safe_member(name: str) -> str:
    member = PurePosixPath(name)
    if (member.is_absolute() or PureWindowsPath(name).drive or "\\" in name or not member.parts
            or any(part in ("", ".", "..") for part in member.parts)):
        raise DatasetError(f"unsafe path in ZIP archive: {name!r}")
    return name


def _members(archive_path: Path, suffixes=(".jsonl", ".gz")) -> list[str]:
    with zipfile.ZipFile(archive_path) as archive:
        return [_safe_member(i.filename) for i in archive.infolist()
                if not i.is_dir() and Path(i.filename).suffix in suffixes]


def _append_zip(archive_path: Path, out) -> int:
    """Append the single JSONL member of a chunk to ``out``; returns its non-empty lines."""
    names = [n for n in _members(archive_path) if n.endswith(".jsonl")]
    if len(names) != 1:
        raise DatasetError(f"{archive_path.name}: expected one .jsonl member, found {names}")
    lines = 0
    with zipfile.ZipFile(archive_path) as archive, archive.open(names[0]) as source:
        last = b""
        for block in iter(lambda: source.read(1 << 20), b""):
            out.write(block)
            lines += block.count(b"\n")
            last = block
        if last and not last.endswith(b"\n"):
            raise DatasetError(f"{archive_path.name}: last line has no newline")
    return lines


class _Gzip:
    """Gzip writer whose bytes depend only on the content (no name, mtime 0)."""

    def __init__(self, path: Path):
        self.path = path
        self.partial = path.with_name(path.name + ".part")

    def __enter__(self):
        self.raw = self.partial.open("wb")
        self.gz = gzip.GzipFile(fileobj=self.raw, mode="wb", compresslevel=6, mtime=0, filename="")
        return self.gz

    def __exit__(self, kind, value, trace):
        self.gz.close()
        self.raw.close()
        if kind is None:
            self.partial.replace(self.path)
        else:
            self.partial.unlink(missing_ok=True)


def _assemble_jsonl(archives: list[Path], target: Path, compressed: bool) -> int:
    target = output_path(target)
    if compressed:
        with _Gzip(target) as out:
            return sum(_append_zip(a, out) for a in archives)
    partial = target.with_name(target.name + ".part")
    try:
        with partial.open("wb") as out:
            records = sum(_append_zip(a, out) for a in archives)
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)
    return records


def _chunks(lock: dict, package: str, prefix: str = "", exclude: str = "") -> list[Path]:
    files = [e for e in lock["packages"][package]["files"] if e["path"].startswith(prefix) and e["path"].endswith(".zip")
             and not (exclude and exclude in e["path"])]
    paths = [chunk_path(package, e) for e in sorted(files, key=lambda e: e["path"])]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        raise DatasetError(f"missing chunk {missing[0]}; run `fetch-data` first")
    return paths


def assembled_files(lock: dict | None = None) -> dict[str, Path]:
    """Name → path of every assembled file the research reads."""
    names = {f"wikidata/{s}.jsonl.gz": ASSEMBLED / "wikidata" / f"{s}.jsonl.gz" for s in WIKIPEDIA_SPLITS}
    names.update({f"wikidata/bnwiki-{s}.tokens.tsv.gz": ASSEMBLED / "wikidata" / f"bnwiki-{s}.tokens.tsv.gz"
                  for s in WIKIPEDIA_SPLITS})
    names["bangla-newspaper.jsonl"] = ASSEMBLED / "bangla-newspaper.jsonl"
    names.update({f"bard/{c}.jsonl.gz": ASSEMBLED / "bard" / f"{c}.jsonl.gz" for c in BARD_CATEGORIES})
    return names


def assemble(packages=None, log=print) -> dict[str, dict]:
    """Assemble the chunks into the files the research reads and check them
    against the lock. Returns name → {"records", "content_sha256"}."""
    lock = load_lock()
    selected = _packages(packages)
    built: dict[str, dict] = {}
    names = assembled_files(lock)

    def record(name: str, records: int | None, started: float) -> None:
        digest = content_sha256(names[name])
        built[name] = {"records": records, "content_sha256": digest}
        expected = lock.get("assembled", {}).get(name)
        status = "no lock entry" if expected is None else ("matches the lock" if expected["content_sha256"] == digest
                                                           else "DIFFERS FROM THE LOCK")
        log(f"  {name}: {records if records is not None else '-'} records, {status} ({time.time() - started:.0f} s)")
        if expected is not None and expected["content_sha256"] != digest:
            raise DatasetError(f"{name}: content differs from {LOCK_FILE.name}")

    if "wikipedia" in selected:
        for split in WIKIPEDIA_SPLITS:
            started = time.time()
            archives = _chunks(lock, "wikipedia", f"bnwiki-{split}-")
            n = _assemble_jsonl(archives, names[f"wikidata/{split}.jsonl.gz"], True)
            record(f"wikidata/{split}.jsonl.gz", n, started)
            started = time.time()
            sidecar = chunk_path("wikipedia", {"path": f"bnwiki-{split}.tokens.tsv.zip"})
            with zipfile.ZipFile(sidecar) as archive:
                (member,) = [m for m in _members(sidecar) if m.endswith(".tokens.tsv.gz")]
                target = output_path(names[f"wikidata/bnwiki-{split}.tokens.tsv.gz"])
                with archive.open(member) as source, target.open("wb") as out:
                    shutil.copyfileobj(source, out, 1 << 20)
            record(f"wikidata/bnwiki-{split}.tokens.tsv.gz", None, started)
    if "newspaper" in selected:
        started = time.time()
        n = _assemble_jsonl(_chunks(lock, "newspaper", "newspaper-"), names["bangla-newspaper.jsonl"], False)
        record("bangla-newspaper.jsonl", n, started)
    if "bard" in selected:
        for category in BARD_CATEGORIES:
            started = time.time()
            n = _assemble_jsonl(_chunks(lock, "bard", f"{category}/"), names[f"bard/{category}.jsonl.gz"], True)
            record(f"bard/{category}.jsonl.gz", n, started)
    return built


def verify(packages=None, log=print) -> bool:
    """Check downloaded chunks and assembled files against the lock."""
    lock = load_lock()
    ok = True
    for package in _packages(packages):
        files = lock["packages"][package]["files"]
        present = [e for e in files if chunk_path(package, e).is_file()]
        bad = [e["path"] for e in present if not _is_good(chunk_path(package, e), e)]
        log(f"{package}: {len(present)}/{len(files)} chunks present, {len(bad)} wrong")
        ok &= not bad and len(present) == len(files)
    names = assembled_files(lock)
    wanted = {"wikipedia": [n for n in names if n.startswith("wikidata/")], "newspaper": ["bangla-newspaper.jsonl"],
              "bard": [n for n in names if n.startswith("bard/")]}
    for package in _packages(packages):
        for name in wanted[package]:
            path, expected = names[name], lock.get("assembled", {}).get(name)
            if not path.is_file():
                log(f"  {name}: not assembled")
                ok = False
            elif expected is None:
                log(f"  {name}: no lock entry")
            elif content_sha256(path) != expected["content_sha256"]:
                log(f"  {name}: DIFFERS FROM THE LOCK")
                ok = False
            else:
                log(f"  {name}: ok")
    return ok


# --- maintainer: write the lock --------------------------------------------------------

def write_lock(checkout: str | Path, commit: str, assembled: bool = False, log=print) -> Path:
    """Write ``data/datasets.lock.json`` from a local checkout of the collection
    (its per-folder ``manifest.json`` files). With ``assembled`` the content
    hashes of the files in ``data/ban-dataset-collection/assembled`` are
    recorded too; assemble from the pinned chunks first."""
    checkout = Path(checkout)
    previous = json.loads(LOCK_FILE.read_text(encoding="utf-8")) if LOCK_FILE.is_file() else {}
    lock = {"source": f"https://github.com/{REPOSITORY}", "commit": commit,
            "note": "Pinned by `python -m bangla_dh lock-datasets`; ZIP chunks are fetched from raw.githubusercontent.com "
                    "at this commit and verified by SHA-256. `assembled` holds the SHA-256 of the assembled files' "
                    "content (decompressed for .gz).",
            "packages": {}, "assembled": previous.get("assembled", {})}
    for package, folder in PACKAGES.items():
        manifest = json.loads((checkout / folder / "manifest.json").read_text(encoding="utf-8"))
        items = manifest["files"] if "files" in manifest else manifest["chunks"]
        files = []
        for item in items:
            path = checkout / folder / item["path"]
            if sha256_file(path) != item["sha256"]:
                raise DatasetError(f"{path}: SHA-256 differs from {folder}/manifest.json")
            files.append({"path": item["path"], "bytes": path.stat().st_size, "sha256": item["sha256"]})
        lock["packages"][package] = {"folder": folder, "attribution": f"{folder}/ATTRIBUTION.txt",
                                     "files": sorted(files, key=lambda f: f["path"])}
        log(f"{package}: {len(files)} chunks, {sum(f['bytes'] for f in files) / 1e6:,.0f} MB")
    if assembled:
        lock["assembled"] = {name: {"content_sha256": content_sha256(path)}
                             for name, path in assembled_files().items() if path.is_file()}
        for name, entry in lock["assembled"].items():
            log(f"  {name}: {entry['content_sha256'][:16]}…")
    LOCK_FILE.write_text(json.dumps(lock, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return LOCK_FILE


def relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
