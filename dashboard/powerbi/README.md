# Power BI Desktop implementation kit

The public demo uses generated fictional catalog records and simulated finance tables. Native report creation and validation require Windows Power BI Desktop. The kit automates CSV selection, headers, blank normalization, and core type assignments through a reusable M loader.

## Shortest Desktop workflow

1. Run `python -m beauty.demo`. It writes the synthetic catalog to `output/demo/catalog` and simulated finance to `output/demo/finance`.
2. In Desktop, open **Transform data > New source > Blank query > Advanced Editor**, paste [PortfolioTables.pq](PortfolioTables.pq), and replace the two folder paths with your absolute demo paths. Name the query `PortfolioTables` and disable **Enable load** for it.
3. Create one blank query per table you want. In the formula bar, paste `= PortfolioTables[assortment_counts]` and name it `assortment_counts`. Repeat for `portfolio`, `discount_summary`, `comparison_coverage`, `quality_report`, and `fact_simulated_finance` for the first two pages. Add other tables from the record as needed. Select **Close & Apply**.
4. Import [Ivory & Champagne](theme.json). Under **Modeling > New measure**, paste the measures for the loaded tables from [measures.dax](measures.dax). For a first executive page, add source and distinct-product cards, a **Portfolio** category bar, and comparison availability. Use a single vintage, market, and snapshot for each visual. For finance, add a scenario slicer, monthly line chart, operating profit and weighted gross margin.
5. Review the [KPI definitions](../../docs/methodology.md) and add the star-schema tables and relationships below when you extend beyond the first two pages. Validate filters against the synthetic CSVs and the workbook, then save in Desktop.

The M loader is source text. It has not been executed in Power Query Desktop here. The release includes no PBIX or PBIP.

## Model and Power Query

1. Create `ObservedPath` and `FinancePath` text parameters. Use the loader with the desired catalog and finance folders. Keep a separate Desktop file for the public synthetic demo and any licensed local work.
2. Set IDs and counts to whole numbers, prices to decimal, dates to date, flags to nullable whole numbers, and categories to text. Preserve blank flags and prices. Set format for USD and CAD explicitly or show the native currency beside every price visual.
3. Load `dim_brand`, `dim_category`, `dim_market`, and `dim_date`. Create one-to-many single-direction relationships from each key to `fact_product_snapshot`. Reject duplicate dimension keys. Link snapshot `id` to `pricing.id` with a unique ID relationship. Treat each comparison endpoint as a separate role if loading endpoint slicers. Leave preaggregated commercial and QA tables disconnected and give them local slicers.
4. Model scenario and month as separate dimensions for the simulated facts. Expose finance measures independently of observational market and SKU filters. Place the evidence label prominently on each financial page.
5. Paste measures individually from [measures.dax](measures.dax). Check one market/vintage/date at a time for precomputed KPIs. Restrict portfolio shares to the same cohort and deduplicate repeated flag metrics.
6. Configure tab order, alt text, titles and accessible contrasting labels. Test slicers, currency cues, zero denominators, totals and export rights in Desktop before distributing.
7. Compare visual results with SQLite/CSV for observed data and the workbook for finance. Validate Base annual net revenue $700,824.23 and operating profit $155,492.93 with unchanged defaults. Restrict sample exports to approved aggregates.

## Page specifications and wireframes

Each wireframe lists the top KPI strip, central chart pair, and lower detail panel. Keep global menu navigation at the top and page slicers on the left.

| Page | Layout from top to bottom | Slicers and safeguards |
|---|---|---|
| 1 Executive Commercial Overview | Product count, priced coverage, median US list, promo known share / category share bars, price histogram / cohort KPI table | US default, vintage, date. Use single snapshot selection |
| 2 Brand & Product Portfolio | Brands and SKUs / brand × category matrix, flag mix bars / brand-category detail | Brand, category, market, date. Use source counts and known flag denominators |
| 3 Pricing & Premiumization | Median, spread and discount depth / category price bands, price–rating scatter / price ladder table | Category, brand, market, snapshot. Use native currency consistently |
| 4 2023 vs 2026 Price Comparison | Eligible pairs, median change and coverage / matched price-gap histogram, tier migration matrix / status and price-pair table | Category, brand, match status and comparison dates |
| 5 US vs Canada Market Intelligence | FX date, paired count, median USD gap / category gap dots, FX stress ranges / USD/CAD list-price pairs | Same-day snapshot and product/SKU scope. Show FX direction |
| 6 Consumer & Review Intelligence | Review count, rated coverage / historical sentinel rating and topic bars / product review summary | Historical product. Keep review text out of exports |
| 7 Commercial Finance & P&L | Revenue, gross margin and operating profit / monthly P&L trend, operating profit waterfall / budget versus simulated actual table | One case and month. Label simulated USD |
| 8 Forecast & Scenario Planning | Annual scenario comparison / case operating-profit lines, month × case matrix / drivers and variance | Case and month. Use weighted annual margins |
| 9 Promotion & Profitability | Incremental contribution, ROI and breakeven / discount-versus-contribution curve, sensitivity matrix / campaign cost detail | Select one uplift and discount for headline cards |
| 10 Data Quality & Methodology | Invalid, missing and duplicate issues / issue-by-file bar, candidate status chart / lineage dictionary | Vintage, member, issue and field. Display source licensing status |

Use ivory backgrounds, black foregrounds, muted champagne accent fills and differentiated taupe supporting series. Add direct labels on charts that depend on color.

### Readiness and unavailable evidence

Load `assortment_counts`, `discount_summary`, `comparison_coverage`, and `quality_completeness` as separate aggregate tables. Use shared cohort slicers only where dimension grain agrees. Use a single market, vintage and snapshot to display distinct counts from precomputed aggregates. Keep the underlying numeric gaps blank for calculations. Use **Matched Gap Display** and **Comparison Availability** on the price-pair summary cards, with accepted and priced pair counts beside them. Use `match_coverage` for confidence and reason counts and present `quality_completeness` alongside issue rates. Some comparison tables may have only headers, so check source types explicitly and retain an availability card from the coverage table. Dashboard assets have no native Power BI Desktop validation in this environment.

See [theme formatting and PBIP/PBIR workflow](theme-formatting.md) for schema validation, supported typography defaults, and a method to restyle an existing Desktop report in place.
