"""Exact separate objectives, cached swaps, reproducibility and safe resume."""
from fractions import Fraction
from pathlib import Path
import random
import tempfile
import unittest

from bangla_dh.experimental.actions import from_style, j_reference
from bangla_dh.experimental.continuous import evaluate_cache
from bangla_dh.experimental.continuous_counts import DEFAULT, load_verified
from bangla_dh.experimental.inputs import load_candidates, frequency_path, read_json
from bangla_dh.experimental.joint_engine import Archive, search
from bangla_dh.experimental.joint_problem import JointProblem, JointState, achievement, WEIGHTS
from bangla_dh.experimental.joint_search import (
    VERSION, atomic_json, classify_exact, prepare, recover_checkpoint, settings_digest)
from bangla_dh.paths import PROJECT_ROOT, output_path, write_json
from bangla_dh.reference import sha256_file


class ObjectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        references, _ = load_candidates(False)
        cls.problems = {c.style: JointProblem(c.style, c.layout) for c in references}

    def test_fast_and_exact_scores_match_independent_action_scoring(self):
        rng = random.Random(927)
        for style, problem in self.problems.items():
            for _ in range(3):
                perm = list(range(problem.j1.n))
                rng.shuffle(perm)
                j, s = problem.verify(perm)
                assignment = {**problem.assignment(perm), **problem.fixed}
                expected_j = expected_s = 0.0
                for corpus, weight in WEIGHTS.items():
                    cache, _ = load_verified(DEFAULT, "style", style, corpus)
                    tables = from_style(read_json(frequency_path(style, corpus)), assignment)
                    expected_j += float(weight) * j_reference(tables, problem.model)["J1"]
                    report = evaluate_cache(cache, problem.model, assignment)
                    self.assertEqual(report["coverage"], 1)
                    expected_s += float(weight) * report["bounds"]["same_finger_different_key"]["lower"]
                self.assertAlmostEqual(float(j), expected_j, places=12)
                self.assertAlmostEqual(float(s), expected_s, places=14)

    def test_both_cached_swap_deltas_and_undo_match_full_rescoring(self):
        rng = random.Random(821)
        for problem in self.problems.values():
            state = JointState(problem, problem.reference_perm, .5)
            state.j.log, state.s.log = [], []
            for _ in range(80):
                i, k = rng.sample(range(problem.j1.n), 2)
                old_j, old_s, old_energy = state.j.score, state.s.score, state.energy
                d, dj, ds = state.delta(i, k)
                changed = list(state.perm)
                changed[i], changed[k] = changed[k], changed[i]
                self.assertAlmostEqual(problem.j1.score(changed) - old_j, dj, places=12)
                self.assertAlmostEqual(problem.movement.score(changed) - old_s, ds, places=13)
                state.swap(i, k, dj, ds)
                self.assertAlmostEqual(state.energy - old_energy, d, places=13)
                self.assertEqual(state.j.perm, state.s.perm)
            state.j.undo()
            state.s.undo()
            self.assertEqual(state.perm, problem.reference_perm)
            self.assertAlmostEqual(state.j.score, problem.ref_j, places=12)
            self.assertAlmostEqual(state.s.score, problem.ref_s, places=13)

    def test_seeded_search_and_ils_are_reproducible(self):
        problem = self.problems["A"]
        first = search(problem, 291, .25, problem.reference_perm, 300, 4, 5)
        second = search(problem, 291, .25, problem.reference_perm, 300, 4, 5)
        first.pop("seconds")
        second.pop("seconds")
        self.assertEqual(first, second)
        for row in first["archive"]:
            j, s = problem.verify(row["perm"])
            self.assertEqual(row["j"], float(j))
            self.assertEqual(row["s"], float(s))

    def test_exploration_energy_and_exact_success_are_distinct(self):
        self.assertLess(achievement(9, 9, 10, 10, .5), 0)
        self.assertGreater(achievement(9, 11, 10, 10, .5), 0)
        self.assertLess(achievement(9, 11, 10, 10, 0), 0)
        self.assertFalse(classify_exact(Fraction(9), Fraction(11), Fraction(10), Fraction(10))["joint_training_improvement"])
        self.assertFalse(classify_exact(Fraction(10), Fraction(9), Fraction(10), Fraction(10))["joint_training_improvement"])
        self.assertTrue(classify_exact(Fraction(9), Fraction(9), Fraction(10), Fraction(10))["joint_training_improvement"])

    def test_same_physical_key_base_shift_is_not_different_key_movement(self):
        problem = self.problems["A"]
        a = problem.slots.index(("F", "base"))
        b = problem.slots.index(("F", "shift"))
        self.assertEqual(problem.movement.B[a][b], 0)
        self.assertGreater(problem.j1.B[a][b], 0)


class ArchiveTests(unittest.TestCase):
    def test_dominance_and_crowding_preserve_observed_joint_success(self):
        archive = Archive(2, (10, 10))
        archive.offer(5, 15, [0])
        archive.offer(15, 5, [1])
        archive.offer(9, 9, [2])
        self.assertEqual(len(archive.rows), 2)
        self.assertIn([2], [r["perm"] for r in archive.retained()])
        archive.offer(8, 8, [3])
        self.assertEqual(archive.goal["perm"], [3])


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        parent = output_path(PROJECT_ROOT / "work/evaluator-experiments/joint-tests")
        parent.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "run"
        self.settings = {"styles": ["A"], "seeds": 1, "first_seed": 7}
        self.inputs = {"test-input": "pinned"}

    def test_fresh_output_refuses_existing_and_resume_checks_settings(self):
        prepare(self.root, self.settings, self.inputs)
        with self.assertRaises(FileExistsError):
            prepare(self.root, self.settings, self.inputs)
        prepare(self.root, self.settings, self.inputs, True)
        with self.assertRaisesRegex(ValueError, "resume refused"):
            prepare(self.root, {**self.settings, "seeds": 2}, self.inputs, True)
        with self.assertRaisesRegex(ValueError, "resume refused"):
            prepare(self.root, self.settings, {"test-input": "changed"}, True)

    def test_recovery_of_run_saved_before_progress_update(self):
        _, _, progress = prepare(self.root, self.settings, self.inputs)
        path = self.root / "runs/A-7.json"
        atomic_json(path, {"id": "A-7", "version": VERSION, "settings_sha256": settings_digest(self.settings), "verified": True})
        write_json(self.root / "runs/unfinished.json.tmp", {"incomplete": True})
        recover_checkpoint(self.root, self.settings, progress, {"A-7"})
        self.assertEqual(progress["completed"], {"A-7": sha256_file(path)})
        _, _, resumed = prepare(self.root, self.settings, self.inputs, True)
        self.assertEqual(resumed, progress)
        output_path(path).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            prepare(self.root, self.settings, self.inputs, True)

    def test_completed_run_is_not_overwritten_by_resume(self):
        prepare(self.root, self.settings, self.inputs)
        write_json(self.root / "run-manifest.json", {"complete": True})
        with self.assertRaisesRegex(ValueError, "already complete"):
            prepare(self.root, self.settings, self.inputs, True)

    def test_other_seasons_and_published_layouts_are_not_output_targets(self):
        for folder in ("results/evaluator-e3/new-joint-run", "results/kala-keyboards/new-joint-run"):
            with self.assertRaisesRegex(ValueError, "joint search output"):
                prepare(PROJECT_ROOT / folder, self.settings, self.inputs)


if __name__ == "__main__":
    unittest.main()
