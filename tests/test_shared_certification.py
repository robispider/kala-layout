"""Independent brute-force checks of deltas, enclosures, scope and replay."""
from collections import Counter
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import random
import tempfile
import unittest

from bangla_dh.paths import PROJECT_ROOT as ROOT, output_path
from bangla_dh.shared_certification import (Checker, PairPolynomial, Interval,
    DirectWitness, enclosure, balance_interval, input_digest, neighbourhood, run, verify)


class SharedCertificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = Checker()

    def test_neighbourhood_is_complete_without_duplicates(self):
        for size in range(2,7):
            generated = []
            for changes in neighbourhood(size):
                p = list(range(size))
                for i,j in changes: p[i]=j
                generated.append(tuple(p))
            brute = {p for p in itertools.permutations(range(size)) if 2 <= sum(i!=j for i,j in enumerate(p)) <= 3}
            self.assertEqual(set(generated),brute)
            self.assertEqual(len(generated),len(brute))
        self.assertEqual(Counter(len(c) for c in neighbourhood(52)),{2:1326,3:44200})

    def test_integer_delta_matches_direct_polynomial_for_every_small_permutation(self):
        rng = random.Random(232)
        size, variable = 6,4
        costs = [[rng.randrange(-30,80) for _ in range(size)] for _ in range(size)]
        table = [costs[min(i,j)][max(i,j)] for i in range(size) for j in range(size)]
        pairs = [(i,j,rng.randrange(25)) for i in range(size) for j in range(size)]
        unary = {i:rng.randrange(30) for i in range(size)}
        keys = [rng.randrange(-20,80) for _ in range(size)]
        kernel = PairPolynomial(list(range(size)),variable,unary,pairs,keys,table,97)
        for perm in itertools.permutations(range(variable)):
            ids = list(perm)+[4,5]
            changes = [(i,j) for i,j in enumerate(perm) if i!=j]
            direct = sum(c*keys[ids[i]] for i,c in unary.items())+sum(c*table[ids[i]*size+ids[j]] for i,j,c in pairs)
            self.assertEqual(kernel.value(changes),Fraction(direct,97))
        asymmetric = list(table); asymmetric[1]+=1
        with self.assertRaisesRegex(ValueError,'asymmetric'):
            PairPolynomial(list(range(size)),variable,unary,pairs,keys,asymmetric,97)

    def test_positive_sum_error_bound_encloses_actual_float_chain(self):
        rng = random.Random(82)
        for n in (1,20,4500):
            for _ in range(3):
                terms = [(rng.randrange(1,10**9),rng.random()*4) for i in range(n)]
                exact = sum((count*Fraction(distance) for count,distance in terms),Fraction())/123456789
                actual = 0.
                for count,distance in terms: actual += count*distance
                actual /= 123456789
                bound = enclosure(exact,n+6)
                self.assertLessEqual(bound.lo,actual); self.assertGreaterEqual(bound.hi,actual)

    def test_interval_balance_handles_negative_terms_and_max_changes(self):
        c = self.checker
        rng = random.Random(228)
        for style in ('A','D'):
            cal = c.data['calibration'][style]
            for _ in range(20):
                values = [a+(rng.random()-.5)*t*4 for a,t in zip(cal['aspirations'],cal['scales'])]
                bound = balance_interval([Interval(v) for v in values],cal)
                scores=[]
                for setting in cal['settings']:
                    terms = [w*(x-a)/t for x,a,t,w in zip(values,cal['aspirations'],cal['scales'],setting['weights'])]
                    scores.append(max(0.,(max(terms)+setting['rho']*sum(terms))/sum(setting['weights'])-setting['b_minus']))
                self.assertLessEqual(bound.lo,max(scores)); self.assertGreaterEqual(bound.hi,max(scores))

    def assert_portable_enclosed(self, changes):
        c = self.checker
        actual = c.scorer.evaluate(c.submission(changes),c.data)
        bounds = c.intervals(changes)
        for style in ('A','D'):
            row = actual['scores'][style]
            self.assertEqual(c.kernels[style]['J1'].value(changes),Fraction(row['training']['J1_exact']))
            for key,field in [('J1','J1'),('W','within_distance'),('C','cross_distance'),('O','order_lower')]:
                self.assertLessEqual(bounds[style][key].lo,row['training'][field])
                self.assertGreaterEqual(bounds[style][key].hi,row['training'][field])
            if row['balance']['eligible']:
                self.assertLessEqual(bounds[style]['R'].lo,row['balance']['R'])
                self.assertGreaterEqual(bounds[style]['R'].hi,row['balance']['R'])
        checked = c.check(changes)
        if checked['status'] in ('effort_ineligible','within_ineligible'):
            self.assertFalse(actual['eligible'])
        elif checked['status']=='cannot_dominate':
            self.assertFalse(actual['improves_reference'])

    def test_full_scorer_parity_on_finalist_and_diverse_moves(self):
        c = self.checker
        positions = {a:i for i,a in enumerate(c.actions)}
        a,b = positions['W','shift'],positions['X','shift']
        self.assert_portable_enclosed(((a,b),(b,a)))
        for ix,changes in enumerate(neighbourhood(52)):
            if ix in (0,100,500,1000,1325,1326,1400,2000,10000,30000,45525):
                self.assert_portable_enclosed(changes)
        self.assertTrue(all(c.verify_reference().values()))

    def test_an_ambiguous_boundary_is_not_a_certificate(self):
        # Identity is not enumerated. Its overlapping bounds must not be
        # mistaken for either a strict improvement or certified exclusion.
        row = self.checker.check(())
        self.assertEqual(row['status'],'unresolved')
        self.assertFalse(row['observed']['improves_reference'])

    def test_direct_witness_rejects_incorrect_exact_record(self):
        c=self.checker
        for changes in neighbourhood(52,2):
            row=c.check(changes)
            if row['status']=='effort_ineligible':
                direct=DirectWitness(c)
                direct.check(row,changes)
                row['exact_J1']='0'
                with self.assertRaisesRegex(ValueError,'independent effort witness'):
                    direct.check(row,changes)
                break

    def test_artifact_replay_and_tamper_detection(self):
        parent=output_path(ROOT/'work/shared-certificate-tests'); parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            out=Path(temp)
            quiet=lambda *args,**kwargs: None
            result=run(out,2,quiet)
            self.assertEqual(result['checked_alternatives'],1326)
            self.assertEqual(result['classification'],'certified neighbourhood non-dominance')
            self.assertTrue(verify(out,quiet))
            with self.assertRaisesRegex(ValueError,'empty output'):
                run(out,2,quiet)
            path=output_path(out/'certificate.json')
            path.write_text('{}\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                verify(out,quiet)

    def test_source_hashes_survive_line_endings_but_detect_semantic_changes(self):
        parent=output_path(ROOT/'work/shared-certificate-tests'); parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            path=output_path(Path(temp)/'source.py')
            path.write_bytes(b'x = 1\n')
            digest=input_digest(path)
            path.write_bytes(b'x = 1\r\n')
            self.assertEqual(input_digest(path),digest)
            path.write_bytes(b'x = 2\r\n')
            self.assertNotEqual(input_digest(path),digest)


if __name__ == '__main__': unittest.main()
