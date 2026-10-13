"""Meaningful mathematical and event-scope regressions for the isolated study."""
import unittest
from fractions import Fraction
from collections import Counter

from bangla_dh.experimental.balance_study import score, deficit, average
from bangla_dh.experimental.joint_problem import achievement
from bangla_dh.experimental.actions import ActionTables, diagnostics
from bangla_dh.experimental.mechanics import evaluator
from bangla_dh.scoring.model import KeyModel


class BalanceStudyTests(unittest.TestCase):
    def test_augmented_strict_dominance_when_max_unchanged(self):
        # Max alone ties; augmentation must reward improvement in another component.
        self.assertLess(score([2,1],[0,0],[1,1],[3,1],.01),score([2,2],[0,0],[1,1],[3,1],.01))

    def test_units_translation_and_negative_deviations(self):
        a=score([1,2],[2,1],[.5,2],[4,1],.05)
        self.assertAlmostEqual(a,score([100,2],[200,1],[50,2],[4,1],.05))
        self.assertAlmostEqual(a,score([11,2],[12,1],[.5,2],[4,1],.05))
        self.assertLess(score([-2,-1],[0,0],[1,1],[1,1],.1),0)

    def test_scale_weights_missing_and_constants(self):
        for scales,weights,rho,values in [([0,1],[1,1],.1,[1,2]),([1,1],[0,1],.1,[1,2]),([1,1],[1,1],0,[1,2]),([1,1],[1,1],.1,[None,2])]:
            with self.assertRaises(ValueError): score(values,[0,0],scales,weights,rho)
        self.assertEqual(score([2,2],[2,2],[1,1],[1,1],.1),0)

    def test_credit_interval_endpoints_and_missing(self):
        self.assertEqual(deficit(.25,.75),(.25,.75))
        self.assertEqual(deficit(0,.2),(.8,1))
        self.assertEqual(deficit(0,1),(0,1))
        with self.assertRaises(ValueError): deficit(.8,.4)

    def test_source_weighting_is_not_pooled(self):
        a={'J1':1.,'J1_exact':'1','cross_rate':.1,'N':100,'order_evaluated':False}
        b={'J1':3.,'J1_exact':'3','cross_rate':.3,'N':900,'order_evaluated':False}
        mixed=average(a,b)
        self.assertEqual(Fraction(mixed['J1_exact']),2)
        self.assertAlmostEqual(mixed['cross_rate'],.2)
        self.assertNotAlmostEqual(mixed['cross_rate'],.28)

    def test_reference_centered_e4_rejects_higher_j_tradeoff(self):
        self.assertEqual(achievement(1,1,1,1,.5),0)
        self.assertGreater(achievement(1.001,.8,1,1,.5),0)
        self.assertGreater(achievement(1.001,.8,1,1,0),0)

    def test_repeats_and_unsupported_scope(self):
        # Identical physical key across layers is a repeat, not SF travel.
        tables=ActionTables(10,0,Counter({('F','base'):3,('F','shift'):2,('SPACE','base'):0}),
            Counter({(('F','base'),('F','base')):1,(('F','base'),('F','shift')):1}),escaped_units=2)
        d=diagnostics(tables,KeyModel.from_grid())
        self.assertEqual(d['same_physical_key_repeat_count'],2)
        self.assertEqual(d['same_finger_different_key_count'],0)
        self.assertEqual(d['same_finger_center_distance_u_per_unit'],0)
        self.assertEqual(d['escaped_unit_share'],.2)
        ev=evaluator('model-optimal')
        self.assertIsNone(ev.pair('UNKNOWN','F'))
        self.assertEqual(ev.pair('F','F')['engram_same_finger'],0)
        result=ev.score_triples({(('UNKNOWN','base'),('F','base'),('J','base')):4})
        self.assertEqual(result['bounds'],{'lower':0.,'upper':1.})


if __name__=='__main__': unittest.main()
