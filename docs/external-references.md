# External reference data

Copy [the registry template](../data/external/benchmark_template.csv) to `data/external/benchmarks.local.csv`. The local copy and retrieval artifacts are ignored by Git. The cloud proxy denied access to the Bank of Canada API, BLS API, SEC, and Circana during the audit. The template begins empty.

## Reproduce FX and CPI collection in PowerShell

```powershell
New-Item -ItemType Directory -Force 'output/references' | Out-Null
$fxUrl = 'https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date=2026-11-09&end_date=2026-11-13'
Invoke-RestMethod -Uri $fxUrl |
    ConvertTo-Json -Depth 20 | Set-Content 'output/references/boc-fx.json' -Encoding UTF8
$blsUrl = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
$body = @{ seriesid = @('CUUR0000SA0'); startyear = '2023'; endyear = '2026' } | ConvertTo-Json
Invoke-RestMethod -Uri $blsUrl -Method Post -ContentType 'application/json' -Body $body |
    ConvertTo-Json -Depth 20 | Set-Content 'output/references/bls-cpi.json' -Encoding UTF8
if (-not (Test-Path 'data/external/benchmarks.local.csv')) {
    Copy-Item 'data/external/benchmark_template.csv' 'data/external/benchmarks.local.csv'
}
```

- **FX.** In the Bank of Canada response, verify the series metadata and the observation date. The `FXUSDCAD` quote is CAD per USD. Take its reciprocal once, without intermediate rounding, for `fx_usd_per_cad`. Use geography `Canada`, units `USD per CAD`, and measurement period `YYYY-MM-DD`. Document the conversion and the daily reference rate convention. The pipeline uses the snapshot day or the latest supplied prior observation within four calendar days. Review holidays and data gaps.
- **CPI.** Check the API status before using observations. Use BLS series `CUUR0000SA0`, US city average, all items, not seasonally adjusted. Use only monthly periods M01–M12. Add the verified month of each comparable snapshot as `YYYY-MM` with metric `cpi_us`, geography `US`, and units `index (1982-84=100)`. Use the official release calendars and confirm series metadata. If either required month is absent or unpublished, keep the real-price change blank. [BLS CPI releases](https://www.bls.gov/bls/news-release/cpi.htm)
- **Industry context.** For each metric use its actual publication and measurement period, use the full metric definition as the metric label, and record comparable geography and units. Describe channel coverage, sample limits, or reporting basis in limitations. Record the specific public publication URL and verify redistribution terms before publishing an extract. [SEC EDGAR](https://www.sec.gov/edgar/search/) · [Circana](https://www.circana.com/)

Use the actual publication date and your actual access date. The import checks required fields, HTTPS URL structure, dates, finite values, duplicate typed periods, and the two analytical metrics' period format, geography and units. It cannot authenticate a manually entered citation or detect a rate incorrectly inverted by the researcher. Existing config-based rate and CPI maps can still run as local overrides. A conflicting value in the registry is rejected. Prefer the registry for provenance.

Pass the reviewed CSV to `--benchmark data/external/benchmarks.local.csv` when building. Inspect `fact_industry_benchmark.csv` for provenance and `comparison_coverage.csv` for price-pair availability. A reference series cannot make an unaccepted pair comparable.

For a local industry benchmark, open the Circana public press releases or the issuer’s investor relations publications, download the dated source to the ignored `output/references/` folder, and transcribe the matching metric definition, actual publication date, period, units, and source URL into the reviewed local registry. Verify whether the source measures retail value, volume, prestige or mass, and whether the geography and period match the claim. The cloud proxy also denied access to the issuer publication sites during the Version 1.0 review.
