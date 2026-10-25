# Which risk benchmarks does the airline industry use?

Research date: **25 October 2026**. EBITDAR remains useful. Replacing it with book gearing as the main risk measure would lose an important view of airlines' earning capacity. The right change is to reconcile earnings and leases consistently, then connect leverage to cash and contractual obligations.

## What current evidence shows

| Source | Measures used | What it tells us |
|---|---|---|
| Fitch, Lufthansa report, 15 September 2026 | EBITDAR margin, gross and net EBITDAR leverage, fixed-charge coverage | EBITDAR is still a live airline credit benchmark |
| S&P, Lufthansa report, 24 August 2026 | Adjusted debt/EBITDA, funds from operations (FFO)/debt and cash flow measures | Cash generation relative to debt is central; agency adjustments matter |
| Moody's Passenger Airlines methodology, 12 August 2024 | Debt/EBITDA; (FFO + interest)/interest; retained cash flow/net debt | A multi-factor assessment combines leverage, interest capacity and cash generation |

Sources: [Fitch report](https://investor-relations.lufthansagroup.com/fileadmin/downloads/en/more/Fitch_Deutsche_Lufthansa_AG_-_15_Sep_2026.pdf), [S&P report](https://investor-relations.lufthansagroup.com/fileadmin/downloads/en/more/RatingsDirect_DeutscheLufthansaAG_3616411_Aug-24-2026.pdf), [Moody's methodology](https://ratings.moodys.com/api/rmc-documents/426534). The Moody's document is the dated methodology located in this review; its status as the latest effective version was not independently established. The 2026 issuer reports demonstrate actual recent practice, not universal industry cutoffs.

## The investor questions and proposed dashboard

1. **How many years of normalised earnings does the debt represent?** Use lease-consistent gross and net debt/EBITDAR, or a clearly reconciled agency-style adjusted EBITDA measure. Do not mix an agency numerator with an issuer denominator. This is a scale comparison, not literal years to repay: earnings are needed for taxes, investment and other payments.
2. **How much of those earnings is already committed?** Show fixed-charge coverage, with a stated definition of interest and rent/lease payments. Its reciprocal describes the fixed-charge share of positive earnings. It is not full debt-service coverage because principal and investment remain to be paid.
3. **Does the business generate cash after essential investment and financing payments?** Track a reconciled cash bridge and FFO/debt alongside accounting profits. FFO is a defined analytical measure, not simply the cash-flow statement's operating subtotal.
4. **Can it survive a difficult year and refinance on time?** Compare monthly available liquidity with obligations and operating needs under fuel, demand, FX and funding shocks. Test actual covenants separately.

Book debt/equity and debt/assets remain useful context, especially for loss absorption. They should not be the headline credit ranking: buybacks, impairments, fleet age and negative equity can make them misleading.

## Why the calculation changed after 2018

IFRS 16 took effect in 2019. Most former operating-lease expense moved to depreciation and interest, so IFRS EBITDA already excludes much of the old rent charge. US operating-lease presentation differs. **Adding full rent again to an IFRS EBITDA figure can double count the adjustment.** Likewise, include lease liabilities once; do not add a capitalised-rent estimate on top unless explicitly replacing the recorded amount. [IFRS Foundation effects analysis, income-statement comparison and section 8](https://www.ifrs.org/-/media/project/leases/ifrs/published-documents/ifrs16-effects-analysis.pdf).

For this project, begin with reported operating profit, add separately verified depreciation/amortisation, and add only the relevant lease expense still deducted in that subtotal. Publish every adjustment and specify aircraft-only versus broader rental scope. Fixed charges must match that scope: lease interest cannot be counted again inside full lease payments. Non-positive normalised earnings make a debt multiple not meaningful, not reassuringly negative.

We have not yet extracted sufficiently consistent rent and lease cash data across 24 groups to calculate this dashboard. The old EBITDA proxy must not be relabelled EBITDAR. The existing accounting brief remains a factual starting point, complemented by the new [credit story and scenarios](credit-story.md).

## Limits must belong to a company and a definition

For Lufthansa, Fitch's September 2026 downgrade sensitivities include **net EBITDAR leverage above 2.7x and gross above 3.7x**, or **fixed-charge coverage below 2.8x for an extended period**. S&P's August report identifies adjusted **FFO/debt below 40% with limited recovery prospects** as a possible downgrade condition. These are rating sensitivities, not contractual defaults or universal boundaries for every airline. See the reports linked above.

Define three separate kinds of trigger in the database: **contractual**, **agency sensitivity**, and **author stress assumption**. Record source, date, legal entity, numerator/denominator, measurement window, threshold, cure provisions, observed value, and evidence status. Do not colour an airline healthy merely because its observed value is unavailable.

Our comparison chart should eventually use **lease-consistent leverage against fixed-charge coverage**, supported by a liquidity stress panel and maturity timeline. The story must explain the movement and the available response, not simply place a dot in a quadrant.
