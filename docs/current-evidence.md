# Current evidence: second reporting edition

Research cutoff: **25 October 2026**. The annual baseline remains separate. This release adds **133 interim observations, eight repayment/commitment schedules (48 buckets), and 21 dated fuel-hedge records across 12 groups**. It closes Qatar and Korean Air headline annual gaps and replaces ANA's rounded presentation figures with detailed consolidated statements. All 24 groups still have outstanding credit diligence; **no risk ratings are assigned**.

## Reporting dates matter

| Case | Full statement snapshot extracted | Additional evidence | Main unresolved issue |
|---|---|---|---|
| JetBlue | June 2026; six-month flows | June debt, lease and other contractual schedules | Covenants, collateral, liquidity restrictions and subsequent funding changes |
| Alaska | September 2026; nine-month flows | Debt principal and commitments remain June snapshots | Bridge June maturities to September; lease schedules and current hedge confirmation |
| LATAM | June 2026; six-month flows | July 31 quarterly hedge positions | Reconcile gross debt to financial liabilities; full amortisation and lease schedule |
| easyJet | March 2026; six-month flows | June quarter trading update and July hedge disclosure | Full financing notes and proposed acquisition financing |

[JetBlue](https://www.sec.gov/Archives/edgar/data/1158463/000115846326000075/jblu-20260630.htm) and [Alaska](https://www.sec.gov/Archives/edgar/data/766421/000076642126000046/ex99110202026earningsrelea.htm) show selected debt/lease carrying amounts of USD9,386m and USD7,519m respectively, equivalent to 5.91x and 2.13x positive book equity. Those are different dates, not a contemporaneous ranking. Neither ratio measures debt-service capacity.

## Trailing flows and source differences

Trailing twelve months = previous annual value + current year-to-date value − matching prior year-to-date value. Calculations require an explicitly approved metric, matching currency and consolidated perimeter, and contiguous fiscal periods. Missing comparative figures suppress that metric. A standalone quarterly update is not treated as nine-month data.

On this basis, JetBlue's trailing operating loss through June is USD565m; Alaska's through September is USD290m. Different end dates and integration effects still limit comparison. No adjusted earnings or seasonally annualised six-month numbers are substituted. Cash flows retain issuer classifications: easyJet includes dividends paid within operating activities; LATAM classifies interest paid in financing. Consequently, CFO less capex is not a harmonised free-cash-flow measure.

LATAM's issuer gross debt includes leases, but the difference from its other financial-liability lines remains unresolved. Its issuer headline is retained and comparable debt/equity withheld. easyJet's crew expense is not substituted for total staff costs. [LATAM release](https://www.sec.gov/Archives/edgar/data/1047716/000104771626000087/results-eng2q2026.htm), [easyJet interim statements](https://data.fca.org.uk/artefacts/NSM/MFN/b5400e4e-e8f2-48a1-aadd-fdecdb855799.html).

## Maturity schedules are not interchangeable

The current layer stores each schedule's date, currency, basis and scope. JetBlue's USD8,478m carrying-value maturity total excludes operating leases and interest. Its USD11,311m contractual debt/finance-lease payments include interest. These describe overlapping obligations: **never add them together**. Operating-lease cash payments and purchase commitments are separate schedules. Alaska's USD6,123m June schedule is principal; acquisition accounting adjustments prevent a direct equality with carrying debt. Its lease-payment schedules remain outstanding. See [maturity export](../database/current_maturities.csv).

The June 'remainder 2026' buckets are not payments still outstanding in October. A current refinancing model requires repayments, new facilities, covenant tests, pledged assets and subsequent events to bridge the dates. Full schedules have not been completed across the 24 groups.

## Fuel hedges: date, horizon, instrument and units

Evidence is stored separately for each horizon. A target is not an actual position; a derivative asset is not a percentage of future fuel covered; outstanding barrels without expected consumption do not yield a coverage fraction. Missing remains null. Explicit zero is reserved for an issuer statement of no open positions or a closed programme.

Keep earlier disclosures for history, selecting the latest relevant evidence for an overlapping horizon. easyJet's July update supersedes its May forward percentages; its fiscal year ends September. LATAM's capped collars provide protection within a price range, so a covered percentage does not imply that fraction of every price shock disappears. Do not sum quarterly percentages or multiply the annual fuel sensitivity by one minus coverage. [easyJet trading announcement](https://www.investegate.co.uk/announcement/mfn/easyjet--ezj/trading-update-for-the-quarter-ended-30-june-/9682899).

The annual fuel-expense scenario is unchanged: it is a mechanical expense sensitivity, not a hedge-adjusted oil-price forecast. A new scenario requires volumes, maturities, strikes/caps, jet-fuel/crude basis, currency, settlement timing and pricing responses. See [hedge export](../database/fuel_hedges.csv).

## Events and research queue

JetBlue and LATAM scheduled Q3 releases for October27 and November3 respectively, after this cutoff. easyJet's October15 acquisition scheme announcement introduces a separate financing and ownership review; proposed acquisition debt is not added to historical airline debt. [JetBlue announcement](https://www.ir.jetblue.com/news/news-details/2026/JetBlue-Announces-Webcast-of-Third-Quarter-2026-Earnings-Conference-Call/default.aspx), [LATAM announcement](https://ir.latam.com/English/news/press-releases/news-details/2026/Scheduled-Third-Quarter-2026-Publication-Date-2026-CmvKQJFYgv/default.aspx), [easyJet scheme announcement](https://www.investegate.co.uk/announcement/rns/easyjet--ezj/publication-of-the-scheme-document/9823587).

The [24-group readiness register](../database/risk_readiness.md) is the work queue. Twenty groups have no interim statement set extracted in this layer. Even the four case studies require further debt-note, covenant, liquidity and downside cash-flow work. Dates describe what was extracted, not an exhaustive latest-filing search for every group. The global top-20 ranking also remains provisional.

## Reproduce and audit

`data/risk-evidence.json` is the authoritative input. `build_database.py` invokes `risk_reporting.py` to validate it and generate separate SQLite tables and CSVs. Every observation references a report and source locator; report dates, publication dates where verified, retrieval dates and unaudited/review status remain explicit. Derived trailing rows retain all three arithmetic inputs. Unknown exact publication dates remain null.

Tests cover schedule totals, source references, duplicate observations, temporal/perimeter checks, missing comparative data, hedge fractions, non-positive equity and no substitution of unreconciled debt headlines. They establish internal consistency, not an independent audit of issuer reporting. Ratings require completed research and judgement, not merely passing tests or filling nine headline fields.
