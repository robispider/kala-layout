"""Independent scoring, coupled swaps, deterministic search and safe recovery."""
from fractions import Fraction
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from bangla_dh.paths import PROJECT_ROOT as ROOT, output_path, write_json
from bangla_dh.experimental.shared_problem import SharedProblem, SharedState, search_energy, pareto_offer
from bangla_dh.experimental.shared_search import VERSION, prepare, search_one
from bangla_dh.experimental.joint_search import settings_digest


class SharedScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problem = SharedProblem()

    def test_same_map_both_modes_and_six_fast_metrics_match_independent_counts(self):
        p = self.problem
        rng = random.Random(620)
        for perm in (p.starts[0],p.starts[2],rng.sample(range(p.n),p.n)):
            scores = p.evaluate_training(perm)
            self.assertEqual(set(scores),{'A','D'})
            for s in ('A','D'):
                self.assertEqual(Fraction(scores[s]['metrics']['J1_exact']),p.exact_effort(perm,s))
        self.assertTrue(all(c.endswith('/train') for s,c in p.integers))
        self.assertTrue(all(c.endswith('/train') for s,c in p.engines))

    def test_all_cached_deltas_and_resets_match_full_rescoring(self):
        p = self.problem
        state = SharedState(p,p.starts[0],'balance',.5)
        rng = random.Random(98)
        for _ in range(40):
            i,j = rng.sample(range(p.n),2)
            delta,changes = state.delta(i,j)
            trial = list(state.perm)
            trial[i],trial[j] = trial[j],trial[i]
            before = state.energy
            for k,s in enumerate(state.states):
                self.assertAlmostEqual(s.inst.score(trial)-s.score,changes[k],places=11)
            state.swap(i,j,changes)
            self.assertAlmostEqual(state.energy-before,delta,places=10)
            self.assertTrue(all(s.perm==trial for s in state.states))
        state.reset(p.starts[1])
        self.assertEqual(state.perm,p.starts[1])

    def test_original_objective_treats_relative_losses_symmetrically(self):
        self.assertAlmostEqual(search_energy([1.01,2.04],[1,2],'effort'),.02)
        self.assertAlmostEqual(search_energy([1.02,2.02],[1,2],'effort'),.02)
        with self.assertRaises(ValueError):
            self.problem.assignment([0]*52)

    def test_original_and_balance_leader_maps_do_not_pass_both_modes(self):
        for perm in self.problem.starts:
            scores = self.problem.evaluate_training(perm)
            self.assertFalse(all(scores[s]['balance']['eligible'] for s in ('A','D')))

    def test_search_seed_determines_all_saved_content_except_time(self):
        settings = {'steps':40,'ils_iterations':1,'archive_limit':3,'t_ratio':.0001}
        job = ('effort',0,719)
        a = search_one(self.problem,job,settings)
        b = search_one(self.problem,job,settings)
        a.pop('seconds'); b.pop('seconds')
        self.assertEqual(a,b)
        for row in a['archive']:
            self.problem.assignment(row['perm'])


class ParetoTests(unittest.TestCase):
    def test_separate_style_R_frontier_preserves_both_endpoints(self):
        rows=[]
        for perm,pair in enumerate(([1,3],[2,2],[3,1],[4,4],[1.5,2.5])):
            pareto_offer(rows,{'perm':[perm],'R':pair},3)
        self.assertEqual(rows[0]['R'],[1,3])
        self.assertEqual(rows[-1]['R'],[3,1])
        self.assertNotIn([4,4],[r['R'] for r in rows])
        self.assertEqual(len(rows),3)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        parent = output_path(ROOT/'work/evaluator-experiments/shared-tests')
        parent.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)/'run'
        self.settings = {'first_seed':12,'seeds':1}

    @patch('bangla_dh.experimental.shared_search.preserved_files',return_value={})
    def test_resume_rejects_changes_and_completed_runs(self,_):
        prepare(self.out,self.settings,{'input':'hash'})
        prepare(self.out,self.settings,{'input':'hash'},True)
        with self.assertRaisesRegex(ValueError,'resume refused'):
            prepare(self.out,self.settings,{'input':'changed'},True)
        with self.assertRaises(FileExistsError):
            prepare(self.out,self.settings,{'input':'hash'})
        write_json(self.out/'run-manifest.json',{})
        with self.assertRaisesRegex(ValueError,'completed'):
            prepare(self.out,self.settings,{'input':'hash'},True)

    @patch('bangla_dh.experimental.shared_search.preserved_files',return_value={})
    def test_orphan_recovery_and_tamper_detection(self,_):
        prepare(self.out,self.settings,{})
        path = self.out/'runs/effort-12.json'
        data = {'version':VERSION,'settings_sha256':settings_digest(self.settings),
                'id':'effort-12','arm':'effort','ordinal':0,'seed':12}
        write_json(path,data)
        _,_,progress,_ = prepare(self.out,self.settings,{},True)
        self.assertIn('effort-12',progress['completed'])
        write_json(path,{**data,'extra':'tampered'})
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            prepare(self.out,self.settings,{},True)

    def test_published_output_and_outside_workspace_are_rejected(self):
        for path in (ROOT/'results/kala-keyboards/new-run',ROOT.parent/'outside'):
            with self.assertRaisesRegex(ValueError,'output must'):
                prepare(path,self.settings,{})


if __name__=='__main__':
    unittest.main()
