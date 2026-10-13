"""Exact running action windows, cross-space semantics and committed e3 replay."""
from collections import Counter
import random
import tempfile
import unittest

from bangla_dh.bangla.grammar import Escape
from bangla_dh.bangla.styles import Style
from bangla_dh.experimental.actions import SPACE_ACTION
from bangla_dh.experimental.continuous import evaluate_cache, score_boundaries
from bangla_dh.experimental.continuous_counts import (
    DEFAULT, VERSION, CATEGORIES, action_steps, boundary_windows, category,
    committed_style_boundaries, load_verified, reference_windows, summarize)
from bangla_dh.experimental.continuous_run import average, comparisons
from bangla_dh.experimental.evaluate import MODELS
from bangla_dh.experimental.inputs import HELDOUT, read_json, load_candidates, unit_path
from bangla_dh.experimental.mechanics_counts import read_counts, triples_json
from bangla_dh.paths import PROJECT_ROOT, output_path, write_json, gzip_text_writer
from bangla_dh.reference import sha256_file
from bangla_dh.scoring.model import KeyModel
from bangla_dh.scoring import baselines

F, R, J = ("F", "base"), ("R", "shift"), ("J", "base")


class WindowTests(unittest.TestCase):
    def check_stream(self, paragraphs, mapping):
        words = {word for p in paragraphs for word in p.split(" ")}
        summaries = {w: summarize(mapping[w]) for w in words}
        actual, stats = boundary_windows([{"paragraphs": paragraphs}], summaries)
        _, _, expected, identity = reference_windows(paragraphs, mapping.__getitem__)
        self.assertEqual(actual, Counter({t: n for t, n in expected.items() if SPACE_ACTION in t}))
        self.assertEqual(stats["uninterrupted_run_windows"], identity)
        inside = sum(summarize(mapping[w]).inside for p in paragraphs for w in p.split(" "))
        self.assertEqual(inside + sum(actual.values()), identity)
        return actual, stats, summaries

    def test_short_words_multiple_spaces_and_boundaries(self):
        mapping = {"a": [F], "b": [J], "": [], "long": [F, R, J, F]}
        triples, stats, summaries = self.check_stream(["a b a", "long", "a  b", "   ", ""], mapping)
        self.assertEqual(triples[SPACE_ACTION, J, SPACE_ACTION], 1)
        self.assertEqual(triples[F, SPACE_ACTION, J], 1)
        self.assertEqual(triples[F, SPACE_ACTION, SPACE_ACTION], 1)
        self.assertEqual(triples[SPACE_ACTION, SPACE_ACTION, J], 1)
        self.assertEqual(triples[SPACE_ACTION, SPACE_ACTION, SPACE_ACTION], 1)
        self.assertEqual(summaries["long"].observed, [1, 1, 1])
        self.assertEqual(stats["space_units"], 7)

    def test_escapes_keep_supported_suffix_and_punctuation(self):
        mapping = {"a": [F, R], "b": [Escape("?"), J, F],
                   "c": [J, Escape("?"), R], "d": [F, R, Escape("?"), J, F],
                   "p": [(".", "base"), F], "e": [Escape("?")]}
        triples, _, _ = self.check_stream(["a b c d p e a"], mapping)
        self.assertNotIn((R, SPACE_ACTION, J), triples)
        self.assertIn((J, F, SPACE_ACTION), triples)
        self.assertIn((F, SPACE_ACTION, (".", "base")), triples)
        self.assertNotIn((SPACE_ACTION, SPACE_ACTION, F), triples)

    def test_documents_never_connect(self):
        summaries = {"a": summarize([F]), "b": summarize([J])}
        triples, stats = boundary_windows([{"paragraphs": ["a"]}, {"paragraphs": ["b"]}], summaries)
        self.assertFalse(triples)
        self.assertEqual(stats["uninterrupted_run_windows"], 0)

    def test_randomized_reference_and_optimized_scanners(self):
        rng = random.Random(314159)
        mapping = {str(i): [rng.choice([F, R, J, Escape("?")])
                           for _ in range(rng.randrange(10))] for i in range(40)}
        mapping[""] = []
        paragraphs = [" ".join(rng.choices(list(mapping), k=rng.randrange(1, 20))) for _ in range(600)]
        self.check_stream(paragraphs, mapping)

    def test_classification_is_exhaustive(self):
        for a in (F, SPACE_ACTION):
            for b in (F, SPACE_ACTION):
                for c in (F, SPACE_ACTION):
                    self.assertIn(category((a, b, c)), CATEGORIES)

    def test_actual_style_and_fixed_layout_encoders(self):
        paragraphs = ["আক আম", "র্ক কা", "ক, ক।", "অ অ"]
        words = {w for p in paragraphs for w in p.split(" ")}
        stream_totals = []
        for name in ("A", "D"):
            style = Style(name)
            mapping = {w: [s if isinstance(s, Escape) else (s, "base") for s in style.encode(w)] for w in words}
            _, stats, _ = self.check_stream(paragraphs, mapping)
            stream_totals.append(stats["uninterrupted_run_windows"])
        self.assertNotEqual(*stream_totals)
        for entry in baselines.load_registry():
            keymap = baselines.keymap(entry, KeyModel.from_grid(MODELS["traditional"]))
            mapping = {w: keymap.encode(w) for w in words}
            self.check_stream(paragraphs, mapping)


