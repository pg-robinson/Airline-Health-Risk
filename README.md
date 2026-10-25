# Airline Health Risk

**Research question:** Which major airline groups can absorb a sustained rise in fuel costs, weaker demand and tighter financing without exhausting their available funding?

**Annual reporting database now populated:** 24 airline groups, 426 sourced financial observations, and a separate Emirates airline-only supplement. Updated 25 October 2026. The revenue-based top 20 remains provisional; current-risk assessment and full debt-note extraction are incomplete.

This project examines gearing, cost structure, debt maturity and liquidity using public company disclosures. The intended coverage is 20 major passenger airline groups selected by revenue, plus four additional case studies: **easyJet, LATAM Airlines Group, Alaska Air Group and JetBlue Airways**. The provisional scope is 24 distinct groups; the revenue-based top 20 remains subject to verification. It includes listed and state-owned airlines where sufficiently comparable disclosures exist.

Alaska and JetBlue will receive a direct comparison of gearing, cost structure, liquidity and refinancing exposure, as requested for the study. All four additional cases will use the same financial definitions and stress scenarios as the core sample.

## Start here: an investor conversation

[Read the investor brief (PDF)](reports/investor/investor_brief.pdf) · [Plain-English guide](docs/investor-guide.md) · [Python investor workbook](notebooks/investor_conversation.ipynb)

1. **How much have you borrowed?** Debt and leases relative to book equity and assets.
2. **Do earnings cover interest?** Reported operating profit versus gross interest expense.
3. **Can you meet the repayments?** Scheduled cash interest, principal and leases, with other commitments shown separately.
4. **What is the risk profile?** Explain observed pressures, available funding and unresolved evidence.

These are defined analytical ratios drawn from reported US GAAP, IFRS or local accounts—not a claim that all issuers have been restated to US GAAP. The earlier borrowing-rate and EBITDA proxies are no longer the main investor presentation. Full cash debt-service coverage and overall credit ratings remain unassigned where evidence is incomplete.

## Supporting research workbook

- [Python research workbook](notebooks/airline_resilience.ipynb): executed Jupyter notebook with commentary, charts, gearing, costs and an Alaska–JetBlue fuel sensitivity.
- [HTML reading copy](reports/airline_resilience.html): download and open in a browser to read without code.
- [Reporting workflow](docs/reporting-workflow.md): reproduce the edition and update the research.

The report combines the annual baseline with a separate dated interim evidence layer. It does not assign current risk ratings. Install `requirements-report.txt` before running the full test suite or rendering the notebook. The database builder itself needs no extra packages.

## Current evidence and outstanding work

The update adds 133 interim observations for the four additional cases, eight debt/commitment schedules and 21 dated fuel-hedge records across 12 groups. Coverage is partial: statements, trading updates and notes retain their actual dates. Twenty of 24 groups still lack an extracted interim statement set in this layer.

- [Risk research readiness](database/risk_readiness.md): the outstanding work for every group.
- [Current evidence guide](docs/current-evidence.md): definitions, dates and limitations.
- [Interim comparisons](database/interim_comparison.csv) and [trailing metrics](database/ttm_metrics.csv).
- [Debt and commitment schedules](database/current_maturities.csv) and [fuel hedge evidence](database/fuel_hedges.csv).

## Open the database

- [Annual comparison](database/annual_comparison.csv): each airline’s figures in its reporting currency.
- [Source-linked observations](database/observations.csv): evidence and caveats for every figure.
- [Coverage and gaps](database/coverage.md): what is populated for each airline.
- [Database guide](docs/database-guide.md): definitions, accounting differences and reproducibility.
- [SQL database export](database/database.sql): import into SQLite or rebuild from the curated JSON.

```sh
python3 build_database.py
python3 -m unittest discover -s tests -p "test_database.py"
```

The build creates `database/airline_financials.sqlite` and refreshes the exports. Missing observations remain blank. Debt and leases are combined without double counting; ratios with non-positive equity are withheld. The database preserves original currencies and reporting periods.

## Read the research

- [Methodology](docs/methodology.md): definitions, selection rules and stress scenarios.
- [JetBlue pilot](docs/jetblue-pilot.md): current public evidence and the first calculations.
- [Coverage candidates](data/coverage-candidates.json): screening pool, not a verified ranking.
- [Data specification](docs/data-specification.md): inputs and evidence needed for the full study.

## Reproduce the pilot

Python 3.10 or later; the original pilot uses no third-party packages.

```sh
python3 analysis.py
python3 -m unittest discover -s tests -p "test_analysis.py"
```

The calculation reads the public-source observations in `data/jetblue.json`. It prints ratios and a clearly labelled illustrative fuel sensitivity. It does not calculate a probability of default or assign credit ratings.

## Remaining research

1. Verify the candidate universe and rank eligible consolidated groups using the selection rule.
2. Complete the flagged annual gaps and extract latest interim statements, lease notes, maturities, liquidity restrictions and hedges for each selected group.
3. Reconcile accounting definitions and build a monthly cash bridge for each airline.
4. Produce the comparative risk map and explain each risk designation with evidence.
5. Review all references and calculations before describing the project as a completed sector study.

Only newly authored research and small, attributed public-source observations belong in this repository. Full third-party reports are linked rather than redistributed. No reuse licence has yet been selected for the original project code and commentary.

## Earlier visual reconstruction

The [legacy-style curves](notebooks/research_curves.ipynb) remain available as a historical analytical supplement. Their interest-expense and EBITDA proxies should not be read as GAAP line items, actual borrowing rates or cash available for debt repayment. Use the investor brief above for the current presentation.
