"""Checked source values and vector figures for the integrated work sample."""
from collections import Counter
from contextlib import closing
from math import isclose
from statistics import median
import sqlite3

from reportlab.lib.colors import HexColor

from beauty.finance import Drivers, SCENARIOS, SKU_MIX, SEASONALITY, promotion
from .evidence import DEMO, net, pct, read
from .render import BROWN, GOLD, INK, PAPER, RULE, put

LOSS = HexColor("#A0594F")
GAIN = HexColor("#567660")


def enrich(data):
    categories = [name for name, _ in data["category"]]
    catalog = [r for r in read("catalog", "portfolio") if r["market"] == "US" and r["vintage"] == "recent"]
    counts = Counter({(r["brand"].title(), r["category"].title()): int(r["products"]) for r in catalog})
    totals = [sum(counts[b, k] for b, _ in data["brand"]) for k in categories]
    assert totals == [n for _, n in data["category"]]
    data["matrix"] = [(b, *(counts[b, k] for k in categories), n) for b, n in data["brand"]]
    data["matrix"] += [("Category total", *totals, sum(totals)),
                       ("Share of US range", *(pct(n/sum(totals)) for n in totals), "100.0%")]
    positions = [r for r in read("catalog","product_position") if r["market"] == "US" and r["vintage"] == "recent"]
    data["brand_price"] = [
        (brand, *(f"{median(float(r['price']) for r in positions if r['brand'].title() == brand and r['category'].title() == category):,.2f}"
                  for category in categories))
        for brand, _ in data["brand"]
    ]
    with closing(sqlite3.connect(DEMO/"catalog/commercial.sqlite")) as conn:
        missing, lower, equal, other, total = conn.execute(
            "SELECT SUM(f.sale IS NULL), SUM(f.sale > 0 AND f.sale < f.price), "
            "SUM(f.sale > 0 AND f.sale = f.price), SUM(f.sale IS NOT NULL AND "
            "(f.price IS NULL OR f.sale <= 0 OR f.sale > f.price)), COUNT(*) "
            "FROM fact_product_snapshot f JOIN source s ON s.id=f.source_id WHERE s.vintage='recent'"
        ).fetchone()
    assert missing + lower + equal + other == total == 63
    data["sale_status"] = [("Sale price unavailable", missing), ("Observed lower sale price", lower),
                           ("Sale equals list price", equal), ("Other populated sale-price records", other)]
    base = data["summary"]["Base"]
    assert [round(base[k]) for k in ("net_revenue","operating_profit")] == [700824, 155493]
    assert [pct(base[k]/base["net_revenue"]) for k in ("gross_profit","operating_profit")] == ["60.3%", "22.2%"]
    data["waterfall"] = [(label, sign*base[key], sign > 0) for label, key, sign in (
        ("Net revenue", "net_revenue", 1), ("COGS", "cogs", -1), ("Gross profit","gross_profit",1),
        ("Variable exp.","variable_expenses",-1), ("Contribution","contribution",1),
        ("Fixed exp.","fixed",-1), ("Operating profit","operating_profit",1))]
    for step in (0, 2, 4):
        entries = data["waterfall"]
        assert isclose(entries[step][1] + entries[step+1][1], entries[step+2][1], abs_tol=1e-8)
    data["pnl_cents"] = [(label, f"{value:,.2f}") for label, value, _ in data["waterfall"]]
    pvm = read("finance", "fact_simulated_pvm")
    data["pvm_effects"] = [(k.title(), net(pvm,k)) for k in ("volume","mix","price","new","removed")]
    delta = data["summary"]["Bull"]["net_revenue"] - base["net_revenue"]
    assert isclose(sum(v for _,v in data["pvm_effects"]), delta, abs_tol=1e-7)
    assert isclose(net(pvm,"residual"), 0, abs_tol=1e-7)
    data["revenue_bridge"] = [("Base",base["net_revenue"],True),
                              *((name, value, False) for name,value in data["pvm_effects"]),
                              ("Bull",data["summary"]["Bull"]["net_revenue"],True)]
    data["pvm_cents"] = [(label, f"{value:,.2f}" if abs(value) >= .005 else "0.00")
                         for label,value in [*data["pvm_effects"],("Total change",delta)]]
    data["assumptions"] = [(case,f"{growth:+.0%}",f"{cost:+.0%}",f"{discount*100:+.0f} pp",
                            pct(Drivers().discount+discount))
                           for case in ("Bear","Base","Bull") for growth,cost,discount in [SCENARIOS[case]]]
    sku_data = read("finance","fact_simulated_sku")
    d = Drivers()
    data["sku_economics"] = []
    for name, (mix, price_factor, _) in SKU_MIX.items():
        rows = [r for r in sku_data if r["scenario"] == "Base" and r["sku"] == name]
        units = sum(SEASONALITY)*d.units*(1+SCENARIOS["Base"][0])*mix
        assert isclose(net(rows,"gross_sales"), units*d.price*price_factor)
        contribution, revenue = (net(rows,k) for k in ("contribution","net_revenue"))
        data["sku_economics"].append((name,f"{revenue:,.0f}",f"{contribution:,.0f}",
                                      pct(contribution/revenue),pct(contribution/base["contribution"]),f"{contribution/units:,.2f}"))
    data["options"] = [("8% baseline / no campaign",0)] + [
        (f"{discount:.0%} off / {uplift:.0%} uplift", promotion(d,discount,uplift,1500)["incremental_contribution"])
        for discount,uplift in ((.15,.20),(.10,.20),(.15,.30))]
    assert [round(v) for _,v in data["options"]] == [0,-455,2973,2067]
    return data


