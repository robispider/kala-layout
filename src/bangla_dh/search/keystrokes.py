"""Per-style keystroke frequencies (Phase 3, task 2).

A style turns every token into the same label stream for every layout
(``bangla.styles``), so its keystroke statistics are computed once per style
and corpus from the Phase 2 token tables:

* ``label_counts``: keystrokes per key label (a double tap counts twice);
* ``pair_counts``: consecutive keystrokes inside a token, including the
  repeated key of a double tap (free in J, like any repeat) and pairs with
  space at token boundaries that are not paragraph boundaries;
* ``escaped``: units the style cannot type (no key, invalid text, rule
  collisions) and characters outside the inventory; both break the chain.

N is the number of typing units of the text (space included), the same N as
Phase 2, so ``u = label_counts / N`` and ``v = pair_counts / N`` give J per
unit of text and every style and layout scores on one scale.
"""
from __future__ import annotations

import multiprocessing as mp
from collections import Counter
from pathlib import Path

from ..bangla.grammar import Escape, UnitSet, segment
from ..bangla.inventory import SPACE
from ..bangla.styles import Style
from ..paths import gzip_text_lines, relative_to_project
from ..reference import sha256_file

VERSION = "bangla-dh-keystrokes-v1"
BATCH = 40_000

_style: Style | None = None
_units: UnitSet | None = None


def _init(style_name: str) -> None:
    global _style, _units
    _style = Style(style_name)
    _units = UnitSet.from_inventory()


def count_batch(batch: list[tuple[str, int, int, int]]) -> dict:
    style, is_unit = _style, _units.is_unit
    labels, pairs, escaped_units, oov = Counter(), Counter(), Counter(), Counter()
    units = keystrokes = 0
    for token, count, first, last in batch:
        units += count * sum(1 for piece in segment(token) if is_unit(piece))
        steps = style.encode(token)
        previous = None
        for step in steps:
            if isinstance(step, Escape):
                (escaped_units if is_unit(step.char) else oov)[step.char] += count
                previous = None
                continue
            labels[step] += count
            keystrokes += count
            if previous is not None:
                pairs[(previous, step)] += count
            previous = step
        if steps:
            if count - first and not isinstance(steps[0], Escape):
                pairs[(SPACE, steps[0])] += count - first
            if count - last and not isinstance(steps[-1], Escape):
                pairs[(steps[-1], SPACE)] += count - last
    return {"labels": labels, "pairs": pairs, "escaped_units": escaped_units, "oov": oov,
            "units": units, "keystrokes": keystrokes}


def _batches(token_table: Path):
    batch = []
    for line in gzip_text_lines(token_table):
        if not line or line.startswith("# "):
            continue
        token, count, first, last = line.split("\t")
        batch.append((token, int(count), int(first), int(last)))
        if len(batch) == BATCH:
            yield batch
            batch = []
    if batch:
        yield batch


def compute(style_name: str, record: dict, project_root: Path, workers: int | None = None) -> dict:
    """Keystroke tables of one style over the token table of a Phase 2
    frequency record (one corpus split)."""
    table = project_root / record["token_table"]
    total = {"labels": Counter(), "pairs": Counter(), "escaped_units": Counter(), "oov": Counter(),
             "units": 0, "keystrokes": 0}
    workers = workers or max(1, min(16, mp.cpu_count() - 2))
    with mp.Pool(workers, initializer=_init, initargs=(style_name,)) as pool:
        for part in pool.imap_unordered(count_batch, _batches(table)):
            for key in ("labels", "pairs", "escaped_units", "oov"):
                total[key].update(part[key])
            total["units"] += part["units"]
            total["keystrokes"] += part["keystrokes"]
    space = record["tokens"] - record["paragraphs"]
    n = total["units"] + space
    if n != record["N"]:
        raise ValueError(f"style {style_name}: N {n} differs from the Phase 2 record ({record['N']})")
    labels = total["labels"]
    labels[SPACE] = space
    return {
        "version": VERSION, "style": style_name,
        "token_table": relative_to_project(table), "token_table_sha256": sha256_file(table),
        "N": n, "space_units": space, "keystrokes_excluding_space": total["keystrokes"],
        "escaped_unit_count": sum(total["escaped_units"].values()),
        "outside_inventory_count": sum(total["oov"].values()),
        "label_counts": dict(sorted(labels.items(), key=lambda kv: (-kv[1], kv[0]))),
        "pair_counts": [[a, b, c] for (a, b), c in sorted(total["pairs"].items(), key=lambda kv: (-kv[1], kv[0]))],
        "escaped_units": dict(sorted(total["escaped_units"].items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def frequencies(record: dict) -> tuple[dict[str, float], dict[tuple[str, str], float]]:
    n = record["N"]
    return ({label: c / n for label, c in record["label_counts"].items()},
            {(a, b): c / n for a, b, c in record["pair_counts"]})
