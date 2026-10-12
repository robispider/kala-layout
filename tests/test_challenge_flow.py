"""The run-it-yourself flow: leaderboard, search comparison and the reproduction check."""
import json
import shutil
import unittest
from pathlib import Path

from bangla_dh import generate, leaderboard, mix, reproduction
from bangla_dh.paths import PROJECT_ROOT

SCRATCH = PROJECT_ROOT / "work" / "test-flow"
CHALLENGE = PROJECT_ROOT / "challenge"


def _write(path: Path, data) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


class FlowTests(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        SCRATCH.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, SCRATCH, True)
        self.reference = json.loads((CHALLENGE / "D-reference.json").read_text(encoding="utf-8"))

    def test_leaderboard_scores_ranks_and_flags_problems(self):
        better = json.loads(json.dumps(self.reference))
        a, b = better["layout"]["Q"], better["layout"]["W"]  # swap two keys: a valid, different layout
        better["layout"]["Q"], better["layout"]["W"] = b, a
        better.update(name="swapped", author="tester")
        broken = json.loads(json.dumps(self.reference))
        broken["layout"]["Q"][0] = broken["layout"]["W"][0]
        files = [_write(SCRATCH / "swapped.json", better), _write(SCRATCH / "copy.json", self.reference),
                 _write(SCRATCH / "broken.json", broken), _write(SCRATCH / "also-swapped.json", better)]
        board = leaderboard.score_files(files)
        names = [e["file"] for e in board["styles"]["D"]["entries"]]
        self.assertEqual(names, ["swapped.json"])
        problems = {p["file"]: " ".join(p["problems"]) for p in board["problems"]}
        self.assertIn("reference", problems["copy.json"])
        self.assertIn("placed twice", problems["broken.json"])
        self.assertIn("swapped.json", problems["also-swapped.json"])
        entry = board["styles"]["D"]["entries"][0]
        self.assertEqual(entry["author"], "tester")
        self.assertEqual(entry["beats_reference"], entry["J1"] < board["styles"]["D"]["reference"]["J1"])
        self.assertIn("swapped", leaderboard.render(board))

    def test_the_published_search_compares_as_the_same_layout(self):
        weights = dict(mix.DEFAULT_WEIGHTS)
        for style in ("A", "D"):
            result = generate.compare(style, mix.RESULTS, weights)
            self.assertTrue(result["same_layout"], style)
            self.assertEqual(result["keys_that_differ"], 0)
            self.assertAlmostEqual(result["training_J1"]["yours"], result["training_J1"]["published"], places=12)
            self.assertIn("the same layout", generate.render(result))

    def test_a_different_layout_is_reported_with_its_scores(self):
        search = SCRATCH / "search"
        record = json.loads((mix.SEARCH / "D.json").read_text(encoding="utf-8"))
        layout = record["best"]["layout"]
        first, second = sorted(layout)[:2]
        layout[first], layout[second] = layout[second], layout[first]
        _write(search / "D.json", record)
        result = generate.compare("D", SCRATCH, dict(mix.DEFAULT_WEIGHTS))
        self.assertFalse(result["same_layout"])
        self.assertEqual(result["keys_that_differ"], 2)
        self.assertGreater(result["training_J1"]["yours"], result["training_J1"]["published"])
        self.assertIn("higher training J1", result["verdict"])

    def test_generate_refuses_to_overwrite_the_published_results(self):
        with self.assertRaises(SystemExit):
            generate.run(styles=["D"], seeds=1, out=mix.RESULTS)

    def test_reproduction_hash_ignores_run_details_only(self):
        a = _write(SCRATCH / "a.json", {"x": 1, "seconds": 5, "runs": [{"seconds": 1, "best": [1, 2]}]})
        b = _write(SCRATCH / "b.json", {"seconds": 99, "x": 1, "runs": [{"best": [1, 2], "seconds": 7}]})
        c = _write(SCRATCH / "c.json", {"x": 1, "runs": [{"best": [1, 3]}]})
        self.assertEqual(reproduction.canonical_sha256(Path(a)), reproduction.canonical_sha256(Path(b)))
        self.assertNotEqual(reproduction.canonical_sha256(Path(a)), reproduction.canonical_sha256(Path(c)))

    def test_published_results_match_the_reproduction_lock(self):
        self.assertTrue(reproduction.check_results(log=lambda *_: None))


if __name__ == "__main__":
    unittest.main()
