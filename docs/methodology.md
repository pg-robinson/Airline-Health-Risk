# Methodology

## Coverage and dates

Use consolidated passenger airline groups as the unit of analysis. Include state-owned groups with accessible financial statements. Exclude pure cargo companies, lessors, airports and diversified travel conglomerates unless standalone airline financials can be reconciled. Do not count a subsidiary separately when its parent is included.

For the first edition, select by consolidated operating revenue for financial years ending between 1 April 2025 and 31 March 2026, using only statements published by 24 October 2026. This captures calendar-2025 and March-2026 reporters without presenting their periods as identical. Translate revenue using the average exchange rate for each actual reporting period; retain the original currency and rate source. Record material non-airline revenue, including refinery sales, and show whether excluding it changes the boundary of the top 20. Test the cut-off against additional candidates rather than assuming the screening pool is exhaustive.

Use the latest available interim balance sheet for current risk. Prefer trailing-twelve-month earnings calculated as prior full year plus current year-to-date less comparable prior year-to-date. Never divide a full-year balance-sheet stock by a single quarter's earnings and label it annual leverage. Preserve a common full-year comparison alongside the latest-period view. Include easyJet, LATAM Airlines Group, Alaska Air Group and JetBlue Airways as four explicitly selected additional cases, irrespective of whether they qualify for the revenue-based top 20. The current provisional selection therefore covers 24 distinct groups. If a selected additional case enters the verified top 20, retain its case-study designation but count the group only once; do not distort the revenue ranking to force 24 unique names. Apply the same metrics and scenarios to both cohorts. Include a direct Alaska–JetBlue comparison of gearing, costs, liquidity and refinancing exposure.

## Financial measures

| Question | Measure | Treatment |
| --- | --- | --- |
| How much financial leverage? | Gross and net financial debt; debt/equity | Define debt components. If equity is zero or negative, flag it and suppress the multiple. Never use an absolute value to turn negative equity into normal gearing. |
| How much lease exposure? | Financial debt plus lease liabilities, less eligible cash | Add only lease liabilities not already in financial debt. Present the bridge. |
| Can earnings cover interest? | EBIT / gross interest expense | Retain negative earnings. Show cash interest coverage separately where cash payments are available. Net interest can obscure financing burden. |
| How much recurring cash generation? | Cash flow from operations less cash capex and lease principal classified in financing | Reconcile interest and lease classifications first. Include aircraft deposits. Show asset-sale proceeds separately. |
| When does funding become tight? | Monthly liquidity after debt maturities, lease cash payments, capex and minimum operating cash | Separate unrestricted cash, liquid investments and drawable committed facilities. Do not count pledged securities both as cash and as the basis for a facility without adjustment. |
| How quickly do rates reset? | Unhedged floating debt and scheduled refinancing | Instrument-level rates, swaps, currencies and reset dates; bank-versus-bond share alone is insufficient. |
| What drives operating exposure? | Fuel, labour, maintenance, airport/handling, rent and other costs as shares of revenue and costs | Separate depreciation and exceptional items. Compare unit costs within similar stage lengths and business models. |

IFRS 16 uses a single lessee model with recognised lease assets and liabilities, subject to exemptions. US GAAP retains different expense and cash-flow presentation for operating leases. Therefore, reported EBITDA and operating cash flow need reconciliation before cross-border ranking. See [IFRS 16](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-16-leases/) and the [IASB comparison with US GAAP, paragraphs 44–45](https://www.ifrs.org/content/dam/ifrs/meetings/2025/march/iasb/ap7b-overall-assessment-ifrs-16.pdf).

For a supplementary pre-rent earnings measure, start with operating profit, add depreciation and amortisation, and add only rental expense still deducted in that starting profit. Do not add cash lease payments on top of lease depreciation already removed. Show the reconciliation and avoid comparing issuer-defined EBITDAR without it. Exclude nonpositive earnings multiples from ordinal leverage rankings; retain the loss flag.

## Fuel and disruption scenarios

Use jet fuel exposure, with region and currency specified. Crude oil alone misses refining spreads, delivery costs and basis risk. The [IATA June 2026 outlook](https://www.iata.org/en/iata-repository/publications/economic-reports/global-outlook-for-air-transport-june-2026/) describes substantial variation in fuel supply pressure and hedge protection across regions. This is dated context, not an October spot-price assumption.

The first full model should run these **analyst-selected sensitivities, not forecasts or probabilities**:

| Case | Fuel | Demand and response | Finance |
| --- | --- | --- | --- |
| Fuel shock | +20% and +40% jet fuel price | Test 0%, 25% and 50% recovery of incremental fuel cost through fares, with lags | Existing terms |
| Demand shock | Base fuel price | Passenger revenue -10%; distinguish fare/yield change from capacity cuts and model saved variable costs | Existing terms |
| Refinancing shock | Base fuel price | Base operations | +200bp and +400bp on actual unhedged resets and refinancing only |
| Combined shock | +40% jet fuel price | Demand stress, partial fare recovery and capacity response | +400bp on exposed debt; reduced funding access |
| Disruption | Region-specific | Groundings, airspace closure or disruption lasting 30/60/90 days | Compensation timing and cash collateral explicitly modelled |

Simple fuel sensitivity: incremental expense = baseline fuel expense × price change × unprotected share. Net operating effect = incremental expense × (1 − recovery fraction). This approximation holds volumes and foreign exchange constant; nonlinear hedges require instrument-level modelling. Do not add a separate fare increase to revenue if it is already included as recovery.

Rate sensitivity: incremental interest = exposed debt × rate change × fraction of year exposed. Keep refinancing principal and interest separate. Build currency shocks on net currency exposure after revenue offsets and hedges.

For the cash bridge: opening eligible cash + operating cash generation + committed drawable financing − capex − debt principal − lease payments not already in operating cash flow − other required cash outflows = closing cash. Compare each month with minimum operating cash and covenant requirements. Do not subtract interest twice if already in operating cash generation.

## Risk interpretation

Publish separate assessments of earnings resilience, liquidity, refinancing and operating concentration. A high debt/equity ratio alone cannot establish imminent failure. Government or parent ownership is contextual support, not cash until a binding facility or guarantee is evidenced.

Use these decision rules once the cash models are populated:

- **Funding shortfall:** base case breaches minimum cash or a binding covenant without an identified remedy.
- **Stress-sensitive:** base case passes but at least one specified stress causes a shortfall.
- **Resilient within tested cases:** all specified cases pass, with the amount of headroom disclosed.
- **Insufficient evidence:** a material liquidity, maturity, covenant or cash-flow input is unavailable.

Show the assumptions and first month of any breach. These categories are scenario outcomes, not agency ratings or default probabilities. An optional composite score should wait until the component definitions and sensitivity to weighting have been validated. Avoid expressing an arbitrary weighted score as a percentage probability.
