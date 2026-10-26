"""One financial map plus an evidence-based, non-exclusive risk exposure register."""
import json
import math
from pathlib import Path
import pandas as pd
from reporting import load_baseline, ROOT
from risk_reporting import load_evidence, snapshot_rows, ttm_rows

ISSUES=['fuel','geopolitics','demand','financing','fx','labour','parts']
LABELS={'delta':'Delta','alaska':'Alaska','iag':'IAG','ryanair':'Ryanair','turkish':'Turkish','qatar':'Qatar','korean':'Korean Air','easyjet':'easyJet','qantas':'Qantas','airchina':'Air China','eastern':'China Eastern','cathay':'Cathay','afklm':'Air France-KLM','lufthansa':'Lufthansa','ana':'ANA','united':'United','southwest':'Southwest','jetblue':'JetBlue','singapore':'Singapore','canada':'Air Canada','american':'American','latam':'LATAM','southern':'China Southern','emirates':'Emirates Group'}
COLORS={'distress':'#b2393b','earnings_pressure':'#da7445','watch':'#d4aa42','positive':'#32857d','incomplete':'#8b98a6'}
STATUS={'distress':'Serious warning signs','earnings_pressure':'Earnings fall short','watch':'Cash shortfall or profit squeeze','positive':'Profits and cash: positive signs','incomplete':'Not enough information'}


def finite(x):
    return x is not None and isinstance(x,(int,float)) and math.isfinite(x)


def classify(op,interest,cash_gap,margin_change=None,distress=False):
    if distress:return 'distress'
    if not finite(op):return 'incomplete'
    if op<=0 or (finite(interest) and interest>op):return 'earnings_pressure'
    if (finite(cash_gap) and cash_gap<0) or (finite(margin_change) and margin_change<-.5):return 'watch'
    if finite(cash_gap) and cash_gap>=0:return 'positive'
    return 'incomplete'


