"""Build the role alignment and evidence coverage inventories."""
import csv
from pathlib import Path
import re

from .evidence import ROOT, checked_data

OUT=ROOT/"portfolio/v3"
COMPETENCIES=[
 ("Commercial performance reporting","Power BI: Executive Overview","Commercial flagship pp. 1–2","Cohort counts describe the sample."),
 ("Sales and profitability analysis","Excel: Monthly P&L; Power BI: Financial Performance","Finance case pp. 2–3","Sales are simulated."),
 ("Budgeting and forecasting","Excel: Revenue Forecast; Streamlit: Financial performance","Finance case pp. 3–5","Base/Bull/Bear are modeled."),
 ("Variance analysis","Excel: Budget vs Actual; Power BI: Budget Variance","Finance case pp. 5–6","Bull is simulated actual."),
 ("Pricing and promotion analysis","SQLite pricing and discount exports; Streamlit simulator","Commercial case pp. 5–7, 11–12","No elasticity estimate."),
 ("Product and assortment performance","assortment_counts.csv and portfolio.csv","Commercial case pp. 2–4","Coverage differs from sell-through."),
 ("Brand and category analysis","Power BI Brand & Category Performance","Commercial case pp. 3–4","Fictional brands in public release."),
 ("Merchandising economics","Excel Product Economics; simulated SKU CSV","Commercial case p. 9","Actual unit economics unavailable."),
 ("Channel profitability","Excel Channel Profitability; simulated channel CSV","Finance case p. 8","Illustrative channel costs."),
 ("Customer insights","review_summary.csv and review_topic.csv","BI case p. 9","Lexicon signals only."),
 ("KPI development","TMDL cohort and margin guards; methodology","BI case pp. 4, 7–8","Licensed benchmark comparisons unavailable."),
 ("Excel financial modeling","15-sheet workbook and reconciliation cells","Finance case p. 11","Worksheet preview reconstructed."),
 ("Power BI reporting","10-page native PBIR with TMDL and theme","BI case pp. 7–8, 11","Desktop images unavailable."),
 ("SQL and data management","SQLite cohort count and quality assertions","BI case pp. 2–3","Public build uses synthetic data."),
 ("Cross-functional communication","Two executive decision memos","Executive Decision Memo pp. 1–2","Illustrative decision roles."),
 ("Executive recommendations","Commercial campaign funding and verification gates","Commercial case pp. 11–14","No realized business impact."),
]
SOURCES=[
 ("Sephora","https://jobs.sephora.com/"),
 ("L’Oréal","https://careers.loreal.com/"),
 ("LVMH","https://www.lvmh.com/en/join-us/our-job-offers"),
 ("Sephora","https://careers.smartrecruiters.com/Sephora"),
]
POWERBI=[
 ("Executive Overview","Commercial p. 1; Chromium 01","Reconstructed evidence"),
 ("Market & Assortment Intelligence","Commercial pp. 2–3; SQLite cohort count","Derived analytics"),
 ("Brand & Category Performance","Commercial pp. 3–4; Chromium 02","Reconstructed evidence"),
 ("Pricing & Promotional Intelligence","Commercial pp. 5–6","Derived analytics"),
 ("Customer Reviews & Product Intelligence","Commercial p. 8; BI p. 9","Derived analytics"),
 ("Cross-Market & Historical Comparison","Commercial p. 7; BI p. 6","Unavailable gaps disclosed"),
 ("Financial Performance & P&L","Finance pp. 2–4; Chromium 03","Reconstructed evidence"),
 ("Budget Variance & Scenario Forecasting","Finance pp. 4–6","Modeled outputs verified"),
 ("SKU, Channel & Promotion Profitability","Finance pp. 7–10","Modeled outputs verified"),
 ("Data Quality & Methodology","BI p. 5; quality chart","Derived analytics"),
]
STREAMLIT=[
 ("Executive overview","Chromium 01","Browser capture"),
 ("Commercial intelligence","Chromium 02","Browser capture"),
 ("Pricing analytics","Commercial pp. 5–6; existing AppTest","Outputs and existing test"),
 ("Customer intelligence","BI p. 9; existing AppTest","Outputs and existing test"),
 ("Financial performance","Chromium 03 and 04","Base and Bull captured"),
 ("Promotion & scenario simulator","Chromium 05 and 06; 72-second walkthrough","Offer and uplift change verified"),
 ("Data quality & limitations","BI p. 5; existing AppTest","Outputs and existing test"),
 ("Portfolio sensitivity and inventory views","Live application and repository","Linked, scenario CSV download and inventory controls not captured for V3"),
]
EXCEL=[
 ("ReadMe","Finance pp. 11–12; tracked workbook"),("Control Panel","Finance p. 11"),
 ("Assumptions","Finance pp. 2, 9–11"),("Industry Benchmarks","Empty verified-input structure; no observations"),
 ("Product Economics","Finance p. 7"),("Monthly P&L","Finance pp. 2–3, 11"),
 ("Budget vs Actual","Finance p. 5"),("Revenue Forecast","Finance pp. 3–4"),
 ("Channel Profitability","Finance p. 8; scenario-specific workbook differs from standalone Python channel example"),
 ("Promotion ROI","Finance pp. 9–11"),("Price–Volume–Mix","Finance p. 6"),
 ("Scenario Analysis","Finance p. 4"),("Sensitivity Analysis","Finance p. 10; Python cost sensitivity is a separate illustration"),
 ("Executive Summary","Finance executive brief; tracked worksheet"),("Model Checks","Finance p. 11; calculator required for live checks"),
]


