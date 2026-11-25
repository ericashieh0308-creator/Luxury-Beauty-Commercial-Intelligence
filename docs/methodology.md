# Evidence, data model and KPI definitions

```mermaid
flowchart LR
    A[Licensed local ZIP or CSV] --> B[Header inspection and source mapping]
    B --> C[Streaming normalization and validation]
    C --> D[SQLite facts and source lineage]
    D --> E[Pricing, comparability and quality tables]
    E --> F[Restricted Power BI inputs]
    G[Simulated financial drivers] --> H[Python finance]
    H --> I[Streamlit and finance CSVs]
    G --> J[Linked Excel model]
```

## Source registry

| Source | Intended evidence | Status |
|---|---|---|
| [Kaggle historical catalog and reviews](https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews) | US product list prices, flags and historical reviews | Archive, dates and applicable license require verification |
| [Cartpie sample](https://cartpie.com/datasets/sephora/sample) | Recent US and CA list prices and available SKU/attribute fields | Archive schema, collection dates, sampling and redistribution terms require verification |
| [Federal Reserve H.10](https://www.federalreserve.gov/releases/h10/) | Dated USD per CAD after converting quoted convention if needed | Candidate source. Record rate, date, quotation convention and link before use |
| [BLS CPI](https://www.bls.gov/cpi/) | Monthly US CPI index with consistent series and base | Candidate source. Verify series and data vintages |
| Circana, SEC filings, LVMH and L'Oréal releases | Industry context | The benchmark registry template starts empty. The cloud proxy denied access to Circana, BLS and SEC during setup. Enter verified observations with measurement definitions.|

The [benchmark template](../data/external/benchmark_template.csv) validates exact headers, completeness, dates, finite numbers and HTTPS source links. Validation of metric meaning and provenance remains manual. In a local config use `fx_usd_per_cad` as an ISO-date-to-rate map and `cpi_us` as a YYYY-MM-to-index map. Keep verified FX/CPI citations with the benchmark registry. FX selection uses the nearest supplied observation within four calendar days, breaking ties toward the earlier date. Supply official business-day observations only.

## ERD and data dictionary

```mermaid
erDiagram
    SOURCE ||--o{ FACT_PRODUCT_SNAPSHOT : ingests
    SOURCE ||--o{ FACT_REVIEW : ingests
    SOURCE ||--o{ QUALITY : logs
    FACT_PRODUCT_SNAPSHOT ||--o| PRICING : describes
    FACT_PRODUCT_SNAPSHOT ||--o{ BRIDGE_PRODUCT_MATCH : left
    FACT_PRODUCT_SNAPSHOT ||--o{ BRIDGE_PRODUCT_MATCH : right
    DIM_BRAND ||--o{ FACT_PRODUCT_SNAPSHOT : groups
    DIM_CATEGORY ||--o{ FACT_PRODUCT_SNAPSHOT : groups
    DIM_MARKET ||--o{ FACT_PRODUCT_SNAPSHOT : groups
    DIM_DATE ||--o{ FACT_PRODUCT_SNAPSHOT : dates
```

| Entity | Grain and fields |
|---|---|
| source | One file member. Vintage, member path, SHA-256 and header JSON |
| fact_product_snapshot | One input record with lineage `source_id,line`. Local market, currency, snapshot, native product/SKU, category, size, variant, list/sale price, rating, engagement and nullable binary flags |
| fact_sku_snapshot | Product snapshot view restricted to records with SKU IDs |
| dim_brand/category/market/date | Normalized brand/category, two market/currency codes, or distinct nonempty snapshot date |
| dim_product | Distinct market/product/brand/name attributes. Use source and date when resolving changing labels |
| fact_review | One historical review record. Product, date, rating, sentiment; excludes text and reviewer ID |
| review_summary / review_topic | Product review aggregates and counts per product/topic |
| pricing / product_position | Eligible representative product price tier, category gap, discount depth, positioning score, rating and engagement |
| price_comparison | One eligible accepted pair. Native and USD list prices, gaps, FX date, stress bounds, CPI change, tier and promotion fields |
| bridge_product_match | Candidate pairs by endpoint IDs and comparison; method and status |
| commercial_kpi / portfolio | Cohort aggregates, including explicit flag denominators and product selection rules |
| category_diagnostics / sku_portfolio | Category-level price relationship and concentration metrics, and distinct SKU counts and price ranges |
| quality_report / duplicate_keys | Field exceptions by file and cross-file product/SKU duplicate keys |
| fact_industry_benchmark | Contextual statistic with organization, dated period, geography, metric, value, units, URL, retrieval date and limitations |
| finance_assumptions / fact_simulated_finance | Separate finance CSVs with simulation labels; driver or scenario-month grain |

## Quality and interpretation

Read `quality_report.csv` and `duplicate_keys.csv` before using any KPI. Text normalization is Unicode NFKC, case-folding and space collapse for brand, category, size and variant. It intentionally preserves size units. Missing values remain null, invalid values are logged and nulled, unidentified rows are excluded and counted, suspicious nonnegative prices are retained and flagged. Duplicate rows remain in the snapshot fact. Source row ordinal uses CSV record order. Prices outside expected currencies are excluded from comparable pricing. Full review text stays in raw archives. The pipeline streams review rows in 5,000-record writes.

| KPI | Definition and interpretation |
|---|---|
| Products | One explicit parent per source vintage–market–date–product where unique. A single SKU can serve as a product representative. Ambiguous and variants-only multisets stay in SKU analysis |
| Brands and SKUs | Distinct known brand within the cohort. SKU volume counts distinct product/SKU identities, never units sold |
| Assortment share | Segment products divided by selected cohort products. It describes catalog composition |
| Mean/median and range | Positive list prices among expected-currency representative products |
| Price tier | Inclusive category quartiles computed within market, vintage and snapshot. Ties remain in the lower band. At least four eligible products are required |
| Concentration | Brand Herfindahl index among eligible priced products with known brands |
| Rating and engagement | Mean known rating and sum of known catalog engagement counts, with coverage. Engagement is a historical platform signal |
| Flag shares | True records divided by known true or false values for that flag. Snapshot availability reflects a point-in-time observation |
| Discount depth | One minus sale divided by list, where list is positive and sale is no higher than list |
| Premium proxy | Midrank percentile of category list price × 0.8 plus exclusive flag × 0.2, on a 0–100 scale. Sensitivity weights are 0.95 / 0.05. Unknown exclusivity leaves the score blank |
| Price relationships | Pearson association with rating and engagement, with complete-pair count. Constant or fewer than three pairs yield a blank |

The lexicon baseline counts positive minus negative term presence. Zero represents neutral or unscored language. Topic counts support qualitative triage. Before reporting sentiment rates, have a second reviewer independently label a permitted local sample. Record criterion, agreement, precision/recall, negation errors and neutral-class coverage. Historical review findings only describe the historical review pool.

## Product comparison

Candidates are blocked by normalized brand. Auto-acceptance requires reciprocal uniqueness within the paired snapshot, exact normalized brand/name/size/variant and known dates. Comparable identifiers can identify exact SKU or exact product-plus-variant matches. Enable `comparable_ids` only after confirming identifier semantics. Missing SKU variants and fuzzy name matches go to manual review. Review packaging, reformulation, units and list-price semantics before interpreting accepted pairs. Cross-market comparisons require the same snapshot day and correct local currency. Report accepted and eligible pair counts, source denominators, directional gaps and coverage by category. Missing sample items have unknown disposition. Sample selection, survival and matched-product coverage limit generalization.

Nominal difference is right USD list minus left USD list. Relative gap divides that difference by left list. Longitudinal CPI change is right/left price ratio multiplied by old/new CPI minus one. Tier migration can be evaluated at fixed left-snapshot thresholds. US/Canada FX stress applies ±5% to the supplied USD-per-CAD rate. Taxes, import costs, fulfillment and regional positioning are possible explanatory hypotheses requiring evidence.
