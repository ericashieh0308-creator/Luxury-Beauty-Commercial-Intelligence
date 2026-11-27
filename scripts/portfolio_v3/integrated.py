"""Render the standalone commercial work sample from checked public demo evidence."""
from html import escape

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .evidence import checked_data
from .polish import architecture, bars, enrich, heatmap, label, pricing, waterfall
from .render import BROWN, CREAM, EXCEL, GOLD, INK, LIVE, OUT, PAPER, REPO, RULE, TABLES, WIDTH, draw_table, put

FILENAME = "Commercial_Business_Analytics_Integrated_Work_Sample.pdf"
EVIDENCE = REPO + "/tree/portfolio/v3-employer-ready/portfolio/v3"
AUTHOR = "Ya-Cheng (Erica) Hsieh"
LINKEDIN = "https://www.linkedin.com/in/ya-cheng-hsieh-0192a5341"
LINKS = (
    ("Live Streamlit app", LIVE),
    ("GitHub repository", REPO),
    ("Excel workbook", EXCEL),
    ("Power BI KPI definitions", EVIDENCE.replace("/tree/", "/blob/") + "/Power_BI_Evidence.md"),
    ("LinkedIn", LINKEDIN),
    ("Validation evidence", EVIDENCE.replace("/tree/", "/blob/") + "/Portfolio_Validation_Report.md"),
)

TABLES.update({
    "matrix": (("US brand", "Skincare", "Fragrance", "Makeup", "Total"), "portfolio.csv · recent US synthetic representatives"),
    "brand_price": (("US brand", "Skincare", "Fragrance", "Makeup"), "Median list price in USD · recent US product_position.csv · sample sizes above."),
    "sale_status": (("Recent sale-price evidence", "Records"), "SQLite · recent US and Canada synthetic facts"),
    "pnl_cents": (("P&L line", "Base annual USD"), "Annual sources summed at full precision; displayed items rounded independently to cents."),
    "pvm_cents": (("Effect", "Revenue variance · USD"), "Volume-first PVM · components may differ from the total by USD 0.01 when rounded."),
    "assumptions": (("Case", "Unit growth", "Cost inflation", "Discount shift", "Final discount"), "Python forecast drivers · final discount starts from 8%."),
    "sku_economics": (("SKU", "Net revenue", "Contribution", "Contrib. margin", "Contrib. share", "Contrib. / unit"), "Annual Base · USD · per modeled ordered unit, before returns."),
    "roadmap": (("Function", "Proposed action", "Timing", "KPI", "Decision threshold", "Data required"), "Illustrative implementation roadmap · proposed actions and gates."),
})

