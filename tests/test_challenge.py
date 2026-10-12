"""Challenge kit: the standalone scorer agrees with the project's key model
and table scorer, and validates layouts."""
import random
import unittest
from fractions import Fraction

from bangla_dh import challenge_template as public
from bangla_dh.bangla.grammar import Action
from bangla_dh.scoring.j0 import score_units
from bangla_dh.scoring.model import KeyModel
from bangla_dh.search.problem import load_problem, parse_slot, slots

MODEL = KeyModel.from_grid()
PROBLEM = load_problem()
FIXED = {k: parse_slot(v) for k, v in PROBLEM["fixed"].items()}
KEYS = sorted({k for k, _ in slots()} | {k for k, _ in FIXED.values()})


def model_data() -> dict:
    return {"keys": {k: [repr(MODEL.keys[k].effort), MODEL.keys[k].finger, MODEL.keys[k].row] for k in KEYS},
            "shift_keys": {n: repr(MODEL.effort(n)) for n in ("LSHIFT", "RSHIFT")},
            "same_finger": [repr(x) for x in MODEL.same_finger],
            "neighbour_by_outer_finger": [[repr(x) for x in row] for row in MODEL.neighbour]}


def fake_data(style: str, rng: random.Random) -> dict:
    symbols = PROBLEM["styles"][style]["searched_symbols"]
    placed = symbols + list(FIXED)
    labels = {s: rng.randint(0, 5000) for s in placed}
    pairs = [[a, b, rng.randint(1, 900)] for a in placed for b in placed if a != b and rng.random() < 0.2]
    return {"version": "test", "model": model_data(),
            "objective": {"weights": {"one": "1/3", "two": "2/3"}},
            "styles": {style: {"symbols": symbols, "fixed": {s: list(v) for s, v in FIXED.items()},
                               "corpora": {"one": {"N": 123457, "labels": labels, "pairs": pairs},
                                           "two": {"N": 98765, "labels": dict(reversed(list(labels.items()))),
                                                   "pairs": pairs[::2]}},
                               "reference": {"J1_exact": "2"}}}}


class PublicScorer(unittest.TestCase):
    def test_key_model_matches(self):
        model = public.Model({"model": model_data()})
        for a in KEYS:
            for layer in ("base", "shift"):
                self.assertEqual(Fraction(model.cost(a, layer), public.SCALE),
                                 Fraction(repr(MODEL.effort(a) + MODEL.modifier_effort(a, layer))).limit_denominator(10 ** 6))
            for b in KEYS:
                kind, value = MODEL.penalty_keys(a, b, False)
                self.assertEqual(model.penalty(a, b), (kind, round(value * public.SCALE)))

    def test_score_matches_table_scorer(self):
        rng = random.Random(7)
        for style in ("A", "D"):
            data = fake_data(style, rng)
            symbols = list(data["styles"][style]["symbols"])
            rng.shuffle(symbols)
            placed = dict(zip(symbols, slots()))
            got = public.score(style, placed, data)["J1"]
            actions = {s: Action(k, l, s) for s, (k, l) in {**placed, **FIXED}.items()}
            expected = 0.0
            for name, w in data["objective"]["weights"].items():
                corpus = data["styles"][style]["corpora"][name]
                u = {s: c / corpus["N"] for s, c in corpus["labels"].items()}
                v = {(a, b): c / corpus["N"] for a, b, c in corpus["pairs"]}
                expected += float(Fraction(w)) * score_units(actions, u, v, MODEL)["J1"]
            self.assertAlmostEqual(float(got), expected, places=12)

    def test_validation(self):
        data = fake_data("D", random.Random(1))
        symbols = data["styles"]["D"]["symbols"]
        layout = {key: ["", ""] for key in public.LETTER_KEYS}
        for symbol, (key, layer) in zip(symbols, slots()):
            layout[key][0 if layer == "base" else 1] = symbol
        style, placed, problems = public.parse_layout({"style": "d", "layout": layout}, data)
        self.assertEqual((style, problems), ("D", []))
        # Dotted circles and the precomposed ড় are accepted.
        drawn = {k: [("◌" + s if s in "ািীুূৃেৈোৌ্ংঃঁ" else s).replace("ড়", "ড়") for s in v]
                 for k, v in layout.items()}
        self.assertEqual(public.parse_layout({"style": "D", "layout": drawn}, data)[1], placed)
        broken = {k: list(v) for k, v in layout.items()}
        broken["Q"][0] = broken["W"][0]
        self.assertTrue(public.parse_layout({"style": "D", "layout": broken}, data)[2])
        del broken["M"]
        self.assertTrue(any("keys missing" in p for p in public.parse_layout({"style": "D", "layout": broken}, data)[2]))
        self.assertTrue(public.parse_layout({"style": "B", "layout": layout}, data)[2])
        for junk in ([1, 2], "D", None, {"style": "D", "layout": [1]}, {"style": "D", "layout": {"Q": [None, 3]}}):
            result = public.evaluate(junk, data, "sha")
            self.assertFalse(result["valid"])
            self.assertTrue(result["problems"])


if __name__ == "__main__":
    unittest.main()
