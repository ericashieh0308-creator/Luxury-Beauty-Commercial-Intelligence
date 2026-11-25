# Power BI Desktop implementation kit

Prioritize pages 1 and 7. Import the observed CSVs from `data/processed` and the simulated facts from `output/finance` via **Get Data > Text/CSV**. Import [Ivory & Champagne](theme.json) from **View > Themes > Browse for themes**. This kit requires Windows Power BI Desktop to build and validate a native project.

## Model and Power Query

1. Create `ObservedPath` and `FinancePath` text parameters. Use `Csv.Document(File.Contents(ObservedPath & "\\fact_product_snapshot.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])` and promote headers. Repeat for the tables selected below.
2. Set IDs and counts to whole numbers, prices to decimal, dates to date, flags to nullable whole numbers, and categories to text. Preserve blank flags and prices. Set format for USD and CAD explicitly or show the native currency beside every price visual.
3. Load `dim_brand`, `dim_category`, `dim_market`, and `dim_date`. Create one-to-many single-direction relationships from each key to `fact_product_snapshot`. Reject duplicate dimension keys. Link snapshot `id` to `pricing.id` with a unique ID relationship. Treat each comparison endpoint as a separate role if loading endpoint slicers. Leave preaggregated commercial and QA tables disconnected and give them local slicers.
4. Model scenario and month as separate dimensions for the simulated facts. Expose finance measures independently of observational market and SKU filters. Place the evidence label prominently on each financial page.
5. Paste measures individually from [measures.dax](measures.dax). Check one market/vintage/date at a time for precomputed KPIs. Restrict portfolio shares to the same cohort and deduplicate repeated flag metrics.
6. Configure tab order, alt text, titles and accessible contrasting labels. Test slicers, currency cues, zero denominators, totals and export rights in Desktop before distributing.
7. Compare view results with SQLite/CSV for observed data and the workbook for finance. Validate Base annual net revenue $700,824.23 and operating profit $155,492.93 with unchanged defaults. Restrict sample exports to approved aggregates.

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
