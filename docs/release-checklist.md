# Release checklist

[Version 1.0.0](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/releases/tag/v1.0.0) is published. The [live Streamlit dashboard](https://luxury-beauty-commercial-intelligence.streamlit.app/) is the public demo. Use this checklist for future releases.

1. Pull the development branch and run `python -m pytest -q` on Windows. Generate public data with `python -m beauty.demo` and verify the synthetic banner in Streamlit. Review the dashboard preview images in the rendered README.
2. Regenerate the Excel model with `python -m beauty.workbook`, recalculate in Excel, and confirm all five checks for Base, Bull and Bear. The existing shipped workbook was recalculated in LibreOffice and reconciled with Python.
3. If a native Power BI file is part of your release, follow the [short Desktop workflow](../dashboard/powerbi/README.md) and verify slicers, currency, null values, and scenario totals. The kit can be published as documentation while Desktop work is pending.
4. Review `git status --short` and `git ls-files` before packaging. Include only source, public screenshots, documentation, and the simulated workbook. Keep archive ZIPs, private SQLite, derived outputs, local settings, and any private dashboard file out of release assets.
5. Open a GitHub release targeting the reviewed development commit, select a new version tag, and describe the synthetic and simulated scope. Verify links and assets from the rendered release page. Keep licensed data local unless redistribution is authorized.

Incomplete cross-market and longitudinal comparisons are documented limitations for this release. Authentic external benchmarks may be added independently after verification.
