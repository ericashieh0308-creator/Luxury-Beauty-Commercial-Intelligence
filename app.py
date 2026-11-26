"""Interactive catalog and simulated commercial finance portfolio."""
import os
from pathlib import Path
import tempfile

import altair as alt
import pandas as pd
import streamlit as st

from beauty.demo import build_catalog
from beauty.finance import Drivers, SCENARIOS, forecast, pnl, promotion

REQUIRED_CATALOG = (
    "assortment_counts", "portfolio", "commercial_kpi", "product_position", "review_summary",
    "review_topic", "quality_report", "quality_completeness", "comparison_coverage", "discount_summary",
)

st.set_page_config(page_title="Beauty Commercial Intelligence", layout="wide")

@st.cache_data(show_spinner="Building the synthetic catalog…")
def demo_catalog():
    with tempfile.TemporaryDirectory() as work:
        target = Path(work)
        build_catalog(target)
        return load_catalog(target)

def load_catalog(target):
    return {name: pd.read_csv(target / f"{name}.csv") for name in REQUIRED_CATALOG}

def count(value):
    return f"{value:,.0f}" if pd.notna(value) else "Not available"

def money(value, currency="USD"):
    return f"{currency} {value:,.0f}" if pd.notna(value) else "Not available"

def pct(value):
    return f"{value:.1%}" if pd.notna(value) else "Not available"

def chart(frame, x, y, title, horizontal=False):
    if frame.empty:
        st.info("Not available for the selected cohort.")
        return
    base = alt.Chart(frame, title=title).mark_bar(color="#835936", cornerRadiusEnd=3)
    if horizontal:
        plot = base.encode(x=alt.X(y, title=None), y=alt.Y(x, sort="-x", title=None), tooltip=[x,y])
    else:
        plot = base.encode(x=alt.X(x, title=None), y=alt.Y(y, title=None), tooltip=[x,y])
    st.altair_chart(plot, use_container_width=True)

def show_comparison(data):
    coverage = data["comparison_coverage"]
    st.subheader("Price comparison coverage")
    if coverage.empty:
        st.info("Not available. Price comparisons require an eligible pair.")
        return
    table = coverage[["comparison","candidate_pairs","accepted_pairs","comparable_gaps","availability"]].copy()
    table["comparison"] = table["comparison"].replace({"longitudinal":"Across snapshots","cross_market":"US and Canada"})
    st.dataframe(table.rename(columns={"comparison":"Comparison","candidate_pairs":"Candidates","accepted_pairs":"Accepted",
                         "comparable_gaps":"Usable price gaps","availability":"Pricing status"}),
        hide_index=True, use_container_width=True)

def select_cohort(frame, selection):
    vintage, market, date = selection
    dated = frame["snapshot"].isna() if pd.isna(date) else frame["snapshot"].eq(date)
    return frame.loc[frame["vintage"].eq(vintage) & frame["market"].eq(market) & dated]

def catalog_page(page, data):
    cohorts = data["assortment_counts"].sort_values(["vintage","market"], ascending=[False,True])
    if cohorts.empty:
        st.info("Not available. The catalog contains no usable source cohorts.")
        return
    options = {
        f"{vintage.title()} · {market} · {day if pd.notna(day) else 'Date unavailable'}": (vintage, market, day)
        for vintage, market, day in cohorts[["vintage","market","snapshot"]].itertuples(index=False, name=None)
    }
    labels = list(options)
    default = next((i for i, item in enumerate(options.values()) if item[:2] == ("recent", "US")), 0)
    selection = options[st.selectbox("Catalog cohort", labels, index=default)]
    currency = {"US":"USD","CA":"CAD"}.get(selection[1], "Native currency")
    header = select_cohort(cohorts, selection).iloc[0]
    kpi = select_cohort(data["commercial_kpi"], selection)
    portfolio = select_cohort(data["portfolio"], selection)
    pricing = select_cohort(data["product_position"], selection)
    discounts = select_cohort(data["discount_summary"], selection)
    if page == "Executive overview":
        st.subheader("Catalog snapshot")
        for column, (field, label) in zip(st.columns(3), (("source_records","Catalog records"),
                  ("distinct_products","Distinct products"),("distinct_product_skus","Explicit SKU keys"))):
            column.metric(label,count(header[field]))
        st.caption(f"One cohort at a time · {currency} for listed prices · Catalog counts describe assortment coverage")
        a,b = st.columns([1.15,1])
        with a:
            totals = portfolio.groupby("category",dropna=True)["products"].sum().reset_index()
            chart(totals, "category", "products", "Representative products by category", horizontal=True)
        with b:
            st.subheader("Promotion decision")
            promo = promotion(Drivers(),.15,.20,1500)
            st.metric("Simulated contribution impact",money(promo["incremental_contribution"]))
            st.write("At the model defaults, the offer lifts net revenue but falls short of contribution breakeven.")
            st.caption("15% proposed discount · 20% assumed unit uplift · USD 1,500 campaign cost")
        show_comparison(data)
    elif page == "Commercial intelligence":
        st.subheader("Brand and category portfolio")
        chart(portfolio.groupby("brand",dropna=True)["products"].sum().reset_index(), "brand", "products",
              "Representative products by brand", horizontal=True)
        st.dataframe(portfolio[["brand","category","products","mean_rating","bestsellers","bestseller_known",
                  "new_arrivals","new_arrival_known","exclusive_products","exclusive_known"]],
                  hide_index=True,use_container_width=True)
        flags = kpi.loc[kpi["dimension"].eq("overall"), ["metric","known","flagged","share"]].copy()
        flags["share"] = flags["share"].map(pct)
        st.subheader("Assortment flags")
        st.dataframe(flags,hide_index=True,use_container_width=True)
        st.caption("Share divides flagged products by records with a known flag. Missing shares display as Not available.")
    else:
        st.subheader(f"Pricing architecture · {currency}")
        tier_order = ["Entry","Core","Premium","Luxury","Insufficient cohort"]
        tiers = pricing["tier"].value_counts().reindex(tier_order).dropna().rename_axis("Price tier").reset_index(name="Products")
        chart(tiers, "Price tier", "Products", "Product representatives by category-relative price tier")
        price_columns = ["brand","category","price","tier","rating","engagement","premium_proxy"]
        st.dataframe(pricing[price_columns],hide_index=True,use_container_width=True)
        st.subheader("Valid discount depth")
        values = discounts[["category","priced_product_representatives","valid_discount_observations","mean_discount_depth"]].copy()
        values["mean_discount_depth"] = values["mean_discount_depth"].map(pct)
        st.dataframe(values,hide_index=True,use_container_width=True)
        show_comparison(data)

