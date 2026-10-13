"""Read the current season; retain provenance and validate every candidate map."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

from ..paths import PROJECT_ROOT, gzip_text_lines
from ..phase3 import problem_fixed
from ..search.problem import load_problem, parse_slot

TRAIN = ("bnwiki/train", "newspaper/train")
HELDOUT = ("bnwiki/heldout", "newspaper/heldout", "bard-novel/heldout")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frequency_path(style, corpus):
    if corpus not in (*TRAIN, *HELDOUT):
        raise ValueError("unknown experimental corpus")
    directory = "phase3" if corpus.startswith("bnwiki/") else "phase3-crosscheck"
    return PROJECT_ROOT / "results" / directory / "frequencies" / f"{style}-{corpus.replace('/', '-')}.json"


def unit_path(corpus):
    directory = "phase2" if corpus.startswith("bnwiki/") else "phase3-crosscheck"
    return PROJECT_ROOT / "results" / directory / "frequencies" / f"{corpus.replace('/', '-')}.json"


def token_rows(path):
    for line in gzip_text_lines(path):
        if line and not line.startswith("# "):
            token, count, first, last = line.split("\t")
            yield token, int(count), int(first), int(last)


@dataclass
class Candidate:
    id: str
    style: str
    layout: dict
    names: list[str] = field(default_factory=list)
    origins: list[dict] = field(default_factory=list)

    def assignment(self):
        return {**self.layout, **problem_fixed(load_problem())}

    def json(self):
        return {"id": self.id, "style": self.style, "names": self.names,
                "layout": {k: "/".join(v) for k, v in self.layout.items()}, "origins": self.origins}


def validate_layout(style, layout):
    problem = load_problem()
    if style not in ("A", "D"):
        raise ValueError("experimental candidates must preserve A or D grammar")
    if set(layout) != set(problem["styles"][style]["searched_symbols"]):
        raise ValueError("candidate does not preserve the searched inventory")
    if len(set(layout.values())) != 52 or set(layout.values()) != {parse_slot(s) for s in problem["slots"]}:
        raise ValueError("candidate is not a bijection of the frozen 52 slots")
    return layout


def load_candidates(include_runs=False):
    found = {}
    inputs = []

    def add(style, layout, origin, name=None):
        layout = validate_layout(style, layout)
        canonical = json.dumps([style, sorted((k, list(v)) for k, v in layout.items())], ensure_ascii=False)
        cid = style + "-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]
        if cid in found and found[cid].layout != layout:
            raise ValueError("candidate identity collision")
        c = found.setdefault(cid, Candidate(cid, style, layout))
        c.origins.append(origin)
        if name and name not in c.names:
            c.names.append(name)

    for style in ("A", "D"):
        path = PROJECT_ROOT / "results" / "mix-search" / "search" / f"{style}.json"
        inputs.append(path)
        data = read_json(path)
        slots = [parse_slot(s) for s in data["slots"]]
        add(style, {k: parse_slot(v) for k, v in data["best"]["layout"].items()},
            {"file": path.relative_to(PROJECT_ROOT).as_posix(), "kind": "published", "seed": data["best"]["seed"]},
            "Kala Goti" if style == "A" else "Kala Jhor")
        if not include_runs:
            continue
        for kind in ("runs", "polish", "confirmation"):
            for run in data[kind]:
                labels = run["layout"]
                if len(labels) != len(slots):
                    raise ValueError("invalid stored run layout length")
                add(style, dict(zip(labels, slots)),
                    {"file": path.relative_to(PROJECT_ROOT).as_posix(), "kind": kind,
                     "seed": run["seed"], "origin": run.get("origin")})
        for phase in ("phase3", "phase3-crosscheck"):
            earlier = PROJECT_ROOT / "results" / phase / "search" / f"{style}.json"
            inputs.append(earlier)
            record = read_json(earlier)
            add(style, {k: parse_slot(v) for k, v in record["best"]["layout"].items()},
                {"file": earlier.relative_to(PROJECT_ROOT).as_posix(), "kind": "earlier"}, phase + " " + style)
    return sorted(found.values(), key=lambda c: c.id), inputs
