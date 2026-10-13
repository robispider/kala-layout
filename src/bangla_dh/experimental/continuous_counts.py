"""Season e3: exact space-touching action windows from pinned running text.

Words are encoded independently, with the same canonical policy as e2. Only
compact boundary summaries remain in memory; no corpus text is serialized.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
import os
import time

from ..bangla.grammar import Escape
from ..bangla.styles import Style
from ..corpus.frequency import iter_documents
from ..paths import PROJECT_ROOT
from ..reference import sha256_file
from ..scoring import baselines
from ..scoring.model import ANSI_TRADITIONAL_GRID, KeyModel
from .actions import SPACE_ACTION
from .inputs import read_json, token_rows, unit_path
from .mechanics_counts import count_stream, read_counts, triples_from_json, triples_json

VERSION = "continuous-actions-v1"
DEFAULT = PROJECT_ROOT / "results/evaluator-e3/run-v1"
E2 = PROJECT_ROOT / "results/evaluator-e2/run-v1"
CATEGORIES = ("within_word", "edge_space", "spanning_space", "multiple_spaces")


def cache_name(kind, identity, corpus):
    slug = identity.lower().replace(" ", "-").replace("(", "").replace(")", "")
    return f"{kind}-{slug}-{corpus.replace('/', '-')}.json.gz"


def action_steps(steps):
    return tuple(None if isinstance(s, Escape) else s if isinstance(s, tuple)
                 else (s.key, s.layer) for s in steps)


def category(triple):
    spaces = triple.count(SPACE_ACTION)
    if spaces == 0:
        return "within_word"
    if spaces > 1:
        return "multiple_spaces"
    return "spanning_space" if triple[1] == SPACE_ACTION else "edge_space"


def windows(n):
    return max(n - 2, 0)


@dataclass(slots=True)
class WordSummary:
    head: tuple
    tail: tuple
    length: int
    prefix_run: int
    suffix_run: int
    inside: int
    has_escape: bool
    expected: tuple = ()
    observed: list = field(default_factory=lambda: [0, 0, 0])


def summarize(steps):
    steps = action_steps(steps)
    run = prefix = inside = 0
    escaped = False
    for step in steps:
        if step is None:
            inside += windows(run)
            if not escaped:
                prefix = run
            escaped = True
            run = 0
        else:
            run += 1
    inside += windows(run)
    if not escaped:
        prefix = run
    return WordSummary(steps[:2], steps[-min(2, run):] if run else (),
                       len(steps), prefix, run, inside, escaped)


def reference_windows(paragraphs, encode):
    """Independent simple scanner for tests/small audits, including interiors."""
    triples, unigrams, pairs = Counter(), Counter(), Counter()
    identity = 0
    for paragraph in paragraphs:
        previous = []
        run = 0
        for i, word in enumerate(paragraph.split(" ")):
            steps = ((SPACE_ACTION,) if i else ()) + action_steps(encode(word))
            for step in steps:
                if step is None:
                    identity += windows(run)
                    run = 0
                    previous.clear()
                    continue
                unigrams[step] += 1
                if previous:
                    pairs[previous[-1], step] += 1
                if len(previous) == 2:
                    triples[previous[0], previous[1], step] += 1
                previous.append(step)
                previous = previous[-2:]
                run += 1
        identity += windows(run)
    if identity != sum(triples.values()):
        raise ValueError("reference uninterrupted-run identity failed")
    return unigrams, pairs, triples, identity


def boundary_windows(documents, summaries):
    """Scan only cached prefixes/suffixes; retain independent run-length totals."""
    triples = Counter()
    stats = dict(documents=0, paragraphs=0, tokens=0, space_units=0,
                 uninterrupted_run_windows=0)
    for document in documents:
        stats["documents"] += 1
        for paragraph in document["paragraphs"]:
            stats["paragraphs"] += 1
            words = paragraph.split(" ")
            stats["tokens"] += len(words)
            stats["space_units"] += len(words) - 1
            tail = ()
            run = 0
            for i, word in enumerate(words):
                summary = summaries[word]
                summary.observed[0] += 1
                if i == 0:
                    summary.observed[1] += 1
                if i == len(words) - 1:
                    summary.observed[2] += 1
                if i:
                    if len(tail) == 2:
                        triples[tail + (SPACE_ACTION,)] += 1
                    tail = (tail + (SPACE_ACTION,))[-2:]
                    stats["uninterrupted_run_windows"] += windows(run + 1) - windows(run)
                    run += 1
                for step in summary.head:
                    if step is None:
                        tail = ()
                    else:
                        triple = tail + (step,)
                        if len(tail) == 2 and SPACE_ACTION in triple:
                            triples[triple] += 1
                        tail = triple[-2:]
                if summary.length >= 2:
                    tail = summary.tail
                if summary.has_escape:
                    stats["uninterrupted_run_windows"] += (
                        windows(run + summary.prefix_run) - windows(run)
                        + summary.inside - windows(summary.prefix_run))
                    run = summary.suffix_run
                else:
                    stats["uninterrupted_run_windows"] += windows(run + summary.length) - windows(run)
                    run += summary.length
    return triples, stats


def peak_memory_bytes():
    """Process peak working set on Windows; peak RSS elsewhere, when available."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize",
                "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            return counters.PeakWorkingSetSize
        return None
    try:
        import resource
        import sys
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return peak if sys.platform == "darwin" else peak * 1024
    except ImportError:
        return None


