"""Rebuild the source-backed SQLite database and review exports. Standard library only."""
import csv
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
DEBT_BASES = [
    ('combined_debt_and_leases', ['debt_including_leases_current', 'debt_including_leases_noncurrent']),
    ('borrowings_plus_ifrs_leases', ['borrowings_current', 'borrowings_noncurrent', 'leases_current', 'leases_noncurrent']),
    ('debt_finance_leases_plus_operating_leases', ['debt_finance_leases_current', 'debt_finance_leases_noncurrent', 'operating_leases_current', 'operating_leases_noncurrent']),
]
CORE = ['revenue', 'assets', 'equity', 'cash', 'fuel_cost', 'staff_cost', 'cfo', 'capex', 'debt_and_lease_carrying_amount']
INSTANT = {'assets','equity','equity_parent','equity_perpetuals','cash','short_term_investments','total_investments','cash_and_investments','issuer_debt','fuel_financing','leases_fleet'}
DEFINITIONS = {
 'revenue':'Issuer consolidated revenue; other income included where stated in observation notes. No FX conversion.',
 'operating_profit':'Issuer statutory operating result as mapped; scope differences retained in report notes. Not adjusted EBIT.',
 'operating_profit_reported':'Issuer operating subtotal that excludes further operating charges; unsuitable for a comparable EBIT margin.',
 'operating_expenses':'Issuer operating expense subtotal or stated arithmetic aggregation; see notes for included other income.',
 'operating_expenses_reported':'Issuer partial expense subtotal; further operating charges excluded.',
 'general_admin':'General and administration expense separately disclosed below issuer operating subtotal.',
 'other_operating_income':'Other operating income, sometimes net of operating charges as explicitly noted.',
 'fuel_cost':'Reported fuel expense including hedges or SAF only where indicated; not a uniform unhedged fuel measure.',
 'staff_cost':'Reported employee cost. Separately disclosed incentives may be excluded; see staff_incentives.',
 'staff_incentives':'Separate incentive/profit-sharing expense; additional to staff_cost in the affected report.',
 'crew_cost':'Crew cost subset; do not add to total staff cost.',
 'cfo':'Net cash from operating activities as reported. Interest/dividend classification varies by issuer.',
 'capex':'Positive cash capital expenditure; purchase deposits, intangibles, netting and capitalised interest differ as noted.',
 'cash':'Cash/cash equivalents or cash-and-bank line as stated; unrestricted availability not yet assessed.',
 'cash_and_investments':'Issuer cash/investment or liquidity aggregate; not equivalent to unrestricted cash.',
 'short_term_investments':'Separate deposits/securities; eligibility for netting against debt requires review.',
 'total_investments':'Investments across maturities; do not assume all immediately liquid.',
 'assets':'Consolidated total assets.',
 'equity':'Total consolidated book equity including non-controlling interests and equity-classified hybrids where applicable.',
 'equity_parent':'Equity attributable to parent owners only; not substituted for total equity.',
 'equity_perpetuals':'Equity-classified perpetual securities subset; already included in equity.',
 'net_profit':'Consolidated net profit/loss after tax including non-controlling interests.',
 'net_profit_parent':'Profit/loss attributable to parent owners; not substituted for consolidated profit.',
 'interest_expense':'Gross interest expense as disclosed, distinct from broad finance costs and net interest.',
 'interest_net':'Net interest expense as disclosed; do not treat as gross interest.',
 'interest_expense_net_capitalised':'Interest expense after capitalised interest, before interest income.',
 'finance_costs':'Broad finance costs; may include FX, valuation or unwinding charges. Not a uniform interest denominator.',
 'depreciation_amortisation':'Depreciation/amortisation subtotal; impairment/provisions included only as noted.',
 'issuer_debt':'Issuer debt headline with source-specific perimeter; not automatically used in derived leverage.',
 'fuel_financing':'Separate fuel financing liability; excluded from the selected debt/lease carrying subtotal.',
 'leases_fleet':'Fleet leases subset only; not total lease liabilities.',
}
for base,label in [('borrowings','Borrowings excluding separately shown leases'),('leases','IFRS lease liabilities'),('debt_including_leases','Combined debt and lease liabilities'),('debt_finance_leases','Debt and finance lease obligations (other financial liabilities may be included as noted)'),('operating_leases','US GAAP operating lease liabilities')]:
 for term in ['current','noncurrent']:
  DEFINITIONS[base+'_'+term]=label+'; '+term+'. Carrying value, not necessarily contractual principal.'

