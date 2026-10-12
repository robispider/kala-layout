"""Phase 3 cross-check: news-corpus cleaning and the baseline registry."""
import json
import tempfile
import unittest
from pathlib import Path

from bangla_dh.crosscheck import _clean, sentence_digests
from bangla_dh.bangla.grammar import Action
from bangla_dh.scoring import avro_fixed, baselines
from bangla_dh.scoring.layouts import unijoy_keymap
from bangla_dh.scoring.model import KeyModel

MODEL = KeyModel.from_grid()


def clean(paragraphs, repair=True):
    return _clean((json.dumps({"id": 7, "paragraphs": paragraphs}, ensure_ascii=False), repair))


class CleaningTest(unittest.TestCase):
    def test_glued_sentence_marks_get_a_space(self):
        _, _, paragraphs, repairs, _ = clean(["শ্রমিকেরা।সফিপুর যান? না!হ্যাঁ। ঠিক।"])
        self.assertEqual(paragraphs, ["শ্রমিকেরা। সফিপুর যান? না! হ্যাঁ। ঠিক।"])
        self.assertEqual(repairs, 2)

    def test_repair_is_optional_and_leaves_latin_alone(self):
        _, _, paragraphs, repairs, _ = clean(["এক।দুই", "a.b।c"], repair=False)
        self.assertEqual((paragraphs, repairs), (["এক।দুই", "a.b।c"], 0))
        _, _, paragraphs, repairs, _ = clean(["a!b।c"])
        self.assertEqual((paragraphs, repairs), (["a!b।c"], 0))

    def test_normalization_and_paragraph_split(self):
        document_id, _, paragraphs, _, _ = clean(["  ক​খ  \nগ ঘ ", ""])
        self.assertEqual((document_id, paragraphs), ("7", ["কখ", "গ ঘ"]))

    def test_sentence_digests_skip_short_pieces(self):
        long = "এটি একটি যথেষ্ট দীর্ঘ বাক্য।"
        self.assertEqual(len(sentence_digests([f"ছোট। {long} {long}"])), 2)
        self.assertEqual(sentence_digests([long]), sentence_digests([f"শিরোনাম। {long}"])[-1:])


class BaselineRegistryTest(unittest.TestCase):
    def test_registry_unijoy_is_kala_unijoy(self):
        entry = next(e for e in baselines.load_registry() if e["name"] == "UniJoy")
        ours, theirs = baselines.keymap(entry, MODEL), unijoy_keymap(MODEL)
        for text in ["আমি বই পড়ি।", "ক্ষমতা ও উৎসর্গ", "ঐতিহ্য ঔষধ ঋণ ঊর্ধ্ব ঈদ"]:
            self.assertEqual(ours.encode(text), theirs.encode(text))

    def test_keymap_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text(json.dumps({"layers": {"base": {"J": "ক", "F": "া", "G": "্"}, "shift": {"J": "খ"}},
                                        "sequences": {"্া": "আ"}}), encoding="utf-8")
            entry = {"name": "X", "kind": "keymap", "file": str(path)}
            original = baselines.source_path
            baselines.source_path = lambda e: path
            try:
                km = baselines.keymap(entry, MODEL)
            finally:
                baselines.source_path = original
            self.assertEqual([(a.key, a.layer) for a in km.encode("কাখআ")],
                             [("J", "base"), ("F", "base"), ("J", "shift"), ("G", "base"), ("F", "base")])

    def test_keymap_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text(json.dumps({"layers": {"base": {"KP1": "ক"}}}), encoding="utf-8")
            original = baselines.source_path
            baselines.source_path = lambda e: path
            try:
                with self.assertRaises(ValueError):
                    baselines.keymap({"name": "X", "kind": "keymap", "file": str(path)}, MODEL)
            finally:
                baselines.source_path = original


# A tiny avro-fixed layout (virtual-key codes): consonants, signs, ্, ঁ, reph, ্য, ।
AVRO_LAYERS = {
    "normal": {"75": "ক", "66": "ব", "67": "চ", "82": "র", "90": "য", "77": "ম", "65": "া", "68": "ি", "85": "ু",
               "69": "ে", "71": "্", "88": "ঁ", "190": "।", "70": "র্", "86": "্য"},
    "shift": {"65": "আ"},
}


class AvroFixedTest(unittest.TestCase):
    def setUp(self):
        self.km = avro_fixed.AvroFixedKeyMap("T", AVRO_LAYERS, {}, MODEL.effort)
        self.key = {a.output: a for a in self.km.actions}

    def typed(self, *outputs):
        return self.km.decode([self.key[o] for o in outputs])

    def test_port_of_kala_rules(self):
        self.assertEqual(self.typed("ি"), "ই")              # sign at word start → independent vowel
        self.assertEqual(self.typed("ক", "া", "ি"), "কাই")  # sign after a sign → independent vowel
        self.assertEqual(self.typed("ব", "্", "ি"), "বই")   # ্ + sign → independent vowel
        self.assertEqual(self.typed("ক", "্", "্"), "ক্‌")
        self.assertEqual(self.typed("ক", "া", "য", "র্"), "কার্য")  # reph moves before the cluster
        self.assertEqual(self.typed("ক", "্", "ম", "ু", "র্"), "র্ক্মু")
        self.assertEqual(self.typed("চ", "ঁ", "া"), "চাঁ")   # ঁ before a sign moves after it
        self.assertEqual(self.typed("র", "্য"), "র‍্য")

    def test_encoder_is_cheapest_and_round_trips(self):
        for word in ["আমি", "বই", "কাজ", "এই", "কার্য", "চাঁদ", "ক্ষমতা", "বাবা।", "র‍্যাব", "ম্যাক"]:
            ok, escapes = self.km.round_trip(word)
            self.assertTrue(ok, word)
        self.assertEqual(len(self.km.encode("বই")), 3)       # ব ্ ি
        self.assertEqual(len(self.km.encode("কার্য")), 4)    # reph key saves a keystroke over র ্
        self.assertEqual(len(self.km.encode("আম")), 2)       # া at word start
        self.assertTrue(all(isinstance(s, Action) and s.layer in ("base", "shift") for s in self.km.encode("চাঁদ")
                            if not isinstance(s, avro_fixed.Escape)))

    def test_discovery_skips_phonetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, kind in (("a", "avro-fixed"), ("b", "phonetic"), ("c", "wfstphonetic")):
                (Path(tmp) / name).mkdir()
                (Path(tmp) / name / "layout.json").write_text(
                    json.dumps({"type": kind, "name": name.upper(), "layers": AVRO_LAYERS}), encoding="utf-8")
            found, skipped = baselines.discover(tmp)
            self.assertEqual([e["name"] for e in found], ["A"])
            self.assertEqual({s["type"] for s in skipped}, {"phonetic", "wfstphonetic"})


if __name__ == "__main__":
    unittest.main()