def build_data():
    annual,frame=load_baseline();risk=load_evidence()
    evidence=json.loads((ROOT/'data/risk-map-evidence.json').read_text())
    snapshots={r['airline_id']:r for r in snapshot_rows(annual,risk)}
    trailing={(r['airline_id'],r['metric']):r for r in ttm_rows(annual,risk)}
    rows=[];exposures=[]
    macros={m['id']:m for m in evidence['macro_issues']}
    for aid,a in frame.iterrows():
        av={o['metric']:o['value'] for o in annual['observations'] if o['report_id']==aid}
        op=av.get('operating_profit',av.get('operating_profit_reported'))
        rev=av.get('revenue');margin=100*op/rev if finite(op) and finite(rev) and rev>0 else None
        debt=a.get('debt_and_lease_carrying_amount');assets=av.get('assets')
        x=100*debt/assets if finite(debt) and finite(assets) and assets>0 else None
        cfo=av.get('cfo');capex=av.get('capex');gap=cfo-capex if finite(cfo) and finite(capex) else None
        latest_op=op;latest_interest=av.get('interest_expense');latest_gap=gap
        cash_gap_basis='Annual';latest_margin=None;change=None;trend='Not assessed';to_date=None;end_x=None;end_y=None
        if (aid,'operating_profit') in trailing and (aid,'revenue') in trailing:
            t=trailing[(aid,'operating_profit')];latest_op=t['value'];latest_margin=100*latest_op/trailing[(aid,'revenue')]['value']
            change=latest_margin-margin;to_date=t['period_end']
            trend='Margin falling' if change<-.5 else 'Margin improving' if change>.5 else 'Little margin change'
            latest_interest=trailing.get((aid,'interest_expense'),{}).get('value')
            if (aid,'cfo') in trailing and (aid,'capex') in trailing:
                latest_gap=trailing[(aid,'cfo')]['value']-trailing[(aid,'capex')]['value'];cash_gap_basis='Trailing twelve months'
            else:
                v={o['metric']:o['value'] for o in risk['observations'] if o['report_id']==snapshots[aid]['report_id'] and o['period']=='current'}
                latest_gap=v['cfo']-v['capex'] if 'cfo' in v and 'capex' in v else None;cash_gap_basis='Current year to date'
            ss=snapshots[aid]
            if finite(ss['debt_and_lease_carrying_amount']) and finite(ss['assets']) and ss['assets']>0:
                end_x=100*ss['debt_and_lease_carrying_amount']/ss['assets'];end_y=latest_margin
        override=evidence.get('financial_overrides',{}).get(aid)
        status=classify(latest_op,latest_interest,latest_gap,change,override is not None)
        report_sources=sorted({o.get('source_url',a.source_url) for o in annual['observations'] if o['report_id']==aid and o['metric'] in ['operating_profit','operating_profit_reported','revenue','assets','cfo','capex']})
        interim_source=next((r['source_url'] for r in risk['reports'] if aid in snapshots and r['id']==snapshots[aid]['report_id']),None)
        point_date=to_date if end_x is not None else a.period_end
        row=dict(airline_id=aid,entity=a.entity,label=LABELS[aid],currency=a.currency,annual_date=a.period_end,
                 annual_x=x,annual_y=margin,x=end_x if end_x is not None else x,y=end_y if end_y is not None else margin,
                 point_date=point_date,arrow=end_x is not None,latest_margin=latest_margin,margin_change_pp=change,trend=trend,trend_date=to_date,
                 status=status,status_label=STATUS[status],annual_cfo_less_capex=gap,latest_cash_gap=latest_gap,cash_gap_basis=cash_gap_basis,
                 fuel_to_revenue_pct=100*av['fuel_cost']/rev if 'fuel_cost' in av and rev>0 else None,
                 source_urls=report_sources,interim_source=interim_source,
                 distress_evidence=override,
                 placement_note=('Debt/lease comparison incomplete; not placed on numeric axes' if x is None else
                                 'Annual point retained; newer margin trend available, but current debt reconciliation unresolved' if aid=='latam' else
                                 'Matched TTM earnings and contemporaneous balance sheet' if end_x is not None else
                                 'Annual baseline only; current direction not established'))
        rows.append(row)
        def add(issue,group,level,note,url=None,date=None,locator=None):
            exposures.append(dict(airline_id=aid,entity=a.entity,issue=issue,group=group,evidence_level=level,note=note,
               as_of=date or a.period_end,source_url=url or a.source_url,source_locator=locator or 'Issuer annual baseline / author screening inference'))
        hs=[h for h in risk['hedges'] if h['airline_id']==aid]
        if hs:
            newest=max(h['as_of'] for h in hs);latest=[h for h in hs if h['as_of']==newest]
            if any(h['status'] in ['no_open_positions','programme_closed'] for h in latest):
                group='No open fuel hedges disclosed';level='disclosed'
            elif any(h['status'].startswith('positions_disclosed') or h['status']=='volume_without_denominator' for h in latest):
                group='Dated hedge positions disclosed';level='mitigation'
            else:group='Hedge policy only';level='unknown'
            h=latest[0];note='; '.join(f"{v['coverage_horizon'] or 'horizon unresolved'}: {str(round(v['coverage_fraction']*100))+'%' if v['coverage_fraction'] is not None else 'fraction not established'}" for v in latest)
            add('fuel',group,level,note+'. Dated positions are not current guaranteed protection. Physical availability and hedge basis/expiry still matter.',h['source_url'],newest,h['source_locator'])
        else:add('fuel','Hedge protection not assessed','unknown','All airlines have fuel exposure. Absence of extracted hedge data does not mean no hedges.',macros['fuel']['source_url'],macros['fuel']['source_date'],'Industry context; issuer hedge data pending')
        if aid in ['qatar','emirates']:
            add('geopolitics','Gulf hub concentration','inferred','Author geographic exposure grouping: Doha/Dubai hub concentration. Route-level loss, insurance and mitigation not quantified.')
        else:add('geopolitics','Network / indirect exposure','inferred','Potential airspace, rerouting and network spillovers. Company-specific affected revenue and capacity have not been mapped; this is not a low-risk designation.')
        cargo=aid in ['cathay','korean','singapore','qatar','emirates','turkish','lufthansa']
        add('demand','Cargo and passenger review priority' if cargo else 'Passenger demand exposure','inferred','Author business-mix grouping for investigation, not a measured elasticity or exclusive group. All groups have passenger-demand exposure; cargo can benefit from diversion while volumes weaken.')
        add('financing',STATUS[status],'calculated','Financial screen only. Principal maturities, floating-rate share, collateral and covenant headroom must determine refinancing vulnerability. Cash investment gaps may finance growth.',interim_source if end_x is not None else None,to_date if end_x is not None else None)
        add('fx','Non-USD reporting: check mismatch' if a.currency!='USD' else 'USD reporting: check mismatch','inferred',f'Reporting currency {a.currency} is only a screening tag. It does not establish net FX risk, natural hedges, local-currency revenues, dollar debt or protection; no severity assigned.')
        for k in ['labour','parts']:
            records=[v for v in evidence['operational_evidence'] if v['airline_id']==aid and v['issue']==k]
            if records:
                e=records[0];add(k,e['group'],e['evidence_level'],e['note'],e['source_url'],e['as_of'],e['source_locator'])
            else:add(k,'Not assessed','unknown','Issuer-specific operational evidence not extracted for this overlay. Do not interpret as low risk or no shortage.')
    return evidence,rows,exposures


