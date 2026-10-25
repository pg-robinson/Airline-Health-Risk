"""Investor questions answered from reported accounts, with defined analytical ratios."""
import json
from pathlib import Path
import pandas as pd
from reporting import load_baseline
from risk_reporting import load_evidence, snapshot_rows, ttm_rows, values

ROOT=Path(__file__).resolve().parent


def ratios(debt, equity, assets, operating_profit, interest):
    """None means unavailable/not meaningful; never turn a loss into a positive coverage share."""
    def valid(x):return x is not None and pd.notna(x)
    return {
        'debt_to_equity':debt/equity if valid(debt) and valid(equity) and equity>0 else None,
        'debt_to_assets_pct':100*debt/assets if valid(debt) and valid(assets) and assets>0 else None,
        'equity_to_assets_pct':100*equity/assets if valid(equity) and valid(assets) and assets>0 else None,
        'interest_cover':operating_profit/interest if valid(operating_profit) and valid(interest) and interest>0 else None,
        'interest_share_of_operating_profit_pct':100*interest/operating_profit if valid(operating_profit) and operating_profit>0 and valid(interest) and interest>=0 else None,
        'interest_reading':('Operating result unavailable' if not valid(operating_profit) else
                            'Operating loss: interest is not covered by operating earnings' if operating_profit<=0 else
                            'Gross interest not extracted; coverage unavailable' if not valid(interest) else
                            'No positive interest denominator' if interest<=0 else
                            'Operating earnings below interest expense' if operating_profit<interest else
                            'Operating earnings exceed interest expense' if valid(operating_profit) else 'Operating result unavailable'),
    }


def annual_screen():
    data,frame=load_baseline();rows=[]
    for aid,r in frame.iterrows():
        result=ratios(r.get('debt_and_lease_carrying_amount'),r.get('equity'),r.get('assets'),r.get('operating_profit'),r.get('interest_expense'))
        rows.append(dict(airline_id=aid,entity=r.entity,currency=r.currency,period_end=r.period_end,**result))
    return pd.DataFrame(rows)


def cases():
    annual,_=load_baseline();risk=load_evidence()
    snapshots={r['airline_id']:r for r in snapshot_rows(annual,risk)}
    trailing={(r['airline_id'],r['metric']):r['value'] for r in ttm_rows(annual,risk)}
    answers={
      'jetblue':('Significant funding pressure','Operating losses, negative operating cash flow and a small book-equity cushion relative to debt and leases. Review refinancing and available liquidity first.'),
      'alaska':('Earnings and funding pressure','Lower book leverage than JetBlue, but trailing operating earnings no longer cover interest. Nine-month operating cash flow did not cover capital spending. June maturity notes need a September update.'),
      'latam':('Cash generation positive; financing review incomplete','June operating cash flow exceeded capital spending, before financing-classified interest and lease payments. Debt reconciliation, amortisation and covenant review remain incomplete.'),
      'easyjet':('Lower book leverage; seasonal and transaction risks','Debt and leases are below book equity, and trailing operating profit is positive. Winter-half cash flow, reported after dividends, did not cover capital spending. Acquisition financing needs separate review.')}
    out=[]
    for aid in ['jetblue','alaska','latam','easyjet']:
        r=snapshots[aid];v=values(risk,r['report_id']);op=trailing.get((aid,'operating_profit'));interest=trailing.get((aid,'interest_expense'))
        m=ratios(r['debt_and_lease_carrying_amount'],r['equity'],r['assets'],op,interest)
        description,reason=answers[aid]
        out.append({**r,**m,'ttm_operating_profit':op,'ttm_interest_expense':interest,'ytd_cfo':v.get('cfo'),'ytd_capex':v.get('capex'),
                    'ytd_cfo_less_capex':v['cfo']-v['capex'] if 'cfo' in v and 'capex' in v else None,
                    'observed_profile':description,'interpretation':reason,'risk_rating':'Not assigned','debt_service_share':None,
                    'debt_service_status':'Not calculated: comparable cash available, gross cash interest and full scheduled repayments are incomplete.'})
    return pd.DataFrame(out)


def jetblue_commitments():
    """One mutually exclusive contractual basis; never combine carrying principal with interest-inclusive cash payments."""
    risk=load_evidence()
    selected={s['kind']:s for s in risk['maturity_schedules'] if s['report_id']=='jetblue-2026h1' and s['basis'].startswith('contractual')}
    rows=[]
    for bucket in ['remainder_2026','2027']:
        def amount(kind):return next(b['value'] for b in selected[kind]['buckets'] if b['label']==bucket)
        debt=amount('debt_finance_lease_cash_payments');lease=amount('operating_lease_cash_payments')
        aircraft=amount('aircraft_purchase_commitments');other=amount('other_commitments')
        rows.append(dict(period=bucket,as_of='2026-06-30',currency='USD',debt_and_finance_lease_payments_including_interest=debt,
                         operating_lease_payments=lease,debt_and_lease_cash_commitments=debt+lease,
                         aircraft_purchase_commitments=aircraft,other_contractual_commitments=other,
                         total_listed_commitments=debt+lease+aircraft+other,
                         source_url=next(r['source_url'] for r in risk['reports'] if r['id']=='jetblue-2026h1'),source_locator='Form10-Q contractual obligations, p36'))
    return pd.DataFrame(rows)
