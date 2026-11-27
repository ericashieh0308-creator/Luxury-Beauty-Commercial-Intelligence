"""Derive publication tables from checked synthetic exports and tracked models."""
from collections import defaultdict
import csv
from dataclasses import replace
from math import ceil, isclose
from pathlib import Path
from statistics import median

from openpyxl import load_workbook
from beauty.finance import Drivers, SCENARIOS, forecast, pnl, promotion
from scripts.validate_powerbi import validate_finance

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "output/portfolio-v3-demo"
WORKBOOK = ROOT / "models/excel/Luxury_Beauty_Commercial_Financial_Model.xlsx"


def read(group, table):
    with (DEMO / group / f"{table}.csv").open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def net(rows, key):
    return sum(float(row[key]) for row in rows)


def money(n):
    rounded = round(n)
    return f"({abs(rounded):,})" if rounded < 0 else f"{rounded:,}"


def pct(n):
    return f"{n:.1%}"


def checked_data():
    validate_finance(DEMO)
    c = lambda table: read("catalog", table)
    f = lambda table: read("finance", table)
    finance = f("fact_simulated_finance")
    cohorts = [(r["vintage"].title(),r["market"],r["snapshot"],r["source_records"],
                r["distinct_products"],r["distinct_product_skus"]) for r in c("assortment_counts")]
    brand = defaultdict(int)
    category = defaultdict(int)
    for row in c("portfolio"):
        if row["market"]=="US" and row["vintage"]=="recent":
            brand[row["brand"].title()] += int(row["products"])
            category[row["category"].title()] += int(row["products"])
    pricing = defaultdict(list)
    for row in c("product_position"):
        if row["vintage"]=="recent":
            pricing[row["market"],row["category"].title()].append(float(row["price"]))
    prices = [(m,"USD" if m=="US" else "CAD",k,str(len(v)),f"{median(v):,.2f}") for (m,k),v in sorted(pricing.items())]
    reviews = defaultdict(int)
    for row in c("review_topic"):
        reviews[row["topic"].title()] += int(row["mentions"])
    review_count=sum(int(r["reviews"]) for r in c("review_summary"))
    quality = [(r["field"].replace("_"," ").title(),r["denominator"],pct(float(r["completeness_rate"])),pct(float(r["parse_valid_rate"])))
               for r in c("quality_completeness") if r["vintage"]=="recent"
               and r["field"] in {"country","rating","sale_price","collected_at"}]
    comparison=[("US–Canada" if r["comparison"]=="cross_market" else "Across snapshots",
                 r["candidate_pairs"],r["accepted_pairs"],r["comparable_gaps"]) for r in c("comparison_coverage")]
    discounts=[(r["category"].title(),r["priced_product_representatives"],r["valid_discount_observations"],
                pct(float(r["mean_discount_depth"]))) for r in c("discount_summary")
               if r["market"]=="US" and r["vintage"]=="recent" and r["mean_discount_depth"]]
    scenarios, summary, monthly = [], {}, []
    for name in SCENARIOS:
        group = [row for row in finance if row["scenario"]==name]
        value = {key:net(group,key) for key in ("gross_sales","net_revenue","cogs","gross_profit",
                                                "variable_expenses","contribution","fixed","operating_profit")}
        r,g,o=(value[k] for k in ("net_revenue","gross_profit","operating_profit"))
        summary[name]=value
        scenarios.append((name,money(r),money(g),money(o),pct(g/r),pct(o/r)))
        if name=="Base":
            monthly = [(r["month"],money(float(r["net_revenue"])),money(float(r["gross_profit"])),
                        money(float(r["operating_profit"]))) for r in group]
    assert isclose(summary["Base"]["net_revenue"],700824.23424) and isclose(summary["Base"]["operating_profit"],155492.9310144)
    pnl_rows=[(label,money(summary["Base"][key])) for label,key in [
        ("Gross sales","gross_sales"),("Net revenue","net_revenue"),("COGS","cogs"),("Gross profit","gross_profit"),
        ("Variable expenses","variable_expenses"),("Contribution","contribution"),("Fixed expenses","fixed"),("Operating profit","operating_profit")]]
    variance = [(r["metric"].replace("_"," ").title(),money(float(r["ytd_variance"]))) for r in f("fact_simulated_variance") if r["month"]=="12"]
    pvm=f("fact_simulated_pvm")
    bridge=[(k.title(),money(net(pvm,k))) for k in ("price","volume","mix","new","removed","total","residual")]
    sku=f("fact_simulated_sku")
    sku_rows=[]
    for name in ("Core","Premium"):
        rows=[r for r in sku if r["scenario"]=="Base" and r["sku"]==name]
        sku_rows.append((name,money(net(rows,"net_revenue")),money(net(rows,"gross_profit")),money(net(rows,"contribution"))))
    channels=[(r["channel"],money(float(r["net_revenue"])),money(float(r["contribution"])),
               pct(float(r["contribution"])/float(r["net_revenue"]))) for r in f("fact_simulated_channel")]
    drivers=Drivers()
    offer=promotion(drivers,.15,.20,1500)
    alternatives=[("Keep 8% baseline; no campaign","0","0","—")]
    for label,discount,uplift in (("15% offer, 20% uplift",.15,.2),("10% offer, 20% uplift",.10,.2),("15% offer, 30% uplift",.15,.3)):
        result=promotion(drivers,discount,uplift,1500)
        alternatives.append((label,money(result["incremental_revenue"]),money(result["incremental_contribution"]),pct(result["roi"])))
    sensitivity=[]
    for change in (0,.10,.20):
        d=replace(drivers,cost=drivers.cost*(1+change))
        p=promotion(d,.15,.20,1500)
        sensitivity.append((pct(change),f"{d.cost:.2f}",money(pnl(d)["contribution"]),
                            money(p["incremental_contribution"]),str(ceil(p["breakeven_units"]))))
    with WORKBOOK.open("rb") as s:
        book=load_workbook(s)
    formulas=[
        ("Scenario selector","01_Control_Panel B2",str(book["01_Control_Panel"]["B2"].value)),
        ("Weighted gross margin","05_Monthly_PnL H14",book["05_Monthly_PnL"]["H14"].value),
        ("Operating margin","05_Monthly_PnL M14",book["05_Monthly_PnL"]["M14"].value),
        ("Promotion ROI","09_Promotion_ROI C7",book["09_Promotion_ROI"]["C7"].value),
        ("Bridge verification","14_Model_Checks C5",book["14_Model_Checks"]["C5"].value),
    ]
    return dict(cohorts=cohorts,brand=sorted(brand.items()),category=sorted(category.items(),key=lambda x:-x[1]),
                prices=prices,reviews=sorted(reviews.items(),key=lambda x:-x[1]),review_count=review_count,
                quality=quality,comparison=comparison,discounts=discounts,scenarios=scenarios,summary=summary,
                monthly=monthly,pnl=pnl_rows,variance=variance,bridge=bridge,sku=sku_rows,channels=channels,
                alternatives=alternatives,sensitivity=sensitivity,formulas=formulas)
