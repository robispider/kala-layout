"""Frequency tables (Phase 2, task 4): ``bangla-dh compute-frequency``.

From each corpus file (one domain and split) this computes, in binary64:

* a **token table**: whitespace-delimited tokens with their counts and how
  often each starts or ends a paragraph (``data/corpus/…tokens.tsv.gz``);
  scoring of multi-keystroke layouts encodes each token type once;
* **unit counts** n_i and **adjacent-unit counts** n_ij over typing units
  (``bangla.grammar.segment``), with space as an explicit unit. Pairs are
  formed only inside a paragraph, so no pair crosses a paragraph or document
  boundary. A character outside the inventory is not a unit; it is counted
  separately and breaks the pair chain.

``u_i = n_i / N`` and ``v_ij = n_ij / N`` with N = Σ n_i (RESEARCH_SPEC 5.2,
space included). The optimization frequencies are the α-weighted mixture of
the domain tables named in the corpus config.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..bangla.grammar import UnitSet, segment
from ..bangla.inventory import SPACE
from ..paths import gzip_text_lines, gzip_text_writer, output_path, relative_to_project
from ..reference import sha256_file

VERSION = "bangla-frequency-v1"


def iter_documents(path: Path):
    for line in gzip_text_lines(path):
        if line:
            yield json.loads(line)


def count_tokens(path: Path) -> dict:
    tokens, first, last = Counter(), Counter(), Counter()
    documents = paragraphs = 0
    for document in iter_documents(path):
        documents += 1
        for paragraph in document["paragraphs"]:
            parts = paragraph.split(" ")
            tokens.update(parts)
            first[parts[0]] += 1
            last[parts[-1]] += 1
            paragraphs += 1
    return {"tokens": tokens, "first": first, "last": last, "documents": documents, "paragraphs": paragraphs}


def unit_counts(tokens: Counter, first: Counter, last: Counter, paragraphs: int, units: UnitSet) -> dict:
    unigrams, bigrams, oov = Counter(), Counter(), Counter()
    is_unit = units.is_unit
    for token, count in tokens.items():
        pieces = segment(token)
        previous = None
        for piece in pieces:
            if is_unit(piece):
                unigrams[piece] += count
                if previous is not None:
                    bigrams[(previous, piece)] += count
                previous = piece
            else:
                oov[piece] += count
                previous = None
        if pieces:
            after_space = count - first[token]
            before_space = count - last[token]
            if after_space and is_unit(pieces[0]):
                bigrams[(SPACE, pieces[0])] += after_space
            if before_space and is_unit(pieces[-1]):
                bigrams[(pieces[-1], SPACE)] += before_space
    unigrams[SPACE] = sum(tokens.values()) - paragraphs
    return {"unigrams": unigrams, "bigrams": bigrams, "oov": oov}


def write_token_table(path: Path, counted: dict) -> Path:
    first, last = counted["first"], counted["last"]
    with gzip_text_writer(path) as stream:
        stream.write("# token\tcount\tparagraph_first\tparagraph_last\n")
        for token, count in sorted(counted["tokens"].items(), key=lambda kv: (-kv[1], kv[0])):
            stream.write(f"{token}\t{count}\t{first[token]}\t{last[token]}\n")
    return output_path(path)


def read_token_table(path: Path):
    """(token, count) pairs of a token table."""
    for line in gzip_text_lines(path):
        if line and not line.startswith("# "):
            token, count, _first, _last = line.split("\t")
            yield token, int(count)


def compute(corpus_file: Path, units: UnitSet, inventory_sha: str) -> tuple[dict, Path]:
    counted = count_tokens(corpus_file)
    table = write_token_table(Path(str(corpus_file).replace(".jsonl.gz", ".tokens.tsv.gz")), counted)
    tables = unit_counts(counted["tokens"], counted["first"], counted["last"], counted["paragraphs"], units)
    unigrams, bigrams, oov = tables["unigrams"], tables["bigrams"], tables["oov"]
    n = sum(unigrams.values())
    record = {
        "version": VERSION,
        "corpus_file": relative_to_project(corpus_file), "corpus_sha256": sha256_file(corpus_file),
        "inventory_symbol_list_sha256": inventory_sha,
        "token_table": relative_to_project(table), "token_table_sha256": sha256_file(table),
        "documents": counted["documents"], "paragraphs": counted["paragraphs"],
        "tokens": sum(counted["tokens"].values()), "token_types": len(counted["tokens"]),
        "N": n, "space_units": unigrams[SPACE],
        "out_of_inventory_characters": sum(oov.values()),
        "unit_counts": dict(sorted(unigrams.items(), key=lambda kv: (-kv[1], kv[0]))),
        "bigram_counts": [[a, b, c] for (a, b), c in sorted(bigrams.items(), key=lambda kv: (-kv[1], kv[0]))],
        "out_of_inventory_counts": dict(sorted(oov.items(), key=lambda kv: (-kv[1], kv[0]))),
    }
    return record, table


def load_table(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frequencies(record: dict) -> tuple[dict[str, float], dict[tuple[str, str], float]]:
    """u and v (binary64) of one frequency record."""
    n = record["N"]
    u = {unit: count / n for unit, count in record["unit_counts"].items()}
    v = {(a, b): count / n for a, b, count in record["bigram_counts"]}
    return u, v


def mixture(records: dict[str, dict], weights: dict[str, float]) -> tuple[dict[str, float], dict[tuple[str, str], float]]:
    """u_i = Σ_d α_d n_i,d / N_d and v_ij likewise (RESEARCH_SPEC 5.2)."""
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-12:
        raise ValueError(f"domain weights sum to {total}, not 1")
    u: dict[str, float] = {}
    v: dict[tuple[str, str], float] = {}
    for name, alpha in weights.items():
        du, dv = frequencies(records[name])
        for unit, value in du.items():
            u[unit] = u.get(unit, 0.0) + alpha * value
        for pair, value in dv.items():
            v[pair] = v.get(pair, 0.0) + alpha * value
    return u, v


def write_mixture(path: Path, u: dict, v: dict, weights: dict, sources: dict) -> Path:
    data = {"version": VERSION, "weights": weights, "sources": sources,
            "u": dict(sorted(u.items(), key=lambda kv: (-kv[1], kv[0]))),
            "v": [[a, b, value] for (a, b), value in sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))]}
    target = output_path(path)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return target
