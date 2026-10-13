"""Upstream fidelity, lossless Bangla triples and conservative coverage bounds."""
from collections import Counter
import json
import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bangla_dh.bangla.grammar import Action, KeyMap
from bangla_dh.experimental.actions import ActionTables, from_tokens
from bangla_dh.experimental.mechanics import Mechanics, audit, verify_sources, SOURCE
from bangla_dh.experimental.mechanics_counts import count_stream, triples_json, triples_from_json
from bangla_dh.experimental.mechanics_run import comparisons, averaged
from bangla_dh.experimental.mechanics_counts import read_counts, map_triples
from bangla_dh.experimental.inputs import read_json
from bangla_dh.reference import sha256_file
from bangla_dh.paths import PROJECT_ROOT, output_path


def actions(steps):
    return ActionTables(len(steps), 0, Counter(steps), Counter(zip(steps, steps[1:])))


class FidelityTests(unittest.TestCase):
    def test_all_original_functions_and_distributed_rows(self):
        result = audit()
        self.assertEqual(result["pair_function_cases"], 42**2)
        self.assertEqual(result["triple_function_cases"], 42**3)
        self.assertEqual(result["distributed_triple_domain"], 32**3)
        self.assertEqual(result["distributed_table_rows"], 49152)
        self.assertLessEqual(result["distributed_table_max_absolute_error"], 1e-6)
        self.assertFalse(result["human_validation"])

    def test_original_quirks_are_preserved(self):
        model = Mechanics()
        # The source awards remote credit to same-row repeats before checking
        # same finger. This differs from the prose comment and is preserved.
        self.assertEqual(model.pair("F", "F")["dvorak7_remote"], 1)
        self.assertEqual(model.pair("F", "R")["dvorak7_remote"], 0)
        self.assertGreater(model.pair("A", "F")["dvorak7_inward"], model.pair("F", "A")["dvorak7_inward"])
        self.assertEqual(model.triple("F", "J", "F"), 1)
        self.assertEqual(model.triple("F", "F", "F"), 0)
        self.assertIsNotNone(model.pair("1", "F"))

    def test_adapted_geometry_is_separate_and_does_not_mutate_original(self):
        original = Mechanics()
        expected = original.pair("C", "F")
        adapted = Mechanics("model-optimal")
        self.assertNotEqual(expected, adapted.pair("C", "F"))
        self.assertEqual(Mechanics().pair("C", "F"), expected)
        self.assertEqual(original.pair("C", "F"), expected)

    def test_hash_tampering_fails_before_execution(self):
        parent = output_path(PROJECT_ROOT / "work/evaluator-experiments/tests")
        parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            directory = Path(directory)
            lock = json.loads((SOURCE / "source-lock.json").read_text(encoding="utf-8"))
            output_path(directory / "source-lock.json").write_text(json.dumps(lock), encoding="utf-8")
            output_path(directory / lock["files"][0]["file"]).write_bytes(b"tampered")
            with patch("bangla_dh.experimental.mechanics.SOURCE", directory):
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    verify_sources()


class CoverageTests(unittest.TestCase):
    def test_weighted_aggregation_against_distributed_tables(self):
        pairs = Counter({(("F","base"),("R","shift")):2,
                         (("R","shift"),("F","base")):3,
                         (("J","base"),("J","base")):7})
        table = ActionTables(16,0,Counter({("F","base"):4,("R","shift"):3,("J","base"):9}),pairs)
        result = Mechanics().score(table)
        for filename, column, metric, scale in (
            ("keypair_dvorak7_scores.csv", "dvorak7_score", "dvorak7", 7),
            ("engram_2key_scores_avg4.csv", "engram_avg4_score", "engram_avg4", 1),
        ):
            with (SOURCE / "upstream/tables" / filename).open(encoding="utf-8",newline="") as stream:
                lookup = {r["key_pair"]:float(r[column])/scale for r in csv.DictReader(stream)}
            expected = (2*lookup["FR"]+3*lookup["RF"]+7*lookup["JJ"])/12
            self.assertAlmostEqual(result["bounds"][metric]["lower"],expected,places=14)
            self.assertAlmostEqual(result["bounds"][metric]["upper"],expected,places=14)

    def test_unknown_mass_bounds_include_every_possible_assignment(self):
        table = actions([("F", "base"), ("J", "shift"), ("-", "base"), ("F", "base")])
        model = Mechanics()
        result = model.score(table)
        self.assertEqual(result["pair_count"], 3)
        self.assertEqual(result["supported_pair_count"], 1)
        self.assertEqual(result["shift_involving_pair_count"], 2)
        self.assertFalse(result["complete_domain"])
        self.assertFalse(result["whole_typing_comfort"])
        for metric in ("dvorak7", "engram_avg4"):
            score = model.pair("F", "J")[metric]
            interval = result["bounds"][metric]
            self.assertAlmostEqual(interval["lower"], score/3)
            self.assertAlmostEqual(interval["upper"], (score+2)/3)
            self.assertAlmostEqual(result["conditional_means"][metric], score)

    def test_no_supported_pairs_has_bounds_but_no_conditional_mean(self):
        result = Mechanics().score(actions([("-", "base"), ("=", "base")]))
        self.assertEqual(result["conditional_means"], {})
        self.assertEqual(result["bounds"]["dvorak7"], {"lower": 0, "upper": 1})
        single = Mechanics().score(actions([("F", "base")]))
        self.assertEqual(single["bounds"], {})
        self.assertIsNone(single["pair_coverage"])

    def test_shift_projection_and_scaling_are_explicit(self):
        steps = [("F", "base"), ("R", "base"), ("F", "base")]
        base = Mechanics().score(actions(steps))
        shifted = Mechanics().score(actions([(k,"shift") for k,_ in steps]))
        self.assertEqual(base["bounds"], shifted["bounds"])
        self.assertEqual(shifted["shift_involving_pair_count"], 2)
        scaled = ActionTables(9, 0, Counter({a:3*n for a,n in actions(steps).unigrams.items()}),
                              Counter({p:3*n for p,n in actions(steps).pairs.items()}))
        scaled_result = Mechanics().score(scaled)
        for metric, interval in base["bounds"].items():
            for side in ("lower", "upper"):
                self.assertAlmostEqual(interval[side], scaled_result["bounds"][metric][side], places=14)
        for metric in ("dvorak7", "engram_avg4"):
            self.assertAlmostEqual(sum(p[metric+"_deficit"] for p in base["top_deficits"][metric]),
                                   1-base["bounds"][metric]["lower"])

    def test_altgr_and_triple_missing_coverage_remain_unsupported(self):
        result = Mechanics().score(actions([("F", "altgr"), ("J", "base")]))
        self.assertEqual(result["supported_pair_count"], 0)
        triples = Counter({(("F","base"),("J","shift"),("F","base")): 2,
                           (("F","base"),("-","base"),("F","base")): 1})
        score = Mechanics().score_triples(triples)
        self.assertEqual(score["triple_count"], 3)
        self.assertEqual(score["bounds"], {"lower": 2/3, "upper": 1})

    def test_overlap_cannot_become_a_definite_ranking(self):
        values = {
            "A": {"J1": 1, **{m: {"lower": .4, "upper": .6} for m in ("dvorak7","engram_avg4","engram_order")}},
            "B": {"J1": 2, **{m: {"lower": .5, "upper": .7} for m in ("dvorak7","engram_avg4","engram_order")}},
        }
        self.assertIsNone(comparisons(values)[0]["dvorak7"]["higher"])


