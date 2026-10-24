"""Reproduce the limited JetBlue pilot using only the Python standard library."""
import json
from math import isfinite
from pathlib import Path


def ratio(numerator, denominator):
    """Missing or nonpositive denominator is not an interpretable multiple."""
    if numerator is None or denominator is None or denominator <= 0:
        return None
    if not isfinite(numerator) or not isfinite(denominator):
        raise ValueError("Inputs must be finite")
    return numerator / denominator


def fuel_sensitivity(expense, price_change, protected_share, recovery):
    """Constant-volume incremental fuel expense net of assumed fare recovery."""
    if any(x is None for x in (expense, price_change, protected_share, recovery)):
        return None
    if not all(isfinite(x) for x in (expense, price_change, protected_share, recovery)):
        raise ValueError("Inputs must be finite")
    if expense < 0 or price_change < -1:
        raise ValueError("Invalid expense or price change")
    if not 0 <= protected_share <= 1 or not 0 <= recovery <= 1:
        raise ValueError("Shares must be between zero and one")
    return expense * price_change * (1 - protected_share) * (1 - recovery)


def calculate(document):
    observations = document["observations"]
    for item in observations.values():
        if item["source"] not in document["sources"] or not item.get("locator"):
            raise ValueError("Every observation needs a known source and locator")
    values = {key: item["value"] for key, item in observations.items()}
    def subtract(*keys):
        items = [values.get(k) for k in keys]
        return None if any(v is None for v in items) else items[0] - sum(items[1:])
    costs = [values.get("fuel"), values.get("labour")]
    combined = None if any(v is None for v in costs) else sum(costs)
    return {
        "debt_to_equity_x": ratio(values.get("debt"), values.get("equity")),
        "debt_less_cash_usd_m": subtract("debt", "cash"),
        "half_year_operating_margin": ratio(values.get("ebit"), values.get("revenue")),
        "half_year_ebit_gross_interest_x": ratio(values.get("ebit"), values.get("interest")),
        "fuel_and_labour_share_of_operating_cost": ratio(combined, values.get("operating_costs")),
        "cfo_less_capex_and_deposits_usd_m": subtract("cfo", "capex", "aircraft_deposits"),
        "illustrative_fuel_20pct_no_protection_no_recovery_usd_m": fuel_sensitivity(values.get("fuel"), .20, 0, 0),
        "illustrative_fuel_20pct_no_protection_50pct_recovery_usd_m": fuel_sensitivity(values.get("fuel"), .20, 0, .50),
        "liquidity_risk_category": "Unassigned: monthly cash bridge and supporting inputs required"
    }


if __name__ == "__main__":
    source = Path(__file__).parent / "data" / "jetblue.json"
    print(json.dumps(calculate(json.loads(source.read_text())), indent=2, allow_nan=False))
