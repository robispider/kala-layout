"""Fetch pinned MIT sources and extract their scoring code without rewriting it.

Run explicitly with --fetch. Normal evaluation and tests use the vendored files.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import urllib.request

from ..paths import PROJECT_ROOT, output_path, write_json, write_text

COMMIT = "179e1c08b220ae1b02f6c425a7d1cbd1150c1db2"
BASE = f"https://raw.githubusercontent.com/binarybottle/keyboard_layout_scorers/{COMMIT}/"
SOURCE = PROJECT_ROOT / "data/evaluators/mechanics-v1"
PORTS = PROJECT_ROOT / "src/bangla_dh/experimental/ports"
GENERATORS = {
    "dvorak7": "prep/prep_keypair_dvorak7_scores.py",
    "engram": "prep/prep_keypair_engram_scores.py",
    "engram_triples": "prep/prep_keytriple_engram_scores.py",
}
FUNCTIONS = {"get_key_info", "is_finger_in_column", "score_bigram_dvorak7",
             "score_bigram", "score_trigram", "get_all_qwerty_keys"}


def extract(source: str, path: str) -> str:
    """Keep upstream assignments and scoring functions verbatim, with no writers."""
    nodes = ast.parse(source).body
    parts = []
    for node in nodes:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)) or (
            isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS
        ):
            parts.append(ast.get_source_segment(source, node))
    return (f'"""Source-derived scoring port of {path} at {COMMIT}.\n\n'
            'Copyright Arno Klein; MIT license: data/evaluators/mechanics-v1/LICENSE.\n'
            'Extracted by mechanics_sources; scoring bodies and constants are unchanged.\n'
            'Bangla adaptation is in experimental/mechanics.py.\n"""\n\n' + "\n\n".join(parts) + "\n")


def fetch():
    paths = ["LICENSE", *GENERATORS.values(), "prep/prep_all_keypair_scoring_tables.py", "score_layouts.py"]
    paths += [f"tables/keypair_dvorak7_{c}_scores.csv" for c in
              ("distribution", "strength", "home", "vspan", "columns", "remote", "inward")]
    paths += ["tables/keypair_dvorak7_scores.csv", "tables/engram_2key_scores_avg4.csv"]
    paths += [f"tables/engram_2key_scores_{c}.csv" for c in
              ("key_preference", "row_separation", "same_row", "same_finger", "outside", "scissor", "half_scissor")]
    paths += ["tables/engram_3key_scores_order.csv"]
    files = []
    for path in paths:
        raw = urllib.request.urlopen(BASE + path, timeout=60).read()
        local = "LICENSE" if path == "LICENSE" else "upstream/" + path
        target = output_path(SOURCE / local)
        if target.exists() and target.read_bytes() != raw:
            raise ValueError(f"refusing to replace different pinned source: {local}")
        target.write_bytes(raw)
        files.append({"file": local, "upstream_path": path, "source_url": BASE + path,
                      "sha256": hashlib.sha256(raw).hexdigest()})
        print(f"Pinned {path}", flush=True)
    write_json(SOURCE / "source-lock.json", {
        "version": "mechanics-source-v1", "repository": "https://github.com/binarybottle/keyboard_layout_scorers",
        "commit": COMMIT, "author": "Arno Klein", "license": "MIT", "files": files,
        "score_direction": "higher", "engram_pair_formula": "mean(row_separation, same_row, same_finger, outside)",
        "dvorak7_formula": "sum of seven criteria / 7", "engram_order": "separate trigram-order diagnostic",
        "composite_warning": "The upstream unifier averages more Engram columns under the avg4 name. We use the explicit four-criterion generator; no combined pair/triple comfort total is invented.",
    })
    for name, path in GENERATORS.items():
        source = (SOURCE / "upstream" / path).read_text(encoding="utf-8")
        write_text(PORTS / (name + ".py"), extract(source, path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", required=True)
    parser.parse_args()
    fetch()
