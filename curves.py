"""Rebuild the five legacy-style research charts with explicit modern definitions."""
import base64
import html
import json
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import pandas as pd
from reporting import load_baseline
from risk_reporting import load_evidence, snapshot_rows, ttm_rows

ROOT=Path(__file__).resolve().parent
REGIONS={
 'Greater China':['airchina','eastern','southern','cathay'],
 'Americas':['delta','alaska','united','southwest','jetblue','canada','american','latam'],
 'Europe':['iag','ryanair','easyjet','afklm','lufthansa'],
 'Middle East & Africa':['turkish','qatar','emirates'],
 'Asia Pacific':['korean','qantas','ana','singapore']}
# Turkey is grouped in Middle East & Africa for this presentation; classification is disclosed.
COLORS={'Greater China':'#d73737','Americas':'#77b449','Europe':'#37a3d9','Middle East & Africa':'#edc743','Asia Pacific':'#7851a9'}
NAMES={'delta':'Delta','alaska':'Alaska','iag':'IAG','ryanair':'Ryanair','turkish':'Turkish Airlines','qatar':'Qatar','korean':'Korean Air','easyjet':'easyJet','qantas':'Qantas','airchina':'Air China','eastern':'China Eastern','southern':'China Southern','cathay':'Cathay Pacific','afklm':'Air France–KLM','lufthansa':'Lufthansa','ana':'ANA','united':'United','southwest':'Southwest','jetblue':'JetBlue','singapore':'Singapore Airlines','canada':'Air Canada','american':'American','latam':'LATAM','emirates':'Emirates Group'}
DESCRIPTIONS={
 'debt':('Who owes the most debt and leases?','Selected debt and lease carrying amounts · common-FX USD billions','debt_usd_bn'),
 'interest':('Who has the highest interest-expense proxy?','Annual gross interest / closing financing debt (%) · not a portfolio borrowing rate','interest_proxy_pct'),
 'revenue':('Who generates the most revenue?','Reported consolidated revenue · common-FX USD billions','revenue_usd_bn'),
 'earnings':('Who generates the most operating earnings?','EBITDA proxy · common-FX USD billions · not EBITDAR or cash retained','ebitda_proxy_usd_bn')}
BASE_NOTE='Annual baseline: FY ends June 2025–March 2026 · provisional 24-group sample · prepared 25 October 2026'


def financing_debt(row):
    """Exclude US operating leases from expense/debt proxy; keep separately recognised finance leases."""
    us=['debt_finance_leases_current','debt_finance_leases_noncurrent']
    if all(pd.notna(row.get(k)) for k in us):return sum(row[k] for k in us)
    return row.get('debt_and_lease_carrying_amount',float('nan'))


def prepare():
    data,frame=load_baseline()
    fx=json.loads((ROOT/'data/chart-fx.json').read_text())
    if set(frame.currency)-set(fx['rates']):raise ValueError('Missing currency conversion')
    frame['region']=[next(region for region,ids in REGIONS.items() if aid in ids) for aid in frame.index]
    frame['chart_name']=[NAMES[i] for i in frame.index]
    frame['fx_local_per_usd']=frame.currency.map(fx['rates'])
    frame['revenue_usd_bn']=frame.revenue/frame.fx_local_per_usd/1000
    frame['debt_usd_bn']=frame.debt_and_lease_carrying_amount/frame.fx_local_per_usd/1000
    frame['financing_debt']=frame.apply(financing_debt,axis=1)
    frame['interest_proxy_pct']=100*frame.interest_expense/frame.financing_debt.where(frame.financing_debt>0)
    frame['interest_coverage']=frame.operating_profit/frame.interest_expense.where(frame.interest_expense>0)
    # Known mixed impairment/provision add-backs cannot be labelled clean D&A.
    mixed={o['report_id'] for o in data['observations'] if o['metric']=='depreciation_amortisation' and any(w in o['notes'].lower() for w in ['impairment','provisions'])}
    frame['ebitda_proxy']=frame.operating_profit+frame.depreciation_amortisation
    frame.loc[frame.index.isin(mixed),'ebitda_proxy']=float('nan')
    frame['ebitda_proxy_usd_bn']=frame.ebitda_proxy/frame.fx_local_per_usd/1000
    coverage=[]
    for aid,r in frame.iterrows():
        reasons={
          'debt':'Comparable debt/lease perimeter missing',
          'interest':'Gross interest or matched financing-debt subtotal missing; net interest/finance costs not substituted',
          'revenue':'Revenue missing',
          'earnings':'D&A includes impairment/provisions' if aid in mixed else 'Statutory operating profit or clean D&A missing',
          'map':'Positive book equity, comparable debt/leases or gross-interest coverage missing'}
        for key in [*DESCRIPTIONS,'map']:
            available=pd.notna(r[DESCRIPTIONS[key][2]]) if key!='map' else pd.notna(r.debt_to_equity) and pd.notna(r.interest_coverage)
            coverage.append(dict(airline_id=aid,entity=r.entity,chart=key,included=bool(available),reason='' if available else reasons[key]))
    return data,frame,fx,pd.DataFrame(coverage)


