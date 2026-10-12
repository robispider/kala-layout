"""Bangla-related Phase 1 checks: the original tool's caseless-script quirk and
the Kala data inventory used by Phase 2."""
import unittest

from bangla_dh.kala_data import inventory
from bangla_dh.reproduce import caseless_script_check


class CaselessScriptTests(unittest.TestCase):
    def test_original_analyzer_double_counts_bangla(self):
        check = caseless_script_check()
        self.assertEqual(check["key_chars"], ["কক", "াা", "িি"])
        self.assertAlmostEqual(check["base_effort_all_keys_effort_1"], 2.0, places=6)


class KalaInventoryTests(unittest.TestCase):
    def test_core_sources_present_and_hashed(self):
        sources = {s["path"]: s for s in inventory()["sources"]}
        for path in ("data/bn/Alphabet.json", "kala/layout/bn/UniJoy.json", "tools/kala-eval/datasets/top20k.tsv"):
            with self.subTest(path=path):
                self.assertTrue(sources[path]["present"])
                self.assertEqual(len(sources[path]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