def label(c, text, x, y, size=9, color=INK, font="Helvetica"):
    c.setFont(font,size)
    c.setFillColor(color)
    c.drawString(x,y,str(text))


def bars(c, title, rows, y, maximum, fmt, start=173, row_height=24):
    label(c,title,50,y-11,11,BROWN,"Helvetica-Bold")
    left = min(0,min(v for _,v in rows))
    width = 310
    def x(value):
        return start + (value-left)/(maximum-left)*width
    zero = x(0)
    c.setStrokeColor(RULE)
    c.line(zero,y-22,zero,y-24-len(rows)*row_height)
    for i,(name,value) in enumerate(rows):
        baseline = y-35-i*row_height
        label(c,name,50,baseline,9.2)
        c.setFillColor(LOSS if value<0 else GOLD)
        c.rect(min(zero,x(value)),baseline-3,max(.65,abs(zero-x(value))),10,stroke=0,fill=1)
        label(c,fmt(value),max(zero,x(value))+6,baseline,9)
    return y-29-len(rows)*row_height-9


def waterfall(c, title, rows, y, maximum):
    label(c,title,50,y-11,11,BROWN,"Helvetica-Bold")
    bottom, height = y-162, 119
    left, space, bar_width = 52, 73, 49
    level = 0
    c.setStrokeColor(RULE)
    c.line(left,bottom,559,bottom)
    for i,(name,value,total) in enumerate(rows):
        new_level = value if total else level + value
        low, high = (0,value) if total else sorted((level,new_level))
        x = left + i*space + 7
        top = bottom + high/maximum*height
        c.setFillColor(BROWN if total else (LOSS if value<0 else GOLD))
        c.rect(x,bottom+low/maximum*height,bar_width,max(.8,(high-low)/maximum*height),stroke=0,fill=1)
        if i + 1 < len(rows):
            cy = bottom+new_level/maximum*height
            c.line(x+bar_width,cy,x+space,cy)
        c.setFont("Helvetica",8.4)
        c.setFillColor(INK)
        shown = 0 if abs(value)<.005 else value
        c.drawCentredString(x+bar_width/2,top+5,f"{shown/1000:,.1f}")
        c.drawCentredString(x+bar_width/2,bottom-13,name)
        level = new_level
    return bottom-27


def pricing(c, data, y):
    for market, unit, maximum in (("US","USD",135),("CA","CAD",180)):
        rows = [(f"{category} (n={n})",float(value.replace(",","")))
                for m,_,category,n,value in data["prices"] if m==market]
        y = bars(c,f"{market} median list price · {unit} · independent scale",rows,y,maximum,
                 lambda v:f"{v:,.2f}",row_height=20)
    rows = [(f"{category} ({count}/{priced})",float(depth.rstrip("%")))
            for category,priced,count,depth in data["discounts"]]
    return bars(c,"US mean discount depth · valid sales / priced representatives",rows,y,24,
                lambda v:f"{v:.1f}%",row_height=20)


