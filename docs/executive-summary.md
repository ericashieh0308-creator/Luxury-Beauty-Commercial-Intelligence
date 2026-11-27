# Executive summary | Luxury & Beauty Commercial Intelligence

[Launch the live Streamlit dashboard](https://luxury-beauty-commercial-intelligence.streamlit.app/)

## The decision

A commercial team can use catalog evidence to decide which categories, brands, or price points deserve review. A finance team still needs to decide how much a proposed offer must sell to cover discounts, costs, and campaign spend. This independent case brings those workflows together while making the evidence behind each one explicit.

## Analytical approach

Python validates and normalizes local catalog inputs, records provenance and exceptions, and loads facts into SQLite. SQL and Python generate cohort-level assortment, price, discount, review, and quality tables. Power BI and Streamlit consume the analytical outputs. A separate financial simulation and formula-driven Excel workbook use illustrative assumptions for unit volume, prices, discounts, returns, unit costs, and expenses. See the [architecture diagram](../README.md#system-architecture).

## What a commercial team can do

- **Prioritize assortment review.** Compare representation by market, brand, and category using scoped product counts, eligible prices, and known merchandising flags.
- **Assess evidence before comparing prices.** Preserve USD and CAD cohorts. A pair needs defensible product comparability and valid point prices before it can support a price-gap calculation.
- **Use review signals to guide follow-up.** Topic counts and valid ratings can identify questions for qualitative review. They do not establish demand or customer behavior.

## What a finance team can do

Compare 12-month forecasts and weighted margins, reconcile Base-to-Bull budget variance through a price–volume–mix bridge, and test modeled SKU, channel, and offer contribution.

| Simulated result | Base case |
|---|---:|
| Annual net revenue | USD 700,824.23 |
| Annual operating profit | USD 155,492.93 |
| Gross margin | 60.3% |
| Operating margin | 22.2% |

At a 15% proposed discount and a 20% assumed unit uplift, the simulator reports **USD 6,110** more net revenue and **USD 455** less contribution. The modeled contribution hurdle is **1,219 whole units**. At those settings, the decision is to hold the offer pending evidence that the hurdle can be met, or test revised terms. Before a real spend decision, validate landed costs, channel fees, returns, and incremental demand using actual transaction or experiment data.

## Evidence and limitations

The public report uses synthetic catalog and review records and simulated financial results. No accepted comparison pairs produce usable price gaps, and the public project has no verified industry benchmarks, FX, or CPI inputs. Catalog records describe the source sample. The owner confirmed that the optimized report opened and refreshed in Windows Power BI Desktop, all ten pages displayed data, and the Base figures matched. Independent checks cover demo generation, financial reconciliation, and model deserialization.

**Skills shown:** commercial analytics, scenario planning and FP&A, SQL data modeling, Python ingestion and validation, Excel reconciliation, Power BI semantic modeling, and evidence-led communication. [See the visual portfolio](../assets/portfolio/README.md)
