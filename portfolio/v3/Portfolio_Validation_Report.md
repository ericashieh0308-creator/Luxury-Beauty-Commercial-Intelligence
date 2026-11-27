# Portfolio V3 validation report

## Financial and commercial evidence

The SQLite cohort query grouped retained snapshot facts by vintage, market and date. It matched the exported cohort totals. Public scope comprises 36 recent US records, 27 recent Canadian records, and 36 historical US records. The recent US category representatives are 15 skincare, 12 fragrance, and 9 makeup. Review and pricing outputs use the cohort and eligibility rules in the source project.

The existing finance validator reconciles 36 forecast rows, 72 SKU rows, two channel rows, 60 budget variance rows, 12 monthly PVM bridges and 35 campaign combinations against Python computations. Base annual net revenue is USD 700,824.23 and operating profit is USD 155,492.93. The annual scenario totals matched the recalculated workbook. Gross and operating margins were recalculated as ratios of totals. The Base-versus-Bull budget and PVM view is simulated. The standalone monthly channel illustration and workbook scenario channel view use different scopes.

Native DAX margins were inspected for the ratio-of-totals expression, and the native price measure was checked for a single-market guard. The portfolio independently tested those arithmetic patterns against demo rows. No native DAX engine query was run. Microsoft TOM deserialized the optimized model, including 28 tables, 32 measures, 25 relationships and two date variation targets. Windows Desktop rendering and refresh were previously owner-reported and were not rerun for V3. There are no native Power BI or Excel screenshots in the package.

## Publication gate

- All 38 repository tests passed on Linux. The product application and analytics were kept intact.
- Seven PDFs contain 43 pages, with 172 clickable annotations to the live app, GitHub, Power BI project and workbook. Page count, text boundaries, evidence labels, and rendering were checked for every page. A visual audit used raster previews and larger inspection of selected dense pages.
- Six genuine local Chromium captures show the public demo, Base and Bull, the 15% offer, and the recalculation after changing uplift from 20% to 30%. The 72-second MP4 is a captioned sequence of those captures.
- Coverage includes all ten Power BI pages, seven primary Streamlit views, and all 15 workbook sheets by evidence or reference. Some capabilities have output or source evidence only. The inventory and sensitivity views are linked. Native Excel and Power BI previews, deployment telemetry, and full native DAX execution remain unavailable in this run.
- Corporate careers sites returned proxy HTTP 403. The employer source log identifies the endpoints and access date. The competency matrix maps requested role families to genuine project evidence. No current vacancy or employer-specific requirement was verified or asserted.
- Match candidates are visible, and the public output has no eligible cross-market or historical price gaps. FX, CPI, and benchmark observations are unavailable for those comparisons.
- The bundle contains public synthetic or simulated evidence. Licensed datasets, private processed files, databases, caches, credentials, PBIX files, and local paths are excluded.

## Rerun

Use the [V3 reproduction steps](README.md#reproduce-v3). The package generator rechecks the PDFs, SQLite cohort count, finance outputs, DAX expressions, and local documentation links, then writes checksums and tests ZIP integrity.