def derive(values):
    out = {'debt_and_lease_carrying_amount': None, 'debt_basis': None, 'debt_to_equity': None}
    for basis, fields in DEBT_BASES:
        if all(k in values for k in fields):
            out['debt_and_lease_carrying_amount'] = round(sum(values[k] for k in fields), 6)
            out['debt_basis'] = basis
            break
    debt, equity = out['debt_and_lease_carrying_amount'], values.get('equity')
    if debt is not None and equity is not None and equity > 0:
        out['debt_to_equity'] = debt / equity
    out['equity_ratio_status'] = 'non_positive_equity' if equity is not None and equity <= 0 else ('available' if out['debt_to_equity'] is not None else 'missing_inputs')
    return out

def build(destination=None):
    data=json.loads((ROOT/'data/annual-reporting.json').read_text())
    dest=Path(destination) if destination else ROOT/'database'
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/'airline_financials.sqlite'
    if path.exists(): path.unlink()
    con=sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript('''
    CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE reports(report_id TEXT PRIMARY KEY,entity TEXT NOT NULL,cohort TEXT NOT NULL,currency TEXT NOT NULL,period_start TEXT NOT NULL,period_end TEXT NOT NULL,period_type TEXT NOT NULL,perimeter TEXT NOT NULL,supplementary INTEGER NOT NULL CHECK(supplementary IN(0,1)),notes TEXT NOT NULL);
    CREATE TABLE sources(source_id INTEGER PRIMARY KEY,url TEXT UNIQUE NOT NULL,retrieved_on TEXT NOT NULL,sha256 TEXT);
    CREATE TABLE metrics(metric TEXT PRIMARY KEY,definition TEXT NOT NULL,period_kind TEXT NOT NULL);
    CREATE TABLE observations(report_id TEXT REFERENCES reports,metric TEXT REFERENCES metrics,value REAL NOT NULL,unit TEXT NOT NULL CHECK(unit='currency_million'),source_id INTEGER REFERENCES sources,source_locator TEXT NOT NULL,audit_status TEXT NOT NULL,original_scale TEXT NOT NULL,extraction_status TEXT NOT NULL,notes TEXT NOT NULL,PRIMARY KEY(report_id,metric));
    CREATE TABLE debt_maturities(report_id TEXT REFERENCES reports,bucket TEXT,value REAL NOT NULL,unit TEXT NOT NULL,source_id INTEGER REFERENCES sources,source_locator TEXT NOT NULL,basis TEXT NOT NULL,PRIMARY KEY(report_id,bucket));
    CREATE TABLE derived_metrics(report_id TEXT PRIMARY KEY REFERENCES reports,debt_and_lease_carrying_amount REAL,debt_basis TEXT,debt_to_equity REAL,equity_ratio_status TEXT NOT NULL);
    CREATE TABLE coverage_gaps(report_id TEXT REFERENCES reports,metric TEXT NOT NULL,status TEXT NOT NULL,PRIMARY KEY(report_id,metric));
    CREATE VIEW source_backed_observations AS SELECT r.*,o.metric,o.value,o.unit,s.url AS source_url,o.source_locator,o.audit_status,o.original_scale,o.extraction_status,o.notes AS observation_notes FROM observations o JOIN reports r USING(report_id) JOIN sources s USING(source_id);
    CREATE VIEW baseline_observations AS SELECT * FROM source_backed_observations WHERE supplementary=0;
    ''')
    for k,v in data['metadata'].items():con.execute('INSERT INTO metadata VALUES(?,?)',(k,json.dumps(v)))
    ids={}
    for r in data['reports']:
        con.execute('INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?,?)',(r['id'],r['entity'],r['cohort'],r['currency'],r['period_start'],r['period_end'],r['period_type'],r['perimeter'],int(r['supplementary']),r['notes']))
        ids[r['id']]=r
    hashes={r['source_url']:r.get('source_sha256') for r in data['reports']}
    urls=sorted({o['source_url'] for o in data['observations']}|{m['source_url'] for m in data['debt_maturities']})
    sources={u:i+1 for i,u in enumerate(urls)}
    retrieved={u:max(o.get('retrieved_on',data['metadata']['source_cutoff']) for o in data['observations']+data['debt_maturities'] if o['source_url']==u) for u in urls}
    con.executemany('INSERT INTO sources VALUES(?,?,?,?)',[(i,u,retrieved[u],hashes.get(u)) for u,i in sources.items()])
    metrics=sorted({o['metric'] for o in data['observations']})
    for m in metrics:
        if m not in DEFINITIONS:raise ValueError('Missing definition: '+m)
        con.execute('INSERT INTO metrics VALUES(?,?,?)',(m,DEFINITIONS[m],'instant' if m in INSTANT or m.endswith('_current') or m.endswith('_noncurrent') else 'duration'))
    wide=[]
    for o in data['observations']:
        con.execute('INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?)',(o['report_id'],o['metric'],o['value'],o['unit'],sources[o['source_url']],o['source_locator'],o['source_audit_status'],o['original_scale'],o['extraction_status'],o['notes']))
    for m in data['debt_maturities']:
        con.execute('INSERT INTO debt_maturities VALUES(?,?,?,?,?,?,?)',(m['report_id'],m['bucket'],m['value'],m['unit'],sources[m['source_url']],m['source_locator'],m['basis']))
    for rid,r in ids.items():
        values={o['metric']:o['value'] for o in data['observations'] if o['report_id']==rid}
        derived=derive(values)
        con.execute('INSERT INTO derived_metrics VALUES(?,?,?,?,?)',(rid,*derived.values()))
        combined=values|derived
        gaps=[m for m in CORE if combined.get(m) is None]
        con.executemany('INSERT INTO coverage_gaps VALUES(?,?,?)',[(rid,m,'not_extracted_or_not_comparable; not zero') for m in gaps])
        wide.append(dict(report_id=rid,entity=r['entity'],cohort=r['cohort'],currency=r['currency'],period_end=r['period_end'],perimeter=r['perimeter'],**values,**derived,core_fields_missing='; '.join(gaps)))
    from risk_reporting import build_risk_tables
    build_risk_tables(con, dest, data)
    con.commit()
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    (dest/'database.sql').write_text('\n'.join(con.iterdump())+'\n')
    def csvwrite(name,rows,fields):
        with (dest/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    fields=['report_id','entity','cohort','currency','period_end','perimeter']+metrics+list(derive({}))+['core_fields_missing']
    csvwrite('annual_comparison.csv',wide,fields)
    cursor=con.execute('SELECT * FROM source_backed_observations ORDER BY report_id,metric')
    cols=[x[0] for x in cursor.description]
    csvwrite('observations.csv',[dict(zip(cols,row)) for row in cursor],cols)
    lines=['# Annual reporting coverage','',f"Source cutoff: {data['metadata']['source_cutoff']}. 24 groups plus one supplementary reporting perimeter. Missing fields below mean not extracted or not comparable, never zero.",'','Amounts remain in each report’s currency. This is an annual baseline, not a current credit rating or verified top-20 ranking.','','| Group | Year end | Currency | Observations | Core gaps |','|---|---|---|---:|---|']
    for r in wide:
        n=sum(o['report_id']==r['report_id'] for o in data['observations'])
        lines.append(f"| {r['entity']}{' (airline only)' if r['cohort']=='supplementary' else ''} | {r['period_end']} | {r['currency']} | {n} | {r['core_fields_missing'] or 'None in the nine-field checklist'} |")
    lines+=['','Core checklist: revenue, assets, total equity, cash, fuel cost, staff cost, operating cash flow, capex, and a debt/lease carrying subtotal. This is not a completeness measure for credit analysis. Maturities, covenants, encumbrances, liquidity restrictions, hedges and current interim reports remain incomplete.','',f"{len(data['observations'])} financial observations; {len(data['debt_maturities'])} JetBlue maturity buckets. All have primary-source links and locators."]
    (dest/'coverage.md').write_text('\n'.join(lines)+'\n')
    con.close()
    print(f"Built {path}: {len(ids)} reporting perimeters, {len(data['observations'])} observations, {len(sources)} source URLs")
    return path

if __name__=='__main__':build()
