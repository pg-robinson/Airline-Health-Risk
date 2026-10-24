import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_database import ROOT, build, derive

class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=build(cls.temp.name)
        cls.db=sqlite3.connect(cls.path)
        cls.data=json.loads((ROOT/'data/annual-reporting.json').read_text())
    @classmethod
    def tearDownClass(cls):cls.db.close();cls.temp.cleanup()
    def test_scope(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM reports WHERE supplementary=0').fetchone()[0],24)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reports WHERE cohort='additional_case'").fetchone()[0],4)
    def test_periods(self):
        for r in self.data['reports']:
            self.assertTrue('2025-04-01'<=r['period_end']<='2026-03-31')
            self.assertLess(r['period_start'],r['period_end'])
    def test_all_provenance(self):
        for o in self.data['observations']:
            self.assertTrue(o['source_url'].startswith('https://'))
            self.assertTrue(o['source_locator'])
            self.assertTrue(o['source_audit_status'])
            self.assertIn(o['original_scale'],['thousands','millions','billions'])
    def test_database_integrity(self):
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertFalse(self.db.execute('PRAGMA foreign_key_check').fetchall())
    def test_roundtrip_sql(self):
        other=sqlite3.connect(':memory:')
        other.executescript((Path(self.temp.name)/'database.sql').read_text())
        self.assertEqual(other.execute('SELECT COUNT(*) FROM observations').fetchone()[0],len(self.data['observations']))
        other.close()
    def test_no_duplicate_lease_addition(self):
        self.assertEqual(derive(dict(debt_including_leases_current=100,debt_including_leases_noncurrent=200,leases_current=20,leases_noncurrent=30))['debt_and_lease_carrying_amount'],300)
    def test_us_leases_added(self):
        self.assertEqual(derive(dict(debt_finance_leases_current=10,debt_finance_leases_noncurrent=20,operating_leases_current=3,operating_leases_noncurrent=4))['debt_and_lease_carrying_amount'],37)
    def test_missing_is_not_zero(self):
        self.assertIsNone(derive(dict(borrowings_current=0,borrowings_noncurrent=0))['debt_and_lease_carrying_amount'])
        self.assertEqual(derive(dict(debt_including_leases_current=0,debt_including_leases_noncurrent=0,equity=10))['debt_to_equity'],0)
    def test_negative_equity(self):
        self.assertIsNone(self.db.execute("SELECT debt_to_equity FROM derived_metrics WHERE report_id='american'").fetchone()[0])
    def test_emirates_perimeters(self):
        self.assertIsNone(self.db.execute("SELECT debt_and_lease_carrying_amount FROM derived_metrics WHERE report_id='emirates'").fetchone()[0])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM baseline_observations WHERE report_id='emirates-airline'").fetchone()[0],0)
    def test_jetblue_maturity_total(self):
        self.assertEqual(self.db.execute("SELECT SUM(value) FROM debt_maturities WHERE report_id='jetblue'").fetchone()[0],8498)
    def test_jetblue_lease_adjusted_amount(self):
        self.assertEqual(self.db.execute("SELECT debt_and_lease_carrying_amount FROM derived_metrics WHERE report_id='jetblue'").fetchone()[0],9416)
    def test_operating_reconciliation(self):
        # Only statements with this exact presentation; not all issuer EBIT definitions match.
        for rid in ['delta','alaska','iag','ryanair','turkish','airchina','eastern','cathay','united','southwest','jetblue','singapore','canada','american','latam','southern','emirates-airline']:
            v={o['metric']:o['value'] for o in self.data['observations'] if o['report_id']==rid}
            self.assertAlmostEqual(v['revenue']+v.get('other_operating_income',0)-v['operating_expenses'],v['operating_profit'],delta=1.01,msg=rid)
    def test_scale_examples(self):
        v={(o['report_id'],o['metric']):o for o in self.data['observations']}
        self.assertEqual(v['eastern','revenue']['original_scale'],'millions')
        self.assertEqual(v['ana','revenue']['original_scale'],'billions')
        self.assertEqual(v['qatar','revenue']['original_scale'],'thousands')

if __name__=='__main__':unittest.main()
