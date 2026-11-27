"""Render the standalone commercial work sample from checked public demo evidence."""
from html import escape

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .evidence import checked_data
from .render import BROWN, CREAM, EXCEL, GOLD, INK, LIVE, OUT, REPO, ROOT, RULE, WIDTH, draw_table, put

FILENAME = "Commercial_Business_Analytics_Integrated_Work_Sample.pdf"
EVIDENCE = REPO + "/tree/portfolio/v3-employer-ready/portfolio/v3"
LINKS = (
    ("Live Streamlit app", LIVE),
    ("GitHub repository", REPO),
    ("Excel workbook", EXCEL),
    ("Power BI KPI definitions", EVIDENCE.replace("/tree/", "/blob/") + "/Power_BI_Evidence.md"),
    ("Validation evidence", EVIDENCE.replace("/tree/", "/blob/") + "/Portfolio_Validation_Report.md"),
)

# Blocks are rendered in reading order. Evidence tables use the checked demo exports.
PAGES = (
    ("Executive decision brief", "Commercial & Business Analytics",
     "An integrated work sample in assortment, pricing and profit decisions for a modeled beauty retailer.",
     ("Show where to investigate assortment, how to protect contribution and when to approve a promotion.",),
     (("image", "01-executive", "Interaction captured in local Chromium | Synthetic Streamlit Executive Overview."),
      ("call", "Assortment", "Use the 36-product US snapshot as a starting point for range review. Validate demand, availability and margin before changing listings."),
      ("call", "Financial plan", "Anchor planning on Base operating profit of USD 155,493. Use the Bear case to size the downside."),
      ("call", "Promotion", "Withhold a broad 15% offer at the assumed 20% unit uplift. Evaluate a 10% test with a holdout and a contribution gate."))),
    ("Assortment and brand positioning", "Start with the range before proposing a reset",
     "Skincare accounts for 15 of 36 recent US representatives. Fragrance accounts for 12 and Makeup for nine.",
     (),
     (("image", "commercial-overview", "Chart generated from synthetic commercial exports | Synthetic US assortment by category."),
      ("table", "brand"),
      ("call", "Commercial readout", "The three fictional brands each have 12 US representatives. Equal range counts alone give no basis to infer share, sell-through or brand strength. Compare each brand’s category roles and price ladder before considering edits."))),
    ("Pricing and discount discipline", "Protect category price architecture",
     "The US fragrance median is USD 119.50 versus USD 60.00 for skincare and USD 48.00 for makeup.",
     (),
     (("table", "prices"), ("table", "discounts"),
      ("call", "Trade-off", "Makeup has the deepest mean observed US sale discount at 19.8%, based on three eligible observations. A blanket discount could sacrifice margin across items with different price roles."),
      ("call", "Decision", "Use category-specific guardrails and keep CAD and USD separate. Request accepted product matches and dated FX before making a cross-market premium claim."))),
    ("Customer signals and evidence limits", "Turn review themes into research questions",
     "Texture appears in 72 mentions and packaging in 36 across 144 synthetic historical reviews. Each review can contribute to multiple themes.",
     (),
     (("table", "reviews"), ("table", "comparison"), ("table", "quality"),
      ("call", "Next action", "Test clearer texture descriptions on product pages. Gather dated conversion and return data before treating review mentions as drivers of sales or satisfaction."),
      ("call", "Reporting decision", "Both comparison queues have zero accepted pairs. Recent sale-price fields are 28.6% present and parse-valid. Keep matched gaps unavailable and disclose the denominator when reporting discount depth."))),
    ("Financial performance", "Use the P&L as the planning baseline",
     "The simulated Base plan produces USD 700,824.23 in annual net revenue and USD 155,492.93 in operating profit.",
     (),
     (("image", "financial-overview", "Chart generated from simulated financial exports | Base annual P&L in USD."),
      ("table", "pnl", (1, 2, 3, 5, 7)),
      ("call", "Implication", "Base retains 60.3% at gross profit and 22.2% at operating profit. Use weighted margins from summed dollars to evaluate mix and margin protection."))),
    ("Budget variance and scenarios", "Separate controllable drivers from upside",
     "Bull adds USD 48,529 in operating profit versus Base. Bear delivers USD 68,604, a shortfall of about USD 86,889 versus Base.",
     (),
     (("table", "scenarios"), ("table", "variance"),
      ("call", "Revenue bridge", "Higher units explain USD 53,910 of the USD 70,317 Bull revenue uplift. Price accounts for USD 16,407. The bridge reconciles to the modeled revenue difference."),
      ("call", "Planning decision", "Treat Base as a planning reference. Use Bear for commitment and spending gates. Track volume versus plan alongside realized net price and variable expense before releasing additional spend."))),
    ("SKU and channel profitability", "Test contribution before allocating more volume",
     "The Core SKU contributes about USD 215K of USD 347K in annual Base contribution. Total dollars reflect both volume and unit economics.",
     (),
     (("table", "sku"), ("table", "channels"),
      ("call", "Channel trade-off", "The standalone monthly illustration yields a 53.6% Store contribution margin and 46.5% in E-commerce. Allocated volume and cost assumptions differ by channel; test incremental economics before moving inventory or media."),
      ("call", "Decision", "Protect Core availability first. Use contribution per incremental unit and the cost to serve to assess new volume. The channel illustration uses a separate monthly basis and should be reviewed independently of the annual SKU totals."))),
    ("Promotion ROI", "Require incremental contribution to clear the gate",
     "At 15% off and 20% assumed uplift, simulated sales rise USD 6,110 while contribution falls USD 455 after campaign cost.",
     (),
     (("image", "05-offer", "Local Chromium capture | 15% discount, 20% assumed uplift and USD 1,500 campaign cost."),
      ("table", "alternatives"),
      ("call", "Decision", "Pilot the 10% offer if the targeted customer group supports the assumed uplift. Measure incremental contribution against an untreated holdout and monitor returns before expanding."))),
    ("Sensitivity and approval threshold", "Recheck the gate when costs or response move",
     "At 15% off, raising assumed uplift to 30% lifts modeled incremental contribution to USD 2,067. That uplift is an assumption.",
     (),
     (("image", "06-uplift", "Local Chromium capture | The same offer after moving assumed unit uplift from 20% to 30%."),
      ("table", "sensitivity"),
      ("call", "Downside test", "At the original 20% uplift, increasing landed cost by 10% deepens the loss to USD 888. The break-even threshold rises from 1,219 to 1,239 total units. Re-estimate the threshold with current landed cost before approval."))),
    ("How the results were validated", "Trace the decision from SQL to the scorecard",
     "Python generates the demo outputs and promotion sensitivities. SQLite preserves the source vintage, market and snapshot for each catalog cohort.",
     (),
     (("code", "SQL | Cohort grain", "SELECT s.vintage, f.market, f.snapshot, COUNT(*) AS records\nFROM fact_product_snapshot f JOIN source s ON f.source_id = s.id\nGROUP BY s.vintage, f.market, f.snapshot;"),
      ("table", "cohorts"),
      ("code", "Power BI | TMDL measure", "Weighted gross margin =\n    DIVIDE([Simulated gross profit], [Simulated net revenue])"),
      ("table", "formulas"),
      ("call", "Verification boundary", "The cohort SQL reconciled to exported counts. Base, Bull and Bear revenue and operating profit reconciled to a recalculated workbook. Microsoft TOM deserialized the Power BI model; Desktop rendering and native DAX execution were outside this verification."))),
    ("Commercial action plan", "What I would take to the trading meeting",
     "Use the dashboard to prioritize questions and the model to decide which tests deserve investment.",
     (),
     (("call", "01  |  Merchandising", "Review US skincare depth and the fragrance price ladder. Bring demand, stock and margin by SKU before proposing a range reset."),
      ("call", "02  |  Pricing and marketing", "Run the targeted 10% pilot with a holdout. Record realized net price, returns and campaign cost; expand only if measured incremental contribution is positive."),
      ("call", "03  |  Finance", "Update the volume and landed-cost assumptions from the pilot. Reforecast Base and Bear and review commitments with the downside in view."),
      ("call", "04  |  Analytics", "Track valid pricing and review denominators, approve candidate matches before publishing gaps, and document FX coverage before any normalized price comparison."),
      ("links",))),
)


