"""Unit behavior of the analyzer port on small hand-checked inputs."""
import unittest

from bangla_dh.colemak.analysis import perform_analysis
from bangla_dh.colemak.frequency import FreqAnalysis, load_bigram_freqs, load_char_freqs
from bangla_dh.colemak.keyboard import apply_config, load_layout, outermost_finger, parse_layout
from bangla_dh.reference import resource

CONFIG = """effort: 2
1.0 2.0 3.0
4.0 5.0 6.0
penalties:
 2.5 3.0 4.0
 0.5 1.0 1.5
 0.1 0.2 0.3
-0.2 -0.1 0.0
fingers: 2
0 1 2
0 1 3
"""


class LayoutParsingTests(unittest.TestCase):
    def test_default_shifted_characters_and_fingers(self):
        layout = parse_layout("q ; 1 x y z\n", "t")
        self.assertEqual([k.chars for k in layout.keys][:3], ["qQ", ";:", "1!"])
        self.assertEqual([k.finger for k in layout.keys], [0, 1, 2, 3, 3, 6])

    def test_explicit_multi_character_key_is_kept(self):
        layout = parse_layout(",; /<\n", "t")
        self.assertEqual([k.chars for k in layout.keys], [",;", "/<"])

    def test_lookup_matches_either_case(self):
        layout = parse_layout("q w\n", "t")
        self.assertIs(layout.lookup_char("q"), layout.keys[0])
        self.assertIs(layout.lookup_char("Q"), layout.keys[0])

    def test_config_rows_align_to_bottom_of_layout(self):
        layout = parse_layout("a b c\nd e f\n", "t")
        apply_config(layout, CONFIG.replace("effort: 2", "effort: 3").replace("1.0 2.0 3.0", "9 9 9\n1.0 2.0 3.0"))
        self.assertEqual([k.effort for k in layout.keys], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def test_three_row_layout_skips_number_row_of_four_row_config(self):
        layout = load_layout(resource("layout_main/qwerty.keyb"), resource("config/effort_traditional_config.dat"))
        self.assertEqual(layout.rows, 3)
        self.assertEqual(layout.lookup_char("q").effort, 3.0)
        self.assertEqual(layout.lookup_char("f").effort, 1.0)

    def test_penalties_and_type(self):
        layout = load_layout(resource("layout_full/colemak_dh.keyb"), resource("config/effort_ergonomic_config.dat"))
        self.assertEqual(layout.penalty_same_finger, [2.5, 3.0, 4.0])
        self.assertEqual(layout.penalty_neighbour_finger[2], [-0.2, -0.1, 0.0])  # middle-index
        self.assertEqual(layout.keyboard_type, "ANGLE")
        self.assertTrue(layout.has_penalty_neighbour_finger(8))   # right ring: ring-middle row
        self.assertFalse(layout.has_penalty_neighbour_finger(7))  # right middle: benefits only

    def test_outermost_finger(self):
        self.assertEqual(outermost_finger(1, 2), 1)
        self.assertEqual(outermost_finger(7, 8), 8)


class EffortComputationTests(unittest.TestCase):
    def setUp(self):
        self.layout = parse_layout("a b c\nd e f\n", "t")
        apply_config(self.layout, CONFIG)
        alphabet = self.layout.alphabet()
        freq = "A 40\nB 30\nD 20\nE 10\nAD 6\nAB 3\nBE 1\n"
        self.results = perform_analysis(self.layout, load_char_freqs(alphabet, freq), load_bigram_freqs(alphabet, freq))

    def test_base_effort(self):
        # A (1.0) .4 + B (2.0) .3 + D (4.0) .2 + E (5.0) .1
        self.assertAlmostEqual(self.results.effort_totals()["base"], 0.4 + 0.6 + 0.8 + 0.5, places=6)

    def test_same_finger_bigram(self):
        # A-D (finger 0) and B-E (finger 1) on adjacent rows: (0.6 + 0.1) * 3.0
        self.assertEqual([fb.bigram.string for fb in self.results.same_finger_bigrams], ["AD", "BE"])
        self.assertAlmostEqual(self.results.effort_totals()["same_finger"], (0.6 + 0.1) * 3.0, places=6)

    def test_neighbour_finger_bigram(self):
        # A-B fingers 0-1 (pinky-ring, same row): 0.3 * 0.5
        self.assertAlmostEqual(self.results.effort_totals()["neighbour_finger"], 0.3 * 0.5, places=6)

    def test_frequencies_are_binary32(self):
        cf = load_char_freqs("A", "A 1\n")
        self.assertEqual(cf[0].freq, 1.0)
        cf = load_char_freqs("AB", "A 1\nB 2\n")
        self.assertEqual(cf[0].freq, 0.3333333432674408)


class FreqAnalysisTests(unittest.TestCase):
    def test_counts_and_bigrams_do_not_span_whitespace(self):
        analysis = FreqAnalysis("AB")
        analysis.analyze("ab ba\nbb")
        counts = {c.char: c.count for c in analysis.char_freqs}
        bigrams = {b.string: b.count for b in analysis.bigram_freqs}
        self.assertEqual(counts["A"], 2)
        self.assertEqual(counts["B"], 4)
        self.assertEqual(bigrams, {"AB": 1, "BA": 1, "BB": 1, "AA": 0})

    def test_bangla_text(self):
        analysis = FreqAnalysis("কা")
        analysis.analyze("কাকা কা")
        self.assertEqual({c.char: c.count for c in analysis.char_freqs}, {"ক": 3, "া": 3})
        self.assertEqual({b.string: b.count for b in analysis.bigram_freqs}["কা"], 3)


if __name__ == "__main__":
    unittest.main()
