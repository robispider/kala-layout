"""Search-only changes: frozen scores, diversity and paired reproducibility."""
import random
import unittest

from bangla_dh.experimental.shared_explore import (
    CandidateArchive,BalanceOracle,PilotProblem,encode,hamming_encoded,paired_start,search_one,balance_walk)
from bangla_dh.experimental.shared_relaxed import relaxed_evaluate


class DiversityTests(unittest.TestCase):
    def test_encoded_hamming_matches_label_assignment_count(self):
        rng=random.Random(812)
        for _ in range(100):
            a=rng.sample(range(52),52);b=rng.sample(range(52),52)
            self.assertEqual(hamming_encoded(encode(a),encode(b),52),sum(x!=y for x,y in zip(a,b)))

    def test_top_energy_control_and_diverse_archive_remain_bounded(self):
        control=CandidateArchive(8);diverse=CandidateArchive(8,True)
        rng=random.Random(910)
        for i in range(30):
            p=rng.sample(range(12),12)
            values=[float((i+k)%7) for k in range(6)]
            control.offer(p,float(i),values);diverse.offer(p,float(i),values)
        self.assertEqual(len(control.rows),8);self.assertEqual(len(diverse.rows),8)
        self.assertEqual([r['q'] for r in control.retained()],list(map(float,range(8))))
        self.assertEqual(min(r['q'] for r in diverse.retained()),0.)
        self.assertTrue(all(sorted(r['perm'])==list(range(12)) for r in diverse.retained()))


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.problem=PilotProblem()

    def settings(self):
        return {'steps':40,'ils_iterations':0,'t_ratio':.0001,'control_archive':8,'diverse_archive':16,
            'frontier_limit':8,'early_full_budget':8,'full_interval':20,'diversity_interval':10,
            'early_score_batch':2,'early_neighbor_steps':4}

    def test_paired_starts_are_deterministic_and_include_same_4b_maps(self):
        for ordinal in range(12):
            a=paired_start(self.problem,ordinal,920+ordinal)
            b=paired_start(self.problem,ordinal,920+ordinal)
            self.assertEqual(a,b);self.problem.assignment(a[0])
        self.assertEqual(paired_start(self.problem,5,1)[0],self.problem.starts[5])

    def test_oracle_reuses_exact_model_and_enforces_budget_and_cache(self):
        p=self.problem;oracle=BalanceOracle(p,limit=1)
        perm=p.starts[-2];point=oracle.score(perm)
        self.assertIsNotNone(point)
        direct=p.evaluate_training(perm)
        self.assertEqual(point['R'],[relaxed_evaluate(direct[s]['metrics'],p.config['styles'][s])['R'] for s in ('A','D')])
        self.assertEqual(oracle.score(perm),point)
        self.assertIsNone(oracle.score(p.starts[-1]))
        self.assertEqual(oracle.stats['full_evaluations'],1)
        self.assertTrue(all(c.endswith('/train') for s,c in p.engines))

    def test_both_variants_reproduce_seeded_results_and_preserve_start_pairing(self):
        results=[]
        for variant in ('control','enhanced'):
            a=search_one(self.problem,variant,5,891,self.settings())
            b=search_one(self.problem,variant,5,891,self.settings())
            a.pop('seconds');b.pop('seconds');self.assertEqual(a,b)
            results.append(a)
            for r in a['archive']:self.problem.assignment(r['perm'])
        self.assertEqual(results[0]['start_perm'],results[1]['start_perm'])
        self.assertEqual(results[0]['early_full_points'],[])
        self.assertGreater(len(results[1]['early_full_points']),0)
        self.assertEqual(results[1]['search_stats']['early_checkpoints'],2)

    def test_full_score_walk_remains_eligible_and_budgeted(self):
        p=self.problem;oracle=BalanceOracle(p,limit=10)
        oracle.score(p.starts[-2]);oracle.score(p.starts[-1])
        perm,stats=balance_walk(p,oracle,random.Random(44),12,0)
        self.assertLessEqual(stats['neighbor_proposals'],12)
        self.assertTrue(p.eligible_fast(p.values(perm)))
        self.assertTrue(all(p.evaluate_training(perm)[s]['balance']['eligible'] for s in ('A','D')))


if __name__=='__main__':unittest.main()
