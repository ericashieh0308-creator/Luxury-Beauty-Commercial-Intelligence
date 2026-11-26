# Executive report | Premium beauty commercial intelligence

## Executive summary

Use catalog analytics to understand assortment and price positioning, then use a separate financial model to decide whether a campaign can clear a contribution hurdle. The pipeline and workbook support both decisions. The licensed archive run supplied by the project owner produced candidates for cross-market and year-over-year comparison. No pair cleared the comparability requirements, so cross-market price gaps and price inflation remain **not available**. Individual catalog views and the planning model can support Version 1.0 independently.

## Business objectives

- Identify where brand and category coverage is concentrated within each snapshot.
- Characterize the native-currency price ladder, representative products, verified discount observations and platform flags.
- Combine costs, returns, channel assumptions and campaign expense in a simulated profitability decision.
- Explain what evidence a stakeholder would need before making a claim about national price gaps or historical changes.

## Architecture and quality

Python streams licensed files locally into SQLite with source checksums and audit coordinates. Commercial calculations use eligibility checks and known-value denominators, then export tables for Streamlit and the Power BI implementation kit. The public version generates fictional example records with the same pipeline. The finance model uses a separate set of simulated drivers and outputs.

The source validation surfaced missing sale prices, out-of-range ratings, and a sale value above list. The pipeline preserves source evidence and omits invalid values from affected KPIs. Unknown flag shares remain unavailable. Review topics reflect historical language captured by a simple lexicon and need further validation for customer-level decisions. Use the [data dictionary and methodology](../docs/methodology.md) to reconcile source, distinct-item, and KPI representative counts.

## Commercial view

| Lens | Decision use | Interpretation |
|---|---|---|
| Brand and category assortment | Identify segments for a range review | Product and SKU counts reflect sample coverage |
| Price tiers and valid discounts | Inspect category-relative positioning and promotion candidates | Keep USD and CAD separate. Use eligible list prices and explicit sale observations |
| Bestseller, new, exclusive and online-only flags | Identify records for merchandising follow-up | Shares use known flags, with completeness |
| Historical reviews | Identify terms and topics for qualitative follow-up | Coverage and sentiment describe the historical sample |
| Match queues | Prioritize verification of sizes and variants | Candidate counts alone yield no quantitative change or price gap |

## Simulated financial decisions

| Scenario | Annual net revenue | Annual operating profit |
|---|---:|---:|
| Base | USD 700,824 | USD 155,493 |
| Bull | USD 771,141 | USD 204,022 |
| Bear | USD 586,266 | USD 68,604 |

At the default 15% promotional discount, 20% assumed volume uplift, and USD 1,500 campaign cost, simulated revenue increases by USD 6,110 while contribution falls by USD 455. The offer needs at least 1,219 modeled whole units to reach contribution breakeven. The table and campaign values reconcile to the [simulated workbook and case](illustrative-financial-case.md). They describe an illustrative retailer.

## Recommended actions

1. Use the contribution breakeven as a campaign gate. Require actual landed costs, variable fees, return rates and an incrementality estimate before committing budget.
2. Prioritize catalog quality by the decision affected. Verify currency and point-price eligibility first for pricing, and review known flag coverage before comparing merchandising cohorts.
3. Obtain verified product specifications before upgrading match candidates. Add dated reference rates and CPI only for comparisons that already have defensible pairs.

## Limitations and publication

The source snapshots do not measure sales market share, historical assortment growth, or realized sale prices. Benchmark endpoints were inaccessible from the cloud environment. The [external-data guide](../docs/external-references.md) documents local retrieval. The public report and dashboard screenshots use synthetic catalog examples or simulated financial results. They include no licensed row extracts, reviewer text, or identifiable brand-level results.