def customer_page(data):
    st.subheader("Historical customer intelligence")
    reviews, topics = data["review_summary"], data["review_topic"]
    st.metric("Historical review records",count(reviews["reviews"].sum()) if not reviews.empty else "Not available")
    chart(topics.groupby("topic")["mentions"].sum().reset_index(), "topic", "mentions",
          "Review topic mentions", horizontal=True)
    st.dataframe(reviews,hide_index=True,use_container_width=True)
    st.caption("Topic and sentiment scores use a historical lexicon baseline. The table shows aggregated signals.")

def quality_page(data):
    st.subheader("Source completeness and limitations")
    quality = data["quality_report"]
    if quality.empty:
        st.info("No quality issues were reported for this run.")
    else:
        st.dataframe(quality,hide_index=True,use_container_width=True)
    with st.expander("Completeness denominators"):
        st.dataframe(data["quality_completeness"], hide_index=True, use_container_width=True)
    show_comparison(data)
    st.write("Price gaps require verified comparable products, an eligible point price, and dated FX for cross-market results. Catalog coverage reflects the source sample. It cannot establish sales share or historical assortment growth.")

def finance_page():
    st.subheader("Simulated financial performance · USD")
    scenario = st.segmented_control("Scenario", list(SCENARIOS), default="Base") or "Base"
    forecasts = pd.DataFrame(row for _,row,_ in forecast(Drivers(),*SCENARIOS[scenario]))
    annual = forecasts.sum()
    for column, (label, value) in zip(st.columns(4), (
        ("Annual net revenue", money(annual["net_revenue"])), ("COGS",money(annual["cogs"])),
        ("Weighted gross margin",pct(annual["gross_profit"]/annual["net_revenue"])),
        ("Operating profit",money(annual["operating_profit"])))):
        column.metric(label,value)
    monthly = forecasts[["net_revenue","gross_profit","operating_profit"]].copy()
    monthly.index = pd.RangeIndex(1,13,name="Month")
    st.line_chart(monthly, color=["#835936","#526353","#201915"])
    st.dataframe(forecasts[["gross_sales","discounts","returns","net_revenue","cogs","gross_profit",
                            "contribution","operating_profit"]].set_index(monthly.index),use_container_width=True)

