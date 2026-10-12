"""Phase 1 regression: the published Colemak Mod-DH results and the frozen
full-precision baseline in results/phase1/reproduction.json."""
import json
import unittest

from bangla_dh import reproduce
from bangla_dh.reference import PROJECT_ROOT, load_published, verify_vendored

BASELINE = PROJECT_ROOT / "results" / "phase1" / "reproduction.json"


class PublishedTablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = load_published()

    def test_vendored_inputs_match_lock(self):
        self.assertEqual(verify_vendored(), [])

    def test_comparison_table_reproduced_exactly(self):
        table = reproduce.comparison_table(self.published)
        for row in table["rows"]:
            with self.subTest(layout=row["label"], config=row["config"]):
                self.assertEqual(row["reproduced"], row["published"])

    def test_switching_table(self):
        table = reproduce.switching_table(self.published)
        for row in table["rows"]:
            with self.subTest(layout=row["label"]):
                if row["label"] == "Qwpr":
                    # Known stale published cell: equals the pre-2021 model without S2/S1.
                    self.assertEqual(row["reproduced"][:3], row["published"][:3])
                    self.assertIn("explanation", row)
                else:
                    self.assertEqual(row["reproduced"], row["published"])

    def test_experience_curve(self):
        curve = reproduce.experience_curve(self.published)
        self.assertEqual([r["reproduced"] for r in curve["rows"]], [r["published"] for r in curve["rows"]])
        self.assertAlmostEqual(curve["p"], -0.3219280949, places=10)


class FrozenBaselineTests(unittest.TestCase):
    """Bit-for-bit agreement with the committed Phase 1 baseline."""

    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        cls.published = load_published()

    def test_comparison_full_precision(self):
        current = reproduce.comparison_table(self.published)
        for now, frozen in zip(current["rows"], self.baseline["comparison_table"]["rows"]):
            with self.subTest(layout=now["label"], config=now["config"]):
                self.assertEqual(now["full_precision"], frozen["full_precision"])

    def test_switching_full_precision(self):
        current = reproduce.switching_table(self.published)
        for now, frozen in zip(current["rows"], self.baseline["switching_difficulty_table"]["rows"]):
            with self.subTest(layout=now["label"]):
                self.assertEqual(now["switching_difficulty"], frozen["switching_difficulty"])

    def test_frozen_distance_scale(self):
        self.assertEqual(reproduce.FROZEN_DISTANCE_SCALE, self.baseline["effort_grid"]["frozen_distance_scale"])


if __name__ == "__main__":
    unittest.main()
