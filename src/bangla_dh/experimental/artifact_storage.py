"""Lossless gzip storage for large experimental artifacts (stdlib only).

Logical paths in historical manifests still name the original bytes. A missing
logical CSV/JSON may be supplied by its .gz sibling; digesting that logical path
hashes the decompressed bytes. An explicitly named .gz is hashed as stored.
Official reference/dataset hash functions are not changed.
"""
from __future__ import annotations
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil

from ..paths import PROJECT_ROOT,output_path,relative_to_project
from ..reference import sha256_file as physical_sha256

LARGE_BYTES=50*1024*1024


def artifact_path(path):
    logical=Path(path)
    if logical.is_file(): return logical
    compressed=logical.with_name(logical.name+'.gz')
    if compressed.is_file(): return compressed
    raise FileNotFoundError(logical)


def open_text(path,*,encoding='utf-8',newline=None):
    stored=artifact_path(path)
    if stored.suffix=='.gz': return gzip.open(stored,'rt',encoding=encoding,newline=newline)
    return stored.open('r',encoding=encoding,newline=newline)


def artifact_sha256(path):
    logical=Path(path);stored=artifact_path(logical)
    if stored==logical: return physical_sha256(stored)
    digest=hashlib.sha256()
    with gzip.open(stored,'rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):digest.update(block)
    return digest.hexdigest()


def hash_artifacts(paths):
    return {relative_to_project(p):artifact_sha256(p) for p in sorted(paths)}


def verify_artifact(path,manifest):
    """Accept old logical-byte manifests and new physical .gz manifests."""
    logical=Path(path);key=relative_to_project(logical)
    if key in manifest['output_sha256']:
        actual=artifact_sha256(logical)
    else:
        stored=artifact_path(logical);key=relative_to_project(stored)
        actual=physical_sha256(stored)
    expected=manifest['output_sha256'][key]
    if actual!=expected:raise ValueError('artifact hash mismatch: '+str(path))


def compress_file(path):
    """Retain the original and write a deterministic byte-identical gzip copy."""
    original=Path(path);target=original.with_name(original.name+'.gz')
    if target.exists():
        digest=hashlib.sha256()
        with gzip.open(target,'rb') as stream:
            for block in iter(lambda:stream.read(1<<20),b''):digest.update(block)
        if digest.hexdigest()!=physical_sha256(original):
            raise FileExistsError('existing compressed artifact differs: '+str(target))
        return target
    with output_path(target).open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as zipped:
            with original.open('rb') as source:shutil.copyfileobj(source,zipped,1<<20)
    return target


def write_json_compressed(path,data):
    target=Path(path)
    if target.suffix!='.gz':target=target.with_name(target.name+'.gz')
    with output_path(target).open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as zipped:
            with io.TextIOWrapper(zipped,encoding='utf-8',newline='\n') as text:
                json.dump(data,text,ensure_ascii=False,indent=2);text.write('\n')
    return target


def write_csv(path,rows):
    """Small CSVs stay plain; large CSVs are written only as deterministic gzip."""
    if not rows:return None
    fields=list(dict.fromkeys(k for r in rows for k in r))
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fields,extrasaction='raise')
    writer.writeheader();writer.writerows(rows)
    payload=stream.getvalue().encode('utf-8');stream.close()
    target=Path(path)
    if len(payload)>=LARGE_BYTES:
        target=target.with_name(target.name+'.gz')
        with output_path(target).open('wb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as zipped:zipped.write(payload)
    else:
        output_path(target).write_bytes(payload)
    return target
