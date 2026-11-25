"""Luxury Brand Profitability and Premium Positioning decision simulator."""
from dataclasses import replace

import pandas as pd
import streamlit as st

from beauty.finance import Drivers, SCENARIOS, forecast, pnl, promotion

st.set_page_config(page_title="Beauty Commercial Planning", layout="wide")
st.title("Luxury Brand Profitability & Premium Positioning")
st.caption("Independent case study · Simulated assumptions · Model currency USD")
with st.sidebar:
    st.header("Operating assumptions")
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
def money(x):
    return f"${x:,.0f}" if x is not None else "Unavailable"
def pct(x):
    return f"{x:.1%}" if x is not None else "Unavailable"
cols = st.columns(5)
for col, label, value in zip(cols, ["Net revenue", "Gross profit", "Gross margin", "Contribution", "Operating profit"],
                            [money(after["net_revenue"]),money(after["gross_profit"]),pct(after["gross_margin"]),
                             money(after["contribution"]),money(after["operating_profit"])]):
    col.metric(label,value)
st.write(f"Promotion ROI {pct(case['roi'])} · Profit impact {money(after['operating_profit']-baseline['operating_profit'])} · "
         f"Required uplift {pct(case['required_uplift'])} · Breakeven discount {pct(case['breakeven_discount'])}")
st.write(f"Breakeven units {case['breakeven_units']:,.1f}" if case["breakeven_units"] is not None else "Breakeven units unavailable")
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
