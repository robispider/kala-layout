"""Phase 3: problem file, vowel-entry styles, J1, the search's delta scoring
and the independent style verifier."""
import gzip
import json
import random
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from bangla_dh.bangla.grammar import Action, Escape
from bangla_dh.bangla.inventory import INVENTORY_FILE
from bangla_dh.bangla.normalize import normalize_line
from bangla_dh.bangla.styles import load_styles
from bangla_dh.scoring.j0 import score_units
from bangla_dh.scoring.model import ANSI_GRID, KeyModel
from bangla_dh.scoring.verify import verify_style
from bangla_dh.search import keystrokes
from bangla_dh.search.anneal import Instance, State
from bangla_dh.search.problem import PROBLEM_FILE, build_problem, check_problem, load_problem, parse_slot, slots

STYLES = load_styles()
MODEL = KeyModel.from_grid()
TRICKY = ["আমি বই পড়ি।", "দই, বউ আর কাজ!", "তিনিই এটিই সিইও এএফসি নইই নিইই", "ক্ষমতা ও উৎসর্গ", "র‍্যাব (প্রতিষ্ঠান)",
          "পাশ্বর্ীয় সংস্কৃৃত আআ কাআ", "ঐতিহ্য ঔষধ ঋণ ঊর্ধ্ব ঈদ", "৩০ জন: \"ভালো\" - x.y ঽ ॥ —"]


def labels(steps):
    return [s if isinstance(s, str) else f"<{s.char}>" for s in steps]


class ProblemTests(unittest.TestCase):
    def test_frozen_file_matches_build(self):
        problem = load_problem(PROBLEM_FILE)
        self.assertEqual(problem, build_problem())
        self.assertEqual(check_problem(problem), [])
        self.assertEqual(len(problem["slots"]), 52)
        for style in problem["styles"].values():
            self.assertEqual(len(style["searched_symbols"]), 52)


class StyleTests(unittest.TestCase):
    def test_vowel_entry(self):
        expected = {"A": {"বই": ["ব", "্", "ি"], "আমি": ["্", "া", "ম", "ি"]},
                    "B": {"বই": ["ব", "ি", "ি"], "আমি": ["া", "া", "ম", "ি"]},
                    "C": {"বই": ["ব", "ই"], "আমি": ["আ", "ম", "ই", "ই"]},
                    "D": {"বই": ["ব", "ি", "ি"], "আমি": ["া", "ম", "ি"], "দই": ["দ", "ি", "ি"],
                          "বউ": ["ব", "ু", "ু"], "এই": ["ে", "ি"]}}
        for style, words in expected.items():
            for word, keys in words.items():
                with self.subTest(style=style, word=word):
                    self.assertEqual(labels(STYLES[style].encode(word)), keys)

    def test_collisions_are_escaped_not_mistyped(self):
        self.assertEqual(labels(STYLES["B"].encode("ইি")), ["ি", "ি", "<ি>"])
        self.assertEqual(labels(STYLES["D"].encode("ইি")), ["ি", "<ি>"])
        self.assertEqual(labels(STYLES["C"].encode("আআ")), ["আ", "<আ>"])
        self.assertEqual(labels(STYLES["A"].encode("র্ী")), ["র", "্", "<ী>"])
        self.assertEqual(labels(STYLES["C"].encode("কাআ")), ["ক", "আ", "আ", "আ"])

    def test_repeated_presses_pair_from_the_end(self):
        """B and D: a run of one vowel key is single + pairs (odd) or pairs (even)."""
        for style in ("B", "D"):
            machine = STYLES[style]
            with self.subTest(style=style):
                self.assertEqual(labels(machine.encode("তিনিই")), ["ত", "ি", "ন", "ি", "ি", "ি"])
                self.assertEqual(labels(machine.encode("সিইও"))[:4], ["স", "ি", "ি", "ি"])
                for presses, typed in ((1, "নি"), (2, "নই"), (3, "নিই"), (4, "নইই"), (5, "নিইই")):
                    self.assertEqual(machine.decode(["ন"] + ["ি"] * presses), typed)
                self.assertEqual(machine.decode(["ন", "ি", "ি", "ি", "ক", "ি"]), "নিইকি")  # another key ends the run
        for presses, typed in ((1, "ি"), (2, "ই"), (3, "িই"), (4, "ইই")):
            self.assertEqual(STYLES["B"].decode(["ি"] * presses), typed)
        self.assertEqual(STYLES["D"].decode(["ি"] * 3), "ইইই")  # no sign context: no pairing
        self.assertEqual(labels(STYLES["D"].encode("ইই")), ["ি", "ি"])

    def test_round_trip(self):
        for name, style in STYLES.items():
            for text in TRICKY:
                with self.subTest(style=name, text=text):
                    ok, _ = style.round_trip(normalize_line(text))
                    self.assertTrue(ok)

    def test_decoder_does_not_see_the_text(self):
        self.assertEqual(STYLES["D"].decode(["ব", "ি", "ি", "ি"]), "বিই")
        self.assertEqual(STYLES["D"].decode(["া", "ম", "ি"]), "আমি")
        self.assertEqual(STYLES["C"].decode(["ক", "ও", "ও"]), "কো")
        self.assertEqual(STYLES["A"].decode(["ক", "্", "্", "া"]), "ক্আ")


