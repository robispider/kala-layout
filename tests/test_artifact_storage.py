"""Compression, original-byte hashes, and compressed-only reader regressions."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bangla_dh.paths import PROJECT_ROOT,output_path,WriteOutsideProject
from bangla_dh.experimental.artifact_storage import (artifact_sha256,open_text,compress_file,
    write_csv,write_json_compressed,verify_artifact)
from bangla_dh.experimental.inputs import read_json


class ArtifactStorageTests(unittest.TestCase):
    def setUp(self):
        directory=output_path(PROJECT_ROOT/'work/artifact-storage-tests')
        directory.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=directory)
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def test_csv_unicode_crlf_byte_hash_and_compressed_only(self):
        path=self.root/'metrics.csv';payload='symbol,count\r\nক,12\r\n'.encode('utf-8')
        output_path(path).write_bytes(payload)
        zipped=compress_file(path)
        first=zipped.read_bytes();zipped.unlink();self.assertEqual(first,compress_file(path).read_bytes())
        path.unlink()
        self.assertEqual(artifact_sha256(path),hashlib.sha256(payload).hexdigest())
        self.assertEqual(artifact_sha256(zipped),hashlib.sha256(zipped.read_bytes()).hexdigest())
        with open_text(path,newline='') as stream:self.assertEqual(list(csv.DictReader(stream)),[{'symbol':'ক','count':'12'}])
        with gzip.open(zipped,'rb') as stream:self.assertEqual(stream.read(),payload)

    def test_json_logical_fallback_and_small_search_summary(self):
        path=self.root/'results.json';data={'runs':[{'style':'A','symbol':'ক'}]}
        zipped=write_json_compressed(path,data)
        self.assertFalse(path.exists());self.assertTrue(zipped.exists())
        self.assertEqual(read_json(path),data)

    def test_legacy_and_physical_manifests_and_corruption(self):
        path=self.root/'data.csv';zipped=write_json_compressed(path,{'x':1})
        logical_key=path.relative_to(PROJECT_ROOT).as_posix();physical_key=zipped.relative_to(PROJECT_ROOT).as_posix()
        verify_artifact(path,{'output_sha256':{logical_key:artifact_sha256(path)}})
        verify_artifact(path,{'output_sha256':{physical_key:artifact_sha256(zipped)}})
        with self.assertRaises(ValueError):verify_artifact(path,{'output_sha256':{logical_key:'0'*64}})

    def test_csv_large_threshold_and_small_plain_outputs(self):
        rows=[{'name':'ক','value':2}]
        small=write_csv(self.root/'small.csv',rows);self.assertEqual(small.suffix,'.csv')
        with patch('bangla_dh.experimental.artifact_storage.LARGE_BYTES',1):
            large=write_csv(self.root/'large.csv',rows)
        self.assertEqual(large.suffix,'.gz');self.assertFalse((self.root/'large.csv').exists())
        with gzip.open(large,'rb') as f:self.assertEqual(f.read(),small.read_bytes())

    def test_missing_or_conflicting_artifacts_fail(self):
        with self.assertRaises(FileNotFoundError):open_text(self.root/'missing.csv')
        path=self.root/'data.csv';output_path(path).write_bytes(b'original')
        write_json_compressed(path,{'different':True})
        with self.assertRaises(FileExistsError):compress_file(path)

    def test_writer_guard(self):
        with self.assertRaises(WriteOutsideProject):write_json_compressed(PROJECT_ROOT.parent/'outside.json',{})


if __name__=='__main__':unittest.main()
