"""Research-source pair diagnostic. Unsupported conditions are never filled in."""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

from ..paths import DATA
from ..reference import sha256_file
from ..scoring.model import ANSI_TRADITIONAL_GRID, KeyModel
from .actions import SPACE_ACTION, ActionTables

SOURCE = DATA / "evaluators" / "engram-pair-v1"


class PairPreferences:
    def __init__(self, directory: Path = SOURCE):
        self.directory = Path(directory)
        self.lock = json.loads((self.directory / "source-lock.json").read_text(encoding="utf-8"))
        for f in self.lock["files"]:
            target = (self.directory / f["file"]).resolve()
            if not target.is_relative_to(self.directory.resolve()):
                raise ValueError("source file outside pinned directory")
            if sha256_file(target) != f["sha256"]:
                raise ValueError("preference source hash mismatch")
        self.scores = {}
        self.uncertainty = {}
        with (self.directory / "pair-scores.csv").open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["key_pair", "comfort_score", "uncertainty"]:
                raise ValueError("unexpected preference table schema")
            for row in reader:
                pair = row["key_pair"]
                value, uncertainty = float(row["comfort_score"]), float(row["uncertainty"])
                if len(pair) != 2 or pair in self.scores:
                    raise ValueError("invalid or duplicate preference pair")
                if not math.isfinite(value) or not math.isfinite(uncertainty) or uncertainty < 0:
                    raise ValueError("invalid preference score or uncertainty")
                self.scores[pair] = value
                self.uncertainty[pair] = uncertainty
        if len(self.scores) != self.lock["expected_pairs"]:
            raise ValueError("preference table row count mismatch")
        self.traditional = KeyModel.from_grid(ANSI_TRADITIONAL_GRID)

    def evidence(self):
        benchmark = json.loads((self.directory / "lookup-benchmark.json").read_text(encoding="utf-8"))
        total = sum(c for _, c in benchmark["pairs"])
        actual = math.fsum(self.scores[p] * c for p, c in benchmark["pairs"]) / total
        if not math.isclose(actual, float(benchmark["weighted_mean"]), rel_tol=0, abs_tol=1e-14):
            raise ValueError("pinned source lookup benchmark failed")
        return {"model_id": self.lock["model_id"], "source_hashes_verified": True,
                "lookup_benchmark_pass": True, "lookup_benchmark_actual": actual,
                "heldout_prediction_reproduced": False,
                "bangla_human_validation": False, "full_layout_admitted": False,
                "stage2_comfort_selection": "withheld",
                "status": "partial_supported_pair_diagnostic",
                "reason": "Missing key/layer/hand conditions and independent predictive validation.",
                "source": self.lock}

    def score(self, tables: ActionTables, model: KeyModel):
        tables.validate()
        reasons = Counter()
        supported = total = 0
        contributions = []
        for (a, b), count in tables.pairs.items():
            if SPACE_ACTION in (a, b):
                continue
            total += count
            if a[1] != "base" or b[1] != "base":
                reasons["unsupported_layer"] += count
            elif a[0] + b[0] not in self.scores:
                reasons["no_source_pair"] += count
            elif any(model.keys[k].finger != self.traditional.keys[k].finger for k in (a[0], b[0])):
                reasons["different_fingering"] += count
            else:
                supported += count
                contributions.append(count * self.scores[a[0] + b[0]])
        return {"status": "partial_supported_pair_diagnostic",
                "full_layout_score": None, "ranking_allowed": False,
                "conditional_pair_preference": math.fsum(contributions) / supported if supported else None,
                "direction": "higher",
                "supported_pair_count": supported, "non_space_pair_count": total,
                "supported_pair_share": supported / total if total else None,
                "unsupported_pair_counts": dict(sorted(reasons.items())),
                "joint_uncertainty": None,
                "warning": "Conditional mean over a layout-dependent subset; not a comparable full-layout comfort score."}
