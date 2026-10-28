"""Explicit revised caps, frozen calibration and coupled-search correctness."""
from fractions import Fraction
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from bangla_dh.paths import PROJECT_ROOT as ROOT, output_path, write_json
from bangla_dh.experimental.balance_v1 import evaluate
from bangla_dh.experimental.joint_search import settings_digest
from bangla_dh.experimental.shared_relaxed import (
    VERSION, RelaxedProblem, RelaxedState, relaxed_evaluate, search_one, prepare)


class RelaxedScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problem = RelaxedProblem()

    def test_prior_shared_candidate_qualifies_only_under_revised_policy(self):
        p = self.problem
        scores = p.evaluate_training(p.starts[-1])
        for s in ('A','D'):
            row = scores[s]
            self.assertTrue(row['balance']['eligible'])
            self.assertFalse(row['balance']['original_balance_v1_eligible'])
            self.assertIsNone(evaluate(row['metrics'],p.config['styles'][s])['R'])
            self.assertIsNotNone(row['balance']['R'])

    def test_original_eligible_scores_are_identical_without_recalibration(self):
        p = self.problem
        for s,perm in (('A',p.starts[2]),('D',p.starts[3])):
            metrics = p.evaluate_training(perm)[s]['metrics']
            original = evaluate(metrics,p.config['styles'][s])
            revised = relaxed_evaluate(metrics,p.config['styles'][s])
            self.assertTrue(original['eligible'])
            self.assertEqual(original['R'],revised['R'])

    def test_exact_effort_boundary_and_direct_within_boundary(self):
        p = self.problem
        cal = p.config['styles']['A']
        row = p.evaluate_training(p.starts[-1])['A']['metrics']
        boundary = Fraction(cal['reference']['J1_exact'])*Fraction(403,400)
        exact = dict(row,J1_exact=str(boundary),J1=float(boundary),
                     within_distance=cal['reference']['within_distance']*1.075)
        self.assertTrue(relaxed_evaluate(exact,cal)['eligible'])
        excessive = boundary+Fraction(1,10**18)
        self.assertFalse(relaxed_evaluate(dict(exact,J1_exact=str(excessive),J1=float(excessive)),cal)['effort_cap_pass'])
        self.assertFalse(relaxed_evaluate(dict(exact,within_distance=exact['within_distance']+1e-10),cal)['within_cap_pass'])

    def test_six_coupled_swap_deltas_match_full_revised_objective(self):
        p = self.problem
        state = RelaxedState(p,p.starts[-1],'balance',.5)
        rng = random.Random(771)
        for _ in range(24):
            i,j = rng.sample(range(p.n),2)
            d,ds = state.delta(i,j)
            trial = list(state.perm)
            trial[i],trial[j] = trial[j],trial[i]
            other = RelaxedState(p,trial,'balance',.5)
            self.assertAlmostEqual(d,other.energy-state.energy,places=10)
            state.swap(i,j,ds)
            self.assertTrue(all(s.perm==trial for s in state.states))

    def test_revised_seeded_search_is_reproducible(self):
        settings={'steps':60,'ils_iterations':1,'archive_limit':3,'t_ratio':.0001}
        a=search_one(self.problem,('balance',4,924),settings)
        b=search_one(self.problem,('balance',4,924),settings)
        a.pop('seconds');b.pop('seconds')
        self.assertEqual(a,b)
        self.assertIn(a['endpoint'],[r['perm'] for r in a['archive']])


class RelaxedRecoveryTests(unittest.TestCase):
    def setUp(self):
        parent=output_path(ROOT/'work/evaluator-experiments/relaxed-tests')
        parent.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.out=Path(self.tmp.name)/'run'
        self.settings={'seeds':1,'first_seed':42}

    @patch('bangla_dh.experimental.shared_relaxed.preserved_files',return_value={})
    def test_resume_checks_caps_inputs_checkpoints_and_completion(self,_):
        prepare(self.out,self.settings,{})
        prepare(self.out,self.settings,{},True)
        with self.assertRaisesRegex(ValueError,'resume refused'):
            prepare(self.out,{**self.settings,'effort_allowance_exact':'1/200'},{},True)
        path=self.out/'runs/effort-42.json'
        data={'version':VERSION,'settings_sha256':settings_digest(self.settings),
              'id':'effort-42','arm':'effort','ordinal':0,'seed':42}
        write_json(path,data)
        prepare(self.out,self.settings,{},True)
        write_json(path,{**data,'changed':True})
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            prepare(self.out,self.settings,{},True)
        write_json(path,data)
        write_json(self.out/'run-manifest.json',{})
        with self.assertRaisesRegex(ValueError,'completed'):
            prepare(self.out,self.settings,{},True)


if __name__=='__main__':
    unittest.main()
