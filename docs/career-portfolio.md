# Career portfolio materials

## Résumé bullets

Use the bullets that reflect your own contribution. Financial figures in this project describe a simulation.

### Financial Analyst / FP&A

- Built a 12-month Excel and Python planning model with Base, Bull, and Bear P&L scenarios, weighted margins, and five workbook reconciliation checks.
- Reconciled 36 scenario-month observations and a 12-month price–volume–mix bridge to explain modeled revenue and contribution changes.
- Modeled promotion ROI and contribution break-even across 35 discount and volume-response combinations, including the effect of returns, channel cost, and campaign spend.

### Business Analyst / BI Analyst

- Developed a 10-page Power BI report with 76 visuals, a 28-table semantic model, and 32 DAX measures covering commercial analysis, finance, and data quality.
- Implemented a Python and SQLite ingestion workflow with source hashes, validation, and auditable exports for Power BI and Streamlit.
- Designed reproducible synthetic demos and reusable checks for source types, report bindings, scenario totals, and model integrity.

### Luxury & Beauty Commercial Analyst / Merchandising Analyst

- Built cohort-level assortment and pricing views to compare brand and category representation in native USD and CAD.
- Developed product- and SKU-level coverage metrics, category-relative pricing tiers, and eligible discount analysis with documented denominators.
- Combined merchandising signals with a simulated SKU, channel, and promotion contribution model to evaluate when a proposed discount warrants further investigation.

## LinkedIn Projects description

**Luxury & Beauty Commercial Intelligence Platform — Advanced Commercial Decision Intelligence**

An independent case in retail commercial analytics and FP&A. The project uses Python and SQLite to build auditable assortment, pricing, review, and quality views. A separate Excel and Python planning model tests Base, Bull, and Bear scenarios, budget variance, SKU and channel contribution, and promotion break-even. The portfolio includes a ten-page Power BI report and a local Streamlit demo built around synthetic catalog data and simulated financial results.

## LinkedIn Featured description

A beauty retail analytics portfolio with a ten-page Power BI report, an Excel planning workbook, and an interactive Streamlit simulator. The public demo shows how to evaluate assortment coverage and whether a promotion earns its spend under explicit assumptions.

## LinkedIn launch post

I’m sharing an independent beauty retail analytics project built around a practical question: when does a promotion generate enough contribution to justify its cost?

I built a Python and SQLite workflow for assortment, pricing, and review evidence, then created a separate planning model in Excel and Python. The ten-page Power BI report and local Streamlit demo make it possible to follow both workflows. In the illustrative campaign, a 15% discount with 20% assumed unit uplift increases modeled revenue while reducing contribution after campaign cost. The model makes that trade-off auditable.

The public catalog is synthetic and all financial outcomes are simulated. I’ve included the methodology, portfolio visuals, and reproducibility instructions in the GitHub repository.

## Interview introductions

**30 seconds.** I built a beauty retail decision-support project that combines auditable catalog analytics with a simulated financial model. I used Python and SQLite to evaluate assortment, pricing, and review coverage, then Excel and Power BI to explain scenario P&L and promotion break-even. One modeled promotion grows revenue but loses contribution, which shows why I would use a profit hurdle to evaluate an offer.

**60 seconds.** The project starts with two questions: where should a beauty team review assortment and pricing, and what unit response would make a promotion viable? Python and SQLite preserve source lineage and normalize product, market, date, and currency fields. Power BI shows coverage, category tiers, and available review evidence. A separate simulated P&L models units, costs, returns, and expenses. I reconciled planning outputs with Excel and use Streamlit to vary discount and uplift. The public catalog is synthetic. Cross-market gaps are unavailable because the match evidence does not qualify.

**Two minutes.** Begin with the Executive Overview and explain why catalog records measure coverage. Move to pricing and show how market and snapshot filters keep USD and CAD separate. Explain what the matching queue can support and why you would withhold a price-gap claim. Then open the financial workbook or profitability dashboard. Walk through the Base P&L, weighted margins, and Base-versus-Bull variance. Show the promotion example with a 15% discount and 20% assumed unit uplift. Simulated revenue rises USD 6,110, but contribution falls USD 455 after campaign cost. Explain how the modeled 1,219-unit break-even informs a decision to test the offer or revise its terms. Close with how you verified outputs and what actual transactions or experiment data would be needed.

## 15 interview questions and answers

1. **What decision does the project support?** It helps prioritize assortment or price review and separately tests whether promotion contribution covers campaign spend.
2. **What is the catalog fact grain?** One retained source record scoped by vintage, market, snapshot, and product, with a SKU when supplied and file and row lineage.
3. **Why SQLite?** It makes the local case reproducible and supports joins, keyed facts, SQL views, and integrity checks without managing a database server.
4. **How do you avoid double counting product coverage?** Scope distinct counts to a market, vintage, and date, and disclose which record represents a product for assortment KPIs.
5. **How do you use SQL for quality checks?** Query exception counts and evaluated rows by source and field. A grouped issue count is interpreted alongside its denominator and classification.
6. **How do you handle mixed currencies?** Keep prices in native currency by market. Convert only when an eligible matched pair and documented dated FX are both available.
7. **Why are comparison gaps unavailable?** Candidate matches can share a name or identifier, but comparable prices also require verified size or variant and eligible point-in-time prices. The public demo has no qualifying pairs.
8. **How do you handle missing flags and invalid ratings?** Keep missing flags unknown, disclose known denominators, and exclude invalid ratings from rating KPIs while retaining audit evidence.
9. **How does scenario selection work in Power BI?** A scenario dimension filters the simulated forecast and SKU facts. The forecast measure uses Base when the selector is cleared. The fixed Base-versus-Bull variance view is identified separately.
10. **How do you calculate annual gross margin?** Divide summed annual gross profit by summed annual net revenue so each period is weighted by revenue.
11. **How do you calculate promotion ROI?** Divide incremental contribution after campaign cost by the campaign cost when that denominator is positive.
12. **What does break-even mean in your simulator?** It is the modeled unit level required for the offer to match baseline contribution after campaign cost.
13. **How do you interpret an expense variance?** A simulated expense above budget is unfavorable under the documented sign convention. Revenue and profit increases have the opposite interpretation.
14. **How do you validate PVM?** Sum price, volume, mix, and any assortment effects and reconcile the bridge to simulated net revenue change for each month.
15. **What would you need before applying the model in a real business?** Transactional sales and returns, landed costs, channel fees, promotion funding, and an estimate of incremental demand from a credible experiment or comparable evidence.
