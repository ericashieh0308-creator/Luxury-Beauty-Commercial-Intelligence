import csv

from streamlit.testing.v1 import AppTest

from beauty.demo import build_catalog
from beauty.pipeline import ROOT


def test_synthetic_catalog_is_isolated_and_auditable(tmp_path):
    output = tmp_path / "synthetic"
    build_catalog(output)
    assert not list(output.glob("*.zip"))
    with (output / "assortment_counts.csv").open(encoding="utf-8-sig", newline="") as source:
        cohorts = {(row["vintage"], row["market"]):row for row in csv.DictReader(source)}
    assert cohorts["recent","US"]["source_records"] == "36"
    assert cohorts["recent","CA"]["source_records"] == "27"
    with (output / "comparison_coverage.csv").open(encoding="utf-8-sig", newline="") as source:
        coverage = list(csv.DictReader(source))
    assert len(coverage) == 2
    assert all(int(row["candidate_pairs"]) > 0 and row["comparable_gaps"] == "0" for row in coverage)
    assert "Fictional" not in (output / "review_summary.csv").read_text(encoding="utf-8-sig")


def test_dashboard_public_navigation_and_native_currency(monkeypatch):
    monkeypatch.delenv("BEAUTY_LOCAL_CATALOG_DIR", raising=False)
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception and app.metric[0].value == "36"
    for page in ("Commercial intelligence","Pricing analytics","Customer intelligence",
                 "Financial performance","Data quality & limitations"):
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        if page == "Pricing analytics":
            app.selectbox[0].select_index(0).run()
            assert any(section.value == "Pricing architecture · CAD" for section in app.subheader)
        if page == "Customer intelligence":
            assert app.metric[0].value == "144"