def plot_map(rows,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.family':'DejaVu Sans','text.parse_math':False,'svg.fonttype':'none'})
    fig=plt.figure(figsize=(16,10));ax=fig.add_axes([.075,.30,.72,.55]);side=fig.add_axes([.82,.30,.17,.55]);side.axis('off')
    ax.set_xlim(0,80);ax.set_ylim(-10,23);ax.axhspan(-10,0,color='#fbefeb',zorder=0);ax.axhline(0,color='#bb827c',lw=1)
    ax.grid(alpha=.13);ax.spines[['top','right']].set_visible(False)
    ax.set_xlabel('Debt and leases as a share of recorded assets (%) → more borrowing',fontsize=12)
    ax.set_ylabel('Operating profit per $100 of sales → more room for a bad year',fontsize=12)
    offsets={'delta':(-45,-18),'iag':(8,6),'ryanair':(8,8),'turkish':(10,2),'qatar':(8,6),'korean':(10,-6),'easyjet':(-55,3),'qantas':(-55,-1),'airchina':(8,-8),'eastern':(10,-5),'cathay':(-55,9),'afklm':(12,-8),'lufthansa':(-55,-18),'united':(14,0),'southwest':(-65,6),'jetblue':(10,-3),'singapore':(-78,4),'canada':(2,-23),'american':(-63,8),'latam':(8,6),'southern':(10,6),'alaska':(9,-5)}
    for r in rows:
        aid=r['airline_id'];c=COLORS[r['status']]
        if not finite(r['x']) or not finite(r['y']):continue
        if r['arrow']:
            ax.scatter(r['annual_x'],r['annual_y'],s=40,facecolors='white',edgecolors='#8794a0',zorder=3).set_gid('origin-'+aid)
            arrow=ax.annotate('',xy=(r['x'],r['y']),xytext=(r['annual_x'],r['annual_y']),arrowprops=dict(arrowstyle='->',color=c,lw=1.8,shrinkA=5,shrinkB=6));arrow.set_gid('arrow-'+aid)
        mark='*' if aid=='ryanair' else 'o'
        ax.scatter(r['x'],r['y'],s=230 if mark=='*' else 110,c=c,marker=mark,edgecolors='white',linewidth=1.1,zorder=5).set_gid('point-'+aid)
        lab=r['label']+(' †' if aid=='latam' else '')
        label=ax.annotate(lab,(r['x'],r['y']),xytext=offsets.get(aid,(8,7)),textcoords='offset points',fontsize=10,color='#243d50',arrowprops=dict(arrowstyle='-',color='#c0c8cb',lw=.6),zorder=6)
        label.set_gid('label-'+aid)
    ax.text(2,21.3,'HEALTHIER DIRECTION ↖',color='#32796e',fontsize=11,weight='bold')
    ax.text(2,-8.8,'Operating loss: no operating-profit cushion for interest',color='#a64b46',fontsize=10)
    side.text(0,.96,'All 24 groups visible',fontsize=12,weight='bold',color='#243d50')
    side.text(0,.86,'22 on numeric axes\n2 await comparable debt',fontsize=11,color='#586b78',linespacing=1.6)
    side.text(0,.68,'NOT PLACED',fontsize=10,weight='bold',color='#586b78')
    for y,aid in [(.58,'ana'),(.43,'emirates')]:
        r=next(r for r in rows if r['airline_id']==aid)
        side.text(0,y,r['label'],fontsize=12,weight='bold',color='#243d50').set_gid('label-'+aid)
        side.text(0,y-.065,f"Margin {r['annual_y']:.1f}%\n{r['annual_date']}",fontsize=10,color='#586b78')
    side.text(0,.22,'Ryanair ★\nStronger baseline reference;\nnot a current all-clear.',fontsize=10,color='#32796e',linespacing=1.5)
    side.text(0,.02,'† LATAM: margin falling.\nLatest debt reconciliation\nprevents a complete arrow.',fontsize=10,color='#586b78',linespacing=1.5)
    fig.text(.075,.95,'Who has room for a bad year?',fontsize=25,weight='bold',color='#203b4d')
    fig.text(.075,.905,'Provisional screen | Annual baseline plus three complete interim arrows | Research cutoff: 25 October 2026',fontsize=12,color='#526b7b')
    handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=COLORS[k],markersize=9,label=v) for k,v in STATUS.items()]
    fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.068,.175),ncol=3,frameon=False,fontsize=10)
    fig.text(.075,.125,'Arrows: annual baseline → matched trailing earnings and new balance sheet. Four margin trends assessed; 20 remain unknown.\nColours flag evidence, not default probabilities. Positive cash/earnings ≠ verified healthy. Capex gaps can reflect investment, not distress.',fontsize=10,color='#526b7b',linespacing=1.6)
    fig.text(.075,.065,'Fiscal dates differ (June 2025–September 2026). Lease accounting, asset values and cash-flow classifications limit comparability.\nEBITDAR and liquidity-based credit mapping still need reconciled inputs. Sources and individual dates: risk_map.json and the evidence register.',fontsize=9,color='#526b7b',linespacing=1.6)
    fig.savefig(out/'airline_risk_map.png',dpi=160);fig.savefig(out/'airline_risk_map.svg');plt.close(fig)


