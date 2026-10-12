"""Phase 2: inventory, normalization, typing grammar, frequency counting, the
J0 scorer, the independent verifier and the Kala write guard."""
import gzip
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from bangla_dh.bangla.grammar import Action, Escape, UnitSet, segment, single_action_keymap
from bangla_dh.bangla.inventory import INVENTORY_FILE, build_inventory, classify_cluster, load_inventory
from bangla_dh.bangla.normalize import normalize_line
from bangla_dh.colemak.keyboard import load_layout
from bangla_dh.colemak.frequency import load_frequency_file
from bangla_dh.colemak.analysis import perform_analysis
from bangla_dh.corpus.frequency import unit_counts
from bangla_dh.corpus.wikitext import paragraphs
from bangla_dh.paths import PROJECT_ROOT, WriteOutsideProject, output_path
from bangla_dh.reference import resource
from bangla_dh.scoring.j0 import score_tokens, score_units
from bangla_dh.scoring.layouts import english_model_and_assignment, load_english_frequencies, unijoy_keymap
from bangla_dh.scoring.model import ANSI_GRID, KeyModel
from bangla_dh.scoring.verify import verify_j0

RRA = "ড়"  # ড় in NFC


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory, cls.report = build_inventory()

    def test_counts_and_frozen_file(self):
        self.assertEqual(self.inventory["counts"]["placed"], 85)
        self.assertEqual(self.inventory["counts"]["tracked"], 2)
        self.assertEqual(self.inventory["symbol_list_sha256"], load_inventory(INVENTORY_FILE)["symbol_list_sha256"])

    def test_nukta_consonants_are_nfc_two_code_points(self):
        symbols = {e["symbol"]: e for e in self.inventory["symbols"]}
        for unit in (RRA, "ঢ়", "য়"):
            self.assertIn(unit, symbols)
            self.assertEqual(len(symbols[unit]["code_points"]), 2)
        self.assertNotIn("ড়", symbols)

    def test_kala_conjunct_problems_detected(self):
        problems = self.report["conjuncts"]["data/bn/Alphabet.json#conjuncts"]["problems"]
        reasons = {p["entry"]: p["problem"] for p in problems}
        self.assertIn("non-Bengali", reasons["ধ्ष"])
        self.assertIn("রল", reasons)
        self.assertEqual(classify_cluster("স্ত্র"), "cluster")


class NormalizationAndGrammarTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_line("“পড়া”  এবং৷ "), "\"প" + RRA + "া\" এবং।")

    def test_segment(self):
        self.assertEqual(segment("প" + RRA + "া"), ["প", RRA, "া"])
        self.assertEqual(segment("ক্ত"), ["ক", "্", "ত"])

    def test_unijoy_typing(self):
        keymap = unijoy_keymap(KeyModel.from_grid())
        self.assertEqual([str(s) for s in keymap.encode("আমি")], ["G", "F", "M", "D"])
        self.assertEqual([str(s) for s in keymap.encode("ক্র")], ["J", "Z"])
        for word in ("আমি", "রাষ্ট্র", "কর্ম", "র‍্যাব", "প্রত্যয়", "উৎসর্গ", "ঐতিহ্য", "পড়া"):
            with self.subTest(word=word):
                self.assertEqual(keymap.round_trip(normalize_line(word)), (True, 0))
        # Invalid hasant + vowel sign (a legacy-conversion artifact) must not turn into ঈ.
        self.assertEqual(keymap.round_trip("পাশ্বর্ীয়"), (True, 1))
        ok, escapes = keymap.round_trip("ঽ")
        self.assertTrue(ok)
        self.assertEqual(escapes, 1)
        self.assertIsInstance(keymap.encode("ঽ")[0], Escape)


