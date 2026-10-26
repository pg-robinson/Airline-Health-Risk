import unittest
from risk_map import build_data, classify, finite

class RiskMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence, cls.rows, cls.exposures = build_data()
    def test_complete_universe_and_unique_exposures(self):
        self.assertEqual(len(self.rows),24)
        self.assertEqual(len(self.exposures),168)
        self.assertEqual(len({(r['airline_id'],r['issue']) for r in self.exposures}),168)
    def test_missing_debt_not_zero_and_trends_not_invented(self):
        self.assertEqual({r['airline_id'] for r in self.rows if not finite(r['x'])},{'ana','emirates'})
        self.assertEqual({r['airline_id'] for r in self.rows if r['arrow']},{'jetblue','alaska','easyjet'})
        self.assertEqual(sum(r['trend']=='Not assessed' for r in self.rows),20)
        r=next(r for r in self.rows if r['airline_id']=='latam')
        self.assertLess(r['margin_change_pp'],0)
        self.assertEqual(r['x'],r['annual_x'])
    def test_rules_do_not_turn_missing_evidence_into_health(self):
        self.assertEqual(classify(None,None,None),'incomplete')
        self.assertEqual(classify(10,20,5),'earnings_pressure')
        self.assertEqual(classify(10,2,-1),'watch')
        self.assertEqual(classify(10,2,1,-1),'watch')
        self.assertEqual(classify(10,2,1),'positive')
        self.assertEqual(classify(10,2,1,distress=True),'distress')
    def test_evidence_traceable_and_cash_period_explicit(self):
        for r in self.exposures:
            self.assertTrue(r['source_url'].startswith('https://'))
            self.assertTrue(r['as_of'])
        rows={r['airline_id']:r for r in self.rows}
        self.assertEqual(rows['alaska']['cash_gap_basis'],'Current year to date')
        self.assertEqual(rows['jetblue']['cash_gap_basis'],'Trailing twelve months')
        self.assertTrue(rows['jetblue']['distress_evidence'])
