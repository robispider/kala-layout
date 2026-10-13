import unittest
from bangla_dh.experimental.balance_stability import eligible,balance,regret_bounds


class StabilityTests(unittest.TestCase):
    def test_effort_cap_exact_boundary(self):
        ref={'J1_exact':'1','within_distance':1.}
        self.assertTrue(eligible({'J1_exact':'201/200','within_distance':1.05},ref,.5,5))
        self.assertFalse(eligible({'J1_exact':'1005000000001/1000000000000','within_distance':1.},ref,.5,5))

    def test_scope_specific_within_guard(self):
        self.assertFalse(eligible({'J1_exact':'1','within_distance':1.06},{'J1_exact':'1','within_distance':1.},1,5))

    def test_weight_homogeneity(self):
        self.assertAlmostEqual(balance([1,2,3],[8,1,1],.05),balance([1,2,3],[80,10,10],.05))

    def test_regret_zero_negative_and_translation(self):
        expected=[(0,0),(2,2)]
        self.assertEqual(regret_bounds([-3,-1],[-3,-1]),expected)
        self.assertEqual(regret_bounds([0,2],[0,2]),expected)

    def test_coverage_regret_contains_all_realizations(self):
        lower,upper=[0,1],[2,3]
        bounds=regret_bounds(lower,upper)
        for a in [0,1,2]:
            for b in [1,2,3]:
                for value,(lo,hi) in zip([a-min(a,b),b-min(a,b)],bounds): self.assertTrue(lo<=value<=hi)
        self.assertEqual(bounds,[(0,2),(0,3)])

    def test_invalid_bounds(self):
        with self.assertRaises(ValueError): regret_bounds([2],[1])


if __name__=='__main__': unittest.main()
