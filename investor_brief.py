"""A readable investor conversation: reported balances, earnings, payments, then risk."""
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from investor_reporting import annual_screen, cases, jetblue_commitments, ROOT

BLUE='#245c7b';ORANGE='#bb6238';GREEN='#438274';INK='#213d50';GREY='#536b7c'


def page(title,subtitle):
    fig=plt.figure(figsize=(12,9))
    fig.text(.065,.94,title,fontsize=23,weight='bold',color=INK)
    fig.text(.065,.90,subtitle,fontsize=11,color=GREY)
    fig.text(.065,.045,'Airline financial resilience | 25 October 2026 | Reported accounts; analytical ratios; no credit rating',fontsize=9,color=GREY)
    return fig


def paragraph(fig,y,title,body,width=112):
    fig.text(.065,y,title,fontsize=15,weight='bold',color=BLUE)
    fig.text(.065,y-.035,textwrap.fill(body,width),fontsize=12,color=INK,va='top',linespacing=1.55)


def overview():
    fig=page('An investor conversation about airline debt','The questions first. The accounting terms second.')
    paragraph(fig,.82,'1. How much have you borrowed?',
              'Show debt and leases next to shareholders’ book equity. Debt-to-equity of 2x means two dollars of these obligations for every dollar of equity. Debt-to-assets provides another view of the balance sheet.')
    paragraph(fig,.65,'2. Do your earnings cover the interest?',
              'Interest cover is operating profit divided by gross interest expense. At 3x cover, interest equals one-third of operating profit. If operating profit is negative, there is no positive earnings pool to allocate to interest.')
    paragraph(fig,.48,'3. Can you meet the actual cash repayments?',
              'Interest is only part of debt service. Add scheduled principal and show lease payments separately. Compare them with cash available over the same period, allowing for essential capital spending and avoiding deductions already in operating cash flow.')
    paragraph(fig,.29,'4. What does that mean for risk?',
              'Assess the earnings cushion, available cash, repayment dates, refinancing, covenants and downside exposure together. A leverage ratio is a starting point, not a credit rating. Gearing and leverage describe the same financing question.')
    fig.text(.065,.105,'Accounting basis: retain each issuer’s US GAAP, IFRS or local accounts. These ratios are defined analysis,\nnot a claim that all airlines have been restated to US GAAP. EBITDA proxies are not the headline measure.',fontsize=10,color=GREY,linespacing=1.5)
    return fig


def leverage_chart(screen):
    rows=screen.dropna(subset=['debt_to_assets_pct']).sort_values('debt_to_assets_pct')
    fig=page('How much of the balance sheet is debt?',f'Annual baseline | {len(rows)} of 24 groups | debt and leases as a percentage of book assets')
    ax=fig.add_axes([.25,.26,.68,.58])
    bars=ax.barh(rows.entity,rows.debt_to_assets_pct,color=[ORANGE if i in ['JetBlue Airways','Alaska Air Group'] else BLUE for i in rows.entity],height=.65)
    ax.bar_label(bars,labels=[f'{v:.0f}%' for v in rows.debt_to_assets_pct],padding=4,fontsize=9)
    ax.set_xlim(0,max(100,rows.debt_to_assets_pct.max()*1.15));ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    ax.spines[['top','right','bottom']].set_visible(False);ax.tick_params(axis='y',length=0,labelsize=9)
    ax.set_xlabel('Debt and lease carrying amounts / total book assets (%)',fontsize=11)
    fig.text(.065,.12,'The remainder is NOT all equity: suppliers, advance ticket sales and other liabilities also finance assets.\nANA and combined Emirates Group omitted: comparable debt/lease inputs incomplete. Fiscal year ends differ.',fontsize=10,color=GREY,linespacing=1.5)
    return fig


def earnings_chart(screen):
    rows=screen.dropna(subset=['interest_share_of_operating_profit_pct']).sort_values('interest_share_of_operating_profit_pct')
    fig=page('How much operating profit goes on interest?',f'Annual baseline | {len(rows)} groups with positive operating profit and extracted gross interest')
    ax=fig.add_axes([.25,.33,.68,.48])
    bars=ax.barh(rows.entity,rows.interest_share_of_operating_profit_pct,color=BLUE,height=.65)
    ax.bar_label(bars,labels=[f'{v:.0f}%' for v in rows.interest_share_of_operating_profit_pct],padding=4,fontsize=10)
    ax.set_xlim(0,max(110,rows.interest_share_of_operating_profit_pct.max()*1.12));ax.axvline(100,color=ORANGE,linestyle='--',lw=1)
    ax.set_xlabel('Gross interest expense / positive operating profit (%)')
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);ax.spines[['top','right','bottom']].set_visible(False)
    fig.text(.065,.19,'100% means all operating profit is matched by interest expense. This is an earnings comparison, not cash reserved.\nJetBlue has an operating loss, so a percentage is not meaningful. Thirteen further groups lack compatible inputs.',fontsize=11,color=INK,linespacing=1.5)
    fig.text(.065,.105,'Principal repayments are excluded here and must be assessed separately. Gross interest is not broad finance costs.\nLease-expense presentation differs under US GAAP and IFRS; this familiar ratio is not a fully harmonised ranking.',fontsize=10,color=GREY,linespacing=1.5)
    return fig