def heatmap(c, y):
    d = Drivers()
    discounts = [i/100 for i in range(8,20)]
    uplifts = [0,.05,.10,.15,.20,.25,.30,.35,.40]
    left, width, height = 107, 37, 19
    bottom = y-24-len(uplifts)*height
    label(c,"Incremental contribution (USD) · USD 1,500 campaign spend",50,y-10,11,BROWN,"Helvetica-Bold")
    for i,u in enumerate(uplifts):
        cy = bottom+i*height
        label(c,f"{u:.0%}",76,cy+7,8.5)
        for j,discount in enumerate(discounts):
            delta = promotion(d,discount,u,1500)["incremental_contribution"]
            c.setFillColor(HexColor("#DFE9DC" if delta >= 0 else "#F0D9D1"))
            c.setStrokeColor(PAPER)
            c.rect(left+j*width,cy,width,height,fill=1,stroke=1)
            c.setFont("Helvetica",8.7)
            c.setFillColor(INK)
            c.drawCentredString(left+j*width+width/2,cy+6,f"{delta:+,.0f}")
    for j,discount in enumerate(discounts):
        label(c,f"{discount:.0%}",left+j*width+10,bottom-13,8.5)
    def point(discount,uplift):
        return (left+width/2+(discount-.08)/.01*width, bottom+height/2+uplift/.05*height)
    c.setStrokeColor(INK)
    c.setLineWidth(1.6)
    path = c.beginPath()
    for i in range(56):
        discount = .08+i*.002
        uplift = promotion(d,discount,0,1500)["required_uplift"]
        assert isclose(promotion(d,discount,uplift,1500)["incremental_contribution"], 0, abs_tol=1e-8)
        x,cy = point(discount,uplift)
        (path.lineTo if i else path.moveTo)(x,cy)
    c.drawPath(path)
    for discount,uplift,color in ((.10,.20,GAIN),(.15,.20,LOSS)):
        x,cy = point(discount,uplift)
        c.setStrokeColor(color)
        if discount == .10:
            c.rect(x-width/2+1,cy-height/2+1,width-2,height-2,stroke=1,fill=0)
        else:
            c.roundRect(x-width/2+1,cy-height/2+1,width-2,height-2,5,stroke=1,fill=0)
    c.setLineWidth(1)
    c.saveState()
    c.translate(64, bottom+39)
    c.rotate(90)
    label(c,"Assumed unit uplift",0,0,8.5)
    c.restoreState()
    label(c,"Proposed discount",224,bottom-27,9)
    return put(c,"Green = gain · rose = loss · dark curve = break-even · box = 10% pilot · rounded box = 15% proposal. The 8% baseline has no campaign and zero incremental contribution; the 8% grid column includes campaign spend.",
               bottom-36,9,13,BROWN)-12


def architecture(c, y):
    label(c,"Source-to-decision architecture",50,y-11,11,BROWN,"Helvetica-Bold")
    lanes = (
        ("Synthetic catalog", "Python validation", "SQLite / SQL", "Commercial exports", "Power BI / Streamlit"),
        ("Planning drivers", "Python finance", "Scenario exports", "Excel reconciliation", "Power BI / Streamlit"),
    )
    for i,lane in enumerate(lanes):
        cy = y-38-i*24
        for j,node in enumerate(lane):
            x = 50+j*103
            c.setFillColor(PAPER)
            c.setStrokeColor(RULE)
            c.rect(x,cy,98,19,fill=1,stroke=1)
            label(c,node,x+5,cy+6,8.1)
            if j < len(lane)-1:
                c.setStrokeColor(GOLD)
                c.line(x+98,cy+9,x+103,cy+9)
                c.line(x+101,cy+11,x+103,cy+9)
                c.line(x+101,cy+7,x+103,cy+9)
    return put(c,"Commercial and finance outputs inform assortment, price and contribution decisions. The Excel workbook independently calculates from planning inputs.",
               y-69,9,12,BROWN)-12