# Blocks are rendered in reading order. Evidence tables use the checked demo exports.
PAGES = (
    ("Executive decision brief", "Commercial & Business Analytics",
     "", (("cover",),)),
    ("Assortment and brand positioning", "Start with the range before proposing a reset",
     "Skincare accounts for 15 of 36 recent US representatives. Fragrance accounts for 12 and Makeup for nine.",
     (("assortment",),
      ("table", "matrix"), ("table", "brand_price"),
      ("call", "Commercial readout", "The three fictional brands each have 12 US representatives. The category shares describe assortment coverage only. Sales, sell-through and market share require transaction and market data. Demo House has the highest median list price in all three categories. Check whether demand and gross margin support that premium before adding depth."))),
    ("Pricing and discount discipline", "Protect category price architecture",
     "The US fragrance median is USD 119.50 versus USD 60.00 for skincare and USD 48.00 for makeup.",
     (("pricing",),
      ("call", "Trade-off", "Makeup has the deepest mean observed US sale discount at 19.8%, based on three eligible observations. A blanket discount could sacrifice margin across items with different price roles."),
      ("call", "Decision", "Use category-specific guardrails and keep CAD and USD separate. Request accepted product matches and dated FX before making a cross-market premium claim."))),
    ("Customer signals and evidence limits", "Turn review themes into research questions",
     "Texture appears in 72 mentions and packaging in 36 across 144 synthetic historical reviews. Each review can contribute to multiple themes.",
     (("table", "comparison"), ("table", "sale_status"),
      ("call", "Next action", "Test clearer texture descriptions on product pages. Gather dated conversion and return data before treating review mentions as drivers of sales or satisfaction."),
      ("call", "Reporting decision", "Both comparison queues have zero accepted pairs. A blank sale price leaves offer status unknown. Eighteen records show a lower price and zero show an explicit equal-to-list price. Keep matched gaps unavailable. Recent ratings are 100% present and 96.8% parse-valid."))),
    ("Financial performance", "Use the P&L as the planning baseline",
     "The simulated Base plan produces USD 700,824.23 in annual net revenue and USD 155,492.93 in operating profit.",
     (("waterfall", "Base P&L waterfall · USD thousands", "waterfall", 760000),
      ("table", "pnl_cents"),
      ("call", "Implication", "Base retains 60.3% at gross profit and 22.2% at operating profit. Use weighted margins from summed dollars. Display rounding can cause a one-cent difference between a subtotal and the sum of displayed components."))),
    ("Scenario planning", "Use Bear to size the downside",
     "Operating profit ranges from USD 68,604 in Bear to USD 204,022 in Bull. Base earns USD 155,493.",
     (("scenarios",), ("table", "scenarios"), ("table", "assumptions"),
      ("call", "Planning decision", "Use Base for planning and Bear for commitments. Check units, landed costs and discount exposure before increasing fixed spend."))),
    ("Budget variance", "Volume drives the modeled revenue upside",
     "Bull adds USD 70,316.81 in annual net revenue versus Base, the planning budget. Both cases are simulated.",
     (("waterfall", "Base-to-Bull revenue bridge · USD thousands", "revenue_bridge", 830000),
      ("table", "pvm_cents"),
      ("call", "Operating implication", "Bull adds about USD 48,529 of operating profit while variable expenses rise about USD 6,222 and fixed expenses stay flat. The volume-first bridge holds Base net price for the volume and mix effects, then applies the unit-price change to Bull units."))),
    ("SKU and channel profitability", "Test contribution before allocating more volume",
     "The Core SKU contributes about USD 215K of USD 347K in annual Base contribution. Total dollars reflect both volume and unit economics.",
     (("table", "sku_economics"), ("table", "channels"), ("channels",),
      ("call", "Channel trade-off", "The standalone monthly illustration yields a 53.6% Store contribution margin and 46.5% in E-commerce. Allocated volume and cost assumptions differ by channel; test incremental economics before moving inventory or media."),
      ("call", "Decision", "Protect Core availability first. Contribution per unit above is an average. Estimate incremental costs, returns and contribution separately before adding volume. The channel illustration uses a separate monthly basis and should be reviewed independently of the annual SKU totals."))),
    ("Promotion ROI", "Require incremental contribution to clear the gate",
     "At 15% off and 20% assumed uplift, simulated sales rise USD 6,110 while contribution falls USD 455 after campaign cost.",
     (("promotion",),
      ("image", "05-offer", "Genuine local Streamlit crop | Proposed 15% offer at 20% assumed uplift."),
      ("table", "alternatives"),
      ("call", "Decision", "Pilot the 10% offer if the targeted customer group supports the assumed uplift. Measure incremental contribution against an untreated holdout and monitor returns before expanding."))),
    ("Sensitivity and approval threshold", "Recheck the gate when costs or response move",
     "At 15% off, raising assumed uplift to 30% lifts modeled incremental contribution to USD 2,067. That uplift is an assumption.",
     (("heatmap",),
      ("table", "sensitivity"),
      ("call", "Downside test", "At the original 20% uplift, increasing landed cost by 10% deepens the loss to USD 888. The break-even threshold rises from 1,219 to 1,239 total units. Re-estimate the threshold with current landed cost before approval."))),
    ("How the results were validated", "Trace the decision from SQL to the scorecard",
     "Python generates the demo outputs and promotion sensitivities. SQLite preserves the source vintage, market and snapshot for each catalog cohort.",
     (("architecture",),
      ("code", "SQL | Cohort grain", "SELECT s.vintage, f.market, f.snapshot, COUNT(*) AS records\nFROM fact_product_snapshot f JOIN source s ON f.source_id = s.id\nGROUP BY s.vintage, f.market, f.snapshot;"),
      ("table", "cohorts"),
      ("code", "Power BI | TMDL measure", "Weighted gross margin =\n    DIVIDE([Simulated gross profit], [Simulated net revenue])"),
      ("excel",),
      ("call", "Verification boundary", "The cohort SQL reconciled to exported counts. Base, Bull and Bear revenue and operating profit reconciled to a recalculated workbook. Microsoft TOM deserialized the Power BI model; Desktop rendering and native DAX execution were outside this verification."))),
    ("Commercial action plan", "What I would take to the trading meeting",
     "Use the dashboard to prioritize questions and the model to decide which tests deserve investment.",
     (("table", "roadmap"),
      ("links",))),
)


