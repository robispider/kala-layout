"""Kala keyboards: the exported files pass Kala's import checks, every label
sits on its key, Kala Goti types what the research typing machine types and
Kala Jhor leaves its vowel rule to Kala."""
import itertools
import json
import unittest

from bangla_dh.bangla.inventory import HASANT
from bangla_dh.bangla.styles import Style
from bangla_dh.kala_export import (KalaFixedEngine, kala_import_problems, kala_layers, key_map_problems, presses_of,
                                   research_layout, sequences, type_word, typing_rule)
from bangla_dh.paths import kala_path
from bangla_dh.search.problem import load_problem

PROBLEM = load_problem()
ALPHABET = json.loads(kala_path("kala/layout/bn/Alphabet.json").read_text(encoding="utf-8"))
STYLES = {name: Style(name) for name in ("A", "D")}


def keyboard(name: str) -> dict:
    data = {"type": "fixed", "version": "1.0", "language": "bn", "name": f"test {name}",
            "layers": kala_layers(research_layout(name, PROBLEM))}
    if sequences(STYLES[name]):
        data["combinations"] = {"sequences": sequences(STYLES[name])}
    data["rules"] = [{"pattern": t, "action": "pass_through"} for t in ("vowel", "digit", "punctuation", "other")]
    data["about"] = {"style": {"code": name, "typingRule": typing_rule(STYLES[name])}}
    return data


class KalaExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {name: keyboard(name) for name in STYLES}
        cls.keys = presses_of(research_layout("A", PROBLEM))
        cls.engine = KalaFixedEngine(cls.files["A"], ALPHABET)

    def type(self, labels) -> str:
        return type_word(self.engine, [self.keys[label] for label in labels])

    def test_files_pass_kala_import_checks(self):
        for name, data in self.files.items():
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.assertEqual(kala_import_problems(raw), [], name)
        self.assertIn("unsupported fields", " ".join(kala_import_problems(b'{"type":"fixed","x":1}')))
        bad = dict(self.files["A"], about="text")
        self.assertIn("about is not an object", kala_import_problems(json.dumps(bad).encode()))

    def test_every_key_is_mapped_once_and_nukta_letters_are_precomposed(self):
        for name, data in self.files.items():
            self.assertEqual(key_map_problems(research_layout(name, PROBLEM), data), [], name)
            normal, shift = data["layers"]["normal"], data["layers"]["shift"]
            self.assertEqual(normal["32"], " ")
            self.assertEqual([normal[str(48 + d)] for d in range(10)], list("০১২৩৪৫৬৭৮৯"))
            outputs = [v for layer in (normal, shift) for k, v in layer.items() if 65 <= int(k) <= 90]
            self.assertEqual(len(set(outputs)), 52)
            self.assertTrue({"ড়", "ঢ়", "য়"} <= set(outputs), name)

    def test_d_has_no_sequences_and_describes_its_rule(self):
        self.assertNotIn("combinations", self.files["D"])
        self.assertEqual(typing_rule(STYLES["D"])["id"], "context-vowel")
        self.assertEqual(self.files["A"]["combinations"]["sequences"],
                         {HASANT + s: v for s, v in STYLES["A"].vowel_of.items()})

    def test_style_a_types_like_unijoy(self):
        self.assertEqual(self.type(["ব", "ি"]), "বি")
        self.assertEqual(self.type([HASANT, "ি"]), "ই")
        self.assertEqual(self.type(["ব", HASANT, "ি"]), "বই")
        self.assertEqual(self.type(["ক", HASANT, "ষ"]), "ক্ষ")

    def test_a_engine_matches_research_decoder_on_all_short_sequences(self):
        pool = ["ক", "য়", HASANT, "ং", "ঁ", "অ", "।", "ি", "া"]
        for n in range(1, 5):
            for seq in itertools.product(pool, repeat=n):
                self.assertEqual(self.type(seq), STYLES["A"].decode(seq).replace("য়", "য়"), " ".join(seq))

    def test_a_research_encoder_keystrokes_type_each_word(self):
        for word in ["আমি", "বাংলায়", "গান", "গাই", "তিনিই", "বউ", "উৎসব", "আকাশ", "ঐতিহ্য", "ক্ষেত্রে"]:
            self.assertEqual(self.type(STYLES["A"].encode(word)).replace("য়", "য়"), word)


if __name__ == "__main__":
    unittest.main()
