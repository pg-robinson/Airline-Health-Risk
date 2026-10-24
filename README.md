# Airline Health Risk

**Research question:** Which major airline groups can absorb a sustained rise in fuel costs, weaker demand and tighter financing without exhausting their available funding?

Research design and JetBlue pilot, prepared 24 October 2026. **The global top-20 comparison is not yet populated or ranked.**

This project examines gearing, cost structure, debt maturity and liquidity using public company disclosures. The intended coverage is 20 major passenger airline groups selected by revenue, plus JetBlue as an additional case study. It includes listed and state-owned airlines where sufficiently comparable disclosures exist.

## Read the research

- [Methodology](docs/methodology.md): definitions, selection rules and stress scenarios.
- [JetBlue pilot](docs/jetblue-pilot.md): current public evidence and the first calculations.
- [Coverage candidates](data/coverage-candidates.json): screening pool, not a verified ranking.
- [Data specification](docs/data-specification.md): inputs and evidence needed for the full study.

## Reproduce the pilot

Python 3.10 or later; no third-party packages required.

```sh
python3 analysis.py
python3 -m unittest discover -s tests
```

The calculation reads the public-source observations in `data/jetblue.json`. It prints ratios and a clearly labelled illustrative fuel sensitivity. It does not calculate a probability of default or assign credit ratings.

## Remaining research

1. Verify the candidate universe and rank eligible consolidated groups using the selection rule.
2. Extract full-year and latest interim statements, lease notes, maturities, liquidity restrictions and hedges for each selected group.
3. Reconcile accounting definitions and build a monthly cash bridge for each airline.
4. Produce the comparative risk map and explain each risk designation with evidence.
5. Review all references and calculations before describing the project as a completed sector study.

Only newly authored research and small, attributed public-source observations belong in this repository. Full third-party reports are linked rather than redistributed. No reuse licence has yet been selected for the original project code and commentary.