def picture(canvas, name, caption, y):
    # Keep the native KPI content and trim unused navigation and chart space.
    crops = {"01-executive": (362, 280, 1490, 754), "05-offer": (370, 216, 1460, 482)}
    with Image.open(OUT / "evidence" / f"{name}.png") as source:
        crop = source.crop(crops[name])
        width = min(WIDTH, (178 if name == "01-executive" else 135) * crop.width / crop.height)
        height = width * crop.height / crop.width
        canvas.drawImage(ImageReader(crop), 50, y-height, width, height)
    return put(canvas, escape(caption), y-height-7, 9, 12, BROWN)-13


def cover(canvas, data):
    y = put(canvas, escape(AUTHOR), 654, 16, 21, BROWN, "Helvetica-Bold")
    y = put(canvas, "New York University · M.S. in Management &amp; Analytics<br/>Independent Commercial &amp; Business Analytics Portfolio Project",
            y-3, 11, 15)-11
    y = put(canvas, "Commercially minded analyst combining financial modeling, business intelligence, and data analytics to support profitable business decisions.",
            y, 12, 16)-9
    y = put(canvas, "Commercial Analytics | Financial Modeling | Excel | Power BI | SQL | Python | Streamlit",
            y, 9.5, 13, BROWN)-10
    y = put(canvas, "<b>Annual Base simulation</b> · Synthetic catalog and reviews", y, 10, 14, BROWN)-7
    base = data["summary"]["Base"]
    cards = [("Net revenue", f"USD {base['net_revenue']:,.0f}"),
             ("Operating profit", f"USD {base['operating_profit']:,.0f}"),
             ("Gross margin", f"{base['gross_profit']/base['net_revenue']:.1%}"),
             ("Operating margin", f"{base['operating_profit']/base['net_revenue']:.1%}")]
    for i, (name, value) in enumerate(cards):
        x = 50+i*130
        canvas.setFillColor(PAPER)
        canvas.setStrokeColor(RULE)
        canvas.rect(x,y-52,122,52,stroke=1,fill=1)
        label(canvas,name,x+8,y-15,9,BROWN)
        label(canvas,value,x+8,y-37,16,INK,"Helvetica-Bold")
    y = put(canvas, "<b>Decision.</b> Hold the broad 15% offer at 20% assumed uplift. Test a 10% offer with a holdout and require positive incremental contribution.",
            y-66, 11, 15)-12
    y = picture(canvas, "01-executive", "Genuine local Streamlit crop · synthetic executive dashboard.", y)
    y = put(canvas, "<b>Project contribution.</b> Framed the assortment, pricing and contribution questions and interpreted the modeled trade-offs. AI assisted development, documentation, and verification.",
            y, 10, 14)-6
    return put(canvas, f'<link href="{LINKEDIN}" color="#634F43"><u>Connect on LinkedIn</u></link>', y, 10, 14)


