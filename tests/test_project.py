import csv
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
from zipfile import ZipFile

import pytest
from openpyxl import load_workbook

from beauty.finance import Drivers, SCENARIOS, channels, forecast, pnl, promotion, pvm, variance
from beauty.pipeline import build, source_members
from beauty.workbook import SHEETS, build as build_workbook

ROOT = Path(__file__).resolve().parents[1]

def fixture(tmp_path):
    hist = tmp_path/"synthetic-historical.zip"
    with ZipFile(hist,"w") as z:
        z.writestr("nested/product_info.csv",
            "product_id,brand_name,product_name,price_usd,size,sephora_exclusive\n"
            "h,X,Serum,40,30 ml,0\nh2,X,Balm,,10 g,1\nh2,X,Balm,16,10 g,1\n")
        z.writestr("nested/reviews_0-250.csv","product_id,rating,submission_time,review_text\nh,4,2023-02-01,love the pump\n")
    recent = tmp_path/"synthetic-recent.csv"
    recent.write_text("product_id,brand,product_name,list_price,market,currency,snapshot_date,size\n"
                      "r,x,Serum,50,US,USD,2026-11-01,30 ml\n"
                      "c,x,Serum,70,CA,CAD,2026-11-01,30 ml\n")
    cfg = json.loads((ROOT/"config/sources.json").read_text())
    cfg["historical"]["snapshot"] = "2023-02-01"
    cfg["fx_usd_per_cad"] = {"2026-10-30": .75}
    cfg["cpi_us"] = {"2023-02": 100,"2026-11": 110}
    return hist,recent,cfg

def test_pipeline_synthetic(tmp_path):
    hist,recent,cfg = fixture(tmp_path)
    output = tmp_path/"test_outputs"
    build({"historical": hist,"recent": recent},cfg,output,ROOT/"data/external/benchmark_template.csv")
    with sqlite3.connect(output/"commercial.sqlite") as db:
        assert db.execute("SELECT records FROM duplicate_keys").fetchone() == (2,)
        assert db.execute("SELECT count FROM quality_report WHERE field='price_usd' AND issue='missing'").fetchone() == (1,)
        assert db.execute("SELECT mentions FROM review_topic WHERE topic='packaging'").fetchone() == (1,)
        gap, real = db.execute("SELECT percent_gap,real_change FROM price_comparison WHERE comparison='longitudinal'").fetchone()
        assert gap == pytest.approx(.25)
        assert real == pytest.approx(1.25/1.1-1)
        assert db.execute("SELECT percent_gap,fx_date FROM price_comparison WHERE comparison='cross_market'").fetchone() == (.05,"2026-10-30")
    assert "review_text" not in (output/"review_summary.csv").read_text()

def test_missing_fx_and_ambiguous_matches(tmp_path):
    hist,recent,cfg = fixture(tmp_path)
    cfg["fx_usd_per_cad"] = {}
    output = tmp_path/"out"
    paths = {"historical": hist,"recent": recent}
    build(paths,cfg,output)
    with sqlite3.connect(output/"commercial.sqlite") as db:
        assert db.execute("SELECT percent_gap FROM price_comparison WHERE comparison='cross_market'").fetchone() == (None,)
    with recent.open("a") as f:
        f.write("second,x,Serum,52,US,USD,2026-11-01,30 ml\n")
    build(paths,cfg,output)
    with sqlite3.connect(output/"commercial.sqlite") as db:
        assert db.execute("SELECT DISTINCT status FROM bridge_product_match").fetchall() == [("manual_review",)]
        assert db.execute("SELECT COUNT(*) FROM price_comparison").fetchone() == (0,)

def test_invalid_schema_and_zip(tmp_path):
    archive = tmp_path/"bad.zip"
    with ZipFile(archive,"w") as z:
        z.writestr("../test.csv","id\n1")
    with pytest.raises(ValueError,match="Unsafe ZIP"):
        with source_members(archive):
            pass
    bad = tmp_path/"bad.csv"
    bad.write_text("wrong_column\n2\n")
    cfg = json.loads((ROOT/"config/sources.json").read_text())
    with pytest.raises(ValueError,match="missing required"):
        build({"recent": bad},cfg,tmp_path/"output")

def test_pnl_and_channel():
    d = Drivers()
    p = pnl(d)
    assert p["net_revenue"] == pytest.approx(56212)
    assert p["gross_profit"] == pytest.approx(34592)
    assert p["gross_margin"] == pytest.approx(34592/56212)
    assert p["operating_profit"] == pytest.approx(12518.22)
    assert sum(x["contribution"] for x in channels(d).values()) == pytest.approx(p["contribution"])
    assert pnl(replace(d,units=0))["gross_margin"] is None

def test_forecast_and_variance():
    d = Drivers()
    results = {name:list(forecast(d,*drivers)) for name,drivers in SCENARIOS.items()}
    assert all(len(rows)==12 for rows in results.values())
    op = {name:sum(row["operating_profit"] for _,row,_ in rows) for name,rows in results.items()}
    assert op["Bull"] > op["Base"] > op["Bear"]
    budget, actual = results["Base"][0][1], results["Bull"][0][1]
    v = variance(budget,actual)
    assert v["operating_profit"][0] == pytest.approx(v["gross_profit"][0]-v["variable_expenses"][0]-v["fixed"][0])
    assert v["net_revenue"][2] == "Favorable"

def test_promotion_breakeven():
    d = Drivers()
    case = promotion(d,.15,.20,1500)
    assert case["roi"] == pytest.approx(case["incremental_contribution"]/1500)
    assert promotion(d,.15,case["required_uplift"],1500)["incremental_contribution"] == pytest.approx(0,abs=1e-8)
    assert promotion(d,case["breakeven_discount"],.20,1500)["incremental_contribution"] == pytest.approx(0,abs=1e-8)
    assert promotion(d,1,.20,0)["breakeven_units"] is None

def test_pvm():
    v = pvm({"A":(8,10),"B":(12,20),"D":(2,10)},{"A":(10,12),"B":(15,22),"C":(2,15)})
    assert v == {"price":50,"volume":80,"mix":0,"new":30,"removed":-20,"total":140,"residual":0}
    assert pvm({"A":(0,10)},{"A":(10,12)})["residual"] == 0

@pytest.mark.parametrize("kwargs",[{"price":-1},{"discount":1.1},{"units":float("nan")}])
def test_invalid_drivers(kwargs):
    with pytest.raises(ValueError):
        Drivers(**kwargs)

def test_workbook(tmp_path):
    path = tmp_path/"model.xlsx"
    build_workbook(path)
    book = load_workbook(path)
    assert book.sheetnames == [f"{i:02}_{n}" for i,n in enumerate(SHEETS)]
    assert book["05_Monthly_PnL"]["L14"].value == "=SUM(L2:L13)"
    assert all(book["14_Model_Checks"][f"C{r}"].data_type=="f" for r in range(2,7))

def test_streamlit():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT/"app.py")).run(timeout=30)
    assert not app.exception
    assert app.metric[0].label == "Net revenue"
    assert app.metric[0].value == "$62,322"
    app.number_input[2].set_value(0).run()
    assert not app.exception
    assert app.metric[0].value == "$0"