class TripleTests(unittest.TestCase):
    def test_independent_action_counts_repeats_escapes_and_word_boundaries(self):
        km = KeyMap("toy", [Action("F", "base", "ক"), Action("J", "shift", "ম")])
        rows = [("ককম", 2, 1, 1), ("কxম", 1, 0, 0)]
        record = {"N": 10, "space_units": 2, "tokens": 3, "out_of_inventory_characters": 1}
        tables, triples = count_stream(rows, km.encode, record, km.decode)
        independent = from_tokens(rows, km, record)
        self.assertEqual(tables.json(), independent.json())
        self.assertEqual(triples, Counter({(("F","base"),("F","base"),("J","shift")): 2}))
        self.assertEqual(triples_from_json(triples_json(triples)), triples)
        with self.assertRaisesRegex(ValueError, "token/unit"):
            count_stream(rows, km.encode, {**record, "N": 11}, km.decode)


class PublishedMechanicsTests(unittest.TestCase):
    def test_artifact_hashes_and_source_fidelity(self):
        root = PROJECT_ROOT / "results/evaluator-e2/run-v1"
        manifest = read_json(root / "run-manifest.json")
        for name, digest in manifest["output_sha256"].items():
            self.assertEqual(sha256_file(PROJECT_ROOT / name), digest, name)
        self.assertEqual(read_json(root / "source-fidelity.json"), audit())

    def test_public_averages_are_derived_from_all_corpora(self):
        root = PROJECT_ROOT / "results/evaluator-e2/run-v1"
        full = read_counts(root / "scores.json.gz")
        public = read_json(root / "public-summary.json")
        self.assertEqual(len(full["scores"]), (101+6)*3*2)
        self.assertEqual(len(full["candidates"]),101)
        self.assertEqual(full["stored_search_run_count"],1024)
        for scenario in ("traditional","model-optimal"):
            rows = [r for r in full["scores"] if r["public"] and r["scenario"]==scenario]
            self.assertEqual(len(rows),24)
            self.assertEqual(averaged(rows),public["public_summary"][scenario])
            self.assertEqual(comparisons(averaged(rows)),public["comparisons"][scenario])

    def test_direct_scoring_of_each_public_layout_from_saved_counts(self):
        from bangla_dh.experimental.actions import from_style
        from bangla_dh.experimental.inputs import load_candidates, frequency_path
        root = PROJECT_ROOT / "results/evaluator-e2/run-v1"
        public = read_json(root / "public-summary.json")
        candidates,_ = load_candidates(False)
        layouts = {next(n for n in c.names if n.startswith("Kala ")):c for c in candidates}
        for row in public["corpus_scores"]:
            if row["corpus"] != "bnwiki/heldout" or row["scenario"] != "traditional":
                continue
            name = row["name"]
            slug = name.lower().replace(" ","-").replace("(","").replace(")","")
            if name in layouts:
                candidate = layouts[name]
                cache = read_counts(root / "counts" / f"style-{candidate.style.lower()}-bnwiki-heldout.json.gz")
                assignment = candidate.assignment()
                table = from_style(read_json(frequency_path(candidate.style,"bnwiki/heldout")),assignment)
                triples = map_triples(triples_from_json(cache["triples"]),assignment)
            else:
                cache = read_counts(root / "counts" / f"baseline-{slug}-bnwiki-heldout.json.gz")
                table = ActionTables.from_json(cache["action_tables"])
                triples = triples_from_json(cache["triples"])
            mechanics = Mechanics()
            self.assertEqual(mechanics.score(table)["bounds"],row["mechanics"]["bounds"],name)
            self.assertEqual(mechanics.score_triples(triples)["bounds"],row["engram_order"]["bounds"],name)


if __name__ == "__main__":
    unittest.main()
