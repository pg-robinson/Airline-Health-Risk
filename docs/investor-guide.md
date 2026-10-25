# An investor conversation about airline leverage

**Research date: 25 October 2026.** This is the accounting reading guide. It replaces the earlier interest-expense/debt and EBITDA-proxy charts as the recommended way to interpret this project.

**Read next:** [Credit story: losses, limits and stress](credit-story.md) and [current airline benchmarks](airline-credit-benchmarks.md). EBITDAR remains useful when leases are reconciled; book gearing is supporting context, not the preferred headline credit benchmark.

## “How much have you borrowed?”

Start with the balance sheet: loans and bonds, finance leases, operating-lease liabilities, and shareholders' equity. Show the amounts and reporting date before calculating a ratio. For this research, the headline debt total includes the identified debt and lease carrying amounts once. It is not total liabilities: advance ticket sales, suppliers and other liabilities are different obligations.

**Debt-to-equity = debt and leases ÷ book equity.** A result of 2x means two dollars of debt and leases for each dollar of book equity. “Gearing” and “leverage” describe this same financing question; they are not successive conclusions. Higher gearing generally leaves less book-equity cushion, but asset values, covenants and cash generation matter. Negative equity makes this ratio unsuitable; it does not make the company debt-free.

**Debt-to-assets = debt and leases ÷ total book assets.** This provides another view when book equity is small. The remainder is not all shareholders' funding: other liabilities also finance assets. Neither ratio measures the cash obtainable by selling aircraft or pledged collateral.

## “How much of your operating earnings goes on interest?”

Use **interest cover = reported operating profit ÷ gross interest expense**. We use the reported operating subtotal, not an adjusted EBITDA figure or a reconstruction of EBIT from net profit. Three times cover means three dollars of operating profit for every dollar of interest expense.

Its reciprocal answers the question in percentage terms: **interest expense ÷ positive operating profit**. At 3x cover, interest is equivalent to 33% of operating profit. At 0.5x cover it is 200%—earnings do not cover the interest bill. If the company makes an operating loss, there is no positive earnings pool to allocate: say “operating earnings do not cover interest”, rather than publishing a negative percentage.

This is an accounting earnings comparison, not the share of cash already reserved for creditors. Broad finance costs and net interest are not substitutes for gross interest. Operating-lease expenses under US GAAP and IFRS lease interest are presented differently, so even this familiar ratio is not fully harmonised across jurisdictions.

## “And can you actually meet the repayments?”

Interest is only part of servicing debt. The cash question needs **cash interest + scheduled principal repayments**, with finance-lease principal included once. For an airline we should also show operating-lease payments and aircraft commitments separately. A debt maturity schedule that already includes interest must not have interest added again.

A cash debt-service coverage ratio can compare cash available for debt service with those payments **over the same period and on a stated basis**. It is not one universally prescribed GAAP measure. Covenant definitions can differ. Our database does not yet have complete, comparable inputs to publish it across the airlines.

The cash bridge should begin with operating cash flow, identify whether interest and operating leases are already deducted, allow for necessary capital spending, and then consider principal and any lease payments not already deducted. Financing-classified interest must be allowed for separately. Do not subtract an expense twice. Dividends and discretionary growth spending should be identified separately from unavoidable costs. Cash, restricted cash, investments and undrawn facilities must not be conflated.

Until that bridge is complete, show the disclosed payments in dollars and mark the coverage proportion as **not yet established**. Do not divide future repayments by current revenue or an annualised winter-half result and call that debt-service capacity.

## JetBlue: what the existing evidence says

At June 2026, JetBlue reported USD8,478m of debt and finance leases and USD908m of operating-lease liabilities, against USD1,587m of book equity. Including those leases, that is **USD9,386m of obligations, 5.91x equity and 57.3% of book assets**. This is book leverage, not a market valuation.

Through June, the trailing twelve-month operating loss is USD565m, with USD584m of gross interest expense. Operating earnings therefore do not cover interest. For the six months alone, reported operating cash flow was negative USD35m; capital spending and aircraft deposits consumed USD375m, and debt/finance-lease principal repayments were USD570m. These facts identify a funding problem to investigate; they do not establish insolvency or an imminent default. [June filing](https://www.sec.gov/Archives/edgar/data/1158463/000115846326000075/jblu-20260630.htm).

The June contractual schedule lists **USD1,043m of debt/finance-lease payments including interest and USD146m of operating-lease payments for calendar 2027**: USD1,189m combined. Aircraft purchases of USD383m and other commitments of USD397m are additional listed obligations, not additional debt service. These are forecasts from a June snapshot. They are neither the next twelve months from October nor a complete operating cash budget. The corresponding funding-coverage percentage remains unestablished.

## “So what is your risk profile?”

A useful answer separates the evidence from the unknowns:

| Case | Observed financial pressure | What could change the assessment? |
|---|---|---|
| JetBlue | Significant funding pressure: operating losses, negative operating cash generation and high book gearing | Cash genuinely available, covenant headroom, refinancing terms, collateral, repayment timetable and recovery in earnings |
| Alaska | Lower gearing than JetBlue, but deteriorated interest coverage and capital-spending demands | Updated repayment schedule, integration costs, liquidity and evidence of an earnings recovery |
| LATAM | Positive operating cash generation; financing assessment incomplete | Reconcile debt and leases, account for financing cash payments, and complete maturities, covenants and hedge terms |
| easyJet | Lower book gearing and positive trailing operating profit, with seasonal and transaction risks | Summer cash generation, gross interest detail, acquisition financing, full maturity schedule and available liquidity |

These are **qualitative interpretations of extracted evidence**, not a ranking, probability of default, investment recommendation or agency rating. The case studies have different reporting dates. A positive cash-flow period is not proof of low risk, and missing data is not proof of high risk.

A completed profile should address earnings resilience; liquidity after committed payments; refinancing concentration; covenant and collateral constraints; fuel/FX exposure; and a downside cash bridge. We will not collapse these into a traffic-light score while material inputs are missing.

## What “GAAP-based” means here

Use the issuer's reported financial statements, identify its accounting basis, and reconcile any analytical adjustments. US airlines report under US GAAP; much of the international sample uses IFRS or local standards. We have not restated them all to US GAAP. The debt/lease aggregate and ratios are analytical calculations from reported amounts, not new GAAP line items. EBITDA, EBITDAR, net debt and free cash flow are not automatically standard GAAP measures.

The SEC explains the limitations of EBITDA and free-cash-flow presentations in its [non-GAAP guidance](https://www.sec.gov/rules-regulations/staff-guidance/corporation-finance-interpretations/non-gaap-financial-measures). The IFRS Foundation describes the differing lease-expense presentation in its [IFRS 16 effects analysis](https://www.ifrs.org/-/media/project/leases/ifrs/published-documents/ifrs16-effects-analysis.pdf). These differences are why this edition leads with reported balances, operating profit, interest, cash flows and contractual payments.

## Reproduce

Run `python investor_brief.py` to rebuild the readable PDF, figures and audit tables. The companion workbook is `notebooks/investor_conversation.ipynb`. Case figures come from `data/risk-evidence.json`; annual comparison figures from `data/annual-reporting.json`. Original-source links and locators remain in the annual and interim observation exports. The earlier curve workbook is retained as a historical analytical supplement, not the primary investor presentation.
