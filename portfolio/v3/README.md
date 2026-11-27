# Portfolio V3 | Commercial, Finance, and BI

An employer-ready case for an NYU M.S. in Management & Analytics student. Choose the track that fits the role. The project is independent and unaffiliated with any employer. Public catalog data are synthetic and all finance inputs and results are simulated.

## Single attachment for applications

Use the [Integrated Work Sample](Commercial_Business_Analytics_Integrated_Work_Sample.pdf) for Commercial Analyst, Commercial Business Analyst, and Business Analyst applications. The 11-page PDF covers assortment, pricing, customer signals, financial planning, and the promotion decision in one document.

## Tier 1 · Recruiter briefs

- [Commercial & Business Analytics](Commercial_Executive_Brief.pdf)
- [Finance & FP&A](Finance_Executive_Brief.pdf)
- [Business Analytics & BI](BI_Executive_Brief.pdf)

## Tier 2 · Flagship case studies

- [Commercial & Business Analytics](Commercial_Business_Analytics_Flagship_V3.pdf) · 14 pages
- [Finance & FP&A](Finance_FPA_Portfolio_V3.pdf) · 12 pages
- [Business Analytics & BI](Business_Analytics_BI_Portfolio_V3.pdf) · 12 pages
- [Executive decision memos](Executive_Decision_Memo.pdf) · 2 pages
- [Streamlit demo video](Streamlit_Demo.mp4) · 72 seconds · [Storyboard](Streamlit_Storyboard.md)

## Tier 3 · Technical evidence and application materials

- [Portfolio validation](Portfolio_Validation_Report.md), [evidence coverage](Evidence_Coverage_Matrix.csv), [evidence manifest](Evidence_Manifest.json), and [native Power BI evidence extracts](Power_BI_Evidence.md)
- [Job competency mapping](Employer_Competency_Matrix.csv), [career-site access log](Employer_Source_Attempts.csv), and [résumé/LinkedIn copy](Career_Positioning.md)
- [Project README and architecture](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/blob/main/README.md), [Power BI project](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/blob/main/dashboard/powerbi/README.md), [Excel workbook](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/blob/main/models/excel/Luxury_Beauty_Commercial_Financial_Model.xlsx), [Python](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/tree/main/beauty), [SQL](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/tree/main/sql), [methodology](https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence/blob/main/docs/methodology.md), and [live Streamlit](https://luxury-beauty-commercial-intelligence.streamlit.app/)
- [Download the complete ZIP](Recruiter_Portfolio_V3_FINAL.zip)

## Reproduce V3

From the repository root, use Python 3.12 and install the project dependencies. The portfolio pipeline additionally uses ReportLab, PyMuPDF, Playwright and Pillow for PDF and browser evidence, plus FFmpeg with libx264 for video. Install Chromium through Playwright or pass the path to a local Chromium binary. Existing chart assets can be regenerated with the repository’s figure generator.

```text
python -m pip install -r requirements.txt
python -m pip install reportlab pymupdf playwright pillow
python -m playwright install chromium
python -m beauty.demo --output output/portfolio-v3-demo
python -m streamlit run app.py --server.address 127.0.0.1
```

In a second terminal from the repository root:

```text
python -m scripts.portfolio_v3.capture
python -m scripts.portfolio_v3.render
python -m scripts.portfolio_v3.integrated
python -m scripts.portfolio_v3.video
python -m scripts.portfolio_v3.inventory
python -m pytest -q
python -m scripts.portfolio_v3.package
```

The validation report records the evidence and checks performed on the delivered build. Its source-access and availability statements are dated evidence, so update them only after rechecking.
