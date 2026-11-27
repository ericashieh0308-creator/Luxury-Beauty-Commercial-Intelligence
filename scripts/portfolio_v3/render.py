"""Build the three role-specific case studies, executive briefs, and memo."""
from html import escape
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from .evidence import ROOT, checked_data
from .narratives import BI, BRIEFS, COMMERCIAL, FINANCE, MEMO

OUT = ROOT / "portfolio/v3"
CREAM, PAPER, INK, BROWN, GOLD, RULE = map(HexColor, ("#FBF8F1","#FFFDF8","#231F1D","#634F43","#937449","#DDD0BE"))
REPO = "https://github.com/ericashieh0308-creator/Luxury-Beauty-Commercial-Intelligence"
LIVE = "https://luxury-beauty-commercial-intelligence.streamlit.app/"
TECH = REPO + "/tree/main/dashboard/powerbi"
EXCEL = REPO + "/blob/main/models/excel/Luxury_Beauty_Commercial_Financial_Model.xlsx"
WIDTH = 512
SCENARIOS = ("Case","Revenue","Gross profit","Operating profit","GM","OM")
ALT = ("Modeled option","Δ revenue","Δ contribution","ROI")
TABLES = {
    "cohorts": (("Vintage","Market","Snapshot","Records","Products","Product–SKU"),"assortment_counts.csv · synthetic"),
    "category": (("US category","Representatives"),"portfolio.csv · recent US synthetic cohort"),
    "brand": (("US brand","Representatives"),"portfolio.csv · recent US synthetic cohort"),
    "prices": (("Market","Currency","Category","Eligible","Median list"),"product_position.csv · recent synthetic cohort"),
    "discounts": (("Category","Priced","Valid sale","Mean depth"),"discount_summary.csv · recent US synthetic cohort"),
    "comparison": (("Comparison","Candidate pairs","Accepted","Usable gaps"),"comparison_coverage.csv · synthetic match evidence"),
    "reviews": (("Theme","Mentions"),"review_topic.csv · historical synthetic reviews"),
    "quality": (("Source field","Evaluated","Present","Parse-valid"),"quality_completeness.csv · recent synthetic input"),
    "scenarios": (SCENARIOS,"fact_simulated_finance.csv · annual USD, rounded to whole dollars"),
    "monthly": (("Month","Net revenue","Gross profit","Operating profit"),"fact_simulated_finance.csv · Base monthly USD"),
    "pnl": (("P&L line","Base annual USD"),"fact_simulated_finance.csv · simulated"),
    "variance": (("P&L item","Full-year variance"),"fact_simulated_variance.csv · Bull less Base, USD"),
    "bridge": (("Bridge component","Full-year net revenue change"),"fact_simulated_pvm.csv · Bull less Base, USD"),
    "sku": (("Modeled SKU","Net revenue","Gross profit","Contribution"),"fact_simulated_sku.csv · Base annual USD"),
    "channels": (("Channel","Net revenue","Contribution","Contribution margin"),"fact_simulated_channel.csv · standalone monthly USD"),
    "alternatives": (ALT,"Python promotion model · USD changes vs baseline, after campaign cost"),
    "sensitivity": (("Cost change","Unit cost","Baseline contribution","Offer Δ contribution","Break-even units"),"Python promotion model · 15% discount, 20% uplift, USD"),
    "formulas": (("Evidence","Worksheet and cell","Actual workbook value or formula"),"Extracted workbook cells · reconstructed table"),
}

SAMPLES = {
 "A SQLite check ties facts to published counts": "SELECT s.vintage, f.market, f.snapshot, COUNT(*) AS records<br/>FROM fact_product_snapshot f JOIN source s ON f.source_id = s.id<br/>GROUP BY s.vintage, f.market, f.snapshot;",
 "DAX measures keep forecast scenarios separate": "Weighted gross margin = DIVIDE([Simulated gross profit], [Simulated net revenue])",
 "Catalog relationships preserve market scope": "product_position.cohort_key -&gt; dim_cohort.cohort_key<br/>fact_simulated_finance.scenario -&gt; dim_scenario.scenario",
}


