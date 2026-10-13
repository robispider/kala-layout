"""Bangla adapters around source-derived Dvorak-7 and Engram scoring code.

These are layer-insensitive physical-key mechanics, not full typing comfort.
Missing keys remain missing; fixed-denominator bounds retain their mass.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import csv
import importlib.util
import itertools

from ..paths import PROJECT_ROOT
from ..reference import sha256_file
from ..scoring.model import ANSI_GRID, KeyModel
from .actions import SPACE_ACTION
from .inputs import read_json
from .mechanics_sources import SOURCE, PORTS, GENERATORS, COMMIT, extract

AVG4 = ("row_separation", "same_row", "same_finger", "outside")
METRICS = ("dvorak7", "engram_avg4")


def verify_sources():
    lock = read_json(SOURCE / "source-lock.json")
    if lock["commit"] != COMMIT:
        raise ValueError("unexpected mechanics source commit")
    for entry in lock["files"]:
        if sha256_file(SOURCE / entry["file"]) != entry["sha256"]:
            raise ValueError("mechanics source hash mismatch: " + entry["file"])
    for name, path in GENERATORS.items():
        expected = extract((SOURCE / "upstream" / path).read_text(encoding="utf-8"), path)
        if (PORTS / (name + ".py")).read_text(encoding="utf-8") != expected:
            raise ValueError("source-derived scoring port differs: " + name)
    return lock


def _load(path):
    spec = importlib.util.spec_from_file_location("mechanics_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Mechanics:
    def __init__(self, scenario="traditional"):
        if scenario not in ("traditional", "model-optimal"):
            raise ValueError("unknown mechanics fingering")
        self.scenario = scenario
        self.modules = {name: _load(PORTS / (name + ".py")) for name in GENERATORS}
        if scenario == "model-optimal":
            model = KeyModel.from_grid(ANSI_GRID)
            for module in self.modules.values():
                for key, info in list(module.QWERTY_LAYOUT.items()):
                    physical = model.keys[key]
                    hand = "L" if physical.finger <= 4 else "R"
                    finger = physical.finger + 1 if hand == "L" else 10 - physical.finger
                    if len(info) == 4:
                        module.QWERTY_LAYOUT[key] = (info[0], finger, hand, info[-1])
                    else:
                        module.QWERTY_LAYOUT[key] = (info[0], info[1], finger, hand, info[-1])
                # Retain the source inside/outside key set; assign its keys to
                # the new finger. No previously outside key becomes inside.
                inside = {key for fingers in module.FINGER_COLUMNS.values() for keys in fingers.values() for key in keys}
                columns = {hand: {f: [] for f in range(1, 5)} for hand in ("L", "R")}
                for key in sorted(inside):
                    info = module.QWERTY_LAYOUT[key]
                    finger, hand = info[-3:-1]
                    columns[hand][finger].append(key)
                module.FINGER_COLUMNS = columns
        self.supported_keys = set.intersection(*(set(m.QWERTY_LAYOUT) for m in self.modules.values()))

    @lru_cache(maxsize=None)
    def pair(self, a, b):
        if a not in self.supported_keys or b not in self.supported_keys:
            return None
        d = self.modules["dvorak7"].score_bigram_dvorak7(a + b)
        e = self.modules["engram"].score_bigram(a + b)
        return {"dvorak7": sum(d.values()) / 7,
                "engram_avg4": sum(e[c] for c in AVG4) / 4,
                **{"dvorak7_" + k: v for k, v in d.items()},
                **{"engram_" + k: v for k, v in e.items()}}

    @lru_cache(maxsize=None)
    def triple(self, a, b, c):
        if any(k not in self.supported_keys for k in (a, b, c)):
            return None
        return self.modules["engram_triples"].score_trigram(a + b + c)["order"]

    def score(self, tables):
        tables.validate()
        total = covered = shifted = 0
        sums = Counter(dict.fromkeys(self.pair("F", "J"), 0.0))
        missing = Counter()
        contributions = []
        for (a, b), count in sorted(tables.pairs.items()):
            if SPACE_ACTION in (a, b):
                continue
            total += count
            shifted += count if "shift" in (a[1], b[1]) else 0
            values = self.pair(a[0], b[0]) if "altgr" not in (a[1], b[1]) else None
            if values is None:
                missing[a[0] + "/" + a[1] + " → " + b[0] + "/" + b[1]] += count
                continue
            covered += count
            for metric, value in values.items():
                if not 0 <= value <= 1:
                    raise ValueError("upstream mechanics value outside declared 0..1 range")
                sums[metric] += count * value
            contributions.append({"from": list(a), "to": list(b), "count": count})
        # Use the final denominator, not the running one.
        for row in contributions:
            values = self.pair(row["from"][0], row["to"][0])
            for metric in METRICS:
                row[metric + "_deficit"] = row["count"] * (1 - values[metric]) / total if total else 0
        bounds = {metric: {"lower": sums[metric] / total,
                           "upper": (sums[metric] + total - covered) / total}
                  for metric in sums} if total else {}
        return {"scope": "non-space physical-key transitions; layers projected; modifiers excluded",
                "scenario": self.scenario, "score_direction": "higher", "pair_count": total,
                "supported_pair_count": covered, "pair_coverage": covered / total if total else None,
                "shift_involving_pair_count": shifted, "missing_pairs": dict(missing),
                "conditional_means": {m: s / covered for m, s in sums.items()} if covered else {},
                "bounds": bounds, "complete_domain": bool(total and covered == total),
                "whole_typing_comfort": False,
                "top_deficits": {m: sorted(contributions, key=lambda r: (-r[m + "_deficit"], r["from"], r["to"]))[:8]
                                 for m in METRICS}}

    def score_triples(self, triples):
        total = sum(triples.values())
        covered = 0
        value = 0.0
        missing = Counter()
        for actions, count in sorted(triples.items()):
            if len(actions) != 3 or not isinstance(count, int) or count < 0 or SPACE_ACTION in actions:
                raise ValueError("invalid within-token action triple")
            score = self.triple(*(a[0] for a in actions)) if all(a[1] != "altgr" for a in actions) else None
            if score is None:
                missing[" → ".join(a[0] + "/" + a[1] for a in actions)] += count
            else:
                value += score * count
                covered += count
        return {"scope": "within-token physical-key triples; layers projected; modifiers excluded",
                "triple_count": total, "supported_triple_count": covered,
                "coverage": covered / total if total else None,
                "conditional_mean": value / covered if covered else None,
                "bounds": {"lower": value / total, "upper": (value + total - covered) / total} if total else None,
                "missing_triples": dict(missing), "complete_domain": bool(total and total == covered)}


@lru_cache(maxsize=2)
def evaluator(scenario="traditional"):
    verify_sources()
    return Mechanics(scenario)


def audit():
    """Exhaustively compare ports with original code and every distributed row."""
    lock = verify_sources()
    port = Mechanics()
    originals = {name: _load(SOURCE / "upstream" / path) for name, path in GENERATORS.items()}
    keys = originals["engram"].get_all_qwerty_keys()
    pair_count = 0
    for a, b in itertools.product(sorted(port.supported_keys), repeat=2):
        expected_d = originals["dvorak7"].score_bigram_dvorak7(a + b)
        expected_e = originals["engram"].score_bigram(a + b)
        actual = port.pair(a, b)
        if any(actual["dvorak7_" + c] != v for c, v in expected_d.items()) or any(
            actual["engram_" + c] != v for c, v in expected_e.items()
        ):
            raise ValueError("pair source-fidelity failure: " + a + b)
        pair_count += 1
    triple_count = 0
    for abc in itertools.product(sorted(port.supported_keys), repeat=3):
        if port.triple(*abc) != originals["engram_triples"].score_trigram("".join(abc))["order"]:
            raise ValueError("triple source-fidelity failure")
        triple_count += 1
    distributed_rows = 0
    max_error = 0.0
    for entry in lock["files"]:
        if not entry["file"].endswith(".csv"):
            continue
        with (SOURCE / entry["file"]).open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        expected_count = len(keys) ** (3 if "key_triple" in rows[0] else 2)
        if len(rows) != expected_count or len({row.get("key_pair", row.get("key_triple")) for row in rows}) != expected_count:
            raise ValueError("distributed table coverage mismatch")
        for row in rows:
            if "key_triple" in row:
                actual = port.triple(*row["key_triple"])
                column = "engram_order"
            else:
                column = next(c for c in row if c != "key_pair")
                values = port.pair(*row["key_pair"])
                actual = values["engram_avg4" if column == "engram_avg4_score" else
                                "dvorak7" if column == "dvorak7_score" else column]
                if column == "dvorak7_score":
                    actual *= 7
            error = abs(actual - float(row[column]))
            max_error = max(max_error, error)
            if error > 1e-6:
                raise ValueError(f"distributed table mismatch: {entry['file']} {row}")
            distributed_rows += 1
    return {"source_commit": lock["commit"], "source_hashes_pass": True,
            "port_extraction_pass": True, "pair_function_cases": pair_count,
            "triple_function_cases": triple_count, "distributed_table_rows": distributed_rows,
            "distributed_triple_domain": len(keys) ** 3,
            "distributed_table_max_absolute_error": max_error, "tolerance": 1e-6,
            "engram_formula": lock["engram_pair_formula"], "composite_warning": lock["composite_warning"],
            "fidelity_scope": "unmodified traditional ANSI; model-optimal is an explicitly adapted sensitivity scenario",
            "human_validation": False}
