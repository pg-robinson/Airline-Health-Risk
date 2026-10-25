"""Sourced loss history and an explicitly hypothetical reverse liquidity stress test."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def load_story():
    return json.loads((ROOT / 'data/credit-story.json').read_text())


def reverse_stress(inputs, scenario, floor, funding=0):
    """Solve maximum baseline cash consumption compatible with an endpoint cash floor.

    Baseline consumption must include ordinary interest, leases, principal and capex.
    Only incremental shocks are deducted here. No monthly runway is inferred.
    """
    if floor < 0 or funding < 0 or not 0 <= scenario['fuel_recapture'] <= 1:
        raise ValueError('Invalid floor, funding or recapture assumption')
    for key in ['fuel_rise_pct', 'revenue_decline_pct', 'rate_rise_bp', 'cash_holdback']:
        if scenario[key] < 0:
            raise ValueError('Downside scenario inputs must be nonnegative')
    revenue = inputs['annual_revenue_2025'] + inputs['h1_revenue_2026'] - inputs['h1_revenue_2025']
    liquidity = inputs['cash_and_equivalents'] + inputs['investment_securities']
    fuel = inputs['fuel_expense_increase_per_10pct'] * scenario['fuel_rise_pct'] / 10 * (1-scenario['fuel_recapture'])
    demand = revenue * scenario['revenue_decline_pct'] / 100
    interest = inputs['interest_expense_increase_per_100bp'] * scenario['rate_rise_bp'] / 100
    shocks = fuel + demand + interest + scenario['cash_holdback']
    return dict(scenario=scenario['name'], opening_cash_and_investments=liquidity,
                analyst_cash_floor=floor, incremental_fuel=fuel, incremental_demand=demand,
                incremental_interest=interest, hypothetical_holdback=scenario['cash_holdback'],
                total_incremental_shocks=shocks, hypothetical_net_funding=funding,
                maximum_baseline_cash_consumption=liquidity-floor+funding-shocks)


def tables():
    d=load_story()
    losses=pd.DataFrame(d['loss_history'])
    losses['cumulative_net_income_since_2020']=losses.net_income.cumsum()
    stress=pd.DataFrame([reverse_stress(d['inputs'],s,d['analyst_assumptions']['planning_cash_floor']) for s in d['scenarios']])
    return losses,stress


def build():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','text.parse_math':False})
    out=ROOT/'reports/credit';out.mkdir(exist_ok=True,parents=True)
    losses,stress=tables()
    losses.to_csv(out/'jetblue_loss_history.csv',index=False)
    stress.to_csv(out/'reverse_stress.csv',index=False)
    fig,ax=plt.subplots(figsize=(11,6))
    fig.subplots_adjust(left=.10,right=.96,bottom=.25,top=.80)
    bars=ax.bar(losses.period,-losses.net_income,color=['#b35045']*6+['#e7aa64'])
    bars[-1].set_hatch('//')
    ax.bar_label(bars,fmt='%.0f',padding=4)
    ax.set_ylim(0,1550);ax.set_ylabel('Reported net loss (USD million)')
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('JetBlue: six annual losses, then another loss in H1 2026',fontsize=17,x=.10,ha='left')
    fig.text(.10,.86,'2020–2025: $3,605m cumulative losses | Including H1 2026: $4,171m',fontsize=12)
    fig.text(.10,.10,'H1 2026 covers six months; other bars cover twelve. Annual losses do not imply every quarter lost money.\nAccounting losses are not cash burn. Pandemic support and exceptional charges affect comparability.\nSources: JetBlue 2022 and 2025 Form 10-K; June 2026 Form 10-Q. Research cutoff: 25 October 2026.',fontsize=9,linespacing=1.6)
    fig.savefig(out/'jetblue_loss_history.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,6))
    fig.subplots_adjust(left=.35,right=.92,bottom=.31,top=.77)
    bars=ax.barh(stress.scenario,stress.maximum_baseline_cash_consumption,color=['#397d70','#d4954d','#b35045'])
    ax.bar_label(bars,fmt='%.0f',padding=6);ax.invert_yaxis();ax.set_xlim(0,1350)
    ax.set_xlabel('Maximum baseline cash consumption over 12 months (USD million)')
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('How much room remains after a shock?',fontsize=19,x=.07,ha='left')
    fig.text(.07,.86,'Illustrative reverse stress | June 2026 snapshot | $1bn analyst cash floor, no new funding',fontsize=11)
    fig.text(.07,.12,'Bars solve for an unknown cash budget; they are NOT forecast burn, covenant headroom or a default date.\nCombined downside: fuel +20%, 25% recaptured; revenue -3%; rates +200bp; $250m cash holdback.\nBaseline consumption must include normal debt service, leases and capex once. Monthly troughs are unmodelled.\nSource sensitivities: JetBlue June 2026 Form 10-Q. Scenarios and cash floor: author assumptions.',fontsize=9,linespacing=1.6)
    fig.savefig(out/'reverse_stress.png',dpi=160);plt.close(fig)
    return out


if __name__=='__main__':
    print(build())