def picture(canvas, name, caption, y):
    directory = OUT / "evidence" if name[0].isdigit() else ROOT / "assets/portfolio"
    image = ImageReader(str(directory / f"{name}.png"))
    pixels_wide, pixels_high = image.getSize()
    width = min(WIDTH, 252 * pixels_wide / pixels_high)
    height = width * pixels_high / pixels_wide
    x = 50 + (WIDTH - width) / 2
    canvas.drawImage(image, x, y - height, width, height)
    return put(canvas, escape(caption), y - height - 7, 9, 12, BROWN) - 15


def main():
    data = checked_data()
    canvas = Canvas(str(OUT / FILENAME), pagesize=(612, 792), invariant=1)
    canvas.setTitle("Commercial & Business Analytics | Integrated Work Sample")
    canvas.setSubject("Synthetic beauty retail commercial analytics and simulated financial decisions")
    for index, (section, title, intro, context, blocks) in enumerate(PAGES, 1):
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, 612, 792, stroke=0, fill=1)
        canvas.setStrokeColor(GOLD)
        canvas.line(50, 736, 562, 736)
        put(canvas, f"INTEGRATED WORK SAMPLE  /  {escape(section.upper())}", 756, 9, 12, BROWN, "Helvetica-Bold")
        y = put(canvas, escape(title), 714, 28, 31, INK, "Helvetica-Bold")
        y = put(canvas, escape(intro), y - 10, 12, 17, BROWN) - 15
        if context:
            y = put(canvas, escape(context[0]), y, 11, 15) - 13
        for kind, *args in blocks:
            if kind == "table":
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
