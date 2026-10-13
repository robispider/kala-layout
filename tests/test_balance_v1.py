import itertools
import unittest
from bangla_dh.experimental.balance_v1 import cost,credit_deficit,eligibility,evaluate


class BalanceV1Tests(unittest.TestCase):
    def setUp(self):
        self.ref={'J1_exact':'1','within_distance':.1}
        self.cal={'reference':self.ref,'aspirations':[1,.05,.05,.1],'scales':[.005,.02,.005,.02],
            'settings':[{'id':i,'weights':list(w),'rho':rho,'b_minus':0.}
                for i,(w,rho) in enumerate(itertools.product(list(itertools.product([6,8,10],[1],[.75,1,1.25],[.75,1,1.25])),[.025,.05,.075]))]}
        self.row={'J1_exact':'1','J1':1.,'cross_distance':.08,'within_distance':.09,'order_lower':.8,'order_upper':.9}

    def test_exact_effort_boundary_and_exclusion(self):
        self.assertTrue(eligibility({'J1_exact':'201/200','within_distance':.105},self.ref)[0])
        self.assertFalse(eligibility({'J1_exact':'1005000000001/1000000000000','within_distance':.1},self.ref)[0])
        row=dict(self.row,J1_exact='101/100',J1=1.01)
        self.assertIsNone(evaluate(row,self.cal)['R'])

    def test_interval_direction(self):
        self.assertEqual(credit_deficit(.7,.8),(.19999999999999996,.30000000000000004))
        high=evaluate(self.row,self.cal)['R']
        low=evaluate(dict(self.row,order_lower=.9,order_upper=.9),self.cal)['R']
        self.assertLessEqual(low,high)

    def test_fixed_calibration_is_independent_of_other_candidates(self):
        before=evaluate(self.row,self.cal)
        evaluate(dict(self.row,cross_distance=.01,within_distance=.01),self.cal)
        self.assertEqual(before,evaluate(self.row,self.cal))

    def test_component_dominance_is_weak_for_final_R(self):
        self.assertLess(evaluate(dict(self.row,cross_distance=.06),self.cal)['R'],evaluate(self.row,self.cal)['R'])
        # Positive-part truncation can tie strict component improvements at zero.
        self.cal['settings']=[dict(s,b_minus=100.) for s in self.cal['settings']]
        self.assertEqual(evaluate(self.row,self.cal)['R'],0.)
        self.assertEqual(evaluate(dict(self.row,cross_distance=.06),self.cal)['R'],0.)

    def test_unit_invariance_and_negative_deviations(self):
        a=cost([1,.08,.09,.2],[1,.05,.05,.1],[.005,.02,.005,.02],[8,1,1,1],.05)
        b=cost([1,80,.09,.2],[1,50,.05,.1],[.005,20,.005,.02],[8,1,1,1],.05)
        self.assertAlmostEqual(a,b)
        self.assertLess(cost([-1]*4,[0]*4,[1]*4,[1]*4,.05),0.)

    def test_missing_coverage_and_invalid_scale(self):
        self.assertEqual(credit_deficit(0,1),(0,1))
        with self.assertRaises(ValueError): cost([1]*4,[0]*4,[0,1,1,1],[1]*4,.05)
        with self.assertRaises(ValueError): credit_deficit(.9,.8)


if __name__=='__main__': unittest.main()
