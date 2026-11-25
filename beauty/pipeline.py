"""Read ZIP members as streams. Restricted outputs belong under data/processed."""
import argparse
from collections import Counter
from contextlib import closing, contextmanager
import csv
from datetime import date
from hashlib import sha256
from io import TextIOWrapper
import json
from math import isfinite
from pathlib import Path, PurePosixPath
import re
import sqlite3
import tempfile
import unicodedata
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
FLAGS = "exclusive online limited bestseller new_arrival promotion out_of_stock".split()
FIELDS = """snapshot market currency product sku brand name category subcategory size variant price sale
rating engagement exclusive online limited bestseller new_arrival promotion out_of_stock""".split()
HISTORICAL = dict(product="product_id", brand="brand_name", name="product_name",
                  category="primary_category", subcategory="secondary_category", size="size",
                  price="price_usd", sale="sale_price_usd", rating="rating", engagement="reviews",
                  exclusive="sephora_exclusive", online="online_only", limited="limited_edition",
                  out_of_stock="out_of_stock")
TOPICS = {"irritation": {"irritation", "burning", "rash"}, "scent": {"scent", "fragrance", "smell"},
          "texture": {"sticky", "greasy", "texture"}, "packaging": {"pump", "packaging", "leak"},
          "value": {"expensive", "affordable", "overpriced"}}
BENCHMARK = "organization title publication_date measurement_period geography metric value units url access_date limitations".split()

def normalize(value):
    if not value:
        return None
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split()) or None

@contextmanager
def source_members(path):
    if path.is_dir():
        paths = sorted(x for x in path.rglob("*") if x.is_file() and x.suffix.lower() == ".csv")
        yield [(x.relative_to(path).as_posix(), lambda x=x: x.open("rb")) for x in paths]
    elif path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            names = [i.filename for i in archive.infolist() if not i.is_dir()]
            if len(set(names)) != len(names):
                raise ValueError("Duplicate ZIP member names")
            for name in names:
                p = PurePosixPath(name.replace(chr(92), "/"))
                if p.is_absolute() or ".." in p.parts or ":" in p.parts[0]:
                    raise ValueError(f"Unsafe ZIP member name: {name}")
            yield [(n, lambda n=n: archive.open(n)) for n in names if n.lower().endswith(".csv")]
    else:
        yield [(path.name, lambda: path.open("rb"))]

def number(value, low=0, high=float("inf")):
    n = float(value)
    if not isfinite(n) or n < low or n > high:
        raise ValueError("Number outside accepted range")
    return n

def integer(value):
    n = number(value)
    if n != int(n):
        raise ValueError("Expected integer")
    return int(n)

def flag(value):
    return {"1": 1, "0": 0, "true": 1, "false": 0, "yes": 1, "no": 0}[value.casefold()]

def calendar(value):
    return date.fromisoformat(value[:10]).isoformat()

def parse(row, column, converter, issues):
    value = (row.get(column) or "").strip()
    if not value:
        issues[column, "missing"] += 1
        return None
    try:
        return converter(value)
    except (ValueError, KeyError):
        issues[column, "invalid"] += 1
        return None

def text(value):
    return value

