"""Verify public deliverables, write the evidence manifest, and assemble the ZIP."""
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import fitz
from PIL import Image

from .evidence import DEMO, ROOT, checked_data, read
from .integrated import AUTHOR, FILENAME, LINKS, PAGES
from .render import EXCEL, LIVE, REPO, TECH

OUT = ROOT / "portfolio/v3"
COUNTS = {
    "Commercial_Business_Analytics_Flagship_V3.pdf":14,
    "Finance_FPA_Portfolio_V3.pdf":12,
    "Business_Analytics_BI_Portfolio_V3.pdf":12,
    "Commercial_Executive_Brief.pdf":1,
    "Finance_Executive_Brief.pdf":1,
    "BI_Executive_Brief.pdf":1,
    "Executive_Decision_Memo.pdf":2,
    FILENAME:len(PAGES),
}
ASSET_NAMES = {
    "commercial-overview":"portfolio.csv and recent US category counts",
    "financial-overview":"fact_simulated_finance.csv and annual Base totals",
    "scenario-comparison":"fact_simulated_finance.csv and modeled annual operating profit",
    "promotion-profitability":"fact_simulated_promotion.csv at 15 percent discount",
    "data-quality":"quality_completeness.csv and recent synthetic fields",
}
ZIP = "Recruiter_Portfolio_V3_FINAL.zip"
FILE_LIST = (
    *COUNTS,"README.md","Streamlit_Demo.mp4","Streamlit_Storyboard.md","Career_Positioning.md",
    "Employer_Competency_Matrix.csv","Employer_Source_Attempts.csv","Evidence_Coverage_Matrix.csv",
    "Portfolio_Validation_Report.md","Power_BI_Evidence.md",
)


def validation():
    evidence = checked_data()
    results = []
    with closing(sqlite3.connect(DEMO/"catalog/commercial.sqlite")) as conn:
        rows=conn.execute(
            "SELECT s.vintage, f.market, f.snapshot, COUNT(*) "
            "FROM fact_product_snapshot f JOIN source s ON f.source_id=s.id "
            "GROUP BY s.vintage,f.market,f.snapshot"
        ).fetchall()
    assert Counter(rows)==Counter(
        (r["vintage"],r["market"],r["snapshot"],int(r["source_records"])) for r in read("catalog","assortment_counts"))
    model=next((ROOT/"dashboard/powerbi").glob("*.SemanticModel"))/"definition/tables"
    dax=(model/"fact_simulated_finance.tmdl").read_text(encoding="utf-8-sig")
    assert "DIVIDE([Simulated gross profit], [Simulated net revenue])" in dax
    assert "DIVIDE([Simulated operating profit], [Simulated net revenue])" in dax
    assert "HASONEVALUE(product_position[market])" in (model/"product_position.tmdl").read_text(encoding="utf-8-sig")
    assert 0.603 < evidence["summary"]["Base"]["gross_profit"] / evidence["summary"]["Base"]["net_revenue"] < .604
    for name, pages in COUNTS.items():
        expected_links = {url for _, url in LINKS} if name == FILENAME else {LIVE, REPO, TECH, EXCEL}
        if name == FILENAME:
            assert (OUT/name).stat().st_size < 5_000_000
        annotations = 0
        with fitz.open(OUT/name) as pdf:
            assert len(pdf)==pages
            if name == FILENAME:
                assert pdf.metadata["author"] == AUTHOR
                cover = pdf[0].get_text()
                assert all(kpi in cover for kpi in ("USD 700,824", "USD 155,493", "60.3%", "22.2%"))
            for page in pdf:
                text=page.get_text().lower()
                assert "synthetic catalog" in text and "simulated financial" in text
                links = [item["uri"] for item in page.get_links() if "uri" in item]
                assert set(links) == expected_links
                expected_count = len(expected_links)
                if name == FILENAME:
                    if page.number == 0:
                        expected_count += 1
                    elif page.number == pages - 1:
                        expected_count *= 2
                assert len(links) == expected_count
                annotations += len(links)
                for block in page.get_text("blocks"):
                    x0,y0,x1,y1,*_=block
                    assert 0<=x0<x1<=page.rect.width and 0<=y0<y1<=page.rect.height
                page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            results.append({"artifact":name,"pages":pages,"link_annotations":annotations})
    for file in (OUT/"evidence").glob("*.png"):
        with Image.open(file) as image:
            assert image.size==(1540,990)
        assert re.fullmatch(r"0[1-6]-[a-z]+\.png",file.name)
    assert len(list((OUT/"evidence").glob("*.png")))==6
    for document in OUT.glob("*.md"):
        for target in re.findall(r"\]\(([^)\s]+)\)",document.read_text(encoding="utf-8")):
            link=urlsplit(target)
            if not link.scheme:
                assert (document.parent/link.path).exists() or link.path in {ZIP,"Evidence_Manifest.json"}, target
    return results


def add(zipped, archive_name, path):
    info = ZipInfo(archive_name,(2026,1,1,0,0,0))
    info.compress_type = ZIP_DEFLATED
    zipped.writestr(info,path.read_bytes())


def main():
    reports=validation()
    files=[(name,OUT/name) for name in FILE_LIST]
    files.extend((f"evidence/{p.name}",p) for p in sorted((OUT/"evidence").glob("*.png")))
    files.extend((f"evidence/charts/{name}.png",ROOT/"assets/portfolio"/f"{name}.png") for name in ASSET_NAMES)
    files.extend((f"generation/{p.name}",p) for p in sorted((ROOT/"scripts/portfolio_v3").glob("*.py")))
    manifest={
        "catalog_evidence":"Deterministic synthetic catalog and review records",
        "finance_evidence":"Simulated outputs from the tracked Python model, with tracked Excel formulas",
        "screenshot_evidence":"Six genuine local Chromium captures. No native Excel or Power BI screenshots.",
        "video_evidence":"Timed sequence of the six screenshots with captions; no continuous recording or audio",
        "employer_sources":"No individual vacancy verified; access attempts listed separately",
        "pdf_validation":reports,
        "charts":ASSET_NAMES,
        "technical_evidence":{"repository":REPO,"live_dashboard":LIVE,"power_bi":TECH,"excel":EXCEL},
        "files":[{"path":name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
                 for name,path in files],
    }
    path=OUT/"Evidence_Manifest.json"
    path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with ZipFile(OUT/ZIP,"w") as zipped:
        for name,source in [*files,("Evidence_Manifest.json",path)]:
            add(zipped,name,source)
    with ZipFile(OUT/ZIP) as zipped:
        assert zipped.testzip() is None and len(zipped.namelist())==len(files)+1
    print(f"Packaged {len(files)+1} verified artifacts ({sum(COUNTS.values())} PDF pages).")


if __name__=="__main__":
    main()
