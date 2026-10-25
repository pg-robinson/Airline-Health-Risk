# Reporting workflow

The Jupyter notebook is the research workbook: narrative, calculations, editable assumptions, charts and source evidence together. The HTML export is the reading copy. GitHub displays the saved notebook outputs, so readers do not need to run Python to inspect the results.

## Reproduce this edition

The report was tested with Python 3.14. Create an isolated Python environment, install the report requirements, then run:

```sh
python -m pip install -r requirements-report.txt
python build_database.py
python -m unittest discover -s tests
python render_report.py
```

`render_report.py` executes every notebook code cell in a fresh kernel, saves the outputs in `notebooks/airline_resilience.ipynb`, and creates `reports/airline_resilience.html`. It also refreshes three PNG charts. An execution error stops the export. Do not hand-edit saved outputs.

Open the notebook in a Jupyter-compatible editor to explore it interactively. The `FUEL_EXPENSE_SHOCK` cell controls the Alaska–JetBlue sensitivity. It changes reported fuel expense, not the oil price. No assumptions about hedge recovery or fare pass-through are embedded.

The existing pilot and database validation use the standard library. The new reporting tests require pandas from `requirements-report.txt`.

## Editorial structure

1. State the question and reporting date.
2. Explain data coverage and exceptions before presenting comparisons.
3. Show balance-sheet financing, then operating cost exposure.
4. Develop a named case study with compatible currencies, periods and accounting.
5. State each scenario assumption alongside the result.
6. Explain what evidence could change the conclusion.
7. Provide sources and an explicit work queue.

The current edition is an annual baseline screen. It does not make the top-20 revenue ranking final or assign current credit ratings. The next edition should first ingest matching interim periods, debt and lease maturity notes, unrestricted liquidity and fuel hedges. Keep those facts separate from annual selection data. Use an explicit cash-flow bridge before discussing survival horizons.

For each new edition, log source additions and corrections separately from methodology changes. Re-execute, review source links and missingness, inspect exported charts, and then publish both the saved notebook and the HTML reading copy. Do not silently change the historical cutoff when updating a single airline.
