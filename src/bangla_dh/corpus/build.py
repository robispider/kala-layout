"""Corpus construction (Phase 2, task 3): ``bangla-dh build-corpus``.

The Wikipedia text is the prepared corpus published in the public
``ban-dataset-collection`` (``fetch-data`` + ``prepare-data``): Kala's
``bnwiki-prose-v1`` cleaning, ``bangla-dh-text-v1`` normalization, exact
paragraph deduplication and a 90/10 document-level train/held-out split
(``corpus/wikitext.py`` documents the cleaning rules). ``build`` checks the
assembled files against ``data/datasets.lock.json``, rewrites them as one
deterministic gzip JSON-lines file per domain and split under
``data/corpus/<version>/`` (ignored by Git) and records counts and hashes in
the Phase 2 corpus manifest.

Document record: ``{"id": ..., "title": ..., "paragraphs": [...]}``.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .. import datasets
from ..bangla.normalize import describe as describe_normalization
from ..paths import DATA, PROJECT_ROOT, gzip_text_lines, gzip_text_writer, output_path, relative_to_project
from ..reference import sha256_file
from . import wikitext

CORPUS_CONFIG = DATA / "corpus-v1.json"


def load_config(path: Path = CORPUS_CONFIG) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def split_of(document_id: str, split: dict) -> str:
    digest = hashlib.sha256(f"{split['salt']}:{document_id}".encode("utf-8")).hexdigest()
    return "heldout" if int(digest[:8], 16) % 100 < split["heldout_percent"] else "train"


# --- driver -----------------------------------------------------------------

class _Writer:
    """Deduplicating writer of one domain's split files."""

    def __init__(self, directory: Path, domain: str, splits: list[str], seen: set[bytes]):
        self.paths = {s: output_path(directory / f"{domain}-{s}.jsonl.gz") for s in splits}
        self._contexts = {s: gzip_text_writer(p) for s, p in self.paths.items()}
        self.streams = {s: c.__enter__() for s, c in self._contexts.items()}
        self.seen = seen
        self.counts = {s: {"documents": 0, "paragraphs": 0, "characters": 0} for s in splits}
        self.duplicates = 0
        self.empty_documents = 0

    def add(self, split: str, document_id: str, title: str | None, paragraphs: list[str]) -> None:
        kept = []
        for paragraph in paragraphs:
            digest = hashlib.blake2b(paragraph.encode("utf-8"), digest_size=16).digest()
            if digest in self.seen:
                self.duplicates += 1
                continue
            self.seen.add(digest)
            kept.append(paragraph)
        if not kept:
            self.empty_documents += 1
            return
        record = {"id": document_id, "title": title, "paragraphs": kept}
        self.streams[split].write(json.dumps(record, ensure_ascii=False) + "\n")
        c = self.counts[split]
        c["documents"] += 1
        c["paragraphs"] += len(kept)
        c["characters"] += sum(len(p) for p in kept)

    def close(self) -> None:
        for context in self._contexts.values():
            context.__exit__(None, None, None)


def _copy_split(source: Path, target: Path) -> dict:
    """Rewrite one prepared JSON-lines file deterministically, counting what it holds."""
    counts = {"documents": 0, "paragraphs": 0, "characters": 0}
    with gzip_text_writer(target) as out:
        for line in gzip_text_lines(source):
            if not line.strip():
                continue
            record = json.loads(line)
            counts["documents"] += 1
            counts["paragraphs"] += len(record["paragraphs"])
            counts["characters"] += sum(len(p) for p in record["paragraphs"])
            out.write(line + "\n")
    return counts


def build(config: dict, log=print) -> dict:
    directory = PROJECT_ROOT / config["output_directory"]
    lock = datasets.load_lock()
    domains = {}
    for domain in config["domains"]:
        if domain["kind"] != "prepared-jsonl":
            raise ValueError(f"unknown corpus kind {domain['kind']}")
        started = time.time()
        sources = {split: datasets.assembled_files()[name] for split, name in domain["assembled"].items()}
        for split, source in sources.items():
            name = domain["assembled"][split]
            if not source.is_file():
                raise FileNotFoundError(f"{source} is missing: run `bangla-dh fetch-data` and `bangla-dh prepare-data`")
            expected = lock["assembled"][name]["content_sha256"]
            if datasets.content_sha256(source) != expected:
                raise ValueError(f"{name} differs from data/datasets.lock.json")
        splits = {}
        for split, source in sources.items():
            target = output_path(directory / f"{domain['name']}-{split}.jsonl.gz")
            counts = _copy_split(source, target)
            splits[split] = {**counts, "path": relative_to_project(target), "sha256": sha256_file(target),
                             "content_sha256": datasets.content_sha256(target)}
        chunks = lock["packages"][domain["package"]]["files"]
        domains[domain["name"]] = {
            "label": domain["label"],
            "source": {"path": f"ban-dataset-collection/{lock['packages'][domain['package']]['folder']}",
                       "repository": lock["source"], "commit": lock["commit"], "parts": len(chunks),
                       "bytes": sum(c["bytes"] for c in chunks),
                       "sha256": hashlib.sha256("".join(c["sha256"] for c in chunks).encode()).hexdigest(),
                       "assembled_content_sha256": {domain["assembled"][s]: lock["assembled"][domain["assembled"][s]]["content_sha256"]
                                                    for s in sources}},
            "source_counts": {"documents": sum(s["documents"] for s in splits.values())},
            "paragraph_filter": {}, "duplicate_paragraphs_removed": 0, "documents_without_new_paragraphs": 0,
            "splits": splits, "seconds": round(time.time() - started, 1)}
        log(f"{domain['name']}: {json.dumps({s: v['documents'] for s, v in splits.items()})} documents")
    return {"version": config["version"], "config": relative_to_project(CORPUS_CONFIG),
            "config_sha256": sha256_file(CORPUS_CONFIG), "normalization": describe_normalization(),
            "cleaning": wikitext.describe(), "split": config["split"], "deduplication": config["deduplication"],
            "domains": domains}
