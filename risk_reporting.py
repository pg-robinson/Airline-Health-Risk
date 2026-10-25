"""Dated interim evidence and research readiness. No credit-rating model."""
import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TTM_FLOW_METRICS = {'revenue', 'operating_profit', 'fuel_cost', 'interest_expense', 'cfo', 'capex'}


def load_evidence():
    return json.loads((ROOT/'data/risk-evidence.json').read_text())


def values(data, report_id, period='current'):
    return {o['metric']: o['value'] for o in data['observations']
            if o['report_id'] == report_id and o['period'] == period}


def validate(data):
    reports = {r['id']: r for r in data['reports']}
    if len(reports) != len(data['reports']):
        raise ValueError('Duplicate interim report')
    cutoff = data['metadata']['research_cutoff']
    seen = set()
    for r in reports.values():
        if r['period_end'] > cutoff or (r['published_on'] and r['published_on'] > cutoff):
            raise ValueError('Report after research cutoff')
        if r['period_start'] >= r['period_end']:
            raise ValueError('Invalid reporting period')
    for o in data['observations']:
        key = (o['report_id'], o['period'], o['metric'])
        if key in seen or key[0] not in reports:
            raise ValueError('Duplicate or orphan interim observation')
        seen.add(key)
        if not math.isfinite(o['value']) or not o['source_locator']:
            raise ValueError('Invalid observation or missing locator')
    for s in data['maturity_schedules']:
        if s['report_id'] not in reports or not s['basis']:
            raise ValueError('Missing maturity provenance or basis')
        if len({b['label'] for b in s['buckets']}) != len(s['buckets']):
            raise ValueError('Duplicate maturity bucket')
        if not math.isclose(sum(b['value'] for b in s['buckets']), s['reported_total'], abs_tol=.01):
            raise ValueError('Maturity schedule does not reconcile')
    for h in data['hedges']:
        fraction = h['coverage_fraction']
        if h['as_of'] > cutoff or not h['source_locator']:
            raise ValueError('Invalid hedge date or source')
        if fraction is not None and not 0 <= fraction <= 1:
            raise ValueError('Invalid hedge fraction')
        if h['status'] in ('policy_only', 'volume_without_denominator') and fraction is not None:
            raise ValueError('Policy or volume is not a coverage percentage')
        if fraction == 0 and h['status'] not in ('no_open_positions', 'programme_closed'):
            raise ValueError('Zero coverage needs explicit no-position evidence')


def ttm_rows(annual, data):
    """FY + current YTD - matching prior YTD; approved flow metrics only."""
    ar = {r['id']: r for r in annual['reports']}
    rr = {r['id']: r for r in data['reports']}
    out = []
    for rid, approval in data.get('ttm_approvals', {}).items():
        r, a = rr[rid], ar[approval['annual_report_id']]
        if r['report_kind'] != 'interim_statements' or r['currency'] != a['currency'] or r['perimeter'] != a['perimeter']:
            raise ValueError('Incompatible TTM perimeter/currency/report kind')
        if date.fromisoformat(r['period_start']) != date.fromisoformat(a['period_end']) + timedelta(days=1):
            raise ValueError('TTM requires contiguous annual and YTD periods')
        expected_prior_end = str(int(r['period_end'][:4])-1) + r['period_end'][4:]
        if r['prior_period_start'] != a['period_start'] or r['prior_period_end'] != expected_prior_end:
            raise ValueError('TTM prior YTD period mismatch')
        av = {o['metric']:o['value'] for o in annual['observations'] if o['report_id']==a['id']}
        current, prior = values(data, rid), values(data, rid, 'prior_ytd')
        for metric in approval['metrics']:
            if metric not in TTM_FLOW_METRICS:
                raise ValueError('TTM metric must be an approved flow, not a balance')
            if all(metric in x for x in (av, current, prior)):
                out.append(dict(report_id=rid, airline_id=r['airline_id'], period_end=r['period_end'], currency=r['currency'], metric=metric,
                                annual_value=av[metric], current_ytd=current[metric], prior_ytd=prior[metric],
                                value=round(av[metric]+current[metric]-prior[metric],6), basis=approval['basis']))
    return out


