"""Phase 4: integer model, bounds, exchange certificates, CP-SAT and the cell
LP on small instances that brute force can solve, and the sensitivity model."""
import gzip
import itertools
import json
import random
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

from bangla_dh.bangla.grammar import Action
from bangla_dh.bangla.inventory import INVENTORY_FILE
from bangla_dh.bangla.normalize import normalize_line
from bangla_dh.scoring import sensitivity as sens
from bangla_dh.scoring.j0 import score_units
from bangla_dh.scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from bangla_dh.scoring.verify import verify_style
from bangla_dh.search import bounds, keystrokes
from bangla_dh.search.anneal import Instance
from bangla_dh.search.integer import IntegerInstance, to_int
from bangla_dh.search.problem import load_problem, parse_slot, slots

MODEL = KeyModel.from_grid()
PROBLEM = load_problem()
FIXED = {k: parse_slot(v) for k, v in PROBLEM["fixed"].items()}
TEXT = ["আমি বই পড়ি।", "দই, বউ আর কাজ!", "তিনিই এটিই সিইও এএফসি নইই", "ক্ষমতা ও উৎসর্গ", "র‍্যাব (প্রতিষ্ঠান)",
        "ঐতিহ্য ঔষধ ঋণ ঊর্ধ্ব ঈদ", "৩০ জন: \"ভালো\" - কিছু কথা বলার আছে", "সে বাড়িতে গেল এবং খেলা দেখল"]
SMALL_SLOTS = [("F", "base"), ("F", "shift"), ("G", "base"), ("D", "base"), ("J", "base"), ("K", "base")]


def toy_record(style: str) -> dict:
    tokens, first, last = Counter(), Counter(), Counter()
    for paragraph in TEXT:
        parts = normalize_line(paragraph).split(" ")
        tokens.update(parts)
        first[parts[0]] += 1
        last[parts[-1]] += 1
    keystrokes._init(style)
    part = keystrokes.count_batch([(t, c, first[t], last[t]) for t, c in tokens.items()])
    n = part["units"] + sum(tokens.values()) - len(TEXT)
    return {"N": n, "label_counts": dict(part["labels"]), "keystrokes_excluding_space": part["keystrokes"],
            "pair_counts": [[a, b, c] for (a, b), c in part["pairs"].items()]}


def small_instance(style: str = "D") -> IntegerInstance:
    record = toy_record(style)
    labels = sorted(record["label_counts"], key=lambda k: -record["label_counts"][k])
    labels = [l for l in labels if l in PROBLEM["styles"][style]["searched_symbols"]][:6]
    return IntegerInstance(labels, SMALL_SLOTS, FIXED, record, MODEL)


def brute_force(inst: IntegerInstance) -> int:
    return min(inst.score(list(p)) for p in itertools.permutations(range(inst.n)))


class IntegerModelTests(unittest.TestCase):
    def test_conversion_is_exact_or_refused(self):
        self.assertEqual(to_int(3.024686), 3024686)
        self.assertEqual(to_int(-0.2), -200000)
        with self.assertRaises(ValueError):
            to_int(0.1234567)

    def test_integer_objective_equals_float_objective(self):
        record = toy_record("D")
        labels = PROBLEM["styles"]["D"]["searched_symbols"]
        inst = IntegerInstance(labels, slots(), FIXED, record, MODEL)
        u = {k: c / record["N"] for k, c in record["label_counts"].items()}
        v = {(a, b): c / record["N"] for a, b, c in record["pair_counts"]}
        finst = Instance(labels, slots(), FIXED, u, v, MODEL)
        rng = random.Random(1)
        for _ in range(5):
            perm = list(range(inst.n))
            rng.shuffle(perm)
            self.assertAlmostEqual(float(inst.to_j(inst.score(perm))), finst.score(perm), places=12)
            layout = {**inst.assignment(perm), **FIXED}
            actions = {label: Action(k, layer, label) for label, (k, layer) in layout.items()}
            self.assertAlmostEqual(float(inst.to_j(inst.score(perm))), score_units(actions, u, v, MODEL)["J1"], places=12)

    def test_independent_verifier_equals_integer_objective_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "toy.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                paragraphs = [normalize_line(p) for p in TEXT]
                stream.write(json.dumps({"id": "1", "paragraphs": paragraphs}, ensure_ascii=False) + "\n")
            for style in ("A", "B", "C", "D"):
                with self.subTest(style=style):
                    labels = PROBLEM["styles"][style]["searched_symbols"]
                    inst = IntegerInstance(labels, slots(), FIXED, toy_record(style), MODEL)
                    perm = list(range(inst.n))
                    random.Random(7).shuffle(perm)
                    layout = {label: "/".join(slot) for label, slot in {**inst.assignment(perm), **FIXED}.items()}
                    verified = verify_style([path], style, layout, INVENTORY_FILE, ANSI_GRID)
                    self.assertEqual(Fraction(verified["J1_exact"]), inst.to_j(inst.score(perm)))

    def test_subset_delta_equals_full_rescore(self):
        record = toy_record("B")
        inst = IntegerInstance(PROBLEM["styles"]["B"]["searched_symbols"], slots(), FIXED, record, MODEL)
        rng = random.Random(2)
        perm = list(range(inst.n))
        rng.shuffle(perm)
        G = inst.g_table(perm)
        base = inst.score(perm)
        for k in (2, 3, 4, 5):
            for _ in range(20):
                subset = sorted(rng.sample(range(inst.n), k))
                new = [perm[i] for i in subset]
                rng.shuffle(new)
                trial = list(perm)
                for i, s in zip(subset, new):
                    trial[i] = s
                self.assertEqual(bounds._subset_delta(inst, perm, G, subset, new), inst.score(trial) - base)