def plot_matrix(rows,exposures,out):
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    levels={'unknown':0,'inferred':1,'calculated':2,'disclosed':3,'mitigation':4,'historical':5,'observed':6}
    palette=['#edf0f3','#dce8f2','#b3cedd','#e5d4a0','#badbd3','#cfc5dc','#e4a18e']
    codes={'unknown':'?','inferred':'I','calculated':'C','disclosed':'D','mitigation':'M','historical':'H','observed':'O'}
    order=sorted(rows,key=lambda r:r['label']);idx={(r['airline_id'],r['issue']):r for r in exposures}
    vals=[[levels[idx[(r['airline_id'],k)]['evidence_level']] for k in ISSUES] for r in order]
    fig,ax=plt.subplots(figsize=(13,12));fig.subplots_adjust(left=.23,right=.97,bottom=.18,top=.86)
    ax.imshow(vals,cmap=ListedColormap(palette),vmin=0,vmax=6,aspect='auto')
    ax.set_xticks(range(7),['Fuel','Geopolitics','Demand / trade','Financing','Currency','Labour','Parts / engines']);ax.xaxis.tick_top()
    ax.set_yticks(range(len(order)),[r['label'] for r in order]);ax.tick_params(length=0,labelsize=11)
    for i,r in enumerate(order):
        for j,k in enumerate(ISSUES):ax.text(j,i,codes[idx[(r['airline_id'],k)]['evidence_level']],ha='center',va='center',color='#243d50')
    ax.set_xticks([x-.5 for x in range(8)],minor=True);ax.set_yticks([x-.5 for x in range(25)],minor=True);ax.grid(which='minor',color='white',lw=2);ax.tick_params(which='minor',length=0)
    fig.text(.07,.95,'Five macro risks, plus labour and parts',fontsize=23,weight='bold',color='#203b4d')
    fig.text(.07,.91,'An evidence map, NOT a severity heatmap | Every airline can belong to several exposure groups',fontsize=12,color='#526b7b')
    legends={'unknown':'? Not assessed','inferred':'I Structural inference','calculated':'C Financial screen','disclosed':'D Issuer-disclosed exposure','mitigation':'M Dated hedge evidence','historical':'H Historical / settled event','observed':'O Dated operational impact'}
    fig.legend(handles=[Patch(color=palette[levels[k]],label=v) for k,v in legends.items()],loc='lower left',bbox_to_anchor=(.065,.075),ncol=3,frameon=False,fontsize=10)
    fig.text(.07,.035,'Unknown is not low risk. M does not mean fully protected. Labour costs / bargaining / shortages and parts / deliveries are distinct.\nSee exposure_register.csv or select an airline in the dashboard for the group, date, source, mechanism and limitations.',fontsize=10,color='#526b7b',linespacing=1.5)
    fig.savefig(out/'risk_exposure_matrix.png',dpi=150);plt.close(fig)


def build():
    out=ROOT/'reports/risk-map';out.mkdir(parents=True,exist_ok=True)
    evidence,rows,exposures=build_data()
    payload=dict(metadata=evidence,airlines=rows,exposures=exposures)
    # All missing numerical inputs are null, never NaN or fabricated zero.
    def clean(obj):
        if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items()}
        if isinstance(obj,list):return [clean(v) for v in obj]
        if isinstance(obj,float) and not math.isfinite(obj):return None
        return obj
    payload=clean(payload)
    (out/'risk_map.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    pd.DataFrame(payload['airlines']).to_csv(out/'financial_map.csv',index=False)
    pd.DataFrame(exposures).to_csv(out/'exposure_register.csv',index=False)
    plot_map(rows,out);plot_matrix(rows,exposures,out)
    template=(ROOT/'templates/risk-dashboard.html').read_text()
    svg=(out/'airline_risk_map.svg').read_text();svg=svg[svg.index('<svg'):]
    html=template.replace('__MAP_SVG__',svg).replace('__RISK_DATA__',json.dumps(payload,allow_nan=False).replace('</','<\\/'))
    (out/'index.html').write_text(html)
    return out


if __name__=='__main__':print(build())
