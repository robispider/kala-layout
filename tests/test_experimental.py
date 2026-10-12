"""Season e1 checks arithmetic, evidence gates, Bangla actions and preservation."""
import json
import math
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from bangla_dh.bangla.grammar import Action, Escape, KeyMap, UnitSet, nfc, segment
from bangla_dh.bangla.styles import Style
from bangla_dh.paths import PROJECT_ROOT, output_path, write_text
from bangla_dh.scoring.j0 import score_tokens, token_cost
from bangla_dh.scoring.model import ANSI_GRID, ANSI_TRADITIONAL_GRID, KeyModel
from bangla_dh.search.problem import load_problem, parse_slot
from bangla_dh.search import keystrokes
from bangla_dh.experimental.actions import ActionTables, SPACE_ACTION, from_style, from_tokens, j_reference, diagnostics
from bangla_dh.experimental.inputs import load_candidates, validate_layout
from bangla_dh.experimental.preferences import PairPreferences, SOURCE
from bangla_dh.experimental.safety import new_run_directory
from bangla_dh.experimental.evaluate import descriptive_frontier
from bangla_dh.experimental.report import render

TRADITIONAL = KeyModel.from_grid(ANSI_TRADITIONAL_GRID)
OPTIMAL = KeyModel.from_grid(ANSI_GRID)


def table(keys):
    actions = [(k, layer) for k, layer in keys]
    return ActionTables(len(actions), 0, Counter(actions) + Counter(),
                        Counter(zip(actions, actions[1:])))


