import unittest
from reporting import load_baseline, fuel_scenario

class ReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.frame=load_baseline()
    def test_baseline_perimeters(self):
        self.assertEqual(len(self.frame),24)
        self.assertNotIn('emirates-airline',self.frame.index)
    def test_incentives_added_once(self):
        self.assertEqual(self.frame.loc['alaska','employee_cost_including_separate_incentives'],5031)
        self.assertEqual(self.frame.loc['jetblue','employee_cost_including_separate_incentives'],3453)
    def test_scenario_jetblue(self):
        r=fuel_scenario(self.frame.loc['jetblue'],.1)
        self.assertAlmostEqual(r['extra_fuel_expense'],205.7)
        self.assertAlmostEqual(r['scenario_operating_profit'],-573.7)
    def test_zero_shock(self):
        r=self.frame.loc['alaska']
        self.assertEqual(fuel_scenario(r,0)['scenario_operating_profit'],r.operating_profit)
    def test_invalid_or_missing_inputs(self):
        for shock in [-.1,1.1]:
            with self.assertRaises(ValueError):fuel_scenario(self.frame.loc['jetblue'],shock)
        with self.assertRaises(ValueError):fuel_scenario(self.frame.loc['ana'],.1)
    def test_cfo_capex_not_filled(self):
        self.assertTrue(self.frame.loc['korean','cfo_less_capex']!=self.frame.loc['korean','cfo_less_capex'])
    def test_ratios_not_cross_currency(self):
        self.assertAlmostEqual(self.frame.loc['alaska','debt_to_assets_pct'],6893/20361*100)
        self.assertAlmostEqual(self.frame.loc['jetblue','fuel_to_revenue_pct'],2057/9062*100)
    def test_partial_operating_subtotal_excluded(self):
        self.assertTrue(self.frame.loc['qatar','operating_margin_pct']!=self.frame.loc['qatar','operating_margin_pct'])

if __name__=='__main__':unittest.main()