def legend(fig):
    fig.legend(handles=[Patch(facecolor=c,label=r) for r,c in COLORS.items()],loc='upper center',bbox_to_anchor=(.5,.89),ncol=5,frameon=False,fontsize=9)


def footer(fig,text):
    fig.text(.045,.055,BASE_NOTE,fontsize=8.5,color='#536374')
    fig.text(.045,.027,text,fontsize=8.5,color='#536374')


def bar_chart(frame,key):
    title,subtitle,col=DESCRIPTIONS[key]
    rows=frame.dropna(subset=[col]).sort_values(col,ascending=False)
    fig,ax=plt.subplots(figsize=(15,7.5))
    fig.subplots_adjust(left=.075,right=.98,bottom=.30,top=.78)
    fig.suptitle(title,x=.045,y=.975,ha='left',fontsize=23,fontweight='bold',color='#244b70')
    fig.text(.045,.91,subtitle,fontsize=12,color='#536374')
    legend(fig)
    bars=ax.bar(range(len(rows)),rows[col],color=rows.region.map(COLORS),edgecolor='#52667a',linewidth=.5,width=.72)
    ax.set_xticks(range(len(rows)),rows.chart_name,rotation=55,ha='right',fontsize=10)
    ax.tick_params(axis='x',length=0);ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True)
    ax.spines[['top','right','bottom']].set_visible(False)
    ax.spines['left'].set_color('#adb9c5')
    ax.set_ylabel('%' if key=='interest' else 'USD billions at common presentation FX',fontsize=11)
    ax.set_ylim(0,max(rows[col])*1.18)
    ax.bar_label(bars,labels=[f'{v:.1f}' for v in rows[col]],padding=4,fontsize=9,color='#243747')
    missing=', '.join(frame.loc[~frame.index.isin(rows.index),'chart_name']) or 'None'
    fig.text(.045,.145,textwrap.fill(f'Included {len(rows)}/24. Omitted: {missing}.',145),fontsize=9,color='#536374',va='top')
    if key=='interest':note='Expense-to-closing-debt proxy; US operating leases excluded from denominator. Average balances and consistent lease interest are unresolved.'
    else:note='US Treasury FX at 31 December 2025 for all periods; presentation conversion, not period-average USD results. Original currencies retained.'
    footer(fig,note)
    return fig


def risk_map(data,frame):
    rows=frame.dropna(subset=['debt_to_equity','interest_coverage'])
    fig,ax=plt.subplots(figsize=(14,9))
    fig.subplots_adjust(left=.10,right=.73,bottom=.18,top=.78)
    fig.suptitle('Leverage and interest coverage',x=.045,y=.975,ha='left',fontsize=23,fontweight='bold',color='#244b70')
    fig.text(.045,.92,'Gross-interest coverage screen · dated interim updates for Alaska and JetBlue',fontsize=12,color='#536374')
    legend(fig)
    ax.scatter(rows.debt_to_equity,rows.interest_coverage,c=rows.region.map(COLORS),s=95,edgecolors='#334a60',linewidth=.7,zorder=3)
    offsets={'lufthansa':(-78,12),'afklm':(10,-20),'united':(9,8),'canada':(10,8),'southern':(10,8),'alaska':(10,8),'jetblue':(-58,12),'turkish':(10,8),'latam':(10,8),'southwest':(10,8)}
    for aid,r in rows.iterrows():
        ax.annotate(r.chart_name,(r.debt_to_equity,r.interest_coverage),xytext=offsets.get(aid,(8,8)),textcoords='offset points',fontsize=10)
    risk=load_evidence();current={r['airline_id']:r for r in snapshot_rows(data,risk)}
    trailing={(r['airline_id'],r['metric']):r['value'] for r in ttm_rows(data,risk)}
    updates=[]
    for aid in ['alaska','jetblue']:
        r=current[aid];x=r['debt_to_equity'];y=trailing[aid,'operating_profit']/trailing[aid,'interest_expense']
        ax.annotate('',xy=(x,y),xytext=(frame.loc[aid,'debt_to_equity'],frame.loc[aid,'interest_coverage']),arrowprops=dict(arrowstyle='->',color='#556b7d',linestyle='--',lw=1.3),zorder=2)
        ax.scatter([x],[y],s=130,marker='D',color=COLORS['Americas'],edgecolors='#243747',zorder=4)
        ax.annotate(f"{NAMES[aid]} · {r['period_end']}",(x,y),xytext=(-100,-24) if aid=='jetblue' else (8,-24),textcoords='offset points',fontsize=10,fontweight='bold')
        updates.append(dict(airline_id=aid,period_end=r['period_end'],debt_to_equity=x,ttm_operating_profit=trailing[aid,'operating_profit'],ttm_interest_expense=trailing[aid,'interest_expense'],interest_coverage=y))
    ax.axhline(0,color='#8b9baa',lw=.8)
    ax.axhline(1,color='#8b9baa',lw=.8,linestyle=':')
    ax.text(.99,1.05,'1× EBIT / gross interest',ha='right',fontsize=8,color='#627487',transform=ax.get_yaxis_transform())
    ax.set(xlabel='Selected debt and leases / positive book equity (×)',ylabel='Statutory operating profit / reported gross interest expense (×)')
    ax.set_xlim(left=0,right=max([*rows.debt_to_equity,*[r['debt_to_equity'] for r in updates]])*1.22)
    ax.set_ylim(bottom=min(-1.8,rows.interest_coverage.min()-.8),top=rows.interest_coverage.max()*1.2)
    ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
    excluded=', '.join(frame.loc[~frame.index.isin(rows.index),'chart_name'])
    side=f'ANNUAL SAMPLE: {len(rows)} / 24\n\nCircles: annual baseline\nDiamonds: newer balance sheets\nwith trailing-12-month coverage\n\nOMITTED\n{textwrap.fill(excluded,29)}\n\nAmerican has negative equity.\nOther omissions reflect missing\nor incompatible inputs.\n\nA weaker plotted position is a\nresearch signal, not a rating.\nNo healthy/distressed zones\nare assigned.'
    fig.text(.77,.76,side,fontsize=10,color='#40566b',va='top',linespacing=1.5)
    footer(fig,'Coverage uses gross interest, unlike the legacy net-interest chart. Interim end dates differ; arrows do not describe one common reporting date.')
    return fig,updates