class EndpointTests(unittest.TestCase):
    def test_repeat_move_hand_shift_and_missing_mass(self):
        triples = Counter({(F, SPACE_ACTION, F): 2, (F, SPACE_ACTION, R): 3,
                           (F, SPACE_ACTION, J): 4, (("?", "altgr"), SPACE_ACTION, J): 1,
                           (SPACE_ACTION, F, R): 7, (SPACE_ACTION, F, SPACE_ACTION): 5})
        result = score_boundaries(triples, KeyModel.from_grid(MODELS["traditional"]))
        self.assertEqual(result["spanning_count"], 10)
        self.assertEqual(result["supported_spanning_count"], 9)
        self.assertEqual(result["shift_involving_spanning_count"], 3)
        self.assertEqual(result["counts"]["same_key"], 2)
        self.assertEqual(result["counts"]["same_finger_different_key"], 3)
        self.assertEqual(result["bounds"]["same_finger_different_key"], {"lower": .3, "upper": .4})
        self.assertEqual(result["counts"]["same_hand"], 5)
        self.assertEqual(result["counts"]["opposite_hand"], 4)
        self.assertGreater(result["same_finger_distance_u_sum"], 0)
        self.assertEqual(result["category_counts"]["multiple_spaces"], 5)
        self.assertFalse(result["whole_typing_comfort"])

    def test_empty_spanning_domain_and_validation(self):
        model = KeyModel.from_grid(MODELS["traditional"])
        result = score_boundaries(Counter({(SPACE_ACTION, F, R): 1}), model)
        self.assertIsNone(result["coverage"])
        self.assertEqual(result["bounds"], {})
        with self.assertRaises(ValueError):
            score_boundaries(Counter({(F, R, J): 1}), model)

    def test_style_mapping_preserves_space_and_categories(self):
        cache = {"boundary_triples": triples_json(Counter({(("a", "base"), SPACE_ACTION, ("b", "base")): 3})),
                 "category_counts": {"within_word": 4, "edge_space": 0, "spanning_space": 3, "multiple_spaces": 0}}
        model = KeyModel.from_grid(MODELS["traditional"])
        result = evaluate_cache(cache, model, {"a": F, "b": J})
        self.assertEqual(result["within_word_share"], 4/7)
        self.assertEqual(result["bounds"]["opposite_hand"], {"lower": 1, "upper": 1})

    def test_fingering_sensitivity_uses_frozen_grid(self):
        triples = Counter({(("C", "base"), SPACE_ACTION, F): 1})
        traditional = score_boundaries(triples, KeyModel.from_grid(MODELS["traditional"]))
        adapted = score_boundaries(triples, KeyModel.from_grid(MODELS["model-optimal"]))
        self.assertNotEqual(traditional["counts"]["same_finger_different_key"], adapted["counts"]["same_finger_different_key"])

    def test_cache_integrity_and_identity_fail_before_scoring(self):
        import json
        from pathlib import Path
        parent = output_path(PROJECT_ROOT / "work/evaluator-experiments/continuous-tests")
        parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            root = Path(directory)
            path = root / "counts/style-d-bnwiki-heldout.json.gz"
            record = read_json(unit_path("bnwiki/heldout"))
            cache = {"kind": "style", "identity": "D", "corpus": "bnwiki/heldout",
                     "token_table_sha256": record["token_table_sha256"]}
            def save():
                with gzip_text_writer(path) as stream:
                    json.dump(cache, stream)
                write_json(root / "run-manifest.json", {"output_sha256": {
                    path.relative_to(PROJECT_ROOT).as_posix(): sha256_file(path)}})
            save()
            self.assertEqual(load_verified(root, "style", "D", "bnwiki/heldout")[0], cache)
            output_path(path).write_bytes(b"damaged gzip")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_verified(root, "style", "D", "bnwiki/heldout")
            cache["identity"] = "A"
            save()
            with self.assertRaisesRegex(ValueError, "provenance mismatch"):
                load_verified(root, "style", "D", "bnwiki/heldout")


