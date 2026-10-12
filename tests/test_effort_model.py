"""The reconstructed effort-grid model against model.html."""
import unittest

from bangla_dh.geometry.calibrate import compare_grids, config_grid_consistency, round1, summarize
from bangla_dh.geometry.effort_model import EffortParams, effort_grid, key_effort, fingers_for
from bangla_dh.geometry.keyboards import ansi_staggered, iso_staggered, matrix_split
from bangla_dh.reference import load_published, resource
from bangla_dh.reproduce import FROZEN_DISTANCE_SCALE

PARAMS = EffortParams(distance_scale=FROZEN_DISTANCE_SCALE)


class PublishedGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = load_published()
        cls.summary = summarize(compare_grids(cls.published, PARAMS))

    def test_one_unit_keys_within_rounding_noise(self):
        for name, grid in self.summary.items():
            with self.subTest(grid=name):
                self.assertLess(grid["max_abs_deviation_one_unit"], 0.08)

    def test_match_counts_do_not_regress(self):
        counts = {name: g["one_unit_matches"] for name, g in self.summary.items()}
        self.assertEqual(counts, {"iso_optimal_fingers": 46, "iso_traditional_fingers": 46,
                                  "matrix_optimal_fingers": 46})

    def test_published_grid_transcription_matches_analyzer_configs(self):
        """Image-transcribed values agree with the machine-readable configs,
        except the one inconsistency inside the published sources."""
        problems = config_grid_consistency(self.published, resource)
        self.assertEqual([(p["config"], p["key"], p["config_value"], p["image_value"]) for p in problems],
                         [("effort_traditional_config.dat", "]", 5.6, 4.7)])


class ModelPropertiesTests(unittest.TestCase):
    def test_home_keys_cost_finger_factor(self):
        grid = effort_grid(iso_staggered(), PARAMS)
        for key, expected in {"A": 1.6, "S": 1.3, "D": 1.1, "F": 1.0, "J": 1.0, "K": 1.1, "L": 1.3, ";": 1.6}.items():
            self.assertEqual(grid[key].effort, expected)

    def test_left_right_mirror_on_split_board(self):
        grid = effort_grid(matrix_split(), PARAMS)
        for left, right in (("Q", "P"), ("C", ","), ("G", "H"), ("1", "0"), ("V", "M")):
            self.assertAlmostEqual(grid[left].effort, grid[right].effort, places=9)

    def test_wrong_way_stagger_penalizes_left_top_row(self):
        grid = effort_grid(iso_staggered(), PARAMS)
        self.assertGreater(grid["E"].effort, grid["I"].effort)
        self.assertGreater(grid["W"].effort, grid["O"].effort)
        self.assertLess(grid["T"].effort, grid["Y"].effort)

    def test_ansi_main_block_equals_iso(self):
        iso, ansi = effort_grid(iso_staggered(), PARAMS), effort_grid(ansi_staggered(), PARAMS)
        for name in "QWERTYUIOPASDFGHJKL;ZXCVBNM,./":
            self.assertEqual(iso[name].effort, ansi[name].effort)

    def test_effort_grows_with_distance_scale(self):
        board = iso_staggered()
        finger = next(f for f in fingers_for(board, PARAMS) if f.finger_id == "L3")
        low = key_effort(board, board.key("G"), finger, EffortParams(distance_scale=1.0))
        high = key_effort(board, board.key("G"), finger, EffortParams(distance_scale=1.2))
        self.assertLess(low, high)

    def test_round1_half_up(self):
        self.assertEqual(round1(3.45), 3.5)
        self.assertEqual(round1(3.449), 3.4)


if __name__ == "__main__":
    unittest.main()