def build_charts():
    data,frame,fx,coverage=prepare()
    out=ROOT/'reports/curves';out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','savefig.facecolor':'white','figure.facecolor':'white'})
    figures=[(key,bar_chart(frame,key)) for key in DESCRIPTIONS]
    fig,updates=risk_map(data,frame);figures.append(('leverage_coverage',fig))
    with PdfPages(out/'airline_curves.pdf') as pdf:
        for key,fig in figures:
            fig.savefig(out/(key+'.png'),dpi=180)
            fig.savefig(out/(key+'.svg'))
            pdf.savefig(fig)
            plt.close(fig)
    columns=['entity','region','currency','period_start','period_end','fx_local_per_usd','revenue','revenue_usd_bn','debt_and_lease_carrying_amount','debt_usd_bn','financing_debt','interest_expense','interest_proxy_pct','operating_profit','depreciation_amortisation','ebitda_proxy','ebitda_proxy_usd_bn','equity','debt_to_equity','interest_coverage']
    frame[columns].to_csv(out/'chart_data.csv',index_label='airline_id')
    coverage.to_csv(out/'chart_coverage.csv',index=False)
    pd.DataFrame(updates).to_csv(out/'interim_map_updates.csv',index=False)
    sections=[]
    for key,_ in figures:
        encoded=base64.b64encode((out/(key+'.png')).read_bytes()).decode()
        sections.append(f'<section><img alt="{html.escape(DESCRIPTIONS[key][0] if key in DESCRIPTIONS else "Leverage and interest coverage")}" src="data:image/png;base64,{encoded}"></section>')
    intro='''<h1>Airline financial resilience — rebuilt research curves</h1><p>25 October 2026 · Annual baseline with two dated interim overlays</p><p>The five charts recreate the questions in the original study using public-source data. Definitions have changed: debt includes selected leases; the interest chart is an expense proxy; operating earnings use a limited EBITDA proxy, not EBITDAR; coverage uses gross interest. Missing observations are omitted, never zero-filled.</p><p>Common 31 December 2025 US Treasury FX makes currencies comparable for display. It is neither period-average conversion nor a claim that these are current USD balances. The provisional 24-group sample is not a verified global top-20 ranking. Turkish Airlines is grouped in Middle East &amp; Africa for this presentation.</p><p><a href="../../docs/curves-methodology.md">Definitions and omissions</a> · <a href="chart_data.csv">Chart data</a> · <a href="chart_coverage.csv">Coverage audit</a> · <a href="airline_curves.pdf">Five-page PDF</a></p>'''
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Airline research curves</title><style>body{margin:0;background:#eef2f6;font:17px/1.6 system-ui;color:#253d53}header,section{max-width:1400px;margin:24px auto;background:white;padding:24px;box-sizing:border-box;border-radius:8px}header{padding:32px}h1{line-height:1.2}img{width:100%;height:auto}a{color:#17628b}@media print{section{break-after:page}}</style><header>'+intro+'</header>'+''.join(sections)+'</html>'
    (out/'index.html').write_text(document)
    print('Generated five charts: PNG, SVG, PDF, HTML and CSV audit tables.')
    print(coverage.groupby('chart').included.sum().to_string())
    return out

if __name__=='__main__':build_charts()