READOUTS = {
    "The market samples are different sizes": ("The recent US cohort has 36 records versus 27 in Canada. The historical US cohort also has 36. "
        "The historical extract has no explicit SKU keys, so the period comparison cannot establish SKU expansion."),
    "Read the price ladder in native currency": ("In the recent US cohort, fragrance has a USD 119.50 median versus USD 60.00 for skincare. "
        "Read this as category price architecture. The Canadian rows use CAD and cannot establish a converted premium."),
    "Discount depth depends on eligible sale records": ("Each US category has three valid sale observations. The priced denominators differ, so equal valid-sale counts do not imply equal discount coverage."),
    "The match queue has no usable price gaps": ("The synthetic queue contains 102 US–Canada and 132 longitudinal candidates, with zero accepted pairs. A candidate can appear more than once before manual review."),
    "Review themes point to the next question": ("The 72 texture and 36 packaging mentions come from 144 synthetic historical review records. Mention totals may overlap because a review can contribute to more than one topic."),
    "SKU contribution changes the range decision": ("Core contributes about USD 215 thousand of USD 347 thousand total Base contribution. The higher total reflects modeled volume as well as unit economics."),
    "Channel economics depend on fulfillment and fees": ("Store contribution is about 53.6% of channel net revenue versus 46.5% for e-commerce. The modeled split and cost assumptions differ by channel."),
    "A changed assumption changes the recommendation": ("At a 15% discount and 20% uplift, a 10% landed cost increase takes the modeled contribution loss from USD 455 to USD 888. At +20% cost, the break-even rises to 1,264 units."),
    "Build the P&L from operating drivers": ("Base retains 60.3% of revenue at gross profit and 22.2% at operating profit. The gap captures the modeled selling and fixed cost structure."),
    "Track variance with the right sign convention": ("Bull is approximately USD 70 thousand above Base in net revenue and USD 49 thousand above in operating profit. Variable expenses also rise about USD 6 thousand."),
    "Price and volume bridge simulated revenue": ("Volume contributes roughly USD 54 thousand of the USD 70 thousand bridge. The price effect accounts for roughly USD 16 thousand; the residual rounds to zero."),
    "SKU mix affects the profit pool": ("The two Base SKU contributions sum to the P&L contribution line. SKU profitability should be assessed against underlying costs and the volume used to generate it."),
    "Channel contribution depends on variable costs": ("The modeled Store route contributes about USD 18.1 thousand monthly; the E-commerce route contributes about USD 10.4 thousand. The routes start with different allocated order volumes."),
    "Landed cost sensitivity raises the hurdle": ("At higher modeled cost, both baseline contribution and the proposed offer’s economics deteriorate. The last row requires 1,264 whole units versus 1,219 at baseline cost."),
    "Ingestion records what changed and what failed": ("The recent synthetic input has 63 evaluated ratings and all are present. Parse validity is 96.8%, documenting why presence alone overstates usable rating coverage."),
    "A KPI needs an eligible denominator": ("The synthetic US fragrance cohort has 12 priced representatives and three valid sale observations. Mean depth describes those three values."),
    "Unsupported joins should end in a review queue": ("The match table counts candidate pairs. Accepted matches and usable gaps are separately tested states. They are both zero in this demo."),
    "A review visualization needs an interpretation boundary": ("Texture accounts for 72 mentions and packaging for 36. Those are mention counts, and a single review can mention multiple themes."),
    "A governed handoff makes the report reusable": ("Check the quality board before the executive pages. The 28.6% sale-price presence rate means missingness must remain visible in promotional views."),
}


def paragraph(text, size, leading, color=INK, font="Helvetica"):
    style = ParagraphStyle("block",fontName=font,fontSize=size,leading=leading,textColor=color,alignment=TA_LEFT)
    return Paragraph(text,style)


def put(canvas,text,y,size=11,leading=15,color=INK,font="Helvetica"):
    item=paragraph(text,size,leading,color,font)
    _,height=item.wrap(WIDTH,700)
    item.drawOn(canvas,50,y-height)
    return y-height


def draw_table(canvas, name, rows, y):
    headers,source=TABLES[name]
    prepared=[[paragraph(escape(str(cell)),9.2,12,white,"Helvetica-Bold") for cell in headers]]
    prepared.extend([paragraph(escape(str(cell)),9.5,13) for cell in row] for row in rows)
    sizes=[WIDTH/len(headers)]*len(headers)
    if name=="formulas":
        sizes=[112,126,274]
    elif name=="alternatives":
        sizes=[200,105,112,95]
    t=Table(prepared,colWidths=sizes)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),BROWN),
                           ("ROWBACKGROUNDS",(0,1),(-1,-1),[PAPER,CREAM]),
                           ("LINEBELOW",(0,0),(-1,-1),.4,RULE),
                           ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                           ("VALIGN",(0,0),(-1,-1),"TOP")]))
    _,h=t.wrap(WIDTH,700)
    t.drawOn(canvas,50,y-h)
    return put(canvas,escape(source),y-h-7,8.6,11,BROWN)-12