def snapshot_rows(annual, data):
    from build_database import derive
    names={r['id']:r['entity'] for r in annual['reports']}
    out=[]
    for r in data['reports']:
        if r['report_kind']!='interim_statements':continue
        v=values(data,r['id'])
        out.append(dict(airline_id=r['airline_id'],entity=names[r['airline_id']],report_id=r['id'],period_end=r['period_end'],months=r['months'],currency=r['currency'],
                        **{k:v.get(k) for k in ('assets','equity','cash','short_term_investments','issuer_debt','liquidity_including_facilities','liquidity_excluding_facilities')},**derive(v)))
    return out


def readiness_rows(annual, data):
    from build_database import CORE, derive
    specifics={
      'jetblue':'June debt and lease cash schedules extracted. Review covenants, collateral, restricted cash, facilities and post-June funding changes. Q3 scheduled27 October.',
      'alaska':'September results; June debt principal ladder. Extract lease cash schedules and reconcile September repayments/new financing, covenants and current hedge statement.',
      'latam':'June statements / July hedge positions. Reconcile financial liabilities to gross debt; extract full amortisation and lease schedules, facilities and hedge strikes. Q3 scheduled3 November.',
      'easyjet':'March full statements; June trading update and July hedge positions. Full maturities, covenants and acquisition financing/perimeter review outstanding.',
      'ana':'Total equity and cash flows updated. Group fuel/staff and off-balance-sheet operating leases under Japanese GAAP remain unresolved.',
      'emirates':'Combined Emirates/dnata group gaps must not be filled with the airline-only supplement.'}
    rows=[]
    for a in annual['reports']:
        if a['supplementary']:continue
        aid=a['id']; av={o['metric']:o['value'] for o in annual['observations'] if o['report_id']==aid}
        combo=av|derive(av)
        rr=[r for r in data['reports'] if r['airline_id']==aid]
        full=[r['period_end'] for r in rr if r['report_kind']=='interim_statements']
        hh=[h for h in data['hedges'] if h['airline_id']==aid]
        ss=[s for s in data['maturity_schedules'] if s['report_id'] in {r['id'] for r in rr}]
        rows.append(dict(airline_id=aid,entity=a['entity'],annual_gaps='; '.join(k for k in CORE if combo.get(k) is None) or 'None in headline checklist',
                         interim_statement_end=max(full) if full else None,latest_extracted_report_end=max([r['period_end'] for r in rr],default=None),
                         interim_status='partial extraction; review outstanding' if rr else 'not yet extracted',
                         maturity_status=f'{len(ss)} schedules; full financing review incomplete' if ss else 'not yet extracted into current layer',
                         latest_hedge_evidence=max([h['as_of'] for h in hh],default=None),hedge_status='dated evidence; terms/currentness review outstanding' if hh else 'not extracted; not zero',
                         rating_status='withheld',remaining_work=specifics.get(aid,'Extract latest results and comparative periods, full debt/lease cash schedules, facilities, covenants, collateral, fuel positions and downside cash bridge.')))
    return rows


