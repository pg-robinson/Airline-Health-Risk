import unittest
from credit_story import load_story, reverse_stress, tables


class CreditStoryTests(unittest.TestCase):
    def test_nonoverlapping_loss_history(self):
        losses,_=tables()
        self.assertEqual(list(losses.months),[12]*6+[6])
        self.assertEqual(losses.iloc[:6].net_income.sum(),-3605)
        self.assertEqual(losses.net_income.sum(),-4171)

    def test_reverse_stress_conservation(self):
        d=load_story()
        for scenario in d['scenarios']:
            r=reverse_stress(d['inputs'],scenario,1000)
            self.assertAlmostEqual(r['opening_cash_and_investments']-r['maximum_baseline_cash_consumption']-r['total_incremental_shocks'],1000)
        r=reverse_stress(d['inputs'],d['scenarios'][2],1000)
        self.assertAlmostEqual(r['maximum_baseline_cash_consumption'],125.41)

    def test_funding_and_floor_effects(self):
        d=load_story();s=d['scenarios'][2]
        a=reverse_stress(d['inputs'],s,1000)
        b=reverse_stress(d['inputs'],s,1250,600)
        self.assertAlmostEqual(b['maximum_baseline_cash_consumption']-a['maximum_baseline_cash_consumption'],350)

    def test_full_recapture_and_negative_budget(self):
        d=load_story();s=dict(d['scenarios'][2],fuel_recapture=1)
        r=reverse_stress(d['inputs'],s,3000)
        self.assertEqual(r['incremental_fuel'],0)
        self.assertLess(r['maximum_baseline_cash_consumption'],0)
        with self.assertRaises(ValueError):
            reverse_stress(d['inputs'],dict(s,fuel_recapture=1.2),1000)
