# Final Power BI portfolio audit

**Release state:** Ready for Desktop verification. Confirm refresh and rendering before publishing the native report as a finished portfolio artifact.

The audit covered all 10 existing pages, 67 original visuals, 27 starting tables, and 29 starting measures. The final project contains **10 pages, 76 visuals, 28 tables, and 32 measures**. All original page and visual IDs remain. The three hidden date-support tables remain defined. The subsequent stability release restored the baseline date variations and time-intelligence setting. The optimized report keeps ISO format on its direct snapshot dates. See the [release candidates](release-candidates.md).

## Page QA

Every page passed static binding, unique-ID, tab-order, canvas boundary and overlap checks. The last column records the remaining Desktop verification.

| Page | Decision, original issue and change | Analytical and binding check | Desktop sign-off and evidence limit |
|---|---|---|---|
| Executive Overview · 9 | Decide which commercial evidence merits follow-up. Clarified scope and retained the four aligned coverage cards. Added a management note. | Original record-count measures and the recent brand chart are retained. Records measure coverage. | Confirm cards, legend and sample totals. Coverage cannot establish sales or market share. |
| Market & Assortment Intelligence · 8 | Choose a market and snapshot for assortment review. Replaced short market and vintage lists with dropdowns and added ISO snapshot display. | Existing market relationship drives the assortment fact. Additive records are separate from scoped product and SKU counts. | Open both menus and check all values, both dates, totals and sorting. Sample differences cannot establish growth. |
| Brand & Category Performance · 7 | Prioritize sampled segments. Sorted ranks and clarified known merchandising denominators and the cohort picker. | Cohort selection uses the existing relationship. Counts are representative assortment. | Confirm descending ranks, table widths and selection behavior. |
| Pricing & Promotional Intelligence · 8 | Choose categories for follow-up. Added currency to cohort choices, valid-sale context and a missing-flag explanation. | Median requires one market, vintage and snapshot. Discount depth uses weighted valid observations. The existing pipeline excludes ineligible sales. | Switch US to CA and verify pricing remains in its native currency. Check tooltips and missing flags. |
| Customer Reviews & Product Intelligence · 6 | Identify themes for qualitative follow-up. Improved rating precision, review and missing-text labels, and sentiment context. | Per-product means use valid ratings. Review counts and lexicon signals are historical. | Verify headers and readability. No overall unweighted rating, brand-level sentiment or sales inference was added. |
| Cross-Market & Historical Comparison · 7 | Decide whether to quantify a gap or verify more matches. Added English names, a dropdown and usable-gap tooltip. | Shared comparison dimension filters coverage and queues. Availability is driven by usable gaps. | Check both comparison types and **Not available**. Demo has no comparable gaps or verified FX, CPI or benchmarks. |
| Financial Performance & P&L · 7 | Trace simulated sales to operating profit. Added gross sales and operating expenses and standardized USD and percentage formats. | New measures reuse the scenario guard. Operating expenses are variable expenses plus fixed expenses. Both margins use summed profit and revenue. | Confirm Base defaults, Bull/Bear switches, monthly order, table fit and totals. |
| Budget Variance & Scenario Forecasting · 8 | Compare forecast trajectories and identify modeled variance drivers. Added English P&L item labels and explicit PVM currency. | Scenario selection filters the forecast. Variance and PVM use fixed Base versus Bull. YTD, sign and bridge arithmetic were checked. | Switch scenarios and confirm the fixed comparison remains unchanged. |
| SKU, Channel & Promotion Profitability · 9 | Evaluate contribution and campaign hurdles. Added required uplift and weighted channel contribution margin. | SKU follows scenario. Channel and promotion calculations use their standalone inputs. ROI and break-even thresholds match Python. | Verify SKU and campaign filters, channel tooltip and blank threshold behavior. |
| Data Quality & Methodology · 7 | Prioritize quality remediation. Connected issues and completeness to one snapshot-period selector. | Shared one-to-many relationships drive both facts. Parse validity is valid values divided by evaluated values. | Verify both charts and detail respond. Quality counts describe field exceptions. |

## Issue accounting

The audit tracked **14 issue groups**. **12 have programmatic remedies**: ten page-specific groups, shared locale and formatting, and source preflight. **Two remain unresolved**: the actual Desktop warning and refresh/render behavior, and full official PBIR schema validation. The first needs Desktop. The second was blocked by HTTP 403 from Microsoft's PBIR schema host. Static geometry establishes boundaries and overlap. Text clipping, slicer menus, cross-highlight and actual filter propagation require Desktop.

## Refresh triage

1. Generate the demo and run the [project validator](../../scripts/validate_powerbi.py). Every required physical import must have rows and compatible headers and types. The price comparison CSV may intentionally contain headers only. The benchmark registry has no demo observations and is outside the shipped model.
2. Set **DemoRoot** to the generated folder containing both **catalog** and **finance** if the parameter is blank or stale. Apply pending query changes and refresh once.
3. If **Some of the tables have incomplete or no data** remains, open refresh error details and identify the affected table. The price-comparison table can be empty by design. For other tables, inspect the listed Power Query error and DemoRoot. The cloud preflight passed, but the Windows warning has not been reproduced.

## Evidence and publication

- The synthetic public demo passed local PBIP/PBIR and TMDL structural checks. Both theme files passed the official report theme schema. Use the [technical guide](validation.md) to run the full official PBIR check from an accessible network.
- All 36 forecast rows, 72 SKU rows, both channel rows, 60 budget variance rows, 12 monthly PVM bridges and 35 promotion cases reconcile to Python. Weighted gross and operating margins were verified. The workbook check covers all three annual revenue and operating-profit totals, default campaign ROI and the five saved-Base checks.
- The native report labels catalog data as synthetic and planning results as simulated. Private inputs, processed data, local paths, PBIX, ABF and cache files stay out of the release. The report has no brand affiliation or endorsement.
- Complete the ten-page Desktop sign-off before publication. The [setup guide](README.md) covers the single parameter and the one-command repeat workflow.
