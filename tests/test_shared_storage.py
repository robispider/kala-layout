"""Exact archived bytes, deterministic containers and safe fresh-copy access."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from bangla_dh.paths import PROJECT_ROOT as ROOT,output_path,write_json
from bangla_dh.experimental.shared_storage import StoredArtifacts,write_bundle,digest


class SharedStorageTests(unittest.TestCase):
    def setUp(self):
        parent=output_path(ROOT/'work/shared-storage-tests')
        parent.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.payload='{"symbol":"ক","count":12}\r\n'.encode('utf-8')
        self.source=self.root/'run/runs/seed.json'
        output_path(self.source).write_bytes(self.payload)
        rec=write_bundle(self.root/'run/runs.zip',{'seed.json':self.source})
        rec.update(archive='run/runs.zip',logical_root='run/runs')
        snaps=write_bundle(self.root/'before.zip',{'old.txt':b'old\r\n'})
        snaps['archive']='before.zip'
        self.config=self.root/'.gitignore';output_path(self.config).write_bytes(b'new\n')
        self.data={'bundles':[rec],'snapshots':snaps,'gzip_files':[],
            'bookkeeping_revisions':[{'path':'.gitignore','before_sha256':digest(b'old\r\n'),
                'after_sha256':digest(b'new\n'),'snapshot_member':'old.txt'}]}
        self.manifest=self.root/'storage.json';write_json(self.manifest,self.data)

    def store(self):return StoredArtifacts(self.root,self.manifest)

    def test_bundle_is_deterministic_and_exact_with_unicode_crlf(self):
        other=self.root/'second.zip';write_bundle(other,{'seed.json':self.payload})
        self.assertEqual(other.read_bytes(),(self.root/'run/runs.zip').read_bytes())
        with self.store() as store:
            self.assertEqual(store.hash('run/runs/seed.json'),digest(self.payload))
            self.assertEqual(store.read_json('run/runs/seed.json'),{'symbol':'ক','count':12})
            self.assertEqual(store.verify_containers(),2)

    def test_archive_only_fresh_copy_read_and_restore(self):
        self.source.unlink()
        with self.store() as store:
            self.assertEqual(store.hash('run/runs/seed.json',digest(self.payload)),digest(self.payload))
            self.assertEqual(store.restore('run'),{'restored':1,'already_present':0})
            self.assertEqual(self.source.read_bytes(),self.payload)
            self.assertEqual(store.restore('run'),{'restored':0,'already_present':1})

    def test_modified_local_file_is_never_overwritten(self):
        output_path(self.source).write_bytes(b'changed')
        with self.store() as store:
            with self.assertRaises(FileExistsError):store.restore('run')
            self.assertEqual(self.source.read_bytes(),b'changed')
            self.assertEqual(store.hash('run/runs/seed.json'),digest(self.payload))

    def test_historical_bookkeeping_is_separate_from_current_file(self):
        with self.store() as store:
            self.assertEqual(store.hash('.gitignore'),digest(b'new\n'))
            self.assertEqual(store.hash('.gitignore',digest(b'old\r\n')),digest(b'old\r\n'))
            with self.assertRaises(ValueError):store.hash('.gitignore','0'*64)

    def test_gzip_only_derived_table(self):
        path=output_path(self.root/'run/pool.json.gz')
        with path.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as z:z.write(self.payload)
        self.data['gzip_files']=[{'logical_path':'run/pool.json','stored_path':'run/pool.json.gz',
            'stored_sha256':digest(path.read_bytes()),'logical_sha256':digest(self.payload)}]
        write_json(self.manifest,self.data)
        with self.store() as store:
            self.assertEqual(store.read_json('run/pool.json'),{'symbol':'ক','count':12})
            store.verify_containers()
            store.restore('run')
            self.assertEqual((self.root/'run/pool.json').read_bytes(),self.payload)

    def test_archive_corruption_is_detected(self):
        archive=self.root/'run/runs.zip'
        with output_path(archive).open('ab') as f:f.write(b'corrupt')
        with self.store() as store:
            with self.assertRaisesRegex(ValueError,'archive hash'):store.hash('run/runs/seed.json')

    def test_paths_and_member_names_cannot_escape(self):
        with self.store() as store:
            with self.assertRaises(ValueError):store.hash('../outside.json')
            with self.assertRaises(ValueError):store.restore('../outside')
        with self.assertRaises(ValueError):write_bundle(self.root/'bad.zip',{'../bad.json':b'bad'})

    def test_existing_container_is_not_overwritten(self):
        with self.assertRaises(FileExistsError):write_bundle(self.root/'run/runs.zip',{'other.json':b'new'})


if __name__=='__main__':unittest.main()