def write_csv(path, rows):
    if not rows: return
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def build_risk_tables(con, dest, annual):
    data=load_evidence();validate(data)
    con.executescript('''
      CREATE TABLE risk_reports(report_id TEXT PRIMARY KEY,airline_id TEXT REFERENCES reports(report_id),period_start TEXT,period_end TEXT,months INTEGER,currency TEXT,report_kind TEXT,source_url TEXT,published_on TEXT,retrieved_on TEXT,audit_status TEXT,notes TEXT);
      CREATE TABLE risk_observations(report_id TEXT REFERENCES risk_reports,period TEXT CHECK(period IN('current','prior_ytd')),metric TEXT,value REAL,unit TEXT,source_locator TEXT,notes TEXT,PRIMARY KEY(report_id,period,metric));
      CREATE TABLE risk_maturity_schedules(schedule_id INTEGER PRIMARY KEY,report_id TEXT REFERENCES risk_reports,kind TEXT,basis TEXT,reported_total REAL,source_locator TEXT,notes TEXT);
      CREATE TABLE risk_maturity_buckets(schedule_id INTEGER REFERENCES risk_maturity_schedules,bucket TEXT,value REAL,unit TEXT,PRIMARY KEY(schedule_id,bucket));
      CREATE TABLE fuel_hedges(hedge_id INTEGER PRIMARY KEY,airline_id TEXT REFERENCES reports(report_id),as_of TEXT,source_url TEXT,source_locator TEXT,status TEXT,coverage_fraction REAL CHECK(coverage_fraction BETWEEN 0 AND 1),coverage_horizon TEXT,price REAL,price_unit TEXT,notes TEXT,retrieved_on TEXT);
      CREATE TABLE risk_events(airline_id TEXT REFERENCES reports(report_id),event_date TEXT,event TEXT,source_url TEXT);
      CREATE TABLE ttm_metrics(report_id TEXT REFERENCES risk_reports,airline_id TEXT,period_end TEXT,currency TEXT,metric TEXT,annual_value REAL,current_ytd REAL,prior_ytd REAL,value REAL,basis TEXT,PRIMARY KEY(report_id,metric));
      CREATE TABLE research_readiness(airline_id TEXT PRIMARY KEY REFERENCES reports(report_id),entity TEXT,annual_gaps TEXT,interim_statement_end TEXT,latest_extracted_report_end TEXT,interim_status TEXT,maturity_status TEXT,latest_hedge_evidence TEXT,hedge_status TEXT,rating_status TEXT,remaining_work TEXT);
    ''')
    for r in data['reports']:
        con.execute('INSERT INTO risk_reports VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',tuple(r[k] for k in ['id','airline_id','period_start','period_end','months','currency','report_kind','source_url','published_on','retrieved_on','audit_status','notes']))
    for o in data['observations']:
        con.execute('INSERT INTO risk_observations VALUES(?,?,?,?,?,?,?)',tuple(o[k] for k in ['report_id','period','metric','value','unit','source_locator','notes']))
    for i,s in enumerate(data['maturity_schedules'],1):
        con.execute('INSERT INTO risk_maturity_schedules VALUES(?,?,?,?,?,?,?)',(i,*(s[k] for k in ['report_id','kind','basis','reported_total','source_locator','notes'])))
        con.executemany('INSERT INTO risk_maturity_buckets VALUES(?,?,?,?)',[(i,b['label'],b['value'],s['unit']) for b in s['buckets']])
    for i,h in enumerate(data['hedges'],1):
        con.execute('INSERT INTO fuel_hedges VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(i,*(h[k] for k in ['airline_id','as_of','source_url','source_locator','status','coverage_fraction','coverage_horizon','price','price_unit','notes','retrieved_on'])))
    for e in data['events']:
        con.execute('INSERT INTO risk_events VALUES(?,?,?,?)',tuple(e[k] for k in ['airline_id','event_date','event','source_url']))
    ttm=ttm_rows(annual,data);readiness=readiness_rows(annual,data)
    for table,rows in [('ttm_metrics',ttm),('research_readiness',readiness)]:
        for row in rows:con.execute(f'INSERT INTO {table} VALUES({",".join("?" for _ in row)})',tuple(row.values()))
        write_csv(dest/(table+'.csv'),rows)
    write_csv(dest/'interim_comparison.csv',snapshot_rows(annual,data))
    write_csv(dest/'fuel_hedges.csv',data['hedges'])
    reports={r['id']:r for r in data['reports']}
    write_csv(dest/'interim_observations.csv',[{**o,'currency':reports[o['report_id']]['currency'],'period_start':reports[o['report_id']]['period_start' if o['period']=='current' else 'prior_period_start'],'period_end':reports[o['report_id']]['period_end' if o['period']=='current' else 'prior_period_end'],'source_url':reports[o['report_id']]['source_url']} for o in data['observations']])
    write_csv(dest/'current_maturities.csv',[dict(airline_id=reports[s['report_id']]['airline_id'],as_of=reports[s['report_id']]['period_end'],currency=reports[s['report_id']]['currency'],kind=s['kind'],basis=s['basis'],bucket=b['label'],value=b['value'],reported_total=s['reported_total'],source_url=reports[s['report_id']]['source_url'],source_locator=s['source_locator'],notes=s['notes']) for s in data['maturity_schedules'] for b in s['buckets']])
    con.execute('INSERT INTO metadata VALUES(?,?)',('risk_evidence',json.dumps(data['metadata'])))
    lines=['# Risk research readiness','','Research cutoff: '+data['metadata']['research_cutoff']+'. No risk ratings assigned. Dates show extracted evidence, not a claim that every newer filing has been excluded by exhaustive search.','','| Group | Full interim statements through | Latest extracted report through | Hedge evidence date | Remaining work |','|---|---|---|---|---|']
    for r in readiness:lines.append(f"| {r['entity']} | {r['interim_statement_end'] or 'Pending'} | {r['latest_extracted_report_end'] or 'Pending'} | {r['latest_hedge_evidence'] or 'Pending'} | {r['remaining_work']} |")
    (dest/'risk_readiness.md').write_text('\n'.join(lines)+'\n')
