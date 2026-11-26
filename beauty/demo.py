"""Generate the public demonstration entirely from fictional catalog records."""
import argparse
import csv
import json
from pathlib import Path
import tempfile

from .finance_export import build as export_finance
from .pipeline import ROOT, build

CATEGORIES = ("Skincare", "Fragrance", "Makeup")
BRANDS = ("Fictional Atelier", "Sample Studio", "Demo House")
PRODUCTS = ("Cleanser", "Eau de Parfum", "Tint")

def write_rows(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def build_catalog(target):
    config = json.loads((ROOT / "config/sources.json").read_text(encoding="utf-8"))
    config["historical"]["snapshot"] = "2023-03-01"
    historical, recent, reviews = [], [], []
    for brand_index, brand in enumerate(BRANDS):
        for category_index, (category, product) in enumerate(zip(CATEGORIES, PRODUCTS)):
            for item in range((5, 4, 3)[category_index]):
                key = f"{brand_index}{category_index}{item}"
                name = f"{product} {item+1}"
                list_price = (28, 91, 23)[category_index] + 18*brand_index + 7*item
                rating = round(3.6 + .2*((item + brand_index + category_index) % 6), 1)
                historical.append(dict(product_id=f"old-{key}", brand_name=brand, product_name=name,
                    primary_category=category, size="30 mL", price_usd=list_price-3,
                    sale_price_usd=list_price-10 if item==0 else "", rating=rating, reviews=4,
                    sephora_exclusive=int(brand_index == 0), online_only=int(item == 2)))
                for ordinal, sample in enumerate(("love the texture", "great value", "sticky texture", "the pump was excellent")):
                    reviews.append(dict(product_id=f"old-{key}", rating=max(1, rating-.5*(ordinal==2)),
                                        submission_time=f"2023-02-0{ordinal+1}", review_text=sample))
                sample = dict(product_id=f"demo-{key}", sku_id=f"sku-{key}", brand=brand, name=name,
                              price=list_price, price_max=list_price, sale_price=list_price-7 if item==0 else "",
                              top_category=category, rating=0 if key=="000" else rating, review_count=7+3*item,
                              variation_type="Size", variant_count=1, is_bestseller=int(item == 3),
                              is_new=int(item == 1), is_limited_edition=int(item == 0),
                              is_sephora_exclusive=int(brand_index == 0), is_online_only=int(item == 2),
                              collected_at="2026-11-13T09:00:00-05:00")
                recent.append(dict(sample, country="US", country_name="United States", currency="USD"))
                if item != 1:
                    cad = round(list_price*1.35, 2)
                    recent.append(dict(sample, country="CA", country_name="Canada", currency="CAD",
                                       price=cad, price_max=cad, sale_price=cad-9 if item==0 else ""))
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        historic_path = work / "product_info.csv"
        recent_path = work / "sephora_sample_2026-11-13.csv"
        write_rows(historic_path, list(historical[0]), historical)
        write_rows(work / "reviews_demo.csv", list(reviews[0]), reviews)
        write_rows(recent_path, list(config["recent"]["columns"].values()), recent)
        build({"historical": work, "recent": recent_path}, config, target)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/demo"))
    args = parser.parse_args()
    build_catalog(args.output / "catalog")
    export_finance(args.output / "finance")
    print(f"Synthetic catalog and simulated finance tables: {args.output}")
