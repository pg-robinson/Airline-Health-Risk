import unittest
import pandas as pd
from curves import prepare, financing_debt

class CurveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.frame,cls.fx,cls.coverage=prepare()
    def test_complete_region_and_fx_mapping(self):
        self.assertEqual(len(self.frame),24)
        self.assertFalse(self.frame.region.isna().any())
        self.assertFalse(self.frame.fx_local_per_usd.isna().any())
    def test_usd_scale_and_foreign_fx_direction(self):
        self.assertAlmostEqual(self.frame.loc['delta','revenue_usd_bn'],63.364)
        self.assertAlmostEqual(self.frame.loc['easyjet','revenue_usd_bn'],10106/.743/1000)
    def test_proxy_denominator_excludes_us_operating_leases(self):
        self.assertEqual(financing_debt(dict(debt_finance_leases_current=10,debt_finance_leases_noncurrent=20,debt_and_lease_carrying_amount=40)),30)
        self.assertEqual(financing_debt(dict(debt_and_lease_carrying_amount=40)),40)
    def test_no_net_interest_substitution(self):
        self.assertTrue(pd.isna(self.frame.loc['delta','interest_proxy_pct']))
        self.assertTrue(pd.isna(self.frame.loc['iag','interest_coverage']))
    def test_ebitda_excludes_mixed_addbacks(self):
        for aid in ['iag','afklm','canada']:
            self.assertTrue(pd.isna(self.frame.loc[aid,'ebitda_proxy']))
        self.assertEqual(self.frame.loc['jetblue','ebitda_proxy'],320)
    def test_negative_equity_and_missing_debt_excluded(self):
        for aid in ['american','ana','emirates']:
            row=self.coverage[(self.coverage.airline_id==aid)&(self.coverage.chart=='map')].iloc[0]
            self.assertFalse(row.included)
    def test_each_chart_covers_every_candidate_explicitly(self):
        self.assertEqual(len(self.coverage),120)
        self.assertFalse(self.coverage.duplicated(['airline_id','chart']).any())

if __name__=='__main__':unittest.main()
