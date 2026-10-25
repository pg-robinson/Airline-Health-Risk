"""Comparable reporting screens; all amounts remain in original currency millions."""
import json
from pathlib import Path
import pandas as pd
from build_database import derive

ROOT=Path(__file__).resolve().parent

def load_baseline():
    data=json.loads((ROOT/'data/annual-reporting.json').read_text())
    rows=[]
    for r in data['reports']:
        if r['supplementary']:continue
        v={o['metric']:o['value'] for o in data['observations'] if o['report_id']==r['id']}
        row={**r,**v,**derive(v)}
        # Separate incentive costs are included only when expressly disclosed as additional.
        row['employee_cost_including_separate_incentives']=v.get('staff_cost',float('nan'))+v.get('staff_incentives',0)
        rows.append(row)
    frame=pd.DataFrame(rows).set_index('id')
    for numerator,denominator,name in [
        ('debt_and_lease_carrying_amount','assets','debt_to_assets_pct'),
        ('equity','assets','equity_to_assets_pct'),
        ('fuel_cost','revenue','fuel_to_revenue_pct'),
        ('employee_cost_including_separate_incentives','revenue','staff_to_revenue_pct'),
        ('operating_profit','revenue','operating_margin_pct')]:
        frame[name]=100*frame[numerator]/frame[denominator].where(frame[denominator]>0)
    frame['cfo_less_capex']=frame['cfo']-frame['capex']
    return data,frame

def fuel_scenario(row,shock):
    """Pure expense sensitivity: shock to reported fuel expense, not an oil-price forecast."""
    if not 0<=shock<=1:raise ValueError('Fuel-expense shock must be between 0 and 1.')
    required=['fuel_cost','operating_profit','revenue']
    if any(pd.isna(row.get(k)) for k in required):raise ValueError('Missing scenario input.')
    if row['revenue']<=0:raise ValueError('Revenue must be positive.')
    added=row['fuel_cost']*shock
    return {'extra_fuel_expense':added,'scenario_operating_profit':row['operating_profit']-added,'scenario_operating_margin_pct':100*(row['operating_profit']-added)/row['revenue']}
