# Portfolio materials

## Summary

An independent beauty retail strategy case combining source-aware SQLite analytics and simulated commercial planning. Catalog and review evidence flow through quality and price-eligibility filters. A simulated P&L links decisions on price, product mix, channel mix and promotion profitability to operating outcomes.

## LinkedIn Featured copy

I built a beauty retail decision-support platform using Python, SQLite, Excel and Streamlit. The project pairs conservative product-level price comparison and data-quality audit outputs with a formula-driven financial model and a simulator for promotion ROI, breakeven and scenario planning. The financial case uses transparent illustrative assumptions.

## Résumé draft

- Implemented and synthetic-tested a streaming Python and SQLite catalog/review pipeline with source checksums, schema validation, duplicate logging and conservative product matching.
- Built a 15-sheet Excel planning model for an illustrative beauty retailer, including scenario P&L, budget variance, channel contribution, promotion ROI, and a reconciled price–volume–mix bridge.
- Developed a Streamlit simulator with independently adjustable volume response, promotion breakeven and two-way contribution sensitivity, validated with an automated widget-interaction test.

## Verification

| Module | Evidence | Outstanding |
|---|---|---|
| Ingestion and quality | ZIP and CSV tests, schema rejection, required-value and duplicate outputs | Confirm archive shapes, date semantics and licensing |
| Commercial KPIs and pricing | Synthetic pipeline and SQL/CSV generation | Compare coverage and denominators with supplier records |
| Longitudinal and US/CA | Synthetic exact, ambiguous, no-FX, dated FX and CPI behavior | Verify accepted pairs, FX and CPI with official sources |
| Brand and consumer | Historical review aggregation and topic fixture | Manual sentiment validation and real recommendation evidence |
| Financial planning and Excel | Python unit tests, formula generation and LibreOffice/Python comparison | Windows Excel manual verification |
| Streamlit | AppTest baseline and zero-volume interaction | Interactive browser review is optional |
| Power BI | Import files, model guide, measures, theme and wireframes | Build and validate a native project in Desktop |
| Executive report | Structured template and separate simulated case | Produce paginated evidence-based report post-ingestion |