@unittest.skipUnless((DEFAULT / "run-manifest.json").exists(), "e3 published run not yet available")
class PublishedTests(unittest.TestCase):
    def test_manifest_hashes_and_all_count_identities(self):
        manifest = read_json(DEFAULT / "run-manifest.json")
        for filename, digest in manifest["output_sha256"].items():
            self.assertEqual(sha256_file(PROJECT_ROOT / filename), digest, filename)
        for path in (DEFAULT / "counts").glob("*.gz"):
            cache = read_counts(path)
            self.assertEqual(sum(cache["category_counts"].values()), cache["corpus_totals"]["uninterrupted_run_windows"])
            self.assertTrue(all(cache["checks"].values()))
            frozen = read_counts(PROJECT_ROOT / "results/evaluator-e2/run-v1/counts" / path.name)
            self.assertEqual(cache["action_tables"], frozen["action_tables"])
            self.assertEqual(cache["triples"], frozen["triples"])

    def test_public_scoring_and_equal_source_averages(self):
        public = read_json(DEFAULT / "public-summary.json")
        layouts, _ = load_candidates(False)
        candidates = {next(n for n in c.names if n.startswith("Kala ")): c for c in layouts}
        for row in public["corpus_scores"]:
            name, corpus, scenario = row["name"], row["corpus"], row["scenario"]
            candidate = candidates.get(name)
            kind, identity = ("style", candidate.style) if candidate else ("baseline", name)
            cache, _ = load_verified(DEFAULT, kind, identity, corpus)
            actual = evaluate_cache(cache, KeyModel.from_grid(MODELS[scenario]), candidate.assignment() if candidate else None)
            self.assertEqual(actual, row["continuous"])
        for scenario in MODELS:
            for name, expected in public["public_summary"][scenario].items():
                rows = [r for r in public["corpus_scores"] if r["name"] == name and r["scenario"] == scenario]
                self.assertEqual(average(rows, {c: 1/3 for c in HELDOUT}), expected)
            self.assertEqual(comparisons(public["public_summary"][scenario]), public["comparisons"][scenario])

    def test_cached_challenge_counts_are_available(self):
        cache = committed_style_boundaries("D", "bnwiki/heldout")
        self.assertEqual(cache["version"], VERSION)
        self.assertEqual(cache["corpus"], "bnwiki/heldout")


if __name__ == "__main__":
    unittest.main()