class ActionTests(unittest.TestCase):
    def test_hand_counted_direction_repeats_and_chords(self):
        t = table([("F", "base"), ("R", "base"), ("F", "base"), ("J", "base")])
        d = diagnostics(t, TRADITIONAL)
        self.assertEqual(d["non_space_pair_count"], 3)
        self.assertEqual(d["same_finger_different_key_count"], 2)
        self.assertEqual(d["cross_hand_pair_count"], 1)
        repeat = table([("F", "base"), ("F", "base"), ("F", "shift")])
        self.assertEqual(sum(repeat.pairs.values()), 2)
        self.assertEqual(diagnostics(repeat, TRADITIONAL)["same_physical_key_repeat_count"], 2)
        r = j_reference(repeat, TRADITIONAL)
        self.assertAlmostEqual(r["E2_same_finger"], 2.5 / 3)
        self.assertAlmostEqual(r["M"], TRADITIONAL.effort("RSHIFT") / 3)

    def test_independent_direct_scoring_and_scaling(self):
        keys = [("F", "base"), ("R", "base"), ("J", "shift"), ("J", "shift")]
        t = table(keys)
        direct = token_cost([Action(k, l, "") for k, l in keys], TRADITIONAL)
        r = j_reference(t, TRADITIONAL)
        self.assertAlmostEqual(r["J0"], (direct[0] + sum(direct[1].values())) / 4)
        self.assertAlmostEqual(r["J1"], (direct[0] + sum(direct[1].values()) + direct[4]) / 4)
        scaled = ActionTables(12, 0, Counter({a: 3*c for a,c in t.unigrams.items()}),
                              Counter({p: 3*c for p,c in t.pairs.items()}))
        for key, value in r.items():
            self.assertAlmostEqual(value, j_reference(scaled, TRADITIONAL)[key], places=13)
        self.assertAlmostEqual(PairPreferences().score(t, TRADITIONAL)["conditional_pair_preference"],
                               PairPreferences().score(scaled, TRADITIONAL)["conditional_pair_preference"], places=14)

    def test_baseline_nukta_conjunct_digits_modifier_escape_and_boundaries(self):
        km = KeyMap("toy", [Action("F", "base", "ক"), Action("R", "base", "া"),
            Action("J", "base", "ম"), Action("L", "shift", "ি"), Action("D", "base", "ড়"),
            Action("1", "base", "১"), Action("G", "base", "্"), Action("T", "base", "ষ")])
        rows = [("কা",2,1,0), ("মি",1,0,1), ("ড়",1,1,1), ("১",1,1,1), ("ক্ষ",1,1,1), ("x",1,1,1)]
        record = {"N":13,"space_units":2,"tokens":7,"out_of_inventory_characters":1}
        t = from_tokens(rows, km, record)
        self.assertEqual(t.round_trip_types,6)
        self.assertEqual(sum(t.pairs.values()),9)
        self.assertEqual(t.pairs[("F","base"),("R","base")],2)
        self.assertEqual(t.pairs[("R","base"),SPACE_ACTION],2)
        self.assertEqual(t.outside_inventory,1)
        reference = score_tokens(km,[(w,c) for w,c,_,_ in rows],13,TRADITIONAL)
        actual = j_reference(t,TRADITIONAL)
        self.assertAlmostEqual(actual["J0"],reference["J0"],places=12)
        self.assertAlmostEqual(actual["J1"],reference["J1"],places=12)
        shuffled = from_tokens(list(reversed(rows)),km,record)
        self.assertEqual(t.unigrams,shuffled.unigrams)
        self.assertEqual(t.pairs,shuffled.pairs)
        self.assertEqual(t.json(),ActionTables.from_json(t.json()).json())

    def test_escape_breaks_chain_and_altgr_stays_undefined(self):
        km = KeyMap("toy",[Action("F","base","ক"),Action("J","altgr","ম")])
        t = from_tokens([("কxম",1,1,1)],km,{"N":2,"space_units":0,"tokens":1})
        self.assertEqual(sum(t.pairs.values()),0)
        self.assertIsNone(j_reference(t,TRADITIONAL)["J1"])
        self.assertIsNotNone(j_reference(t,TRADITIONAL)["J0"])

    def test_style_grammar_and_repeated_labels_are_preserved(self):
        problem = load_problem()
        units = UnitSet.from_inventory()
        words = [nfc(x) for x in ("বই","তিনিই","ক্ষমতা","ড়ঢ়য়","৩০","কxম")]
        for style in ("A","D"):
            keystrokes._init(style)
            raw = keystrokes.count_batch([(w,1,1,1) for w in words])
            record = {"N":raw["units"],"space_units":0,"label_counts":raw["labels"],
                      "pair_counts":[[a,b,c] for (a,b),c in raw["pairs"].items()],
                      "keystrokes_excluding_space":raw["keystrokes"],
                      "escaped_unit_count":sum(raw["escaped_units"].values()),
                      "outside_inventory_count":sum(raw["oov"].values())}
            mapping = dict(zip(problem["styles"][style]["searched_symbols"],
                               [parse_slot(s) for s in problem["slots"]]))
            mapping.update({k:parse_slot(v) for k,v in problem["fixed"].items()})
            t = from_style(record,mapping)
            direct = 0.0
            for w in words:
                machine = Style(style)
                self.assertEqual(machine.decode(machine.encode(w)),w)
                steps = [x if isinstance(x,Escape) else Action(*mapping[x],x) for x in machine.encode(w)]
                e,parts,_,_,m = token_cost(steps,TRADITIONAL)
                direct += e+sum(parts.values())+m
            self.assertAlmostEqual(j_reference(t,TRADITIONAL)["J1"],direct/record["N"],places=12)
            if style == "D":
                self.assertGreater(sum(c for (a,b),c in t.pairs.items() if a==b),0)
            bad = dict(mapping);bad.pop("ক")
            with self.assertRaises(ValueError):from_style(record,bad)

    def test_bad_denominators_and_counts_fail(self):
        with self.assertRaises(ValueError):ActionTables(0,0).validate()
        with self.assertRaises(ValueError):ActionTables(1,0,Counter({("F","base"):-1})).validate()
        km = KeyMap("toy",[Action("F","base","ক")])
        with self.assertRaises(ValueError):from_tokens([("ক",1,1,1)],km,{"N":2,"space_units":0,"tokens":1})


