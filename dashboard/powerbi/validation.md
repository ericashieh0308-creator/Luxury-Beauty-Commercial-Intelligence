# Power BI project validation

The project extends Desktop-authored commit `1322bf5`. It retains the Executive Overview page and its nine visual IDs, updates the layout, and adds nine pages using the existing PBIR structure and theme registration.

| Page | Visuals |
|---|---:|
| Executive Overview | 9 |
| Market & Assortment Intelligence | 8 |
| Brand & Category Performance | 7 |
| Pricing & Promotional Intelligence | 8 |
| Customer Reviews & Product Intelligence | 6 |
| Cross-Market & Historical Comparison | 7 |
| Financial Performance & P&L | 7 |
| Budget Variance & Scenario Forecasting | 8 |
| SKU, Channel & Promotion Profitability | 9 |
| Data Quality & Methodology | 7 |
| **Total** | **76** |

## Checks performed

- Generated the public synthetic demo and parsed the PBIP and PBIR JSON. Checked ten unique page IDs, 76 unique visual IDs, keyboard order uniqueness, 16:9 canvas bounds, rectangle overlap, and visual field/measure bindings.
- Checked 28 TMDL tables including 32 measures, table references, relationship endpoints, unique lineage metadata, DAX field references, demo CSV availability and header/type compatibility, and placeholder-free source paths. This is structural validation. TOM compilation and DAX engine execution require a compatible Microsoft runtime.
- Reconciled all 36 simulated scenario-month rows against Python. Verified weighted gross margin, PVM residuals and promotion ROI. Recalculated the existing workbook in LibreOffice, matched annual revenue and operating profit for Base, Bull and Bear, and checked the five workbook reconciliation results for the saved Base selection.
- Validated the standalone theme and registered report theme against Microsoft's published theme schema. The proxy returned HTTP 403 for the official PBIR schemas at `developer.microsoft.com`, so the official PBIR JSON schema check remains pending.
- Ran the full repository suite on Linux with **25 tests passed**. Verified Git exclusions and inspected the staged deliverables for private data, machine-specific paths and binary report caches.

## Repeat the validation

```powershell
$python = '.\.venv\Scripts\python.exe'
& $python -m beauty.demo
& $python -m scripts.validate_powerbi
& $python -m pytest -q

# Optional official schema pass, from a network that can fetch Microsoft schema URLs
& $python -m pip install jsonschema
& $python -m scripts.validate_powerbi --schemas
```

## Desktop sign-off

Use the [opening and refresh instructions](README.md). Confirm Desktop opens the PBIP, refreshes after setting DemoRoot, and accepts all report and model definitions. Check the custom visual title typography, Card callouts, long headers, picker labels, charts, table sizing and tab navigation. Exercise one catalog cohort at a time, switch Base to Bull to Bear, and validate the comparison availability card. Check that outputs with missing matches, FX, CPI or verified benchmarks remain unavailable. Desktop rendering, actual clipping, and interactive filter propagation were not exercised here.

See the [final QA report](final-qa-report.md) for page decisions, original issues, and Desktop verification notes.

## TMDL parsing repair

The model audit found the same duplicate on line 10 of the hidden date template and both generated local date tables. Each Date object already had an explicit ISO format, followed by a legacy General Date property. The repair removes only the second property in each file. User-facing snapshot dates remain date-typed and keep yyyy-MM-dd.

Microsoft Analysis Services TOM 19.120.1 deserialized the repaired model on Linux with .NET 8. It reported 28 tables, 32 measures, and 25 relationships. The same parser rejected the original commit d1f2ca1 with DuplicatedProperty on formatString. The Python suite additionally checks duplicate properties by indentation scope across all TMDL files, along with PBIR bindings and registered theme resources. These checks are separate from Power BI Desktop opening, refresh, rendering, and DAX evaluation.

To repeat the official deserialization with a .NET 8 SDK, run this PowerShell command from the repository root:

```powershell
dotnet run --project scripts/tmdl-parser -- 'dashboard/powerbi/Luxury_Beauty_Commercial_Intelligence.SemanticModel/definition'
```