def main():
    data = enrich(checked_data())
    data["roadmap"] = [
        ("Merchandising", "Review US skincare depth and fragrance tiers", "Weeks 1–2", "Sell-through and margin by SKU", "Range change only with verified demand and positive incremental contribution", "SKU sales, stock, landed costs"),
        ("Pricing & Marketing", "Run a targeted 10% offer with holdout", "Weeks 2–4", "Incremental contribution", "Positive after campaign costs and returns", "Assignments, sales, returns, campaign costs"),
        ("Finance", "Reforecast Base and Bear", "Next planning cycle", "Bear operating profit and spend", "Commit spend only within approved downside limits", "Realized uplift, unit costs, obligations"),
        ("Analytics", "Audit price records and approve matches", "Before next report", "Verified match and FX coverage", "Publish only accepted pairs with dated FX where required", "Product keys, match approvals, FX dates"),
    ]
    canvas = Canvas(str(OUT / FILENAME), pagesize=(612, 792), invariant=1)
    canvas.setAuthor(AUTHOR)
    canvas.setCreator("Luxury & Beauty Commercial Intelligence Portfolio")
    canvas.setTitle("Commercial & Business Analytics | Integrated Work Sample")
    canvas.setSubject("Synthetic beauty retail commercial analytics and simulated financial decisions")
    for index, (section, title, intro, blocks) in enumerate(PAGES, 1):
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, 612, 792, stroke=0, fill=1)
        canvas.setStrokeColor(GOLD)
        canvas.line(50, 736, 562, 736)
        put(canvas, f"INTEGRATED WORK SAMPLE  /  {escape(section.upper())}", 756, 9, 12, BROWN, "Helvetica-Bold")
        y = put(canvas, escape(title), 714, 28, 31, INK, "Helvetica-Bold")
        if intro:
            y = put(canvas, escape(intro), y - 10, 12, 17, BROWN) - 15
        for kind, *args in blocks:
            if kind == "cover":
                y = cover(canvas, data)
            elif kind == "assortment":
                rows = data["category"]
                total = sum(count for _, count in rows)
                y = bars(canvas, "Share of recent US assortment · 36 representatives",
                         [(name, count/total) for name, count in rows], y, .5, lambda v:f"{v:.1%}")
            elif kind == "pricing":
                y = pricing(canvas, data, y)
            elif kind == "waterfall":
                title, data_key, maximum = args
                y = waterfall(canvas, title, data[data_key], y, maximum)
            elif kind == "scenarios":
                rows = [(name, data["summary"][name]["operating_profit"]) for name in ("Bear", "Base", "Bull")]
                y = bars(canvas, "Annual operating profit · USD", rows, y, 230000, lambda v:f"{v:,.0f}")
            elif kind == "channels":
                rows = [(name, float(margin.rstrip("%"))) for name, _, _, margin in data["channels"]]
                y = bars(canvas, "Standalone monthly contribution margin", rows, y, 65, lambda v:f"{v:.1f}%")
            elif kind == "promotion":
                y = bars(canvas, "Incremental contribution vs. baseline · USD", data["options"], y, 3300,
                         lambda v:f"{v:+,.0f}" if v else "0", start=190, row_height=21)
            elif kind == "heatmap":
                y = heatmap(canvas, y)
            elif kind == "architecture":
                y = architecture(canvas, y)
            elif kind == "excel":
                for name, cell, formula in data["formulas"][1:4:2]:
                    y = put(canvas, escape(f"Excel | {name} · {cell}"), y, 9.5, 13, BROWN, "Helvetica-Bold")-2
                    y = put(canvas, escape(formula), y, 9, 12, INK, "Courier")-8
            elif kind == "table":
                rows = data[args[0]]
                if len(args) > 1:
                    rows = [rows[position] for position in args[1]]
                y = draw_table(canvas, args[0], rows, y)
            elif kind == "image":
                y = picture(canvas, *args, y)
            elif kind in ("call", "code"):
                label, body = args
                y = put(canvas, escape(label), y, 10, 14, BROWN, "Helvetica-Bold") - 3
                if kind == "code":
                    y = put(canvas, escape(body).replace("\n", "<br/>"), y, 9, 13, INK, "Courier") - 13
                else:
                    y = put(canvas, escape(body), y, 11, 15) - 13
            elif kind == "links":
                y = put(canvas, "Explore the work", y - 10, 13, 17, BROWN, "Helvetica-Bold") - 7
                for label, url in LINKS:
                    y = put(canvas, f'<link href="{url}" color="#634F43"><u>{label}</u></link>', y, 11, 17) - 6
        if y < 84:
            raise ValueError(f"Page {index} extends past the content area ({y:.0f} pt)")
        canvas.setStrokeColor(RULE)
        canvas.line(50, 72, 562, 72)
        canvas.setFont("Helvetica", 8.4)
        canvas.setFillColor(BROWN)
        canvas.drawString(50, 58, "Synthetic catalog and reviews  ·  Simulated financial results")
        canvas.drawRightString(562, 58, f"{index:02} / {len(PAGES):02}")
        x = 50
        for label, url in LINKS:
            canvas.drawString(x, 40, label)
            width = canvas.stringWidth(label, "Helvetica", 8.4)
            canvas.linkURL(url, (x, 38, x + width, 50), relative=0)
            x += width + 14
        canvas.showPage()
    canvas.save()


if __name__ == "__main__":
    main()