def ingest_file(cursor, vintage, member, opener, cfg, review):
    digest = sha256()
    with opener() as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    issues = Counter()
    with TextIOWrapper(opener(), encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames or []
        mapping = {"product": "product_id", "rating": "rating", "date": "submission_time",
                   "review": "review_text"} if review else cfg["columns"]
        required = ["product", "rating", "date", "review"] if review else ["product", "brand", "name", "price"]
        absent = [mapping.get(key, key) for key in required if mapping.get(key) not in headers]
        if absent or len(set(headers)) != len(headers):
            raise ValueError(f"{member}: missing required columns {absent} or duplicate headers. Inspect and configure the source mapping.")
        absent_optional = set(mapping.values()) - set(headers)
        for column in absent_optional:
            issues[column, "absent"] += 1
        source_id = cursor.execute("INSERT INTO source(vintage,member,sha256,headers) VALUES (?,?,?,?)",
                               (vintage, member, digest.hexdigest(), json.dumps(headers))).lastrowid
        seen = set()
        topics = Counter()
        batch = []
        table = "fact_review" if review else "fact_product_snapshot"
        sql = ("INSERT INTO fact_review VALUES (?,?,?,?,?,?)" if review else
               f"INSERT INTO {table}(source_id,line,{','.join(FIELDS)}) VALUES ({','.join('?' for _ in range(2+len(FIELDS)))})")
        for ix, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                issues["row", "field_count_mismatch"] += 1
            def get(key, converter=text):
                column = mapping.get(key)
                return parse(row, column, converter, issues) if column in headers else None
            product = get("product")
            if not product:
                issues["product", "row_excluded_missing_identifier"] += 1
                continue
            rating = get("rating", lambda x: number(x, 1, 5))
            if review:
                review_text = get("review")
                words = set(re.findall(r"[a-z]+", (review_text or "").lower()))
                sentiment = len(words & {"love", "great", "excellent", "smooth", "favorite"}) - len(
                    words & {"hate", "terrible", "rash", "burning", "disappointed"})
                for topic, vocabulary in TOPICS.items():
                    if words & vocabulary:
                        topics[product, topic] += 1
                record = (source_id, ix, product, rating, get("date", calendar),
                          (sentiment > 0)-(sentiment < 0) if review_text else None)
            else:
                market = (get("market") or cfg.get("market") or "UNKNOWN").upper()
                currency = (get("currency") or cfg.get("currency") or "").upper()
                expected = {"US": "USD", "CA": "CAD"}.get(market)
                if not expected or currency != expected:
                    issues["currency", "unknown_or_mismatch"] += 1
                price, sale = get("price", number), get("sale", number)
                if price is not None and (price == 0 or price > 2000):
                    issues["price", "anomaly_retained"] += 1
                if price is not None and sale is not None and sale > price:
                    issues["sale", "exceeds_list"] += 1
                snapshot = get("snapshot", calendar) or cfg.get("snapshot")
                sku = get("sku")
                key = (snapshot, market, product, sku)
                if key in seen:
                    issues["sku" if sku else "product", "duplicate_key_retained"] += 1
                seen.add(key)
                flags = {k: get(k, flag) for k in FLAGS}
                if flags["promotion"] is None and price is not None and sale is not None and sale <= price:
                    flags["promotion"] = int(sale < price)
                record = (source_id, ix, snapshot, market, currency or None, product, sku,
                          get("brand", normalize), get("name"), get("category", normalize),
                          get("subcategory", normalize), get("size", normalize), get("variant", normalize),
                          price, sale, rating, get("engagement", integer), *(flags[k] for k in FLAGS))
            batch.append(record)
            if len(batch) == 5000:
                cursor.executemany(sql, batch)
                batch.clear()
        cursor.executemany(sql, batch)
        cursor.executemany("""INSERT INTO review_topic VALUES (?,?,?) ON CONFLICT(product,topic)
          DO UPDATE SET mentions=mentions+excluded.mentions""", [(p,t,n) for (p,t),n in topics.items()])
    cursor.executemany("INSERT INTO quality VALUES (?,?,?,?)", [(source_id,k,i,n) for (k,i),n in issues.items()])

def build(paths, config, output, benchmark=None):
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output) as tmp:
        temporary = Path(tmp) / "commercial.sqlite"
        with closing(sqlite3.connect(temporary)) as db:
            db.row_factory = sqlite3.Row
            with db, closing(db.cursor()) as cursor:
                cursor.executescript((ROOT/"sql/schema.sql").read_text(encoding="utf-8"))
                for vintage, path in paths.items():
                    cfg = config.get(vintage, {}).copy()
                    if cfg.get("snapshot"):
                        cfg["snapshot"] = date.fromisoformat(cfg["snapshot"]).isoformat()
                    if vintage == "historical":
                        cfg = {"market": "US", "currency": "USD", **cfg,
                               "columns": {**HISTORICAL, **cfg.get("columns", {})}}
                    with source_members(path) as members:
                        selected = 0
                        for name, opener in members:
                            base = PurePosixPath(name).name
                            review = vintage == "historical" and base.startswith("reviews_")
                            if vintage == "historical" and not review and base != "product_info.csv":
                                continue
                            if vintage == "recent" and not re.search(cfg.get("file_pattern", r"\.csv$"), name):
                                continue
                            ingest_file(cursor, vintage, name, opener, cfg, review)
                            selected += not review
                        if not selected:
                            raise ValueError(f"No product CSV selected for {vintage}: {path}")
                if benchmark:
                    with benchmark.open(encoding="utf-8-sig", newline="") as source:
                        reader = csv.DictReader(source)
                        if reader.fieldnames != BENCHMARK:
                            raise ValueError("Benchmark headers do not match template")
                        for row in reader:
                            if any(not row[k] for k in BENCHMARK) or not row["url"].startswith("https://"):
                                raise ValueError("Incomplete benchmark record")
                            row["value"] = number(row["value"], -float("inf"))
                            for key in ("publication_date", "access_date"):
                                row[key] = date.fromisoformat(row[key]).isoformat()
                            cursor.execute("INSERT INTO fact_industry_benchmark VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                       [row[k] for k in BENCHMARK])
                cursor.execute("INSERT INTO dim_brand SELECT DISTINCT brand FROM fact_product_snapshot WHERE brand IS NOT NULL")
                cursor.execute("INSERT INTO dim_category SELECT DISTINCT category FROM fact_product_snapshot WHERE category IS NOT NULL")
                from .commercial import materialize, export
                materialize(cursor, config)
                export(cursor, Path(tmp))
        # Close the SQLite transaction, cursor and file handle before publishing.
        for artifact in Path(tmp).iterdir():
            artifact.replace(output / artifact.name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical", type=Path)
    parser.add_argument("--recent", type=Path)
    parser.add_argument("--config", type=Path, default=ROOT/"config/sources.json")
    parser.add_argument("--benchmark", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT/"data/processed")
    parser.add_argument("--inspect", type=Path, help="Print CSV member names and headers only")
    args = parser.parse_args()
    if args.inspect:
        with source_members(args.inspect) as members:
            for name, opener in members:
                with TextIOWrapper(opener(), encoding="utf-8-sig", newline="") as f:
                    print(name, next(csv.reader(f), []))
        return
    paths = {key: path for key, path in (("historical", args.historical), ("recent", args.recent)) if path}
    if not paths:
        parser.error("Provide --historical, --recent, or --inspect")
    build(paths, json.loads(args.config.read_text(encoding="utf-8")), args.output, args.benchmark)

if __name__ == "__main__":
    main()
