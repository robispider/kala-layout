"""Layout-transfer plumbing uses synthetic coefficients, never fitted rankings."""
import copy
import math
import unittest

from bangla_dh.paths import DATA
from bangla_dh.usage_registry import strict_json
from bangla_dh.usage_evaluator import actions, compare, score, search, support_key
from bangla_dh.usage_metric import InvalidData


def candidate():
    return {"schema": "kala.empirical.candidate/1", "name": "synthetic", "geometry": "ansi", "grammar": "keymap",
            "layers": {"base": {"K": "ক", "F": "খ"}, "shift": {}}}


def model(c):
    trace = actions(c, "কখক")
    keys = {support_key("ansi", a, b): 5 for a,b in zip(trace["downs"], trace["downs"][1:])}
    regression = {"intercept": math.log(.1), "features": [], "coefficients": {}, "means": [], "scales": []}
    return {"final_interval_model": regression, "support_contributors": keys, "bootstrap_models": [regression for _ in range(25)]}


class EvaluatorTests(unittest.TestCase):
    def test_same_sequence_cost_ignores_layout_display_name(self):
        c = candidate(); renamed = dict(c, name="different name")
        result = compare({"a": c, "b": renamed}, "a", [("কখক", 1)], model(c))
        self.assertEqual(result["a"]["status"], "experimental_prediction")
        self.assertAlmostEqual(result["a"]["modeled_ms_per_1000_codepoints"], 200000/3)
        self.assertEqual(result["a"]["reference_index"], 100)
        self.assertEqual(result["a"]["reference_index"], result["b"]["reference_index"])
        self.assertEqual(result["b"]["difference_95pct_ms_per_1000"], [0, 0])

    def test_no_model_never_substitutes_frozen_effort_score(self):
        result = score(candidate(), [("কখক", 1)], None)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertIsNone(result["modeled_ms_per_1000_codepoints"])

    def test_unsupported_contexts_prevent_full_layout_score(self):
        c = candidate(); trained = model(c)
        result = score(c, [("ক খ", 1)], trained)
        self.assertIsNone(result["modeled_ms_per_1000_codepoints"])
        self.assertEqual(result["status"], "unsupported_contexts")
        self.assertTrue(any("space" in reason for reason in result["exclusions"]))
        result = score(c, [("কখক", 1)], dict(trained, support_contributors={}))
        self.assertIsNone(result["modeled_ms_per_1000_codepoints"])

    def test_physical_shift_is_an_explicit_down_not_a_free_layer(self):
        c = candidate(); c["layers"]["shift"]["J"] = "গ"
        trace = actions(c, "গগক")
        self.assertEqual(trace["downs"][0]["position"], "LSHF")
        self.assertEqual(sum(a["kind"] == "modifier" for a in trace["downs"]), 1)
        self.assertTrue(trace["round_trip"])

    def test_research_vowel_recipes_round_trip_with_distinct_strokes(self):
        a = strict_json((DATA / "usage-metric-registry/candidates/kala-goti.json").read_bytes())
        d = strict_json((DATA / "usage-metric-registry/candidates/kala-jhor.json").read_bytes())
        first, second = actions(a, "ই"), actions(d, "ই")
        self.assertTrue(first["round_trip"]); self.assertTrue(second["round_trip"])
        self.assertFalse(first["unreachable"]); self.assertFalse(second["unreachable"])
        self.assertNotEqual(len(first["downs"]), len(second["downs"]))

    def test_unreachable_symbols_stay_visible_even_when_escape_replays(self):
        trace = actions(candidate(), "ক😀")
        self.assertTrue(trace["round_trip"])
        self.assertEqual(trace["unreachable"], [["U+1F600"]])
        self.assertIsNone(score(candidate(), [("ক😀", 1)], None)["modeled_ms_per_1000_codepoints"])

    def test_search_never_uses_same_text_for_development_and_final(self):
        c = {"schema": "kala.empirical.candidate/1", "grammar": "style-D", "mapping": {}, "geometry": "ansi"}
        with self.assertRaises(InvalidData): search(c, [("ক", 1)], [("ক", 1)], None)

    def test_search_does_not_propose_improvements_without_model(self):
        c = strict_json((DATA / "usage-metric-registry/candidates/kala-jhor.json").read_bytes())
        result = search(c, [("কখ", 1)], [("গঘ", 1)], None, locked=["ক"], max_changed=2)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertEqual(result["candidates"], [])

    def test_synthetic_supported_search_honors_locked_keys_and_change_budget(self):
        c = {"schema": "kala.empirical.candidate/1", "grammar": "style-D", "geometry": "ansi",
             "mapping": {"ক": {"key": "K", "layer": "base"}, "খ": {"key": "F", "layer": "base"}, "গ": {"key": "J", "layer": "base"}}}
        support = {}
        for a in "কখগ":
            for b in "কখগ":
                trace = actions(c, a+b)["downs"]
                support[support_key("ansi", trace[0], trace[1])] = 5
        regression = {"intercept": math.log(.1), "features": ["distance_u"], "coefficients": {"distance_u": 1}, "means": [0], "scales": [1]}
        trained = {"final_interval_model": regression, "support_contributors": support, "bootstrap_models": [regression]*25}
        result = search(c, [("কখকখ", 1)], [("খকখক", 1)], trained, locked=["ক"], max_changed=2, steps=1)
        self.assertEqual(result["status"], "experimental_candidates")
        proposed = result["candidates"][0]
        self.assertEqual(proposed["mapping"]["ক"], c["mapping"]["ক"])
        self.assertEqual(len(proposed["changed_labels"]), 2)
        self.assertLess(proposed["search_score"]["modeled_ms_per_1000_codepoints"], result["baseline"]["modeled_ms_per_1000_codepoints"])


if __name__ == "__main__": unittest.main()
