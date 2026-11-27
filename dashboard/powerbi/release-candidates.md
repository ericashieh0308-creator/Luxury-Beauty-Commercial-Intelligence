# Stability-first Power BI release candidates

Use the optimized candidate first. If Power BI Desktop reports a GUI opening or refresh error, close that candidate and launch the fallback. The launcher prepares and validates a local copy before starting Desktop. Desktop GUI errors require the user to choose the fallback.

| Candidate | Contents | Desktop evidence |
|---|---|---|
| A · Optimized | 10 pages, 76 visuals, 28 tables, 32 measures. Preserves the latest English labels, ISO snapshot formatting, dropdowns, decision notes, Ivory & Champagne, and model measures. Restores the baseline date variations, generated date tables, and time-intelligence setting. | Current build passed official TOM deserialization, variation checks, and local project validation. Windows Desktop opening and refresh remain pending. |
| B · Fallback | 10 pages, 67 visuals, 27 tables, 29 measures. Independent, byte-for-byte copy of the native PBIP, PBIR, and TMDL at cf7fbab. It retains the baseline theme, layouts, analytic logic, and date formatting. Later dropdown and locale polish is outside this snapshot. | The project owner identified cf7fbab as the last version that opened in Desktop. The isolated copy passed official TOM and local project checks. Refresh in the new local session still needs verification. |

The preceding version retained hidden tables marked ShowAsVariationsOnly after removing the column variations that referenced them. TOM could deserialize that arrangement, but Power BI Desktop rejected it. The optimized version restores both original variation relationships and hierarchy targets as a unit. The generated hidden date tables use the original metadata and their Date columns have exactly one format property. Direct snapshot columns still use yyyy-MM-dd. The fallback has its own relative report-to-model link and separate resource files.

## Windows workflow

Once the development branch is up to date, launch from the repository root with the existing Python environment.

```powershell
& .\scripts\open-powerbi.ps1 -Candidate optimized -Update
```

If necessary, open an independent fallback session without changing the branch or updating files:

```powershell
& .\scripts\open-powerbi.ps1 -Candidate fallback
```

The Update switch requires a clean worktree and uses a fast-forward-only pull. Each launch creates a fresh ignored directory under output/powerbi-sessions, generates synthetic data and simulated finance, validates the chosen source project, sets DemoRoot in the local copy, prints the path, and opens that copy. Saving in Desktop affects the opened copy only. Reopen the same session PBIP directly to keep working on a saved session. No PBIX, licensed data, credentials or populated machine paths are tracked.

For an initial update from a checkout that predates the two-candidate launcher, pull the development branch first and stop if Git reports an error.

## Validation and acceptance

Both source candidates passed Microsoft Analysis Services TOM 19.120.1 deserialization and checks against its loaded variation, relationship and hierarchy objects. The local checks also covered duplicate properties, report bindings, bounds, overlap, CSV import schemas and simulated finance. The official Microsoft theme schema passed. The cloud proxy denied the official PBIR schema host and there was no Analysis Services engine or Windows Desktop runtime for model loading and refresh. See [technical validation](validation.md).

In Desktop:

1. Open the launched project and refresh once. DemoRoot should already be set.
2. Confirm all ten page tabs open, core slicers respond, and tables and charts are legible.
3. In financial performance, confirm Base annual net revenue **USD 700,824.23** and operating profit **USD 155,492.93**. Switch to Bull and Bear and confirm the figures change.
4. Confirm unavailable comparisons stay unavailable and the catalog and finance evidence labels remain visible. Use the fallback if the optimized build fails opening or refresh. Publish only the candidate that passes these checks with synthetic data.