class PreferenceTests(unittest.TestCase):
    def test_original_source_lookup_and_direction(self):
        m = PairPreferences()
        self.assertEqual(len(m.scores),288)
        self.assertNotEqual(m.scores["FR"],m.scores["RF"])
        t = table([("F","base"),("R","base"),("F","base"),("J","base")])
        result = m.score(t,TRADITIONAL)
        self.assertEqual(result["supported_pair_count"],2)
        self.assertAlmostEqual(result["conditional_pair_preference"],(-0.677292026794966-0.693101883957305)/2)
        self.assertAlmostEqual(result["supported_pair_share"],2/3)
        self.assertIsNone(result["full_layout_score"])
        self.assertFalse(result["ranking_allowed"])
        self.assertTrue(m.evidence()["lookup_benchmark_pass"])
        self.assertFalse(m.evidence()["full_layout_admitted"])
        self.assertFalse(m.evidence()["heldout_prediction_reproduced"])

    def test_shift_missing_fingers_and_no_coverage_are_not_zero(self):
        m = PairPreferences()
        shift = m.score(table([("F","shift"),("R","base")]),TRADITIONAL)
        self.assertEqual(shift["unsupported_pair_counts"],{"unsupported_layer":1})
        self.assertIsNone(shift["conditional_pair_preference"])
        optimal = m.score(table([("C","base"),("F","base")]),OPTIMAL)
        self.assertEqual(optimal["unsupported_pair_counts"],{"different_fingering":1})
        missing = m.score(table([("G","base"),("F","base")]),TRADITIONAL)
        self.assertEqual(missing["unsupported_pair_counts"],{"no_source_pair":1})
        repeat = m.score(table([("F","base"),("F","base")]),TRADITIONAL)
        self.assertEqual(repeat["supported_pair_count"],1)

    def test_source_tampering_rejected(self):
        parent=output_path(PROJECT_ROOT/"work/evaluator-experiments/tests")
        parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            tmp=Path(tmp)
            for p in SOURCE.iterdir():
                if p.is_file():output_path(tmp/p.name).write_bytes(p.read_bytes())
            write_text(tmp/"pair-scores.csv","key_pair,comfort_score,uncertainty\nFF,999,0\n")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):PairPreferences(tmp)


class CandidateAndSafetyTests(unittest.TestCase):
    def test_dedup_retains_all_search_provenance_and_published_maps(self):
        candidates,_=load_candidates(True)
        self.assertEqual(sum(o["kind"]=="runs" for c in candidates for o in c.origins),1024)
        self.assertLess(len(candidates),1024)
        self.assertEqual(sum(any(n.startswith("Kala ") for n in c.names) for c in candidates),2)
        for c in candidates:validate_layout(c.style,c.layout)
        bad=dict(candidates[0].layout);label=next(iter(bad));bad[label]=("1","base")
        with self.assertRaises(ValueError):validate_layout(candidates[0].style,bad)

    def test_output_guard_and_existing_run_refusal(self):
        with self.assertRaises(ValueError):new_run_directory(PROJECT_ROOT/"results/phase1/never-create")
        with self.assertRaises(ValueError):new_run_directory(PROJECT_ROOT/"work/evaluator-experiments/../../results/phase1")
        with self.assertRaises(ValueError):new_run_directory(PROJECT_ROOT.parent/"outside")
        parent=output_path(PROJECT_ROOT/"work/evaluator-experiments/tests")
        parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            path=new_run_directory(Path(tmp)/"new")
            self.assertTrue(path.is_dir())
            with self.assertRaises(FileExistsError):new_run_directory(path)

    def test_descriptive_frontier_and_report_do_not_rank_preference(self):
        rows=[{"id":"a","training_J1":1,"training_shift_per_unit":1,"training_sfb_per_unit":1},
              {"id":"b","training_J1":2,"training_shift_per_unit":2,"training_sfb_per_unit":2},
              {"id":"c","training_J1":0.5,"training_shift_per_unit":2,"training_sfb_per_unit":1}]
        self.assertEqual(descriptive_frontier(rows),["a","c"])
        self.assertIn("Full-layout preference scoring and comfort-based candidate selection are withheld",
                      render({"evidence":PairPreferences().evidence()}))


if __name__=="__main__":unittest.main()
