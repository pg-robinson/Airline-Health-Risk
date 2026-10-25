import unittest
from investor_reporting import ratios, cases, jetblue_commitments, annual_screen

class InvestorReportingTests(unittest.TestCase):
    def test_interest_share_and_cover_are_reciprocals(self):
        r=ratios(200,100,400,30,10)
        self.assertEqual(r['debt_to_equity'],2)
        self.assertEqual(r['interest_cover'],3)
        self.assertAlmostEqual(r['interest_share_of_operating_profit_pct'],100/3)
    def test_loss_has_no_positive_earnings_allocation(self):
        r=ratios(200,100,400,-30,10)
        self.assertIsNone(r['interest_share_of_operating_profit_pct'])
        self.assertEqual(r['interest_cover'],-3)
        self.assertIn('Operating loss',r['interest_reading'])
    def test_missing_and_nonpositive_denominators(self):
        r=ratios(None,-100,0,None,10)
        self.assertIsNone(r['debt_to_equity']);self.assertIsNone(r['debt_to_assets_pct'])
        self.assertEqual(r['interest_reading'],'Operating result unavailable')
        self.assertIsNone(ratios(10,10,20,10,0)['interest_cover'])
    def test_share_can_exceed_one_hundred(self):
        self.assertEqual(ratios(10,10,20,5,10)['interest_share_of_operating_profit_pct'],200)
    def test_case_gearing_and_no_fake_service_ratio(self):
        frame=cases().set_index('airline_id')
        self.assertAlmostEqual(frame.loc['jetblue','debt_to_equity'],9386/1587)
        self.assertAlmostEqual(frame.loc['jetblue','debt_to_assets_pct'],9386/16371*100)
        self.assertTrue(frame.debt_service_share.isna().all())
        self.assertTrue((frame.risk_rating=='Not assigned').all())
    def test_future_payments_not_double_counted(self):
        r=jetblue_commitments().set_index('period').loc['2027']
        self.assertEqual(r.debt_and_lease_cash_commitments,1189)
        self.assertEqual(r.total_listed_commitments,1969)
        self.assertEqual(r.debt_and_finance_lease_payments_including_interest,1043)
    def test_coverage_includes_no_debt_required_for_interest(self):
        frame=annual_screen().set_index('airline_id')
        self.assertGreater(frame.loc['ana','interest_cover'],0)
        self.assertTrue(frame.loc['jetblue','interest_share_of_operating_profit_pct']!=frame.loc['jetblue','interest_share_of_operating_profit_pct'])

if __name__=='__main__':unittest.main()
