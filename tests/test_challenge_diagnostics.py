"""Optional diagnostics must not influence challenge validity, scores or ordering."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from bangla_dh import challenge, cli, leaderboard
from bangla_dh.paths import PROJECT_ROOT, output_path, write_json
from bangla_dh.reference import sha256_file
from bangla_dh.experimental import submissions


class DiagnosticIntegrationTests(unittest.TestCase):
    def setUp(self):
        parent = output_path(PROJECT_ROOT / "work/evaluator-experiments/integration-tests")
        parent.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.reference = json.loads((PROJECT_ROOT / "challenge/D-reference.json").read_text(encoding="utf-8"))
        self.scorer = challenge.load_scorer(challenge.SCRIPT)
        self.data, self.data_hash = self.scorer.load_data()

    def write(self, name, value):
        return str(write_json(self.root / name, value))

    def changed(self):
        value = json.loads(json.dumps(self.reference))
        value["layout"]["Q"], value["layout"]["W"] = value["layout"]["W"], value["layout"]["Q"]
        value.update(name="<script>bad</script> [name] | with spaces", author="tester")
        return value

    def test_direct_reader_matches_official_scores_and_preserves_artifacts(self):
        file = self.write("layout with spaces.json", self.changed())
        before = {p: sha256_file(PROJECT_ROOT / p) for p in (
            "challenge/bangla_dh_challenge.py", "challenge/challenge-data.json", "results/reproduction.lock.json",
            "submissions/leaderboard.json")}
        with contextlib.redirect_stdout(io.StringIO()):
            result = submissions.run([file], self.root / "direct")
        self.assertEqual(result["ranking_effect"], "none")
        self.assertIsNone(result["comfort_rank"])
        self.assertEqual(result["problems"], [])
        actual = result["submissions"][0]
        expected = self.scorer.evaluate(self.changed(), self.data, self.data_hash)
        self.assertEqual(actual["official"], expected)
        self.assertEqual(len(actual["scores"]), 10)
        self.assertEqual(len(result["references"][0]["scores"]), 10)
        self.assertTrue(all(not r["preference"]["ranking_allowed"] for r in actual["scores"]))
        self.assertTrue(all(not r["mechanics"]["whole_typing_comfort"] for r in actual["scores"]))
        self.assertTrue(all("dvorak7" in r["mechanics"]["bounds"] and "engram_avg4" in r["mechanics"]["bounds"]
                            for r in actual["scores"]))
        self.assertTrue(all(r["engram_order"] is not None for r in actual["scores"]))
        if (PROJECT_ROOT / "results/evaluator-e3/run-v1/run-manifest.json").exists():
            self.assertTrue(all(r["continuous"]["available"] for r in actual["scores"]))
            self.assertTrue(all(r["continuous"]["ranking_effect"] == "none" for r in actual["scores"]))
            self.assertTrue(all("corpus_sha256" in r["continuous"] for r in actual["scores"]))
        report = (self.root / "direct/REPORT.md").read_text(encoding="utf-8")
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertIn("cannot rank", report)
        self.assertIn("Source-derived movement diagnostics", report)
        self.assertIn("Change vs reference", report)
        self.assertIn("Continuous-text movement across spaces", report)
        self.assertTrue(all(sha256_file(PROJECT_ROOT / p) == h for p,h in before.items()))
        manifest = json.loads((self.root / "direct/run-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["official_data_version"], challenge.DATA_VERSION)
        self.assertEqual(manifest["submission_inputs"][0]["sha256"], sha256_file(Path(file)))
        for path, digest in manifest["output_sha256"].items():
            self.assertEqual(sha256_file(PROJECT_ROOT / path), digest)

    def test_reader_uses_official_unicode_normalization_and_encoding(self):
        value = json.loads(json.dumps(self.reference))
        value["style"] = "d"
        for key, symbols in value["layout"].items():
            value["layout"][key] = [("◌" + s if s in "ািীুূৃেৈোৌ্ংঃঁ" else s).replace("ড়", "ড়") for s in symbols]
        file = output_path(self.root / "utf16.json")
        file.write_bytes(json.dumps(value, ensure_ascii=False).encode("utf-16"))
        with contextlib.redirect_stdout(io.StringIO()):
            got = submissions.run([file], self.root / "unicode")
        expected = self.scorer.evaluate(self.reference, self.data, self.data_hash)
        self.assertEqual(got["submissions"][0]["official"]["layout_sha256"], expected["layout_sha256"])
        self.assertEqual(got["submissions"][0]["official"]["J1_exact"], expected["J1_exact"])

    @unittest.skipUnless((PROJECT_ROOT / "results/evaluator-e3/run-v1/run-manifest.json").exists(), "e3 not published yet")
    def test_partial_continuous_caches_still_produce_optional_report(self):
        file = self.write("partial.json", self.changed())
        real_lookup = submissions.committed_style_boundaries
        def heldout_only(style, corpus):
            return None if corpus.endswith("/train") else real_lookup(style, corpus)
        with patch.object(submissions, "committed_style_boundaries", side_effect=heldout_only), contextlib.redirect_stdout(io.StringIO()):
            result = submissions.run([file], self.root / "partial")
        self.assertEqual(result["problems"], [])
        for row in result["submissions"][0]["scores"]:
            self.assertEqual(row["continuous"]["available"], not row["corpus"].endswith("/train"))
        self.assertIn("unavailable", (self.root / "partial/REPORT.md").read_text(encoding="utf-8"))
        self.assertTrue((self.root / "partial/scores.csv").exists())

    def test_invalid_missing_oversized_files_never_receive_diagnostics(self):
        bad = json.loads(json.dumps(self.reference))
        bad["layout"]["Q"][0] = bad["layout"]["W"][0]
        files = [self.write("bad.json", bad), str(self.root / "missing.json")]
        malformed = output_path(self.root / "malformed.json")
        malformed.write_text("{broken", encoding="utf-8")
        huge = output_path(self.root / "huge.json")
        huge.write_bytes(b" " * (submissions.MAX_BYTES + 1))
        with contextlib.redirect_stdout(io.StringIO()):
            result = submissions.run(files + [str(malformed), str(huge)], self.root / "invalid")
        self.assertEqual(result["submissions"], [])
        self.assertEqual(len(result["problems"]), 4)
        self.assertIsNone(result["comfort_rank"])

    def test_verification_opt_in_leaves_exit_status_and_exact_score_unchanged(self):
        file = self.write("valid.json", self.changed())
        with contextlib.redirect_stdout(io.StringIO()), patch.object(submissions, "report_optional") as report:
            self.assertEqual(challenge.run_verify([file]), 0)
            report.assert_not_called()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["challenge-verify", file, "--diagnostics", str(self.root / "verify")]), 0)
        result = json.loads((self.root / "verify/submissions.json").read_text(encoding="utf-8"))
        self.assertEqual(result["submissions"][0]["official"]["J1_exact"],
                         self.scorer.evaluate(self.changed(), self.data, self.data_hash)["J1_exact"])

    def test_report_failure_does_not_change_official_success_or_failure(self):
        good = self.write("good.json", self.changed())
        bad = self.write("bad.json", {"style": "B", "layout": {}})
        with contextlib.redirect_stdout(io.StringIO()), patch.object(submissions, "PairPreferences", side_effect=ValueError("source unavailable")):
            self.assertEqual(challenge.run_verify([good], diagnostics=self.root / "failure"), 0)
            self.assertEqual(challenge.run_verify([bad], diagnostics=self.root / "failure2"), 1)
            self.assertEqual(leaderboard.run([good], check=True, diagnostics=self.root / "failure3"), 0)
            self.assertEqual(leaderboard.run([bad], check=True, diagnostics=self.root / "failure4"), 1)

    def test_mechanics_integrity_failure_cannot_change_official_results(self):
        good = self.write("good.json", self.changed())
        bad = self.write("bad.json", {"style": "B", "layout": {}})
        before = leaderboard.score_files([good])
        with contextlib.redirect_stdout(io.StringIO()), patch.object(submissions, "verify_sources", side_effect=ValueError("mechanics hash mismatch")):
            self.assertEqual(challenge.run_verify([good], diagnostics=self.root / "mechanics-failure"), 0)
            self.assertEqual(challenge.run_verify([bad], diagnostics=self.root / "mechanics-bad"), 1)
            self.assertEqual(leaderboard.run([good], check=True, diagnostics=self.root / "mechanics-board"), 0)
        self.assertEqual(leaderboard.score_files([good]), before)

    def test_protected_destination_and_existing_run_do_not_affect_official_result(self):
        file = self.write("good.json", self.changed())
        before = sha256_file(challenge.SCRIPT)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(challenge.run_verify([file], diagnostics=PROJECT_ROOT / "challenge/forbidden"), 0)
            self.assertEqual(challenge.run_verify([file], diagnostics=self.root / "existing"), 0)
            self.assertEqual(challenge.run_verify([file], diagnostics=self.root / "existing"), 0)
        self.assertEqual(sha256_file(challenge.SCRIPT), before)
        self.assertFalse((PROJECT_ROOT / "challenge/forbidden").exists())

    def test_leaderboard_duplicates_and_reference_rules_are_preserved(self):
        files = [self.write("accepted.json", self.changed()), self.write("duplicate.json", self.changed()),
                 self.write("reference.json", self.reference)]
        original = leaderboard.score_files(files)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(leaderboard.run(files, check=True, diagnostics=self.root / "board"), 1)
        self.assertEqual(original, leaderboard.score_files(files))
        result = json.loads((self.root / "board/submissions.json").read_text(encoding="utf-8"))
        self.assertEqual([r["file"] for r in result["submissions"]], ["accepted.json"])
        self.assertEqual(len(result["problems"]), 2)
        self.assertNotIn("preference", original["styles"]["D"]["entries"][0])
        self.assertTrue(result["checks"]["official_integer_and_action_scores_agree"])

    def test_leaderboard_writer_keeps_identical_board_and_markdown(self):
        file = self.write("valid.json", self.changed())
        board = leaderboard.score_files([file])
        with contextlib.redirect_stdout(io.StringIO()), patch.object(leaderboard, "SUBMISSIONS", self.root):
            self.assertEqual(leaderboard.run([file], diagnostics=self.root / "write-board"), 0)
        self.assertEqual(json.loads((self.root / "leaderboard.json").read_text(encoding="utf-8")), board)
        self.assertEqual((self.root / "LEADERBOARD.md").read_text(encoding="utf-8"), leaderboard.render(board))

    def test_ci_step_preserves_filename_and_official_exit_status(self):
        lines = (PROJECT_ROOT / ".github/workflows/submissions.yml").read_text(encoding="utf-8").splitlines()
        start = next(i for i,l in enumerate(lines) if "python - <<'PY'" in l)
        end = next(i for i in range(start + 1, len(lines)) if lines[i] == "          PY")
        code = "\n".join(l[10:] for l in lines[start + 1:end])
        code = code.replace("work/evaluator-experiments/pr-check", (self.root / "ci-diagnostic").as_posix())
        compiled = compile(code, "submissions.yml Python step", "exec")
        for exit_code in (0,1):
            summary = output_path(self.root / f"ci-summary-{exit_code}.md")
            env = {"CHALLENGE_BASE_REF": "main", "GITHUB_STEP_SUMMARY": str(summary)}
            checked = SimpleNamespace(stdout="ok ``` untrusted fence\n", stderr="", returncode=exit_code)
            with patch.dict(os.environ, env), patch.object(subprocess, "check_output", return_value=b"submissions/name with spaces.json\0") as diff, patch.object(subprocess, "run", return_value=checked) as run, contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as ended:
                    exec(compiled, {})
            self.assertEqual(ended.exception.code, exit_code)
            self.assertEqual(run.call_args.args[0][-1], "submissions/name with spaces.json")
            text = summary.read_text(encoding="utf-8")
            self.assertIn("Optional diagnostics unavailable", text)
            self.assertIn("[code fence]", text)


if __name__ == "__main__":unittest.main()