def write(name, headings, rows):
    with (OUT/name).open("w",newline="",encoding="utf-8-sig") as file:
        writer=csv.writer(file)
        writer.writerow(headings)
        writer.writerows(rows)


def main():
    checked_data()
    write("Employer_Competency_Matrix.csv",["competency","project_evidence","portfolio_location","boundary","basis"],
          [(*row,"Project evidence mapped to requested role families; individual posting not verified") for row in COMPETENCIES])
    write("Employer_Source_Attempts.csv",["employer","role","source_url","access_date_America_New_York","status"],
          [(company,"No role verified",url,"2026-11-26","Cloud proxy HTTP 403; not used as job evidence") for company,url in SOURCES])
    write("Evidence_Coverage_Matrix.csv",["artifact","capability","evidence","status"],
          [("Power BI",*r) for r in POWERBI]+[("Streamlit",*r) for r in STREAMLIT]+
          [("Excel",name,evidence,"Workbook/source coverage; no native screenshot") for name,evidence in EXCEL]+
          [("Technical","Python + SQLite","Validation report and BI case pp. 2–3","Executed"),
           ("Technical","Official TOM","Native TMDL and TOM result","Deserialization only")])

    model=next((ROOT/"dashboard/powerbi").glob("*.SemanticModel"))/"definition"
    measures=[]
    for path in (model/"tables").glob("*.tmdl"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if any(line.lstrip().startswith(f"measure '{name}'") for name in (
                    "Native median list price","Weighted gross margin","Weighted operating margin","Valid discount depth")):
                measures.append(line.strip())
    relationships=(model/"relationships.tmdl").read_text(encoding="utf-8-sig")
    relevant=[block for block in relationships.split("\n\n") if (
        "fromColumn: product_position.cohort_key" in block or "fromColumn: fact_simulated_finance.scenario" in block)]
    sample=next((ROOT/"dashboard/powerbi").glob("*.Report"))/"definition/pages"
    definitions=[]
    for file in sample.glob("*/page.json"):
        import json
        page=json.loads(file.read_text())
        definitions.append(f"- {page['displayName']}: {page['width']} × {page['height']}")
    text = "# Native Power BI evidence extracts\n\nThese excerpts come from the optimized PBIP/PBIR/TMDL project. No Desktop screenshot is represented here."
    text += "\n\n## Representative native measures\n\n```text\n"+"\n".join(sorted(measures))+"\n```"
    text += "\n\n## Relationship definitions\n\n```text\n"+"\n\n".join(relevant)+"\n```"
    text += "\n\n## Report pages and canvases\n\n"+"\n".join(sorted(definitions))+"\n"
    (OUT/"Power_BI_Evidence.md").write_text(text,encoding="utf-8")


if __name__=="__main__":
    main()
