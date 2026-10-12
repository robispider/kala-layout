"""Fetch, assemble and verify the public datasets on a tiny synthetic collection."""
import gzip
import hashlib
import io
import json
import shutil
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from bangla_dh import datasets
from bangla_dh.paths import PROJECT_ROOT

SCRATCH = PROJECT_ROOT / "work" / "test-datasets"


def _zip(path: Path, members: dict[str, bytes]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _jsonl(*ids: str) -> bytes:
    return "".join('{"id": "%s", "paragraphs": ["ক খ গ"]}\n' % i for i in ids).encode("utf-8")


def _gz(data: bytes) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0) as stream:
        stream.write(data)
    return out.getvalue()


class DatasetTests(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        self.mirror = SCRATCH / "mirror"
        wiki = self.mirror / "wikidata"
        news = self.mirror / "bangla-newspaper"
        bard = self.mirror / "bard"
        self.lock = {"source": "https://example.invalid", "commit": "0" * 40, "assembled": {}, "packages": {
            "wikipedia": {"folder": "wikidata", "files": [
                _zip(wiki / "bnwiki-train-00001.zip", {"bnwiki-train-00001.jsonl": _jsonl("a", "b")}),
                _zip(wiki / "bnwiki-train-00002.zip", {"bnwiki-train-00002.jsonl": _jsonl("c")}),
                _zip(wiki / "bnwiki-heldout-00001.zip", {"bnwiki-heldout-00001.jsonl": _jsonl("d")}),
                _zip(wiki / "bnwiki-train.tokens.tsv.zip", {"bnwiki-train.tokens.tsv.gz": _gz(b"t\t1\n")}),
                _zip(wiki / "bnwiki-heldout.tokens.tsv.zip", {"bnwiki-heldout.tokens.tsv.gz": _gz(b"h\t1\n")})]},
            "newspaper": {"folder": "bangla-newspaper", "files": [
                _zip(news / "newspaper-00001.zip", {"newspaper-00001.jsonl": _jsonl("n1")}),
                _zip(news / "newspaper-00002.zip", {"newspaper-00002.jsonl": _jsonl("n2", "n3")})]},
            "bard": {"folder": "bard", "files": []}}}
        for category in datasets.BARD_CATEGORIES:
            entry = _zip(bard / category / f"{category}-00001.zip", {f"{category}-00001.jsonl": _jsonl(category)})
            entry["path"] = f"{category}/{category}-00001.zip"
            self.lock["packages"]["bard"]["files"].append(entry)
        patches = [mock.patch.object(datasets, "load_lock", lambda: self.lock),
                   mock.patch.object(datasets, "DOWNLOADS", SCRATCH / "downloads"),
                   mock.patch.object(datasets, "ASSEMBLED", SCRATCH / "assembled")]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, SCRATCH, True)
        self.log = lambda *_: None

    def test_fetch_from_a_mirror_assemble_and_verify(self):
        datasets.fetch(mirror=self.mirror, log=self.log)
        built = datasets.assemble(log=self.log)
        self.assertEqual(built["wikidata/train.jsonl.gz"]["records"], 3)
        self.assertEqual(built["wikidata/heldout.jsonl.gz"]["records"], 1)
        self.assertEqual(built["bangla-newspaper.jsonl"]["records"], 3)
        with gzip.open(datasets.ASSEMBLED / "wikidata" / "train.jsonl.gz", "rt", encoding="utf-8") as stream:
            self.assertEqual([line.split('"')[3] for line in stream], ["a", "b", "c"])
        self.lock["assembled"] = {name: {"content_sha256": info["content_sha256"]} for name, info in built.items()}
        self.assertTrue(datasets.verify(log=self.log))
        # The assembled bytes depend only on the content, so a second assembly gives the same files.
        again = datasets.assemble(log=self.log)
        self.assertEqual(built, again)

    def test_a_changed_chunk_is_refused(self):
        tampered = self.mirror / "bangla-newspaper" / "newspaper-00001.zip"
        data = bytearray(tampered.read_bytes())
        data[-30] ^= 1
        tampered.write_bytes(bytes(data))
        with self.assertRaises(datasets.DatasetError):
            datasets.fetch(["newspaper"], mirror=self.mirror, log=self.log)
        self.assertFalse((datasets.DOWNLOADS / "bangla-newspaper" / "newspaper-00001.zip").exists())

    def test_assembled_content_must_match_the_lock(self):
        datasets.fetch(["newspaper"], mirror=self.mirror, log=self.log)
        self.lock["assembled"]["bangla-newspaper.jsonl"] = {"content_sha256": "0" * 64}
        with self.assertRaises(datasets.DatasetError):
            datasets.assemble(["newspaper"], log=self.log)

    def test_unsafe_member_names_are_refused(self):
        for name in ("../x.jsonl", "/x.jsonl", "a\\b.jsonl"):
            with self.subTest(name=name), self.assertRaises(datasets.DatasetError):
                datasets._safe_member(name)

    def test_the_shipped_lock_is_complete(self):
        real = json.loads(datasets.LOCK_FILE.read_text(encoding="utf-8"))
        self.assertEqual(set(real["packages"]), set(datasets.PACKAGES))
        self.assertEqual(len(real["commit"]), 40)
        for package, info in real["packages"].items():
            self.assertTrue(info["files"], package)
            for entry in info["files"]:
                self.assertEqual(len(entry["sha256"]), 64)
        self.assertEqual(set(real["assembled"]), set(datasets.assembled_files()))


if __name__ == "__main__":
    unittest.main()
