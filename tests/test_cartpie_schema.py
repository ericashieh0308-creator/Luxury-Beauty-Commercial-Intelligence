from contextlib import closing
import csv
from io import StringIO
import json
import sqlite3
from zipfile import ZipFile

from beauty.pipeline import ROOT, build, main

HEADERS = """product_id sku_id brand name country country_name currency price price_max sale_price
price_text top_category rating review_count variation_type variant_count variant_sku_ids
is_bestseller is_new is_limited_edition is_sephora_exclusive is_online_only product_url image_url
collected_at""".split()

def archive(tmp_path):
    path = tmp_path / "synthetic-cartpie.zip"
    parent = dict(product_id="p1", brand="X", name="Serum", country=" usa ",
                  country_name="United States", currency="usd", price="50", price_max="90", sale_price="40",
                  price_text="$50–$90", top_category="Skincare", rating="4.5", review_count="14",
                  variation_type="Size", variant_count="2", variant_sku_ids='["s1","s2"]',
                  is_bestseller="TRUE", is_new="0", is_limited_edition="yes", is_sephora_exclusive="1",
                  is_online_only="false", product_url="https://example.test/p1",
                  image_url="https://example.test/image", collected_at="2026-11-13T23:30:22-05:00")
    rows = [
        parent,
        dict(parent, sku_id="s1", price="50", price_max="50", sale_price="45"),
        dict(parent, sku_id="s2", price="90", price_max="90", sale_price=""),
        dict(parent, country="can", country_name="Canada", currency="CAD", sku_id="s1",
             price="75", price_max="70", sale_price="80", collected_at="2026-11-13T08:00:00Z", is_new="unknown"),
        dict(parent, product_id="p2", country="", country_name="Canada", currency="cad", price="NaN",
             sale_price="-1", collected_at="2026-11-13Tnot-a-time"),
        dict(parent, product_id="p3", country="US", country_name="Canada", price="60"),
    ]
    data = StringIO()
    writer = csv.DictWriter(data, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(rows)
    with ZipFile(path, "w") as zipped:
        zipped.writestr("nested/sephora_sample_2026-11-13.csv", data.getvalue())
        zipped.writestr("manifest.csv", "bad_header\nignored\n")
    return path

def test_cartpie_snapshot_and_quality(tmp_path):
    cfg = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
    cfg["historical"]["snapshot"] = "2023-02-01"
    cfg["comparable_ids"] = True
    hist = tmp_path / "product_info.csv"
    hist.write_text("product_id,brand_name,product_name,price_usd,size\np1,X,Serum,40,30 ml\n", encoding="utf-8")
    output = tmp_path / "processed"
    build({"historical": hist, "recent": archive(tmp_path)}, cfg, output)
    with closing(sqlite3.connect(output / "commercial.sqlite")) as db, closing(db.cursor()) as cursor:
        column_names = """
            market, country_raw, country_name, currency, snapshot, collected_at, price, price_max, sale,
            price_text, category, rating, engagement, variation_type, variant_count, variant_sku_ids,
            bestseller, new_arrival, limited, exclusive, online, product_url, image_url,
            size, variant, subcategory, promotion, out_of_stock
        """
        assert cursor.execute(f"""
            SELECT {column_names} FROM catalog_snapshot
            WHERE vintage='recent' AND market='US' AND sku IS NULL
        """).fetchone() == (
            "US", "usa", "United States", "USD", "2026-11-13", "2026-11-13T23:30:22-05:00", 50, 90, 40,
            "$50–$90", "skincare", 4.5, 14, "Size", 2, '["s1","s2"]', 1, 0, 1, 1, 0,
            "https://example.test/p1", "https://example.test/image", None, None, None, None, None,
        )
        assert cursor.execute("SELECT COUNT(*) FROM catalog_snapshot WHERE vintage='recent'").fetchone() == (6,)
        assert cursor.execute("SELECT market,sku FROM fact_sku_snapshot ORDER BY market,sku").fetchall() == [
            ("CA", "s1"), ("US", "s1"), ("US", "s2")
        ]
        assert cursor.execute("SELECT market,snapshot,price,sale FROM catalog_snapshot WHERE product='p2'").fetchone() == (
            "CA", None, None, None
        )
        issues = set(cursor.execute("SELECT field,issue FROM quality_report WHERE vintage='recent'"))
        assert {("price_max", "below_base_price"), ("sale", "exceeds_list"), ("price", "invalid"),
                ("sale_price", "invalid"), ("collected_at", "invalid"), ("country", "conflicting_country_name"),
                ("is_new", "invalid")} <= issues
        assert cursor.execute("""SELECT DISTINCT status FROM bridge_product_match
            WHERE comparison='longitudinal'""").fetchall() == [("manual_review",)]
        assert cursor.execute("SELECT COUNT(*) FROM price_comparison").fetchone() == (0,)
        assert cursor.execute("""SELECT p.discount_depth FROM pricing p JOIN catalog_snapshot f USING(id)
            WHERE f.vintage='recent' AND f.market='US'""").fetchone() == (None,)

def test_cartpie_diagnostic_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["pipeline", "--diagnose", str(archive(tmp_path))])
    main()
    summary, = json.loads(capsys.readouterr().out)
    assert summary["rows"] == 6
    assert summary["normalized_markets"] == {"US": 3, "CA": 2, "UNKNOWN": 1}
    assert summary["snapshot_dates"] == {"2026-11-13": 5, "<unavailable>": 1}
    assert summary["source_values_top_20"]["currency"] == {"usd": 4, "CAD": 1, "cad": 1}
    assert summary["source_values_top_20"]["is_new"] == {"0": 5, "unknown": 1}
    assert summary["prices"]["price_max"] == {"count": 6, "min": 50, "max": 90}
    assert summary["missing_mapped_columns"] == []