class J1Tests(unittest.TestCase):
    def test_modifier_effort(self):
        self.assertEqual(MODEL.modifier_effort("F", "base"), 0.0)
        self.assertEqual(MODEL.modifier_effort("F", "shift"), MODEL.effort("RSHIFT"))  # left hand → RShift
        self.assertEqual(MODEL.modifier_effort("J", "shift"), MODEL.effort("LSHIFT"))
        self.assertEqual(MODEL.modifier_effort("B", "shift"), MODEL.effort("LSHIFT"))  # B: right index in the model grid
        self.assertIsNone(MODEL.modifier_effort("F", "altgr"))
        self.assertAlmostEqual(MODEL.effort("RSHIFT"), 4.610, places=3)
        self.assertAlmostEqual(MODEL.effort("LSHIFT"), 3.308, places=3)


def toy_tables(style: str) -> dict:
    tokens, first, last = Counter(), Counter(), Counter()
    for paragraph in TRICKY:
        parts = normalize_line(paragraph).split(" ")
        tokens.update(parts)
        first[parts[0]] += 1
        last[parts[-1]] += 1
    keystrokes._init(style)
    part = keystrokes.count_batch([(t, c, first[t], last[t]) for t, c in tokens.items()])
    n = part["units"] + sum(tokens.values()) - len(TRICKY)
    u = {k: c / n for k, c in part["labels"].items()}
    v = {k: c / n for k, c in part["pairs"].items()}
    return {"N": n, "u": u, "v": v, "keystrokes": part["keystrokes"],
            "escaped": sum(part["escaped_units"].values())}


class SearchAndVerifierTests(unittest.TestCase):
    problem = load_problem()

    def random_layout(self, style: str, seed: int) -> dict:
        targets = slots()
        random.Random(seed).shuffle(targets)
        return dict(zip(self.problem["styles"][style]["searched_symbols"], targets))

    def test_verifier_matches_tables_for_every_style(self):
        fixed = {k: parse_slot(v) for k, v in self.problem["fixed"].items()}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "toy.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                paragraphs = [normalize_line(p) for p in TRICKY]
                stream.write(json.dumps({"id": "1", "paragraphs": paragraphs}, ensure_ascii=False) + "\n")
            for style in STYLES:
                with self.subTest(style=style):
                    tables = toy_tables(style)
                    layout = {**self.random_layout(style, 5), **fixed}
                    actions = {label: Action(k, layer, label) for label, (k, layer) in layout.items()}
                    by_tables = score_units(actions, tables["u"], tables["v"], MODEL)
                    verified = verify_style([path], style, {l: f"{k}/{layer}" for l, (k, layer) in layout.items()},
                                            INVENTORY_FILE, ANSI_GRID)
                    self.assertEqual(verified["N"], tables["N"])
                    self.assertEqual(verified["keystrokes_excluding_space"], tables["keystrokes"])
                    self.assertEqual(verified["escaped_units"], tables["escaped"])
                    self.assertAlmostEqual(verified["J1"], by_tables["J1"], places=12)
                    self.assertAlmostEqual(verified["J0"], by_tables["J0"], places=12)

    def test_instance_score_and_deltas(self):
        tables = toy_tables("D")
        fixed = {k: parse_slot(v) for k, v in self.problem["fixed"].items()}
        for objective in ("J0", "J1"):
            inst = Instance(self.problem["styles"]["D"]["searched_symbols"], slots(), fixed, tables["u"],
                            tables["v"], MODEL, objective)
            layout = self.random_layout("D", 9)
            perm = inst.perm_of(layout)
            actions = {label: Action(k, layer, label) for label, (k, layer) in {**layout, **fixed}.items()}
            self.assertAlmostEqual(inst.score(perm), score_units(actions, tables["u"], tables["v"], MODEL)[objective],
                                   places=12)
            state = State(inst, perm)
            rng = random.Random(3)
            for _ in range(300):
                i, j = rng.sample(range(inst.n), 2)
                before = inst.score(state.perm)
                d = state.delta(i, j)
                state.swap(i, j, d)
                self.assertAlmostEqual(inst.score(state.perm) - before, d, places=12)
            marked, marked_score = list(state.perm), state.score
            state.log = []
            for _ in range(20):
                i, j = rng.sample(range(inst.n), 2)
                state.swap(i, j, state.delta(i, j))
            state.undo()
            self.assertEqual(state.perm, marked)
            self.assertAlmostEqual(state.score, marked_score, places=12)
            state.descend()
            self.assertTrue(all(state.delta(i, j) >= -1e-12 for i in range(inst.n) for j in range(i + 1, inst.n)))
            self.assertAlmostEqual(state.score, inst.score(state.perm), places=10)


if __name__ == "__main__":
    unittest.main()
