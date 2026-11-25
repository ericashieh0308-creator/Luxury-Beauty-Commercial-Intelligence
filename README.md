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

Place the archives inside the ignored `data/raw` folder. The pipeline reads ZIP members directly and also accepts extracted directories. Inspect recent CSV member names and headers first, compare them with the mapping in `config/sources.json`, and record confirmed collection dates, currencies, and price definitions in a local copy. Follow the source terms before processing or publishing derived exports.

```powershell
Copy-Item config/sources.json config/sources.local.json
.\.venv\Scripts\python.exe -m beauty.pipeline --inspect 'data/raw/sephora-sample-2026-11.zip'
.\.venv\Scripts\python.exe -m beauty.pipeline --historical 'data/raw/archive (1).zip' --recent 'data/raw/sephora-sample-2026-11.zip' --config config/sources.local.json --benchmark data/external/benchmark_template.csv
```

Without verified dates or reference rates, the affected comparison fields stay blank. The recent mapping is a template. Check market values are US or CA and currency values are USD or CAD. Import `data/processed` and `output/finance` following the [Power BI Desktop guide](dashboard/powerbi/README.md).

## Methodology and portfolio

- [Architecture, data model, governance and KPI dictionary](docs/methodology.md)
- [Financial model formula guide](docs/finance.md)
- [SQL query library](sql/analysis.sql)
- [Executive strategy report template](reports/executive-strategy-template.md)
- [Learning and interview guide](docs/interviews.md)
- [Portfolio copy and verification checklist](docs/portfolio.md)

The checkout contains synthetic test fixtures and simulated retailer planning assumptions. Real-source acquisition, licensing, date and schema checks, benchmark verification, and Power BI Desktop publication belong to the observed-data validation workflow. Sephora, LVMH, and Cartpie have no affiliation with this case study.
