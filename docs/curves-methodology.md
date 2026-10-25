# Rebuilding the research curves

Prepared 25 October 2026. These charts reconstruct the five questions in the supplied historical research using the public database. No historical company figures, branding, internal narrative or risk designations are carried forward.

## Scope and dates

The cross-sectional bars use the 24-group annual baseline, with years ending June 2025–March 2026. These are the current database's annual observations, **not uniformly the latest available financial statements**. The Emirates airline-only supplement is excluded to prevent double counting. Consolidated groups include non-airline operations where reported. The global top-20 selection remains provisional.

The leverage/coverage chart adds arrows for Alaska and JetBlue: annual positions to their dated September and June 2026 balance sheets respectively, combined with matching trailing-twelve-month earnings and interest. Other groups are not silently updated or mixed with quarterly flows. easyJet's March interim and June trading update, and LATAM's June interim, remain available in the database; their comparable gross-interest/debt inputs do not yet support the same overlay.

## What changed from the old charts

| Historical question | Rebuilt measure | Interpretation and limitation |
|---|---|---|
| Who owes the most debt? | Selected debt and lease carrying amount, USD billions | Includes US operating leases; differs from a pure interest-bearing-debt total. No issuer headline substitutes for unresolved lease coverage. |
| Who pays the highest interest rate? | Annual reported gross interest expense / closing financing debt | An expense proxy, **not** a weighted coupon, market yield or actual portfolio borrowing rate. Average debt, capitalised interest and lease-interest classification require further work. US operating leases are excluded from this denominator. |
| Who generates the most revenue? | Reported consolidated annual revenue, USD billions | Revenue definitions and non-airline businesses differ. This does not establish the world's top-20 ranking. |
| Who keeps the most money? | Statutory operating profit + clean reported depreciation/amortisation | An **EBITDA proxy, not EBITDAR or cash retained**. Rent add-backs are unavailable and lease accounting differs. Mixed impairment/provision add-backs are excluded. |
| Leverage versus debt-service capacity | Debt and leases / positive book equity, against operating profit / gross interest | Uses gross interest, unlike the historical net-interest chart. Negative equity, missing inputs and incompatible definitions are omitted, never mapped to zero. |

No positive/negative risk zones, healthy labels or default probabilities are assigned. The 1x coverage line only shows the arithmetic point where operating profit equals gross interest expense; it is not a covenant or a credit-rating boundary. Cash taxes, principal payments, capital spending, lease payments and restricted liquidity are not represented by this scatter plot.

## Currency conversion

All three USD-denominated charts use **one common set of US Treasury reporting rates dated 31 December 2025**. This is a transparent presentation convention for comparing scale across currencies, not conversion at each fiscal year's average or its individual closing rate. A different common date can change relative rankings. Do not interpret these plotted amounts as reported USD results or today's USD debt values.

Formula: local-currency millions ÷ local-currency units per USD ÷ 1,000 = presentation USD billions. USD remains unchanged apart from million-to-billion scaling. Ratios use original-currency figures and need no FX conversion.

Source: [US Treasury rates dataset](https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/treasury-reporting-rates-of-exchange). Exact API URL, original rows, retrieval date and conversion convention are retained in [chart-fx.json](../data/chart-fx.json).

## Coverage and regions

Every chart records included and omitted airlines in [chart_coverage.csv](../reports/curves/chart_coverage.csv). The plotted numbers and underlying ingredients are in [chart_data.csv](../reports/curves/chart_data.csv), linked by airline identifier to the source-backed annual observations. Interim overlay calculations are in [interim_map_updates.csv](../reports/curves/interim_map_updates.csv), with provenance in the current-evidence database.

Regions retain the historical five-colour concept: Greater China (including Hong Kong), Americas, Europe, Middle East & Africa, and Asia Pacific. Turkish Airlines is grouped in Middle East & Africa for this presentation. The colours describe geography only. They encode neither risk nor ownership.

IAG, Air France–KLM and Air Canada's extracted D&A add-backs contain impairment or provisions and are excluded from the EBITDA proxy until those components are separated. ANA and Emirates Group lack a comparable debt/lease subtotal. American's negative book equity prevents a meaningful debt/equity placement. Net interest and broad finance costs are not used as substitutes for gross interest in the rate proxy or coverage screen.

## Outputs and reproduction

- `reports/curves/index.html`: readable chart gallery with embedded images.
- `reports/curves/*.svg`: scalable figures for reuse.
- `reports/curves/*.png`: high-resolution local chart exports.
- `reports/curves/airline_curves.pdf`: five-page local print/export version.
- `notebooks/research_curves.ipynb`: executed companion Python workbook.

Install `requirements-report.txt`, then run `python curves.py`. Run `python -m unittest discover -s tests` for validation. To refresh the companion notebook and its reading copy, run `python render_report.py --notebook notebooks/research_curves.ipynb --output reports/curves/notebook.html`.

The numerical tests check FX direction/scale, debt-perimeter selection, exclusion of mixed add-backs and missing inputs, and matching interim coverage calculations. They do not audit issuer reporting or establish creditworthiness.
