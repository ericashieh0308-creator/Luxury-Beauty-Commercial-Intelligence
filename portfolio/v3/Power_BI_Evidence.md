# Native Power BI evidence extracts

These excerpts come from the optimized PBIP/PBIR/TMDL project. No Desktop screenshot is represented here.

## Representative native measures

```text
measure 'Native median list price' = IF(HASONEVALUE(product_position[vintage]) && HASONEVALUE(product_position[market]) && HASONEVALUE(product_position[snapshot]), MEDIAN(product_position[price]))
measure 'Valid discount depth' = DIVIDE(SUMX(discount_summary, discount_summary[mean_discount_depth] * discount_summary[valid_discount_observations]), SUM(discount_summary[valid_discount_observations]))
measure 'Weighted gross margin' = DIVIDE([Simulated gross profit], [Simulated net revenue])
measure 'Weighted operating margin' = DIVIDE([Simulated operating profit], [Simulated net revenue])
```

## Relationship definitions

```text
relationship 94decf49-a57a-519f-b069-a0ce89f26e81
	fromColumn: fact_simulated_finance.scenario
	toColumn: dim_scenario.scenario

relationship 8803283a-f49c-5c23-a878-6cb9535fd93c
	fromColumn: product_position.cohort_key
	toColumn: dim_cohort.cohort_key
```

## Report pages and canvases

- Brand & Category Performance: 1920 × 1080
- Budget Variance & Scenario Forecasting: 1920 × 1080
- Cross-Market & Historical Comparison: 1920 × 1080
- Customer Reviews & Product Intelligence: 1920 × 1080
- Data Quality & Methodology: 1920 × 1080
- Executive Overview: 1920 × 1080
- Financial Performance & P&L: 1920 × 1080
- Market & Assortment Intelligence: 1920 × 1080
- Pricing & Promotional Intelligence: 1920 × 1080
- SKU, Channel & Promotion Profitability: 1920 × 1080