def draw_image(canvas,name,y):
    local=OUT/"evidence"/f"{name}.png"
    screenshot=local.is_file()
    if not screenshot:
        local=ROOT/"assets/portfolio"/f"{name}.png"
    reader=ImageReader(str(local))
    w,h=reader.getSize()
    width=min(WIDTH,(190 if y < 445 else 210)*w/h) if screenshot else WIDTH
    height=width*h/w
    canvas.drawImage(reader,50,y-height,width,height,mask="auto")
    caption = "Genuine Chromium capture of the local Streamlit public demo." if screenshot else "Generated chart from public demo exports. Synthetic or simulated as labeled."
    return put(canvas,caption,y-height-7,8.6,11,BROWN)-14


def render_pdf(filename, track, pages, data):
    path=OUT/filename
    draw=Canvas(str(path),pagesize=(612,792),invariant=1)
    draw.setTitle(track)
    draw.setAuthor("Luxury & Beauty Commercial Intelligence Portfolio")
    for index,page in enumerate(pages,1):
        draw.setFillColor(CREAM)
        draw.rect(0,0,612,792,fill=1,stroke=0)
        draw.setStrokeColor(GOLD)
        draw.setLineWidth(.9)
        draw.line(50,736,562,736)
        y=put(draw,"PORTFOLIO V3  /  "+escape(track.upper()),756,9,12,BROWN,"Helvetica-Bold")
        y=put(draw,escape(page.title),y-22,26,29,INK,"Helvetica-Bold")
        y=put(draw,escape(page.takeaway),y-12,12,17)-16
        if page.title=="Review themes point to the next question":
            y=put(draw,f"{data['review_count']} historical synthetic review records.",y,10,14,BROWN)-8
        if page.evidence:
            y=draw_table(draw,page.evidence,data[page.evidence],y)
        if page.title in SAMPLES:
            y=put(draw,SAMPLES[page.title],y,9.4,13,BROWN,"Courier")-13
        if page.visual:
            y=draw_image(draw,page.visual,y)
        if page.title in READOUTS:
            y=put(draw,"<b>Evidence readout</b>",y,10,14,BROWN)-3
            y=put(draw,escape(READOUTS[page.title]),y,11,15)-13
        y=put(draw,"<b>Decision and follow-through</b>",y,10,14,BROWN)-3
        y=put(draw,escape(page.action),y,11,15)
        if filename in BRIEFS:
            skills = {
                "Commercial_Executive_Brief.pdf": "Assortment analysis, pricing, promotion economics and decision framing",
                "Finance_Executive_Brief.pdf": "Driver-based forecasting, weighted margins, variance and Excel reconciliation",
                "BI_Executive_Brief.pdf": "SQL data modeling, DAX scope, Power BI reporting and data governance",
            }
            y=put(draw,"<b>Competencies:</b> "+skills[filename],y-14,9.5,13,BROWN)
        if y<91:
            raise ValueError(f"{filename} page {index}: layout bottom {y:.1f}")
        draw.setStrokeColor(RULE)
        draw.line(50,76,562,76)
        draw.setFillColor(BROWN)
        draw.setFont("Helvetica",8.3)
        draw.drawString(50,61,"Synthetic catalog and reviews  ·  Simulated financial inputs and results")
        draw.drawRightString(562,61,f"{index:02} / {len(pages):02}")
        links=[("Live dashboard",LIVE),("Source repository",REPO),("Power BI project",TECH),("Excel workbook",EXCEL)]
        x=50
        for label,url in links:
            draw.drawString(x,45,label)
            w=draw.stringWidth(label,"Helvetica",8.3)
            draw.linkURL(url,(x,42,x+w,54),relative=0)
            x+=w+18
        draw.showPage()
    draw.save()
    print(f"{filename}: {len(pages)} pages")


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=checked_data()
    for name,track,pages in [
        ("Commercial_Business_Analytics_Flagship_V3.pdf","Commercial & Business Analytics",COMMERCIAL),
        ("Finance_FPA_Portfolio_V3.pdf","Finance & FP&A",FINANCE),
        ("Business_Analytics_BI_Portfolio_V3.pdf","Business Analytics & BI",BI),
        ("Executive_Decision_Memo.pdf","Executive Decision Memo",MEMO),
    ]:
        render_pdf(name,track,pages,data)
    for name,page in BRIEFS.items():
        render_pdf(name,"Recruiter Executive Brief",[page],data)


if __name__=="__main__":
    main()