class BoundTests(unittest.TestCase):
    def test_hungarian_matches_brute_force(self):
        rng = random.Random(3)
        for n in (1, 3, 6):
            cost = [[rng.randint(-50, 50) for _ in range(n)] for _ in range(n)]
            value, assign = bounds.hungarian(cost)
            best = min(sum(cost[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))
            self.assertEqual(value, best)
            self.assertEqual(sorted(assign), list(range(n)))

    def test_bounds_are_valid_on_a_small_instance(self):
        for style in ("A", "D"):
            inst = small_instance(style)
            optimum = brute_force(inst)
            with self.subTest(style=style):
                self.assertLessEqual(bounds.lb0(inst), optimum)
                gl = bounds.gilmore_lawler(inst)["Z"]
                self.assertLessEqual(gl, optimum)
                self.assertGreaterEqual(gl, bounds.lb0(inst) - abs(optimum) // 10**6)
                enum = bounds.exhaustive_subproblem(inst, list(range(inst.n)), list(range(inst.n)))
                self.assertEqual(enum["Z_min"], optimum)

    def test_exchange_certificate_finds_an_improvement(self):
        inst = small_instance("D")
        perms = sorted(itertools.permutations(range(inst.n)), key=lambda p: inst.score(list(p)))
        best, worst = list(perms[0]), list(perms[-1])
        self.assertTrue(bounds.exchange_certificate(inst, best, inst.n, workers=1)["proven"])
        cert = bounds.exchange_certificate(inst, worst, 2, workers=1)
        self.assertFalse(cert["proven"])


@unittest.skipUnless(__import__("importlib").util.find_spec("ortools"), "OR-Tools not installed")
class SolverTests(unittest.TestCase):
    def test_cpsat_and_cell_lp_on_a_small_instance(self):
        from bangla_dh.search import cpsat
        from bangla_dh.search.lp_bound import CellLP

        for style in ("A", "D"):
            inst = small_instance(style)
            optimum = brute_force(inst)
            with self.subTest(style=style):
                result = cpsat.solve(inst, MODEL, list(range(inst.n)), 30, workers=2)
                self.assertEqual(result["status"], "OPTIMAL")
                self.assertEqual(result["Z"], optimum)
                self.assertEqual(result["best_bound_Z"], optimum)
                lp = CellLP(inst, MODEL)
                solved = lp.solve(60)
                certified = lp.certify(solved["duals_Z"])
                self.assertLessEqual(certified, optimum)
                self.assertGreaterEqual(certified, bounds.lb0(inst))
                self.assertLessEqual(lp.certify([0] * len(lp.rhs)), optimum)  # any multipliers are valid


class SensitivityTests(unittest.TestCase):
    def test_nominal_theta_reproduces_the_frozen_grids(self):
        for fingering, path in (("optimal", ANSI_GRID), ("traditional", ANSI_TRADITIONAL_GRID)):
            frozen = KeyModel.from_grid(path)
            model = sens.theta_model(sens.NOMINAL, fingering)
            for key, k in frozen.keys.items():
                self.assertEqual(model.keys[key].effort, k.effort)
                self.assertEqual((model.keys[key].finger, model.keys[key].row), (k.finger, k.row))

    def test_action_tables_reproduce_j1(self):
        record = toy_record("D")
        targets = slots()
        random.Random(4).shuffle(targets)
        layout = {**dict(zip(PROBLEM["styles"]["D"]["searched_symbols"], targets)), **FIXED}
        u = {k: c / record["N"] for k, c in record["label_counts"].items()}
        v = {(a, b): c / record["N"] for a, b, c in record["pair_counts"]}
        actions = {label: Action(k, layer, label) for label, (k, layer) in layout.items()}
        expected = score_units(actions, u, v, MODEL)["J1"]
        tables = sens.style_actions(record, layout)
        self.assertAlmostEqual(sens.j1(tables, MODEL), expected, places=12)
        doubled = sens.theta_model({**sens.NOMINAL, "lambda_m": 2.0})
        nominal = sens.theta_model(sens.NOMINAL)
        m = score_units(actions, u, v, MODEL)["M"]
        self.assertAlmostEqual(sens.j1(tables, doubled) - sens.j1(tables, nominal), m, places=6)


if __name__ == "__main__":
    unittest.main()
