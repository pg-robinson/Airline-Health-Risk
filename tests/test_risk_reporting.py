import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from build_database import build, ROOT
from risk_reporting import load_evidence, validate, ttm_rows, snapshot_rows, readiness_rows

class RiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_evidence()
        cls.annual=json.loads((ROOT/'data/annual-reporting.json').read_text())
    def test_source_data_valid(self):validate(self.data)
    def test_schedule_failure(self):
        d=copy.deepcopy(self.data);d['maturity_schedules'][0]['buckets'][0]['value']+=1
        with self.assertRaises(ValueError):validate(d)
    def test_duplicate_observation(self):
        d=copy.deepcopy(self.data);d['observations'].append(d['observations'][0])
        with self.assertRaises(ValueError):validate(d)
    def test_policy_not_actual_coverage(self):
        d=copy.deepcopy(self.data)
        next(h for h in d['hedges'] if h['status']=='policy_only')['coverage_fraction']=.6
        with self.assertRaises(ValueError):validate(d)
    def test_no_unknown_zero(self):
        for h in self.data['hedges']:
            if h['coverage_fraction']==0:self.assertIn(h['status'],['programme_closed','no_open_positions'])
        self.assertIsNone(next(h for h in self.data['hedges'] if h['airline_id']=='eastern')['coverage_fraction'])
    def test_ttm_results(self):
        v={(r['airline_id'],r['metric']):r['value'] for r in ttm_rows(self.annual,self.data)}
        self.assertEqual(v['jetblue','operating_profit'],-565)
        self.assertEqual(v['alaska','operating_profit'],-290)
        self.assertNotIn(('alaska','cfo'),v)
        self.assertEqual(v['jetblue','fuel_cost'],2526)
    def test_ttm_no_mismatched_currency_or_period(self):
        for field,value in [('currency','EUR'),('period_start','2026-02-01')]:
            d=copy.deepcopy(self.data);d['reports'][0][field]=value
            with self.assertRaises(ValueError):ttm_rows(self.annual,d)
    def test_trading_update_not_ttm(self):
        self.assertNotIn('easyjet-2026q3-trading',{r['report_id'] for r in ttm_rows(self.annual,self.data)})
    def test_ttm_rejects_balance_or_wrong_prior_year(self):
        d=copy.deepcopy(self.data)
        d['ttm_approvals']['jetblue-2026h1']['metrics'].append('equity')
        with self.assertRaises(ValueError):ttm_rows(self.annual,d)
        d=copy.deepcopy(self.data);d['reports'][0]['prior_period_end']='2024-06-30'
        with self.assertRaises(ValueError):ttm_rows(self.annual,d)
    def test_debt_perimeters(self):
        rows={r['airline_id']:r for r in snapshot_rows(self.annual,self.data)}
        self.assertEqual(rows['jetblue']['debt_and_lease_carrying_amount'],9386)
        self.assertEqual(rows['alaska']['debt_and_lease_carrying_amount'],7519)
        self.assertEqual(rows['easyjet']['debt_and_lease_carrying_amount'],3012)
        self.assertIsNone(rows['latam']['debt_to_equity'])
    def test_no_ratings_and_distinct_dates(self):
        rows=readiness_rows(self.annual,self.data)
        self.assertEqual(len(rows),24)
        self.assertTrue(all(r['rating_status']=='withheld' for r in rows))
        ej=next(r for r in rows if r['airline_id']=='easyjet')
        self.assertEqual(ej['interim_statement_end'],'2026-03-31')
        self.assertEqual(ej['latest_extracted_report_end'],'2026-06-30')
    def test_sql_roundtrip_includes_risk_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp);db=sqlite3.connect(':memory:')
            db.executescript((Path(tmp)/'database.sql').read_text())
            self.assertEqual(db.execute('SELECT COUNT(*) FROM risk_observations').fetchone()[0],len(self.data['observations']))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM research_readiness').fetchone()[0],24)
            self.assertFalse(db.execute('PRAGMA foreign_key_check').fetchall());db.close()

if __name__=='__main__':unittest.main()
