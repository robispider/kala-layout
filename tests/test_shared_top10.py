"""Selection avoids mixed R scales; gates and means retain the frozen model."""
import importlib.util
from pathlib import Path
import random
import unittest

from bangla_dh.paths import PROJECT_ROOT as ROOT
from bangla_dh.experimental.shared_relaxed import RelaxedProblem
from bangla_dh.experimental.inputs import read_json

spec=importlib.util.spec_from_file_location('shared_top10_analysis',ROOT/'results/shared-top10-comparison-v1/analyze.py')
analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)


def row(identity,a,d):return {'id':identity,'R':[a,d]}


class RankingTests(unittest.TestCase):
    def test_frontier_preserves_tradeoffs_and_equal_vectors(self):
        data=[row('a',1,3),row('a2',1,3),row('b',3,1),row('c',2,3),row('d',4,4)]
        self.assertEqual({r['id'] for r in analysis.frontier(data)},{'a','a2','b'})

    def test_layers_put_dominated_candidates_after_the_front(self):
        data=[row('a',1,3),row('b',3,1),row('c',2,4),row('d',4,2),row('e',5,5)]
        ranked=analysis.top_layers(data,5)
        self.assertEqual([r['id'] for r in ranked[:2]],['a','b'])
        self.assertEqual([r['layer'] for r in ranked],[1,1,2,2,3])

    def test_independent_positive_mode_rescaling_cannot_change_selection(self):
        data=[row(str(i),i+1,20-i) for i in range(12)]+[row('dominated',30,30)]
        changed=[row(r['id'],r['R'][0]*100,r['R'][1]/1000) for r in data]
        self.assertEqual([(r['id'],r['layer']) for r in analysis.top_layers(data)],
                         [(r['id'],r['layer']) for r in analysis.top_layers(changed)])


class MetricTests(unittest.TestCase):
    def test_equal_source_means_do_not_pool_counts(self):
        a={k:1. for k in analysis.METRICS};b={k:9. for k in analysis.METRICS}
        a.update(J1_exact='1',N=1);b.update(J1_exact='9',N=99)
        self.assertEqual(analysis.mean_metrics([a,b])['J1'],5.)
        self.assertEqual(analysis.mean_metrics([a,b])['J1_exact'],'5')

    def test_favorable_baseline_envelope_uses_each_metric_best_case(self):
        a={'J1':2.,'within_distance':.3,'cross_distance':.1,'order_lower':.7,'order_upper':.8}
        b={'J1':1.,'within_distance':.2,'cross_distance':.4,'order_lower':.75,'order_upper':.85}
        e=analysis.favorable_envelope([a,b])
        self.assertEqual([e[k] for k in analysis.LOWER],[1.,.2,.1])
        self.assertEqual(e['order_lower'],.7);self.assertEqual(e['order_upper'],.85)

    def test_bijoy_proxy_is_mapping_equality_not_file_or_engine_identity(self):
        record=analysis.mapping_alias()
        self.assertTrue(all(record['physical_layers_equal'].values()))
        self.assertFalse(record['raw_files_identical'])
        self.assertFalse(record['bijoy_has_own_vowel_rules'])

    def test_early_rejection_gate_matches_original_six_metric_gate(self):
        p=RelaxedProblem();rng=random.Random(882)
        perms=[*p.starts,*[rng.sample(range(p.n),p.n) for _ in range(20)]]
        for name in ('shared-f9096b7bb25243ef','shared-76c9b9dbfc689d0b','shared-7083b1ebfa5aa3a7'):
            raw=read_json(ROOT/'results/shared-layout-relaxed-v1/run-4b-v1/layouts'/(name+'.json'))
            perms.append(p.perm_of({s:tuple(v.split('/')) for s,v in raw['layout'].items()}))
        for perm in perms:self.assertEqual(analysis.fast_gate(p,perm),p.eligible_fast(p.values(perm)))


if __name__=='__main__':unittest.main()
