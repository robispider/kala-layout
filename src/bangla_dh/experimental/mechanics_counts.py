"""Derived within-token triples; token text is never written to results."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import gzip
import json

from ..bangla.grammar import Escape, UnitSet, nfc, segment
from ..bangla.styles import Style
from ..paths import PROJECT_ROOT
from ..reference import sha256_file
from ..scoring import baselines
from ..scoring.model import ANSI_TRADITIONAL_GRID, KeyModel
from .actions import ActionTables, SPACE_ACTION
from .inputs import read_json, token_rows, unit_path, frequency_path


def count_stream(rows, encode, record, decode=None):
    """Count tuples (key/label, layer), keeping boundaries and repeats lossless."""
    units = UnitSet.from_inventory()
    unigrams, pairs, triples = Counter(), Counter(), Counter()
    escaped = unit_count = tokens = types = 0
    for token, count, first, last in rows:
        if count <= 0 or not 0 <= first <= count or not 0 <= last <= count:
            raise ValueError("invalid token boundary counts")
        token = nfc(token)
        steps = encode(token)
        if decode is not None and decode(steps) != token:
            raise ValueError("canonical encoding failed NFC round trip")
        steps = [step if isinstance(step, (Escape, tuple)) else (step.key, step.layer) for step in steps]
        unit_count += count * sum(units.is_unit(piece) for piece in segment(token))
        tokens += count
        types += 1
        previous = []
        for step in steps:
            if isinstance(step, Escape):
                escaped += count * units.is_unit(step.char)
                previous.clear()
                continue
            unigrams[step] += count
            if previous:
                pairs[previous[-1], step] += count
            if len(previous) == 2:
                triples[previous[0], previous[1], step] += count
            previous.append(step)
            previous = previous[-2:]
        if steps:
            if not isinstance(steps[0], Escape):
                pairs[SPACE_ACTION, steps[0]] += count - first
            if not isinstance(steps[-1], Escape):
                pairs[steps[-1], SPACE_ACTION] += count - last
    if tokens != record["tokens"] or unit_count + record["space_units"] != record["N"]:
        raise ValueError("triple input disagrees with frozen token/unit counts")
    unigrams[SPACE_ACTION] = record["space_units"]
    tables = ActionTables(record["N"], record["space_units"], unigrams, pairs,
                          escaped, record.get("out_of_inventory_characters", 0), types).validate()
    return tables, triples


def build_job(kind, identity, corpus):
    record = read_json(unit_path(corpus))
    token_path = PROJECT_ROOT / record["token_table"]
    if sha256_file(token_path) != record["token_table_sha256"]:
        raise ValueError("triple token-table hash mismatch")
    rows = token_rows(token_path)
    if kind == "style":
        style = Style(identity)
        def encode(token):
            return [step if isinstance(step, Escape) else (step, "base") for step in style.encode(token)]
        tables, triples = count_stream(rows, encode, record)
        frozen = read_json(frequency_path(identity, corpus))
        expected_u = Counter({(k, "base"): n for k, n in frozen["label_counts"].items() if k != " "})
        expected_u[SPACE_ACTION] = frozen["space_units"]
        def label(k):
            return SPACE_ACTION if k == " " else (k, "base")
        expected_p = Counter({(label(a), label(b)): n for a, b, n in frozen["pair_counts"]})
        if tables.unigrams != expected_u or tables.pairs != expected_p or tables.escaped_units != frozen["escaped_unit_count"]:
            raise ValueError("new triple pass disagrees with frozen style action counts")
    elif kind == "baseline":
        km = baselines.keymap(identity, KeyModel.from_grid(ANSI_TRADITIONAL_GRID))
        tables, triples = count_stream(rows, km.encode, record, km.decode)
    else:
        raise ValueError("unknown triple job")
    return tables, triples


def triples_json(triples):
    return [[*[list(a) for a in actions], n] for actions, n in sorted(triples.items())]


def triples_from_json(rows):
    out = Counter()
    for a, b, c, n in rows:
        if not isinstance(n, int) or n <= 0:
            raise ValueError("invalid triple count")
        actions = (tuple(a), tuple(b), tuple(c))
        if actions in out:
            raise ValueError("duplicate triple")
        out[actions] = n
    return out


def read_counts(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def map_triples(triples, assignment):
    out = Counter()
    for actions, n in triples.items():
        out[tuple(assignment[a[0]] for a in actions)] += n
    return out


@lru_cache(maxsize=10)
def committed_style_triples(style, corpus):
    """Optional challenge counts, verified against their published manifest."""
    root = PROJECT_ROOT / "results/evaluator-e2/run-v1"
    path = root / "counts" / f"style-{style.lower()}-{corpus.replace('/', '-')}.json.gz"
    if not path.exists() or not (root / "run-manifest.json").exists():
        return None
    manifest = read_json(root / "run-manifest.json")
    if sha256_file(path) != manifest["output_sha256"][path.relative_to(PROJECT_ROOT).as_posix()]:
        raise ValueError("challenge triple-cache hash mismatch")
    saved = read_counts(path)
    if saved["identity"] != style or saved["corpus"] != corpus or saved["token_table_sha256"] != read_json(unit_path(corpus))["token_table_sha256"]:
        raise ValueError("challenge triple-cache provenance mismatch")
    return triples_from_json(saved["triples"])
