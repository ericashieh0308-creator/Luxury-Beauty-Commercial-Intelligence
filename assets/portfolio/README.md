# Visual portfolio

These Ivory & Champagne figures were generated from the public synthetic catalog and simulated finance CSVs. The [Mermaid architecture diagram](../../README.md#system-architecture) shows the actual workflow.

| Asset | Evidence |
|---|---|
| [Commercial overview](commercial-overview.png) | Representative products by category in the synthetic recent US cohort |
| [Financial overview](financial-overview.png) | Annual simulated Base P&L totals |
| [Scenario comparison](scenario-comparison.png) | Annual simulated operating profit across Bear, Base, and Bull |
| [Promotion profitability](promotion-profitability.png) | Simulated contribution at a 15% discount across exported volume-response cases |
| [Data quality](data-quality.png) | Present and parse-valid rates for selected recent synthetic fields |
| [Streamlit commercial screenshot](../streamlit-commercial-demo.png) · [Streamlit finance screenshot](../streamlit-finance-demo.png) | Captured from the running synthetic Streamlit demo |

To regenerate the charts from the repository root:

```powershell
python -m pip install matplotlib
python -m beauty.demo
python -m scripts.build_portfolio_figures
```

## Optional Power BI Desktop screenshots

The owner confirmed the optimized project opens and refreshes in Windows. The Desktop screenshots and locally saved PBIX are outside this repository. For a native preview, capture **Executive Overview**, **Financial Performance & P&L** with Base selected, and optionally **SKU, Channel & Promotion Profitability**. Keep the synthetic and simulated labels in frame. Crop machine paths, usernames, workspace names, and the Windows taskbar. Review every image before committing it.
