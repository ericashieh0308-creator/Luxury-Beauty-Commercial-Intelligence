# GitHub publication handoff

Publication materials are prepared on `build/commercial-intelligence-platform`. GitHub’s default branch is `main`. The updated landing page becomes the repository’s default view after an approved merge or a deliberate default-branch change.

## Repository presentation

**Description:** Independent beauty retail analytics and FP&A portfolio with Python, SQLite, Excel, Power BI, and Streamlit.

**Topics:** `commercial-analytics`, `fp-and-a`, `financial-modeling`, `power-bi`, `dax`, `python`, `sqlite`, `streamlit`, `retail-analytics`, `pricing-analytics`, `data-governance`

Pin the repository on your GitHub profile after publication. Link the README first, then the executive summary, visual portfolio, or workbook as appropriate for the role. Use the simulated promotion case as a short decision walkthrough. See the [career materials](career-portfolio.md) for LinkedIn copy.

## Pull request draft

**Title:** Publish Luxury & Beauty Commercial Intelligence portfolio v1.0

**Base:** `main` · **Compare:** `build/commercial-intelligence-platform`

**Description**

- Presents an independent beauty retail analytics and FP&A case with Python, SQLite, Excel, Streamlit, and a ten-page native Power BI report.
- Includes an optimized report and a separately packaged fallback, with synthetic demo generation and local launch instructions.
- Adds recruiter-facing documentation, actual Streamlit screenshots, and charts generated from public demo exports.
- Reconciles simulated financial outputs and documents unavailable comparisons. The owner confirmed the optimized Power BI report opened and refreshed on Windows and displayed the expected Base results.
- Keeps licensed inputs, private outputs, local configuration, caches, and the locally saved PBIX outside publication.

## Release draft

**Tag:** `v1.0.0`

**Title:** Luxury & Beauty Commercial Intelligence Platform v1.0

**Release notes**

- Reproducible commercial analytics covering assortment, pricing, reviews, and quality.
- Simulated planning with Base, Bull, and Bear, budget variance, weighted margins, channel and SKU economics, and Promotion ROI and break-even.
- Ten-page optimized Power BI model with an independent fallback, a 15-sheet Excel model, and an interactive Streamlit demo.
- Synthetic public catalog inputs and simulated financial values. The demo does not support cross-market or historical gaps or verified benchmark conclusions.

## Publish after approval

1. On GitHub, verify repository visibility and review the [development branch against main](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/compare/main...build/commercial-intelligence-platform). Confirm the README, links, and figures render and the changed files contain no private data or PBIX.
2. Create the pull request using the draft above. Review the changed files, then merge only after explicit approval.
3. From **Releases → Draft a new release**, create `v1.0.0` targeting the approved commit, paste the release notes, verify its source and optional assets, then publish only after explicit approval. The repository already contains the simulated workbook and public preview assets.
4. Verify the landing page and release from an unauthenticated browser if the intended audience is public. Pin the repository and add the approved link to LinkedIn Featured.

Native Power BI screenshots are optional. The [screenshot checklist](../assets/portfolio/README.md#optional-power-bi-desktop-screenshots) covers capture and privacy. The current previews include genuine Streamlit screenshots and generated figures.

## Publication validation record

- The owner confirmed the optimized Power BI project opened and refreshed in Windows Desktop, all ten pages displayed data, and Base results matched. The local PBIX remains private.
- Independent checks covered the repository test suite, both candidate preparation workflows, the Streamlit startup, and the simulated financial outputs. Two fresh synthetic demo builds produced equivalent CSV rows and SQLite contents. SQLite file bytes and quality report row order can differ across runs.
- Official PBIR JSON schema validation remains subject to access to Microsoft's schema host. The public figures and Streamlit previews are sufficient for a repository walkthrough.