def payments_chart(commitments):
    fig=page('What cash payments are already committed?','JetBlue | USD millions | contractual schedule disclosed at 30 June 2026')
    ax=fig.add_axes([.13,.37,.79,.42]);x=[0,1]
    columns=[('debt_and_finance_lease_payments_including_interest','Debt / finance leases, including interest',BLUE),('operating_lease_payments','Operating leases',GREEN),('aircraft_purchase_commitments','Aircraft purchases',ORANGE),('other_contractual_commitments','Other listed commitments','#aab6c1')]
    bottoms=[0,0]
    for key,label,color in columns:
        vals=list(commitments[key]);bars=ax.bar(x,vals,bottom=bottoms,color=color,label=label,width=.5)
        for i,v in enumerate(vals):ax.text(i,bottoms[i]+v/2,f'{v:,.0f}',ha='center',va='center',color='white' if color!= '#aab6c1' else INK,fontsize=11,weight='bold')
        bottoms=[a+b for a,b in zip(bottoms,vals)]
    ax.set_xticks(x,['July–December 2026','Calendar 2027']);ax.set_ylabel('USD millions');ax.set_ylim(0,max(bottoms)*1.15)
    ax.spines[['top','right']].set_visible(False)
    for i,v in enumerate(bottoms):ax.text(i,v+35,f'Total listed: {v:,.0f}',ha='center',fontsize=11)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2,frameon=False,fontsize=9)
    paragraph(fig,.24,'2027 debt and lease payments: $1,189m',
              'This comprises $1,043m of debt/finance-lease payments, including interest, plus $146m of operating leases. Aircraft purchases and other commitments are shown separately. The share covered by available cash is not yet established.',115)
    fig.text(.065,.095,'These June forecasts are not the next 12 months from October. Floating interest estimates may change.\nDo not add the separate carrying-value maturity schedule: it overlaps these payments. This is not a complete cash budget.',fontsize=10,color=GREY,linespacing=1.5)
    return fig


def profile_page(frame):
    fig=page('What would we tell an investor today?','Observed pressures from the extracted evidence | no overall credit ratings assigned')
    y=.82
    for _,r in frame.iterrows():
        debt=f'{r.debt_to_equity:.2f}x debt / equity' if pd.notna(r.debt_to_equity) else 'Debt ratio withheld pending reconciliation'
        cover='Operating loss: interest not covered' if r.ttm_operating_profit<0 else 'Gross interest detail incomplete'
        title=f'{r.entity} — {r.observed_profile}'
        fig.text(.065,y,title,fontsize=13,color=BLUE,weight='bold')
        fig.text(.065,y-.033,f'{r.period_end} | {debt} | {cover}',fontsize=10,color=GREY)
        fig.text(.065,y-.067,textwrap.fill(r.interpretation,104),fontsize=11,color=INK,va='top',linespacing=1.45)
        y-=.18
    fig.text(.065,.075,'Dates and cash-flow classifications differ. Before rating: complete maturities, liquidity restrictions, covenants,\ncollateral and fuel/FX exposure, then build a downside cash forecast. Missing evidence is not a risk rating.',fontsize=10,color=GREY,linespacing=1.5)
    return fig


def build():
    out=ROOT/'reports/investor';out.mkdir(parents=True,exist_ok=True)
    screen=annual_screen();current=cases();commitments=jetblue_commitments()
    screen.to_csv(out/'annual_accounting_ratios.csv',index=False)
    current.to_csv(out/'case_studies.csv',index=False)
    commitments.to_csv(out/'jetblue_cash_commitments.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','savefig.facecolor':'white','text.parse_math':False})
    figs=[('investor_questions',overview()),('balance_sheet_leverage',leverage_chart(screen)),('interest_burden',earnings_chart(screen)),('cash_commitments',payments_chart(commitments)),('risk_discussion',profile_page(current))]
    with PdfPages(out/'investor_brief.pdf') as pdf:
        for name,fig in figs:
            pdf.savefig(fig);fig.savefig(out/(name+'.png'),dpi=160);fig.savefig(out/(name+'.svg'));plt.close(fig)
    print(f'Built investor brief: {len(figs)} pages; {len(current)} dated case studies; no risk ratings.')
    return out

if __name__=='__main__':build()