def verified_result(root, filename):
    root = root.resolve()
    path = root / filename
    manifest = read_json(root / "run-manifest.json")
    if sha256_file(path) != manifest["output_sha256"][path.relative_to(PROJECT_ROOT).as_posix()]:
        raise ValueError("derived result hash mismatch: " + str(path))
    return read_counts(path), path


def load_verified(root, kind, identity, corpus):
    data, path = verified_result(root, "counts/" + cache_name(kind, identity, corpus))
    record = read_json(unit_path(corpus))
    if (data["kind"], data["identity"], data["corpus"], data["token_table_sha256"]) != (
            kind, identity, corpus, record["token_table_sha256"]):
        raise ValueError("derived action-cache provenance mismatch")
    return data, path


def build_job(kind, identity, corpus):
    name = identity if kind == "style" else identity["name"]
    record = read_json(unit_path(corpus))
    corpus_path = PROJECT_ROOT / record["corpus_file"]
    token_path = PROJECT_ROOT / record["token_table"]
    for path, digest in ((corpus_path, record["corpus_sha256"]), (token_path, record["token_table_sha256"])):
        if sha256_file(path) != digest:
            raise ValueError("running-text/token hash mismatch")
    frozen, _ = load_verified(E2, kind, name, corpus)
    if kind == "style":
        style = Style(identity)
        def encoder(token):
            return tuple(s if isinstance(s, Escape) else (s, "base") for s in style.encode(token))
        decode = None
    else:
        km = baselines.keymap(identity, KeyModel.from_grid(ANSI_TRADITIONAL_GRID))
        encoder, decode = km.encode, km.decode
    summaries = {}
    def encode(token):
        steps = encoder(token)
        summaries[token] = summarize(steps)
        return steps
    started = time.perf_counter()
    def rows():
        for token, n, first, last in token_rows(token_path):
            yield token, n, first, last
            summaries[token].expected = (n, first, last)
    tables, inside = count_stream(rows(), encode, record, decode)
    encoding_seconds = time.perf_counter() - started
    if tables.json() != frozen["action_tables"] or inside != triples_from_json(frozen["triples"]):
        raise ValueError("new word extraction differs from e2")
    # Release encoder caches; the running pass needs only compact summaries.
    if kind == "style":
        style._cache.clear()
    elif hasattr(km, "_cache"):
        km._cache.clear()
    expected_edges = Counter()
    for summary in summaries.values():
        n, first, last = summary.expected
        if summary.prefix_run >= 2 and n > first:
            expected_edges[(SPACE_ACTION,) + summary.head] += n - first
        if summary.suffix_run >= 2 and n > last:
            expected_edges[summary.tail + (SPACE_ACTION,)] += n - last
    # Audit the optimized scanner against a separate full-action scanner.
    sample = []
    for document in iter_documents(corpus_path):
        sample.extend(document["paragraphs"][:50 - len(sample)])
        if len(sample) >= 50:
            break
    _, _, reference, _ = reference_windows(sample, encoder)
    audit_boundary, _ = boundary_windows([{"paragraphs": sample}], summaries)
    if audit_boundary != Counter({t: n for t, n in reference.items() if SPACE_ACTION in t}):
        raise ValueError("boundary scanner disagrees with reference sample")
    for summary in summaries.values():
        summary.observed[:] = [0, 0, 0]
    started = time.perf_counter()
    boundary, stats = boundary_windows(iter_documents(corpus_path), summaries)
    scan_seconds = time.perf_counter() - started
    if any(tuple(s.observed) != s.expected for s in summaries.values()):
        raise ValueError("running word counts/paragraph boundaries differ from token table")
    if any(stats[k] != record[k] for k in ("documents", "paragraphs", "tokens", "space_units")):
        raise ValueError("running corpus totals differ from frozen corpus")
    actual_edges = Counter({t: n for t, n in boundary.items() if category(t) == "edge_space"})
    if actual_edges != expected_edges:
        raise ValueError("edge-space windows disagree with boundary formulas")
    if sum(inside.values()) + sum(boundary.values()) != stats["uninterrupted_run_windows"]:
        raise ValueError("continuous uninterrupted-run identity failed")
    counts = {k: 0 for k in CATEGORIES}
    counts["within_word"] = sum(inside.values())
    for t, n in boundary.items():
        counts[category(t)] += n
    return {"version": VERSION, "kind": kind, "identity": name, "corpus": corpus,
            "corpus_sha256": record["corpus_sha256"], "token_table_sha256": record["token_table_sha256"],
            "action_tables": tables.json(), "triples": triples_json(inside),
            "boundary_triples": triples_json(boundary), "category_counts": counts, "corpus_totals": stats,
            "checks": {"e2_action_and_triple_counts": True, "running_token_boundaries": True,
                       "edge_formulas": True, "reference_sample": True, "uninterrupted_runs": True},
            "benchmark": {"encoding_seconds": round(encoding_seconds, 3), "scan_seconds": round(scan_seconds, 3),
                          "cached_word_types": len(summaries), "peak_process_memory_bytes": peak_memory_bytes(),
                          "memory_scope": "process lifetime peak; may include earlier worker jobs"}}


@lru_cache(maxsize=10)
def committed_style_boundaries(style, corpus):
    path = DEFAULT / "counts" / cache_name("style", style, corpus)
    if not path.exists() or not (DEFAULT / "run-manifest.json").exists():
        return None
    data, _ = load_verified(DEFAULT, "style", style, corpus)
    record = read_json(unit_path(corpus))
    if data["version"] != VERSION or data["corpus_sha256"] != record["corpus_sha256"]:
        raise ValueError("continuous-cache version/corpus mismatch")
    return data
