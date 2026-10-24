import copy
import json
from pathlib import Path
import unittest
from analysis import calculate, ratio, fuel_sensitivity


class ResearchChecks(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).parents[1] / 'data/jetblue.json').read_text())

    def test_pilot_ties_to_reported_operating_loss(self):
        v = self.data['observations']
        self.assertEqual(v['revenue']['value'] - v['operating_costs']['value'], v['ebit']['value'])
        result = calculate(self.data)
        self.assertAlmostEqual(result['debt_to_equity_x'], 5.34215500945)
        self.assertEqual(result['cfo_less_capex_and_deposits_usd_m'], -410)
        self.assertLess(result['half_year_ebit_gross_interest_x'], 0)

    def test_negative_equity_is_not_healthy_gearing(self):
        self.assertIsNone(ratio(100, -50))
        self.assertIsNone(ratio(100, 0))
        self.assertLess(ratio(-10, 5), 0)

    def test_missing_cash_does_not_become_zero(self):
        missing = copy.deepcopy(self.data)
        missing['observations']['cash']['value'] = None
        self.assertIsNone(calculate(missing)['debt_less_cash_usd_m'])

    def test_fuel_shock_boundaries(self):
        self.assertEqual(fuel_sensitivity(100, .2, 1, 0), 0)
        self.assertEqual(fuel_sensitivity(100, .2, 0, 1), 0)
        self.assertAlmostEqual(fuel_sensitivity(100, .2, 0, .5), 10)
        self.assertIsNone(fuel_sensitivity(100, .2, None, 0))
        with self.assertRaises(ValueError):
            fuel_sensitivity(100, .2, 1.1, 0)

    def test_source_required(self):
        self.data['observations']['debt']['source'] = 'unknown'
        with self.assertRaises(ValueError):
            calculate(self.data)


if __name__ == '__main__':
    unittest.main()
