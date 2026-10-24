# Data and evidence specification

Each observation needs: entity ID, consolidated perimeter, metric, value, unit, currency, period start/end, publication date, access date, source URL, page/table/note locator, accounting basis, reported/derived status and adjustment rationale. Missing is `null`, never zero. Preserve the reported number separately from the normalised number.

Collect the following for every selected group:

- Statements: revenue, operating profit, depreciation/amortisation, gross interest expense, equity, cash, investments, operating cash flow, cash capex and aircraft deposits.
- Cost structure: fuel, labour, maintenance, airport and handling fees, aircraft rent, other costs, exceptional items, ASKs/ASMs, RPKs/RPMs, load factor, yield and stage length.
- Debt: bonds, bank loans, export-credit debt, finance leases, operating leases, secured/unsecured amounts, currency, fixed/floating rates, hedges, maturity schedule, coupon and covenant definitions.
- Liquidity: restricted cash, security eligibility, committed facilities, drawings, undrawn availability, borrowing-base restrictions, collateral calls, minimum cash and material covenant headroom.
- Exposure: fuel volumes, effective fuel price, hedge volumes/prices/maturity/basis, net currency mismatch, aircraft delivery commitments, groundings, concentration by geography, cargo and loyalty cash flows.

Use regulator filings and audited reports first, then company interim reports and releases. Secondary rankings locate candidates but do not substitute for financial statements. Disclose fiscal-year mismatches, acquisitions and discontinued operations. Keep the latest interim data visibly distinct from the selection-year revenue.

Reconcile cost lines to operating costs, debt components to total debt, maturities to their stated carrying-value or principal basis, and cash movements to statements. Check leases are counted once. Validate ratio denominators and signs. For negative equity or negative earnings, display the financial condition instead of a misleading multiple. Record material missing data beside the affected result.

The JetBlue pilot uses a smaller JSON format with source IDs and table locators. Its observed figures have been manually transcribed and the arithmetic tested. The broader collection pipeline and monthly stress model remain to be implemented.
