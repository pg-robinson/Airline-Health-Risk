# Annual reporting database

Version 0.1, source cutoff 24 October 2026. The database contains 416 manually transcribed or explicitly aggregated financial observations for 24 groups, plus an Emirates airline-only supplement. Sources are issuer reports, issuer releases and regulatory filings. Six additional JetBlue maturity buckets are stored separately.

## What to open

- `database/annual_comparison.csv`: one row per reporting perimeter, in original currency millions. Blank cells are missing or not comparable.
- `database/observations.csv`: every financial observation, with its source link, locator, accounting status and caveat.
- `database/coverage.md`: gaps by airline.
- `database/airline_financials.sqlite`: locally generated database. Rebuild with `python3 build_database.py`, or import the committed `database/database.sql` into SQLite.
- `data/annual-reporting.json`: authoritative curated input. Amend this file when a source correction is required, then rebuild and run tests.

No third-party Python packages are required. A source correction should retain the report period, currency, perimeter, URL and page/table locator. Source hashes are included where a local report was downloaded; hashes identify the downloaded bytes, not audit assurance. Source availability and URLs can change.

## Accounting rules

Financial years end between 1 April 2025 and 31 March 2026. This preserves the agreed annual selection window and is **not the latest balance sheet for every airline**. Qantas therefore uses June 2025 even though a newer annual report exists. The separate JetBlue interim pilot is not merged into this baseline. No revenue ranking or currency translation has been performed.

All observations are in currency millions. Original thousand-unit figures are divided by 1,000; ANA's rounded billion-unit presentation is multiplied by 1,000. Costs and cash capex are positive, losses and operating cash outflows negative. Reported dashes are zero only where the source table supports that reading. Missing values are absent observations, not zero.

The `metrics` table supplies definitions. `observations` has one row per report/metric and links to `reports`, `sources` and `metrics`. `source_backed_observations` joins these for review. `baseline_observations` excludes the supplementary Emirates perimeter. `debt_maturities`, `derived_metrics` and `coverage_gaps` are separate tables.

The debt/lease carrying subtotal chooses one complete, mutually exclusive basis:

1. Combined current and non-current debt including leases; separately reported lease subsets are not added again.
2. Current and non-current borrowings plus current and non-current IFRS leases.
3. US debt/finance leases plus US operating lease liabilities, current and non-current.

This is a subtotal of the selected statement lines, **not a uniform measure of every financing obligation or contractual principal**. Pension deficits, fuel financing, guarantees and other commitments are not automatically added. United's lines include other financial liabilities. No issuer debt headline is substituted when its lease perimeter is unresolved. `debt_basis` records the selected recipe. Source-component observations provide its evidence.

Debt/equity divides that carrying subtotal by positive consolidated book equity. It is blank if equity is non-positive or an input is absent. American's negative equity is explicitly flagged. China Eastern and Air France-KLM include substantial equity-classified perpetual securities; unadjusted book gearing is not ordinary-equity gearing. ANA currently has parent equity and issuer debt only, so total-equity leverage remains blank.

Emirates Group highlights combine Emirates and dnata. The detailed Emirates airline-only statements are a separate supplementary record. Never combine their debt with group revenue or count both as airlines in the sample.

Cash is not yet certified as unrestricted liquidity. Investment balances are not automatically netted from debt. Interest, net interest and broader finance costs have separate metrics. Cash-flow classification, capital-expenditure boundaries, fuel hedges, SAF charges and employee incentives vary; row notes retain those differences. No default probability, credit rating, interest-cover league table or uniform fuel-shock result is calculated from this version.

## Validation and limitations

Checks cover uniqueness, relational integrity, SQL round-trip recovery, reporting windows, source references, selected income-statement reconciliations, debt/lease double counting, negative equity and JetBlue maturity totals. They check transcription consistency and calculation logic; they do not constitute an independent audit of the source extraction.

Twenty of the 24 baseline groups have all nine headline fields in the coverage checklist. Qatar, Korean Air and ANA have remaining extraction gaps. Emirates has a deliberate combined-group disclosure gap and a separately populated airline supplement. Full debt-note work is still required across the sample: maturity ladders, covenant terms, secured assets, undrawn facilities, cash restrictions, lease cash payments and hedge coverage. JetBlue's first maturity schedule excludes operating leases; its 2026 bucket differs from the current-liability classification, so both issuer figures are retained.

The next analytical layer should ingest latest interim reports and comparable prior-year periods, reconcile financing notes, and then apply oil-price, demand, FX and refinancing scenarios. This annual database is the foundation for that work, not a completed current-risk assessment.
