from contextlib import closing
import csv
import sqlite3

import pytest

from beauty.commercial import fx_for, match
from beauty.finance_export import build as export_finance
from beauty.pipeline import ROOT
from beauty.references import FIELDS, load


def test_matching_conflicts_and_reciprocity():
    left = dict(id=1, product="p", sku="sku", brand="brand", name="serum",
                size="30 ml", variant="original", snapshot="2026-11-13", market="US")
    exact = dict(left, id=2, market="CA")
    alternative = dict(exact, id=3, product="other", sku="different")
    results = list(match([left], [exact, alternative], True, same_day=True))
    assert [(r[3], r[4], r[5]) for r in results] == [
        ("manual_review", "ambiguous", "non_unique_reciprocal_pair"),
        ("manual_review", "ambiguous", "non_unique_reciprocal_pair"),
    ]
    assert list(match([left], [exact], False))[0][2:6] == (
        "attributes", "accepted", "exact", "verified_attributes"
    )
    assert list(match([left], [dict(exact, size="50 ml")]))[0][3:6] == (
        "rejected", "rejected", "specification_conflict"
    )
    assert list(match([left], [dict(exact, snapshot="2026-11-14")], same_day=True))[0][5] == "snapshot_date_conflict"
    duplicate = dict(exact, id=4)
    results = list(match([left], [exact, duplicate, alternative], True))
    assert all(pair[3] == "manual_review" for pair in results)
    assert [pair[5] for pair in results] == [
        "duplicate_business_key", "duplicate_business_key", "non_unique_reciprocal_pair"
    ]


@pytest.mark.parametrize("invalid", [None, "units", "duplicate", "future_publication", "conflicting_config"])
def test_external_reference_import(tmp_path, invalid):
    path = tmp_path / "references.csv"
    row = dict(organization="Synthetic test", title="Synthetic observation", publication_date="2026-11-13",
               measurement_period="2026-11-13", geography="Canada", metric="fx_usd_per_cad",
               value=.75, units="USD per CAD", url="https://example.test/fixture", access_date="2026-11-14",
               limitations="Synthetic fixture only")
    if invalid == "units":
        row["units"] = "CAD per USD"
    elif invalid == "future_publication":
        row["publication_date"] = "2026-11-15"
    config = {"fx_usd_per_cad": {"2026-11-13": .72}} if invalid == "conflicting_config" else {}
    cpi = dict(row, metric="cpi_us", geography="US", measurement_period="2026-10", value=300,
               units="index (1982-84=100)", publication_date="2026-11-13")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([row, row if invalid == "duplicate" else cpi])
    with closing(sqlite3.connect(":memory:")) as db, closing(db.cursor()) as cursor:
        cursor.executescript((ROOT/"sql/schema.sql").read_text(encoding="utf-8"))
        if invalid:
            with pytest.raises(ValueError, match="references.csv:"):
                load(cursor, path, config)
        else:
            rates = load(cursor, path, config)
            assert rates["cpi_us"] == {"2026-10": 300}
            assert fx_for("2026-11-14", rates["fx_usd_per_cad"]) == ("2026-11-13", .75)
            assert fx_for("2026-11-12", rates["fx_usd_per_cad"]) == (None, None)
            assert fx_for("2026-11-18", rates["fx_usd_per_cad"]) == (None, None)
            assert cursor.execute("SELECT count(*) FROM fact_industry_benchmark").fetchone() == (2,)


def test_finance_exports_reconcile(tmp_path):
    export_finance(tmp_path)

    def rows(name):
        with (tmp_path / f"{name}.csv").open(encoding="utf-8-sig", newline="") as f:
            data = list(csv.DictReader(f))
        assert data and all(row["evidence"] == "SIMULATED" for row in data)
        return data

    finance = {(r["scenario"], r["month"]): r for r in rows("fact_simulated_finance")}
    assert len(finance) == 36
    for r in rows("fact_simulated_pvm"):
        difference = float(finance["Bull", r["month"]]["net_revenue"]) - float(finance["Base", r["month"]]["net_revenue"])
        assert float(r["total"]) == pytest.approx(difference)
        assert float(r["residual"]) == pytest.approx(0, abs=1e-8)
    for case in ("Base", "Bull", "Bear"):
        for key in ("net_revenue", "cogs", "gross_profit", "contribution", "operating_profit"):
            sku_total = sum(float(r[key]) for r in rows("fact_simulated_sku") if r["scenario"] == case)
            assert sku_total == pytest.approx(sum(float(r[key]) for (scenario, _), r in finance.items() if scenario == case))
