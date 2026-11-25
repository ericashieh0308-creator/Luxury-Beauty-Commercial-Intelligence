"""Observed catalog analytics and conservative, reciprocal product matching."""
from collections import defaultdict
import csv
from datetime import date
from difflib import SequenceMatcher
from math import isfinite
from statistics import correlation
from statistics import mean, median, quantiles

from .pipeline import FLAGS, normalize

def keyed(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    return groups

def eligible(row):
    return (row["currency"] == {"US": "USD", "CA": "CAD"}.get(row["market"])
            and row["market"] in {"US", "CA"} and row["price"] is not None and row["price"] > 0)

def identity(row):
    return tuple(normalize(row[k]) for k in ("brand", "name", "size", "variant"))

def match(left, right, comparable_ids=False):
    by_brand = keyed(right, lambda r: r["brand"])
    candidates = []
    for a in left:
        for b in by_brand[a["brand"]]:
            brand, name, size, variant = identity(a)
            comparable = (brand and name and size and identity(a) == identity(b)
                          and (variant is not None or (a["sku"] is None and b["sku"] is None)))
            same_sku = a["sku"] and a["sku"] == b["sku"] and a["product"] == b["product"]
            same_product = a["product"] == b["product"]
            if comparable:
                method = ("identifier_sku" if comparable_ids and same_sku else
                          "identifier_variant" if comparable_ids and same_product else "attributes")
            elif (comparable_ids and (same_sku or same_product)) or (
                    name and b["name"] and SequenceMatcher(None, name, normalize(b["name"])).ratio() >= .84):
                method = "manual_candidate"
            else:
                continue
            candidates.append((a, b, method))
    exact = [c for c in candidates if c[2] != "manual_candidate"]
    left_counts = keyed(exact, lambda c: (c[0]["id"], c[1]["snapshot"]))
    right_counts = keyed(exact, lambda c: (c[1]["id"], c[0]["snapshot"]))
    rank = {"identifier_sku": 0, "identifier_variant": 1, "attributes": 2}
    def top(group, method):
        scores = sorted(rank[c[2]] for c in group)
        return scores[0] == rank[method] and (len(scores) == 1 or scores[1] > scores[0])

    for a, b, method in candidates:
        accepted = (method != "manual_candidate" and a["snapshot"] and b["snapshot"]
                    and top(left_counts[a["id"], b["snapshot"]], method)
                    and top(right_counts[b["id"], a["snapshot"]], method))
        yield a, b, method, "accepted" if accepted else "manual_review"

def fx_for(snapshot, rates):
    if not snapshot:
        return None, None
    target = date.fromisoformat(snapshot)
    dated = [(abs((date.fromisoformat(day)-target).days), day, value)
             for day, value in rates.items() if isfinite(value) and value > 0]
    if dated and min(dated)[0] <= 4:
        _, day, value = min(dated)
        return day, value
    return None, None

def materialize(cursor, config):
    cursor.executescript("""
        CREATE VIEW catalog_snapshot AS SELECT f.*,s.vintage FROM fact_product_snapshot f JOIN source s ON f.source_id=s.id;
        CREATE VIEW quality_report AS SELECT vintage,member,field,issue,count FROM quality JOIN source ON source_id=id;
        CREATE VIEW duplicate_keys AS SELECT vintage,snapshot,market,product,sku,COUNT(*) AS records
        FROM fact_product_snapshot JOIN source ON source_id=source.id
        GROUP BY vintage,snapshot,market,product,sku HAVING COUNT(*)>1;
        CREATE VIEW review_summary AS SELECT product,COUNT(*) AS reviews,AVG(rating) AS mean_rating,
        SUM(sentiment=1) AS positive,SUM(sentiment=-1) AS negative,SUM(sentiment=0) AS neutral_or_unscored,COUNT(*)-COUNT(sentiment) AS missing_text
        FROM fact_review GROUP BY product;
        CREATE TABLE pricing (id INTEGER PRIMARY KEY,tier TEXT,category_median REAL, price_gap REAL,
        discount_depth REAL,premium_proxy REAL,price_heavy_proxy REAL);
        CREATE TABLE price_comparison (left_id INTEGER,right_id INTEGER,comparison TEXT,
        left_price REAL,right_native REAL,right_usd REAL,absolute_gap REAL,percent_gap REAL,
        fx_date TEXT,fx REAL,fx_low_gap REAL,fx_high_gap REAL,real_change REAL,
        left_tier TEXT,right_tier TEXT,right_tier_at_left_thresholds TEXT,left_promotion INTEGER,right_promotion INTEGER);
    """)
    rows = list(cursor.execute("SELECT f.*, vintage FROM fact_product_snapshot f JOIN source s ON f.source_id=s.id"))
    key = lambda r: tuple(r[k] for k in ("vintage","market","snapshot","product"))
    unique = []
    for group in keyed(rows, key).values():
        parent = [r for r in group if r["sku"] is None]
        if len(parent) == 1:
            unique.extend(parent)
        elif len(group) == 1:
            unique.extend(group)
    cohorts = keyed([r for r in unique if eligible(r)], lambda r: (r["market"],r["snapshot"],r["vintage"],r["category"]))
    tiers = {}
    boundaries = {}
    assign = lambda price, cuts: ("Entry","Core","Premium","Luxury")[sum(price > p for p in cuts)]
    for cohort, group in cohorts.items():
        prices = [r["price"] for r in group]
        midpoint = median(prices)
        cuts = quantiles(prices, n=4, method="inclusive") if len(prices) >= 4 else []
        boundaries[cohort] = cuts
        for r in group:
            price = r["price"]
            tier = assign(price, cuts) if cuts else "Insufficient cohort"
            tiers[r["id"]] = tier
            depth = 1-r["sale"]/price if r["sale"] is not None and r["sale"] <= price else None
            rank = (sum(p < price for p in prices) + .5*prices.count(price))/len(prices)
            exclusive = r["exclusive"]
            score = 100*(.8*rank+.2*exclusive) if exclusive is not None else None
            alternative = 100*(.95*rank+.05*exclusive) if exclusive is not None else None
            cursor.execute("INSERT INTO pricing VALUES (?,?,?,?,?,?,?)", (r["id"],tier,midpoint,price-midpoint,depth,score,alternative))
    cross_inputs = []
    for kind, left, right in [
        ("longitudinal", [r for r in rows if r["vintage"]=="historical" and r["market"]=="US"],
         [r for r in rows if r["vintage"]=="recent" and r["market"]=="US"]),
        ("cross_market", [r for r in rows if r["vintage"]=="recent" and r["market"]=="US"],
         [r for r in rows if r["vintage"]=="recent" and r["market"]=="CA"])]:
        for a,b,method,status in match(left,right,config.get("comparable_ids",False)):
            if status == "accepted" and kind == "cross_market" and a["snapshot"] != b["snapshot"]:
                status = "manual_review"
            cursor.execute("INSERT INTO bridge_product_match VALUES (?,?,?,?,?)", (a["id"],b["id"],kind,method,status))
            if status != "accepted" or not eligible(a) or not eligible(b):
                continue
            fx_date, fx = fx_for(b["snapshot"], config.get("fx_usd_per_cad",{})) if kind=="cross_market" else (None,1)
            converted = b["price"]*fx if fx else None
            delta = converted-a["price"] if converted is not None else None
            gap = delta/a["price"] if delta is not None else None
            cpi = config.get("cpi_us",{})
            old = cpi.get(a["snapshot"][:7],0)
            new = cpi.get(b["snapshot"][:7],0)
            real = (1+gap)*old/new-1 if kind=="longitudinal" and gap is not None and old>0 and new>0 else None
            cuts = boundaries.get((a["market"],a["snapshot"],a["vintage"],a["category"]),[])
            migration = assign(b["price"],cuts) if kind=="longitudinal" and cuts and a["category"]==b["category"] else None
            cursor.execute("INSERT INTO price_comparison VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (a["id"],b["id"],kind,a["price"],b["price"],converted,delta,gap,fx_date,fx,
                 (converted*.95/a["price"]-1) if fx_date else None,(converted*1.05/a["price"]-1) if fx_date else None,
                 real,tiers.get(a["id"]),tiers.get(b["id"]),migration,a["promotion"],b["promotion"]))
            if gap is not None:
                cross_inputs.append((kind,a,b,gap))
    cursor.execute("CREATE TABLE comparison_summary (comparison, left_date,right_date,dimension,segment,matched_records,median_gap)")
    for dim in ("brand","category","overall"):
        for k, group in keyed(cross_inputs,lambda t:(t[0],t[1]["snapshot"],t[2]["snapshot"],t[1][dim] if dim!="overall" else "All")).items():
            cursor.execute("INSERT INTO comparison_summary VALUES (?,?,?,?,?,?,?)",(*k[:3],dim,k[3],len(group),median(t[3] for t in group)))
    cursor.execute("CREATE TABLE match_coverage AS SELECT comparison,status,method,COUNT(*) AS candidate_pairs,COUNT(DISTINCT left_id) AS left_records,COUNT(DISTINCT right_id) AS right_records FROM bridge_product_match GROUP BY comparison,status,method")
    cursor.execute("CREATE TABLE commercial_kpi (vintage,market,snapshot,dimension,segment,products,brands,priced,mean_price,median_price,min_price,max_price,assortment_share,mean_rating,rated,engagement_total,engagement_known,metric,known,flagged,share)")
    for cohort, cohort_rows in keyed(unique,lambda r:(r["vintage"],r["market"],r["snapshot"])).items():
        for dim in ("overall","brand","category","subcategory","tier"):
            for label, group in keyed(cohort_rows,lambda r: ("All" if dim=="overall" else tiers.get(r["id"]) if dim=="tier" else r[dim])).items():
                prices = [r["price"] for r in group if eligible(r)]
                ratings = [r["rating"] for r in group if r["rating"] is not None]
                engagements = [r["engagement"] for r in group if r["engagement"] is not None]
                for f in FLAGS:
                    flags = [r[f] for r in group if r[f] is not None]
                    cursor.execute("INSERT INTO commercial_kpi VALUES ("+",".join(["?"]*21)+")",
                        (*cohort,dim,label,len(group),len({r["brand"] for r in group if r["brand"]}),len(prices),
                         mean(prices) if prices else None,median(prices) if prices else None,
                         min(prices,default=None),max(prices,default=None),len(group)/len(cohort_rows),
                         mean(ratings) if ratings else None,len(ratings),sum(engagements) if engagements else None,
                         len(engagements),f,len(flags),sum(flags),mean(flags) if flags else None))

    cursor.execute("""CREATE TABLE portfolio AS SELECT vintage,market,snapshot,brand,category,
               COUNT(*) AS products,AVG(CASE WHEN (market='US' AND currency='USD') OR (market='CA' AND currency='CAD') THEN price END) AS mean_price,AVG(rating) AS mean_rating,
               SUM(bestseller) AS bestsellers,COUNT(bestseller) AS bestseller_known,
               SUM(new_arrival) AS new_arrivals,COUNT(new_arrival) AS new_arrival_known,
               SUM(exclusive) AS exclusive_products,COUNT(exclusive) AS exclusive_known
               FROM fact_product_snapshot f JOIN source s ON f.source_id=s.id WHERE f.id IN (SELECT value FROM json_each(?))
               GROUP BY vintage,market,snapshot,brand,category""",
               ("[" + ",".join(str(r["id"]) for r in unique) + "]",))
    cursor.executescript("""
        CREATE VIEW sku_portfolio AS
        SELECT vintage,market,snapshot,brand,category,COUNT(DISTINCT json_array(product,sku)) AS skus,
        MIN(price) AS min_sku_price,MAX(price) AS max_sku_price
        FROM fact_sku_snapshot JOIN source ON source.id=source_id
        WHERE (market='US' AND currency='USD') OR (market='CA' AND currency='CAD')
        GROUP BY vintage,market,snapshot,brand,category;
        CREATE VIEW product_position AS SELECT f.id,s.vintage,f.market,f.snapshot,f.category,
            f.brand,f.price,f.rating,f.engagement,p.tier,p.premium_proxy,p.price_heavy_proxy
            FROM fact_product_snapshot f JOIN pricing p USING(id) JOIN source s ON s.id=f.source_id;
        CREATE TABLE category_diagnostics (
            market TEXT, snapshot TEXT, vintage TEXT, category TEXT, priced INTEGER,
            p25 REAL, p75 REAL, brand_hhi REAL, price_rating_n INTEGER, price_rating_r REAL,
            price_engagement_n INTEGER, price_engagement_r REAL);
    """)
    for cohort, group in cohorts.items():
        cuts = boundaries[cohort]
        brand_counts = keyed([r for r in group if r["brand"]],lambda r:r["brand"])
        known = sum(map(len,brand_counts.values()))
        concentration = sum((len(brands)/known)**2 for brands in brand_counts.values()) if known else None
        relationships = []
        for metric in ("rating","engagement"):
            pairs = [(r["price"],r[metric]) for r in group if r[metric] is not None]
            try:
                r_value = correlation(*zip(*pairs)) if len(pairs) >= 3 else None
            except ValueError:
                r_value = None
            relationships.extend((len(pairs),r_value))
        cursor.execute("INSERT INTO category_diagnostics VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                   (*cohort,len(group),cuts[0] if cuts else None,cuts[2] if cuts else None,
                    concentration,*relationships))

def export(cursor, target):
    for table in ("dim_brand","dim_category","dim_market","dim_date","dim_product","fact_product_snapshot","fact_sku_snapshot",
                  "pricing","commercial_kpi","comparison_summary","bridge_product_match","price_comparison",
                  "match_coverage","portfolio","sku_portfolio","product_position","category_diagnostics","review_summary","review_topic","fact_industry_benchmark","quality_report","duplicate_keys"):
        source = "catalog_snapshot" if table == "fact_product_snapshot" else table
        cursor.execute(f"SELECT * FROM {source}")
        with (target/f"{table}.csv").open("w", newline="", encoding="utf-8-sig") as out:
            writer = csv.writer(out)
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor)