def promotion_page():
    st.subheader("Promotion decision support")
    st.caption("Simulated assumptions · Model currency USD")
    def money(x):
        return f"${x:,.0f}" if x is not None else "Not available"
    with st.sidebar.expander("Operating assumptions", expanded=True):
        price = st.number_input("List price (USD)", 0.0, 5000.0, 65.0)
        cost = st.number_input("Unit cost (USD)", 0.0, 5000.0, 23.0)
        units = st.number_input("Baseline monthly units", 0, 10000000, 1000)
        discount = st.slider("Baseline discount (%)", 0, 100, 8) / 100
        promoted = st.slider("Proposed discount (%)", 0, 100, 15) / 100
        response = st.slider("Assumed volume response (%)", -100, 300, 20) / 100
        returns = st.slider("Returns (%)", 0, 100, 6) / 100
        online = st.slider("E-commerce allocation (%)", 0, 100, 40) / 100
        fulfillment = st.number_input("Online fulfillment per unit (USD)", 0.0, 1000.0, 4.0)
        marketing = st.number_input("Incremental marketing (USD)", 0.0, 1000000.0, 1500.0)
        growth = st.slider("Additional growth (percentage points)", -80, 100, 0) / 100
        inflation = st.slider("Additional cost inflation (percentage points)", -50, 100, 0) / 100
        seasonality = st.slider("Seasonality strength (%)", 0, 100, 100) / 100
        fx = st.number_input("Scenario CAD per USD", 0.01, 100.0, 1.35)
        inventory = st.number_input("Available inventory units (assumption)", 0, 10000000, 1250)

    d = Drivers(price=price,cost=cost,units=units,discount=discount,returns=returns,
                online=online,fulfillment=fulfillment)
    baseline = pnl(d)
    case = promotion(d,promoted,response,marketing)
    after = case["after"]
    cols = st.columns(5)
    for col, label, value in zip(cols, ["Net revenue", "Gross profit", "Gross margin", "Contribution", "Operating profit"],
                                [money(after["net_revenue"]),money(after["gross_profit"]),pct(after["gross_margin"]),
                                 money(after["contribution"]),money(after["operating_profit"])]):
        col.metric(label,value)
    st.write(f"Promotion ROI {pct(case['roi'])} · Profit impact {money(after['operating_profit']-baseline['operating_profit'])} · "
             f"Required uplift {pct(case['required_uplift'])} · Breakeven discount {pct(case['breakeven_discount'])}")
    st.write(f"Breakeven units {case['breakeven_units']:,.1f}" if case["breakeven_units"] is not None else "Breakeven units not available")
    tabs = st.tabs(["Forecast","Discount sensitivity","Inventory & positioning"])
    with tabs[0]:
        projections = pd.DataFrame({name: [row["operating_profit"] for _,row,_ in forecast(
            d,g+growth,i+inflation,dd,seasonality)] for name,(g,i,dd) in SCENARIOS.items()},
            index=pd.RangeIndex(1,13,name="Month"))
        st.line_chart(projections)
        payload = projections.sum().rename("Simulated annual operating profit (USD)").to_csv()
        st.download_button("Download annual scenario comparison",payload,"simulated_scenarios.csv","text/csv")
    with tabs[1]:
        table = pd.DataFrame({f"{u:.0%} uplift": [promotion(d,x,u,marketing)["incremental_contribution"]
                              for x in (0,.05,.10,.15,.20,.25,.30)] for u in (0,.1,.2,.3,.4)},
                              index=[0,.05,.10,.15,.20,.25,.30])
        st.line_chart(pd.Series({x: promotion(d,x,response,marketing)["incremental_contribution"]
                                 for x in table.index},name="Incremental contribution (USD)"))
        st.dataframe(table.rename_axis("Discount"))
    with tabs[2]:
        projected = units*(1+response)
        st.metric("Leftover inventory at cost",money(max(0,inventory-projected)*cost))
        st.metric("Projected units above available inventory",f"{max(0,projected-inventory):,.0f}")
        st.metric("Illustrative list price (CAD)",f"C${price*fx:,.2f}")
        risk = min(100,round(max(0,promoted-discount)*300 + promoted*100))
        st.metric("Positioning pressure heuristic",f"{risk}/100")
        st.caption("Heuristic = 300 × incremental discount above baseline + 100 × proposed discount, capped at 100. Inventory exposure uses sell-through before returns. Financial scenarios assume unconstrained demand.")

st.title("Luxury & Beauty Commercial Intelligence")
local = os.environ.get("BEAUTY_LOCAL_CATALOG_DIR")
if local:
    st.caption("PRIVATE LOCAL MODE · Licensed catalog · Financial inputs and results are simulated")
    try:
        catalog = load_catalog(Path(local))
    except (OSError, ValueError):
        st.error("Catalog exports could not be loaded. Rebuild the private catalog before opening this mode.")
        st.stop()
else:
    st.caption("PUBLIC DEMO · Synthetic catalog and reviews · Simulated financial inputs and results")
    catalog = demo_catalog()

page = st.sidebar.radio("Workspace", (
    "Executive overview", "Commercial intelligence", "Pricing analytics", "Customer intelligence",
    "Financial performance", "Promotion & scenario simulator", "Data quality & limitations"),
    label_visibility="collapsed")
if page in {"Executive overview","Commercial intelligence","Pricing analytics"}:
    catalog_page(page,catalog)
elif page == "Customer intelligence":
    customer_page(catalog)
elif page == "Financial performance":
    finance_page()
elif page == "Promotion & scenario simulator":
    promotion_page()
else:
    quality_page(catalog)
