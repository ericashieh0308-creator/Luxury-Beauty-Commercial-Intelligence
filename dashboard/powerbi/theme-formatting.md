# Ivory & Champagne theme and report formatting

Use **View > Themes > Browse for themes** in Power BI Desktop and select [theme.json](theme.json). The schema target is **Power BI Desktop 2.159.x (October 2026, exploration 5.78)**, the newest version in Microsoft's published schema index at validation time. Use a compatible Desktop version and preview a copy of the report before applying it to the working file. [Microsoft theme schema index](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema)

| Element | Theme default or report-level setting |
|---|---|
| Report masthead | Segoe UI, 26 pt, bold for the `largeTitle` text class. Set existing canvas text boxes to 26 pt bold in Desktop or PBIR. A report title in the Service, Desktop window or page tab uses the host interface. |
| Visual title and subtitle | Segoe UI, 16 pt bold and 13 pt regular, respectively, on supported visuals. Title text, visibility and dynamic expressions remain visual settings. |
| Current Card visual | `cardVisual.value` sets the callout to 36 pt bold. `cardVisual.label` sets the category to 14 pt. Reference label typography is 12 pt. The legacy Card has a separate visual type and can be formatted in Desktop. |
| Bars, columns, lines and donuts | Axis titles and labels where applicable, legends and supported data labels default to 12 pt. Label visibility, density and Fit behavior depend on the visual. |
| Tables, matrices and slicers | Headers and values use 12 pt, with bold table/matrix headers. Classic slicer headers are 13 pt bold and items are 12 pt. List, button, and text slicers have their own 12 pt label or input defaults. |
| Canvas and surfaces | Cream canvas, warm off-white surfaces, charcoal text, warm muted secondary text, subtle borders and restrained row dividers. The existing series palette and gold table accent are preserved. Use text labels or other visual cues when categories need to be distinguished. |

A theme sets defaults for supported formatting properties. Existing explicit formatting, field-level settings and conditional formatting can take precedence. Inspect one representative visual per type and reset only the individual formatting cards where appropriate. Resetting the whole visual's formatting can remove intentional overrides. Review small Card tiles, narrow charts and dense tables for wrapping, truncation and responsive behavior. Text-box rich-text runs, page-specific mastheads, individual column widths, and the exact text or geometry of existing visuals need targeted report edits. The theme intentionally leaves title/label visibility and value formatting to the report.

## Reproduce the schema check

Run from the repository root in PowerShell with `jsonschema` installed in the Python environment.

```powershell
$schema = Join-Path $env:TEMP 'reportThemeSchema-2.159.json'
$url = 'https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.159.json'
Invoke-WebRequest -Uri $url -OutFile $schema
python -c "import json,sys; from jsonschema import Draft7Validator; s=json.load(open(sys.argv[1],encoding='utf-8-sig')); t=json.load(open(sys.argv[2],encoding='utf-8-sig')); Draft7Validator(s).validate(t); print('Theme schema validation passed')" $schema 'dashboard/powerbi/theme.json'
```

## Format an existing report through PBIP/PBIR

The repository includes the enhanced PBIR project. For a separate PBIX, first save an enhanced-format working copy before inspecting its layout. PBIP is the project entry point. PBIR is the enhanced report definition with separate page and visual files. An existing Desktop report can generally be converted in place as a **copy** by saving it as a Power BI Project, then enabling or upgrading to the enhanced PBIR format if Desktop prompts. This preserves the existing report project and gives external tools access to the report definition. [Microsoft Power BI projects](https://learn.microsoft.com/power-bi/developer/projects/projects-overview) · [Microsoft PBIR report format](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

1. Open a local copy of the existing PBIX in a current Desktop build and **Save As > Power BI Project (`.pbip`)**. Confirm the report has a `<name>.Report/definition/pages/` tree. If the project only has a legacy report definition, use Desktop to upgrade the working copy to enhanced PBIR before editing.
2. Import the theme in Desktop. If title or typography overrides remain, adjust **one representative visual per type** and save. Compare its exported JSON before and after. Use that diff to identify the actual property path and literal representation for the project’s schema version.
3. Close Desktop. In `definition/pages/<page-id>/visuals/<visual-id>/visual.json`, use the top-level `position` object for `x`, `y`, `width`, and `height`. Align visuals by giving the selected files a common `x` or `y`. Space them from existing page coordinates and preserve layering, tab order, hierarchy and grouped coordinate systems. Inventory page sizes and visual positions before batching edits.
4. Apply only equivalent typography overrides to visuals of the same type, preserving conditional expressions, selectors, data bindings, query state, filters, interactions, bookmarks, and model references. Style title text boxes individually or use a deliberate selection of equivalent rich-text runs. Save through a JSON parser and review the diff. Follow each file’s declared `$schema` for validation.
5. Reopen the `.pbip` in Desktop. Check page bounds, alignment, responsive sizes, title wrapping, slicers, navigation and bookmarks on the modified pages. Save a PBIX copy if needed for delivery. Keep private PBIP data and report definitions local unless authorized for sharing.

For a small report, applying the theme and using Desktop’s Format ribbon to align and distribute multi-selected visuals may be faster. PBIR is most useful for repeating the same placement or typography changes across many visuals. The repository’s PBIR definitions were edited directly and checked for bounds and overlap. Desktop import and rendering remain pending.
