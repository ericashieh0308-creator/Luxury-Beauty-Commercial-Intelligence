# Luxury & Beauty Commercial Intelligence Platform

**Advanced Commercial Decision Intelligence** is an independent portfolio case study on US premium beauty retail, using Sephora catalog snapshots as the intended observational evidence. It pairs commercial pricing and merchandising analytics with an illustrative retailer P&L and decision simulator.

| Decision | Deliverable |
|---|---|
| Where does an assortment sit on the price ladder? | SQLite pipeline, category quartiles, brand portfolio and price-position exports |
| How did comparable list prices differ? | Reciprocal match audit, longitudinal price bridge, and US/Canada comparison with dated FX |
| Is an incremental promotion worth funding? | Formula-driven Excel workbook and interactive USD contribution simulator |
| How should results be presented? | Power BI implementation kit and executive report framework |

## Windows and PyCharm

Open the repository folder in PyCharm. Use PowerShell in the project root and select `.venv\Scripts\python.exe` as the project interpreter.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m beauty.workbook
.\.venv\Scripts\python.exe -m beauty.finance_export
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the [15-sheet Excel workbook](models/excel/Luxury_Beauty_Commercial_Financial_Model.xlsx), choose Base, Bull, or Bear, and recalculate with **F9** in Excel. Read the [illustrative financial case](reports/illustrative-financial-case.md) for a worked planning decision.

## Run with licensed source files

Place the licensed archives in the ignored `data/raw/` folder. The pipeline reads ZIP members directly and also accepts extracted directories. The default configuration selects `sephora_sample_2026-11-13.csv` and maps its reported columns. The diagnostic prints aggregate counts and ranges for local review.

```powershell
$python = '.\.venv\Scripts\python.exe'
$recent = 'data/raw/sephora-sample-2026-11.zip'
& $python -m beauty.pipeline --diagnose $recent
& $python -m beauty.pipeline --historical 'data/raw/archive (1).zip' --recent $recent --benchmark 'data/external/benchmark_template.csv'
```

If you already have `config/sources.local.json`, refresh its recent schema from the tracked configuration and keep your verified historical, FX, and CPI settings:

```powershell
$defaults = Get-Content 'config/sources.json' -Raw | ConvertFrom-Json
$localPath = 'config/sources.local.json'
if (Test-Path $localPath) {
    $local = Get-Content $localPath -Raw | ConvertFrom-Json
    $local | Add-Member -NotePropertyName recent -NotePropertyValue $defaults.recent -Force
    $local | ConvertTo-Json -Depth 20 | Set-Content $localPath -Encoding UTF8
} else {
    Copy-Item 'config/sources.json' $localPath
}
& $python -m beauty.pipeline --diagnose $recent --config $localPath
& $python -m beauty.pipeline --historical 'data/raw/archive (1).zip' --recent $recent --config $localPath --benchmark 'data/external/benchmark_template.csv'
```

The recent snapshot date comes from the date in each ISO collection timestamp, retaining its supplied offset when present. Missing or invalid recent timestamps leave the snapshot date blank. Size, subcategory, observed promotion, and stockout are unavailable in the reported schema. Verify price definitions, actual value distributions, and dates locally before interpreting the results. Keep raw data, diagnostics saved under `output/`, and `data/processed/` local. Import exports following the [Power BI Desktop guide](dashboard/powerbi/README.md).

## Methodology and portfolio

- [Architecture, data model, governance and KPI dictionary](docs/methodology.md)
- [Financial model formula guide](docs/finance.md)
- [SQL query library](sql/analysis.sql)
- [Executive strategy report template](reports/executive-strategy-template.md)
- [Learning and interview guide](docs/interviews.md)
- [Portfolio copy and verification checklist](docs/portfolio.md)

The checkout contains synthetic test fixtures and simulated retailer planning assumptions. Real-source acquisition, licensing, date and schema checks, benchmark verification, and Power BI Desktop publication belong to the observed-data validation workflow. Sephora, LVMH, and Cartpie have no affiliation with this case study.
