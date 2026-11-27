# Luxury & Beauty Commercial Intelligence · Power BI

Open [Luxury_Beauty_Commercial_Intelligence.pbip](Luxury_Beauty_Commercial_Intelligence.pbip) in current Power BI Desktop. The project includes an enhanced PBIR report, TMDL model, Ivory & Champagne theme, and populated report definitions for all ten pages. The public demo uses fictional catalog records and simulated financial results.

## Open and refresh on Windows

For the stability-first workflow, see the [two release candidates](release-candidates.md). The launcher opens a prepared local copy with DemoRoot set. The manual workflow below is available for inspecting the repository PBIP directly.

Run in PowerShell from the repository root with your project Python environment configured.

```powershell
$python = '.\.venv\Scripts\python.exe'
& $python -m beauty.demo
if ($LASTEXITCODE -ne 0) { throw 'Demo generation failed.' }
& $python -m scripts.validate_powerbi
if ($LASTEXITCODE -ne 0) { throw 'Power BI project validation failed.' }
(Resolve-Path 'output/demo').Path
Start-Process (Resolve-Path 'dashboard/powerbi/Luxury_Beauty_Commercial_Intelligence.pbip').Path
```

Set the **DemoRoot** text parameter under **Transform data > Edit parameters** to the absolute folder printed above, then choose **Apply changes** or **Close & Apply** and refresh. Point to the folder containing both `catalog` and `finance`. This is the only source setting required. Save machine-specific settings in a separate untracked copy of the project or revert the parameter value before committing changes. Desktop must load the model on first open after setting this parameter.

For repeat runs, the launcher can open either candidate in a new local working copy. Its optional Update switch uses a fast-forward-only pull and requires a clean worktree.

Use the built-in report page tabs to navigate. No manual recreation of queries, relationships, measures, visuals, or theme import is required for this project. The separate [Power Query expression](PortfolioTables.pq) and [DAX reference](measures.dax) are for reuse or inspection.

## Pages and verification

| Page | What to check in Desktop |
|---|---|
| Executive Overview | Check the four source-count cards and compare market and brand coverage with the synthetic export. |
| Market & Assortment Intelligence | Verify cohort-record counts and that distinct products and SKU keys report at one market, vintage and snapshot. |
| Brand & Category Performance | Pick one cohort and verify that the brand and category charts and known-flag denominators respond. |
| Pricing & Promotional Intelligence | Switch between US and CA cohorts independently. Verify native currency, category tiers, eligible discount ratios, and unknown flag handling. |
| Customer Reviews & Product Intelligence | Confirm historical review counts, lexicon topic mentions, and per-product aggregates. |
| Cross-Market & Historical Comparison | Filter the comparison type. Confirm candidate and accepted counts remain separate and absent gaps read **Not available**. |
| Financial Performance & P&L | Check month order, Base default, Bull and Bear switches, and totals. Base annual revenue is USD 700,824.23 and operating profit is USD 155,492.93 with default drivers. |
| Budget Variance & Scenario Forecasting | Check the scenario trend and fixed Base vs Bull variance and PVM detail. |
| SKU, Channel & Promotion Profitability | Verify scenario KPI isolation, monthly channel contribution, and discount/uplift filters. At 15% discount and 20% uplift, simulated contribution changes by about −USD 455 and ROI is about −30.3%. |
| Data Quality & Methodology | Inspect severity counts, parse-valid denominators, and audit notes by source field. |

## Model and data governance

- Market, category and cohort filters drive compatible catalog facts. The cohort key combines market, vintage and snapshot. Representative-product counts differ from raw records, and distinct counts are scoped to one cohort. Catalog coverage describes the sample.
- Scenario filters drive only simulated forecast and SKU facts. Measures default to Base when the filter is cleared and return blank for an ambiguous multi-scenario selection. Weighted margins divide total profit by total revenue. Channel, budget, PVM and campaign tables are separate modeled grain and assumptions.
- Reviews are historical aggregates. Quality completeness counts evaluated source fields. Match confidence describes candidates. The public demo has no eligible price gaps, verified FX, CPI, or industry benchmark inputs.
- Keep licensed data, private exports, PBIX, and caches local. The native report's labels explicitly describe the generated synthetic catalog and simulated finance. Use a separate private working copy if adapting the report to licensed sources, and update evidence labels before any use.

For visual defaults and mechanics, see the [theme formatting guide](theme-formatting.md). For reproducible checks and remaining Desktop verification, see the [final page-by-page QA report](final-qa-report.md) and [technical validation guide](validation.md).