class ScorerTests(unittest.TestCase):
    model = KeyModel.from_grid()

    def test_penalty_table(self):
        m = self.model
        self.assertEqual(m.penalty_keys("F", "V", False), ("same_finger", 3.0))  # L3, rows 2-3
        self.assertEqual(m.penalty_keys("F", "F", False), ("same_finger", 2.5))  # base vs Shift on one key
        self.assertEqual(m.penalty_keys("F", "F", True), ("none", 0.0))
        self.assertEqual(m.penalty_keys("D", "F", False), ("neighbour_benefit", -0.2))  # middle-index
        self.assertEqual(m.penalty_keys("A", "S", False), ("neighbour_penalty", 0.5))  # pinky-ring
        self.assertEqual(m.penalty_keys("F", "J", False), ("none", 0.0))  # other hand

    def test_penalties_match_vendored_config(self):
        layout = load_layout(resource("layout_full/colemak_dh.keyb"), resource("config/effort_ergonomic_config.dat"))
        self.assertEqual(list(self.model.same_finger), layout.penalty_same_finger)
        self.assertEqual([list(r) for r in self.model.neighbour], layout.penalty_neighbour_finger[:3])

    def test_matches_analyzer_port_on_english(self):
        layout = load_layout(resource("layout_full/colemak_dh.keyb"), resource("config/effort_ergonomic_config.dat"))
        chars, bigrams = load_frequency_file(layout.alphabet(), resource("freq/en_books.freq"))
        port = perform_analysis(layout, chars, bigrams).effort_totals()
        model, assignment = english_model_and_assignment(layout)
        u, v = load_english_frequencies(resource("freq/en_books.freq"), layout.alphabet())
        self.assertAlmostEqual(score_units(assignment, u, v, model)["J0"], port["total"], delta=1e-6)

    def test_three_routes_agree(self):
        units = UnitSet.from_inventory()
        assignment = {"ক": ("J", "base"), "া": ("F", "base"), "র": ("V", "base"), "ি": ("D", "base"),
                      "ম": ("M", "base"), "্": ("G", "base"), "ত": ("K", "base"), RRA: ("F", "shift")}
        paragraphs_ = ["কাম রাক্ত", "মি" + RRA + "া কারা", "করা x মা"]
        tokens = Counter(t for p in paragraphs_ for t in p.split(" "))
        first = Counter(p.split(" ")[0] for p in paragraphs_)
        last = Counter(p.split(" ")[-1] for p in paragraphs_)
        tables = unit_counts(tokens, first, last, len(paragraphs_), units)
        n = sum(tables["unigrams"].values())
        u = {k: c / n for k, c in tables["unigrams"].items()}
        v = {k: c / n for k, c in tables["bigrams"].items()}
        self.assertEqual(tables["oov"], Counter({"x": 1}))
        self.assertEqual(tables["unigrams"][" "], 4)  # 7 tokens in 3 paragraphs
        actions = {unit: Action(k, layer, unit) for unit, (k, layer) in assignment.items()}
        by_tables = score_units(actions, u, v, self.model)["J0"]
        keymap = single_action_keymap("toy", assignment, effort=self.model.effort)
        by_tokens = score_tokens(keymap, tokens.items(), n, self.model)["J0"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "toy.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                stream.write(json.dumps({"id": "1", "paragraphs": paragraphs_}, ensure_ascii=False) + "\n")
            verified = verify_j0([path], {s: k for s, (k, _) in assignment.items()}, INVENTORY_FILE, ANSI_GRID)
        self.assertEqual(verified["N"], n)
        self.assertAlmostEqual(by_tables, by_tokens, places=12)
        self.assertAlmostEqual(by_tables, verified["J0"], places=12)


class CorpusTests(unittest.TestCase):
    def test_wikitext_cleaning(self):
        text = ("{{তথ্যছক|নাম=ক}}\n'''বাংলা''' একটি [[ইন্দো-আর্য ভাষা|ভাষা]]<ref>উৎস</ref>, যা "
                "[[দক্ষিণ এশিয়া]]য় প্রচলিত।\n== ইতিহাস ==\n* তালিকা এক দুই তিন\n"
                "[[বিষয়শ্রেণী:ভাষা]]\nEnglish words only in this line here.")
        self.assertEqual(paragraphs(text, prose=False),
                         ["বাংলা একটি ভাষা, যা দক্ষিণ এশিয়ায় প্রচলিত।"])


class WriteGuardTests(unittest.TestCase):
    def test_refuses_paths_outside_the_project(self):
        for target in (PROJECT_ROOT.parent / "x.json", PROJECT_ROOT.parent / "elsewhere" / "x"):
            with self.subTest(target=target), self.assertRaises(WriteOutsideProject):
                output_path(target)


if __name__ == "__main__":
    unittest.main()
