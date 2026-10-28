"""Compact, lossless Git storage for shared-search evidence; no model changes."""
from __future__ import annotations

import argparse
from contextlib import contextmanager,ExitStack
import gzip
import hashlib
import json
from pathlib import Path,PurePosixPath
import zipfile

from ..paths import PROJECT_ROOT as ROOT,output_path,write_json,write_text,hash_outputs
from ..reference import sha256_file
from .artifact_storage import compress_file

SCOPES=('results/shared-layout-v1','results/shared-layout-relaxed-v1','results/shared-exploration-pilot-v1')
STORAGE='results/shared-storage-v1'
METADATA=STORAGE+'/storage-manifest.json'
INDEX='_members.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def valid_member(name):
    if name in ('','.', '..') or PurePosixPath(name).name!=name or '\\' in name:
        raise ValueError('archive members must be plain filenames')


def write_bundle(path,entries):
    """Deterministic ZIP, byte hashes in its own compressed member index."""
    target=output_path(path)
    if target.exists():raise FileExistsError(target)
    index={}
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        def put(name,payload):
            valid_member(name)
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.create_system=3;info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,payload,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        for name,source in sorted(entries.items()):
            if name==INDEX:raise ValueError('reserved archive member')
            payload=source.read_bytes() if isinstance(source,Path) else source
            index[name]={'sha256':digest(payload),'bytes':len(payload)}
            put(name,payload)
        raw=(json.dumps(index,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
        put(INDEX,raw)
    return {'archive':target.relative_to(ROOT).as_posix(),'sha256':sha256_file(target),
            'index_sha256':digest(raw),'members':len(index),'raw_bytes':sum(x['bytes'] for x in index.values()),
            'stored_bytes':target.stat().st_size}


class StoredArtifacts:
    """Resolve current files, gzip tables, seed ZIPs and declared old revisions."""
    def __init__(self,root=ROOT,manifest=None):
        self.root=Path(root).resolve()
        path=Path(manifest) if manifest is not None else self.root/METADATA
        self.metadata=json.loads(path.read_text(encoding='utf-8'))
        self.stack=ExitStack();self.zips={};self.cache={}

    def __enter__(self):return self
    def __exit__(self,*args):self.stack.close()

    def path(self,name):
        p=(self.root/name).resolve()
        if not p.is_relative_to(self.root):raise ValueError('artifact path outside checkout')
        return p

    def zip(self,record):
        key=record['archive']
        if key not in self.zips:
            p=self.path(key)
            if sha256_file(p)!=record['sha256']:raise ValueError('archive hash mismatch: '+key)
            z=self.stack.enter_context(zipfile.ZipFile(p))
            raw=z.read(INDEX)
            if digest(raw)!=record['index_sha256']:raise ValueError('archive index mismatch')
            members=json.loads(raw)
            for name in members:valid_member(name)
            if set(z.namelist())!={INDEX,*members}:raise ValueError('archive member set mismatch')
            if len(z.namelist())!=len(members)+1:raise ValueError('duplicate archive members')
            self.zips[key]=(z,members)
        return self.zips[key]

    @contextmanager
    def open(self,name,expected=None):
        logical=PurePosixPath(name).as_posix()
        self.path(logical)
        for revision in self.metadata.get('bookkeeping_revisions',[]):
            if logical==revision['path'] and expected==revision['before_sha256']:
                z,index=self.zip(self.metadata['snapshots'])
                with z.open(revision['snapshot_member']) as stream:yield stream
                return
        for item in self.metadata.get('gzip_files',[]):
            if logical==item['logical_path']:
                with gzip.open(self.path(item['stored_path']),'rb') as stream:yield stream
                return
        for bundle in self.metadata.get('bundles',[]):
            if PurePosixPath(logical).parent.as_posix()==bundle['logical_root']:
                z,index=self.zip(bundle)
                member=PurePosixPath(logical).name
                if member not in index:raise FileNotFoundError(logical)
                with z.open(member) as stream:yield stream
                return
        p=self.path(logical)
        if p.is_file():
            with p.open('rb') as stream:yield stream
        elif p.with_name(p.name+'.gz').is_file():
            # Existing large-artifact policy predates this shared-search package.
            with gzip.open(p.with_name(p.name+'.gz'),'rb') as stream:yield stream
        else:raise FileNotFoundError(logical)

    def hash(self,name,expected=None):
        key=(name,expected)
        if key not in self.cache:
            h=hashlib.sha256()
            with self.open(name,expected) as stream:
                for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
            self.cache[key]=h.hexdigest()
        observed=self.cache[key]
        if expected is not None and observed!=expected:
            raise ValueError('logical artifact hash mismatch: '+name)
        return observed

    def read_json(self,name):
        with self.open(name) as stream:return json.load(stream)

    def verify_containers(self):
        members=0
        for record in [*self.metadata.get('bundles',[]),self.metadata['snapshots']]:
            archive,index=self.zip(record)
            if len(index)!=record['members']:raise ValueError('member count mismatch')
            for name,entry in index.items():
                h=hashlib.sha256();size=0
                with archive.open(name) as stream:
                    for block in iter(lambda:stream.read(1<<20),b''):h.update(block);size+=len(block)
                if h.hexdigest()!=entry['sha256'] or size!=entry['bytes']:
                    raise ValueError('archive member bytes changed')
                members+=1
        for item in self.metadata.get('gzip_files',[]):
            if sha256_file(self.path(item['stored_path']))!=item['stored_sha256']:
                raise ValueError('gzip container hash mismatch')
            self.hash(item['logical_path'],item['logical_sha256'])
        for r in self.metadata.get('bookkeeping_revisions',[]):
            self.hash(r['path'],r['before_sha256'])
            if sha256_file(self.path(r['path']))!=r['after_sha256']:
                raise ValueError('current bookkeeping bytes changed')
        return members

    def restore(self,run):
        """Materialize one run's ignored evidence; never replace changed files."""
        relative=PurePosixPath(run).as_posix().rstrip('/')
        self.path(relative)
        restored=existing=0
        items=[]
        for bundle in self.metadata.get('bundles',[]):
            if bundle['logical_root']==relative+'/runs':
                z,index=self.zip(bundle)
                items.extend((bundle['logical_root']+'/'+n,x['sha256']) for n,x in index.items())
        for item in self.metadata.get('gzip_files',[]):
            if PurePosixPath(item['logical_path']).parent.as_posix()==relative:
                items.append((item['logical_path'],item['logical_sha256']))
        if not items:raise ValueError('no packed evidence for that run')
        # Precheck all existing targets before writing any missing file.
        for logical,expected in items:
            p=self.path(logical)
            if p.exists() and (not p.is_file() or sha256_file(p)!=expected):
                raise FileExistsError('refusing to overwrite changed local file: '+logical)
        for logical,expected in items:
            p=self.path(logical)
            if p.exists():existing+=1;continue
            with self.open(logical) as stream:payload=stream.read()
            if digest(payload)!=expected:raise ValueError('restore bytes failed verification')
            output_path(p).write_bytes(payload);restored+=1
        return {'restored':restored,'already_present':existing}


def package():
    destination=ROOT/METADATA
    if destination.exists():raise FileExistsError('storage package already prepared')
    before={name:(ROOT/name).read_bytes() for name in ('.gitignore','.gitattributes')}
    bundles=[];gzip_files=[]
    for scope in SCOPES:
        for folder in sorted((ROOT/scope).rglob('runs')):
            files=[p for p in folder.iterdir() if p.is_file()]
            if not files:continue
            if any(p.suffix!='.json' or p.is_symlink() for p in files):
                raise ValueError('unexpected seed evidence; review before packaging')
            record=write_bundle(folder.parent/'runs.zip',{p.name:p for p in files})
            record['logical_root']=folder.relative_to(ROOT).as_posix();bundles.append(record)
        for p in sorted((ROOT/scope).rglob('*.json')):
            if p.name!='training-pool.json' and p.stat().st_size<50*1024*1024:continue
            packed=compress_file(p)
            gzip_files.append({'logical_path':p.relative_to(ROOT).as_posix(),
                'stored_path':packed.relative_to(ROOT).as_posix(),'logical_sha256':sha256_file(p),
                'stored_sha256':sha256_file(packed),'raw_bytes':p.stat().st_size,'stored_bytes':packed.stat().st_size})
    snapshots={};revisions=[]
    for name,payload in before.items():
        member=digest(payload)+'-'+name.lstrip('.')+'.txt'
        snapshots[member]=payload
        revisions.append({'path':name,'before_sha256':digest(payload),'snapshot_member':member})
    snapshot_record=write_bundle(ROOT/STORAGE/'bookkeeping-before.zip',snapshots)
    ignore=before['.gitignore'].decode('utf-8').replace('\r\n','\n').rstrip()+'\n\n'
    ignore+='# Lossless shared-search evidence is stored in runs.zip / JSON.gz.\n'
    ignore+='\n'.join('/'+b['logical_root']+'/' for b in bundles)+'\n'
    ignore+='\n'.join('/'+x['logical_path'] for x in gzip_files)+'\n'
    attrs=before['.gitattributes'].decode('utf-8').replace('\r\n','\n').rstrip()+'\n'
    attrs+='''# Compact shared-search archives and their pinned text inputs.
*.zip -text
.gitignore text eol=lf
.gitattributes text eol=lf
src/bangla_dh/experimental/shared_*.py text eol=lf
tests/test_shared_*.py text eol=lf
experiments/** text eol=lf
'''
    write_text(ROOT/'.gitignore',ignore);write_text(ROOT/'.gitattributes',attrs)
    for r in revisions:r['after_sha256']=sha256_file(ROOT/r['path'])
    kept=[]
    for scope in SCOPES:
        for p in (ROOT/scope).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts or 'runs' in p.parts:continue
            if any(p==ROOT/x['logical_path'] for x in gzip_files):continue
            kept.append(p)
    kept += [p for p in (ROOT/'experiments').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    kept += list((ROOT/'src/bangla_dh/experimental').glob('shared_*.py'))
    kept += list((ROOT/'tests').glob('test_shared_*.py'))
    kept += [ROOT/'.gitignore',ROOT/'.gitattributes']
    data={'version':'shared-storage-v1','scientific_values_changed':False,'local_originals_retained':True,
          'bundles':bundles,'gzip_files':gzip_files,'snapshots':snapshot_record,
          'bookkeeping_revisions':revisions,'kept_files_sha256':hash_outputs(sorted(set(kept))),
          'raw_evidence_bytes':sum(x['raw_bytes'] for x in [*bundles,*gzip_files]),
          'stored_evidence_bytes':sum(x['stored_bytes'] for x in [*bundles,*gzip_files])}
    write_json(destination,data)
    artifacts=[destination,ROOT/STORAGE/'README.md',ROOT/STORAGE/'bookkeeping-before.zip']
    artifacts += [ROOT/b['archive'] for b in bundles]+[ROOT/x['stored_path'] for x in gzip_files]
    write_json(ROOT/STORAGE/'run-manifest.json',{'version':'shared-storage-v1','new_search':False,'seeds':[],
        'parameters':{'compression':'deterministic ZIP deflate and gzip; exact original bytes',
                      'original_logical_manifests':'preserved','original_local_files':'retained, Git-ignored'},
        'output_sha256':hash_outputs(artifacts)})
    print(json.dumps({'seed_files':sum(b['members'] for b in bundles),'bundles':len(bundles),
                      'raw_bytes':data['raw_evidence_bytes'],'stored_bytes':data['stored_evidence_bytes']}))


def verify(root=ROOT):
    checked=0
    with StoredArtifacts(root) as store:
        members=store.verify_containers()
        for name,expected in store.metadata['kept_files_sha256'].items():store.hash(name,expected);checked+=1
        manifests=[]
        for scope in SCOPES:
            manifests += [p for p in (store.root/scope).rglob('*.json')
                          if p.name.endswith('manifest.json') or p.name in ('search-plan.json','experiment-plan.json')]
        manifests += list((store.root/'experiments').rglob('*manifest.json'))
        for path in sorted(manifests):
            record=json.loads(path.read_text(encoding='utf-8'))
            for key,refs in record.items():
                if not key.endswith('sha256') or not isinstance(refs,dict):continue
                for name,expected in refs.items():
                    if not isinstance(expected,str) or len(expected)!=64:continue
                    store.hash(name,expected);checked+=1
        storage=json.loads((store.root/STORAGE/'run-manifest.json').read_text(encoding='utf-8'))
        for name,expected in storage['output_sha256'].items():store.hash(name,expected);checked+=1
        print(json.dumps({'verified_references':checked,'archived_members':members,
                          'historical_manifests_unchanged':True,'root':str(store.root)}))
        return {'verified_references':checked,'archived_members':members}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('pack')
    p=sub.add_parser('verify');p.add_argument('--root',type=Path,default=ROOT)
    p=sub.add_parser('restore');p.add_argument('--run',required=True)
    args=parser.parse_args()
    if args.command=='pack':package()
    elif args.command=='verify':verify(args.root)
    else:
        with StoredArtifacts() as store:print(json.dumps(store.restore(args.run)))


if __name__=='__main__':main()
