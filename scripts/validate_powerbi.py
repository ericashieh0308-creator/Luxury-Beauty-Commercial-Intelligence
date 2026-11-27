"""Check the PBIP, its bindings, generated data, and optionally Microsoft schemas."""
import argparse
from collections import Counter
import csv
from datetime import date
from itertools import combinations
import json
from math import isclose, isfinite
from pathlib import Path
import re
from urllib.error import URLError
from urllib.request import urlopen

from beauty.finance import Drivers, SCENARIOS, channels, forecast, promotion, variance

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "dashboard/powerbi"
DECLARATION = re.compile(r"^\t(column|measure) (?:'([^']+)'|([\w-]+))(?= |=|\n|$)", re.M)
DAX_REF = re.compile(r"(?:(?P<table>\b\w+|'[^']+')\s*)?\[(?P<field>[^]]+)\]")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def project_paths():
    pbip = next(PROJECT.glob("*.pbip"))
    relative_report, = (artifact["report"]["path"] for artifact in read_json(pbip)["artifacts"] if "report" in artifact)
    report = (pbip.parent / relative_report).resolve()
    require(report.parent == PROJECT.resolve(), "PBIP report must reference a sibling folder")
    relative_model = read_json(report/"definition.pbir")["datasetReference"]["byPath"]["path"]
    model = (report / relative_model).resolve()
    require(model.parent == PROJECT.resolve(), "PBIR model must reference a sibling folder")
    read_json(model/"definition.pbism")
    for path in (report/"definition").rglob("*.json"):
        read_json(path)
    return report, model/"definition"


def validate_model(model, demo):
    fields = {}
    texts = {}
    for path in (model / "tables").glob("*.tmdl"):
        text = path.read_text(encoding="utf-8-sig")
        name = path.stem
        require(text.startswith(f"table {name}\n"), f"{path}: table declaration mismatch")
        entries = [(a, b or c) for a, b, c in DECLARATION.findall(text)]
        require(len(entries) == len(set(entries)), f"{name}: duplicate fields")
        fields[name] = {k: {v for field_type, v in entries if field_type == k} for k in ("column", "measure")}
        texts[name] = text
    model_text = (model/"model.tmdl").read_text(encoding="utf-8-sig")
    require("culture: en-US" in model_text and "sourceQueryCulture: en-US" in model_text,
            "Model and query cultures must be en-US")
    require("__PBI_TimeIntelligenceEnabled = 0" in model_text, "Disable automatic date hierarchies")
    refs = re.findall(r"^ref table (.+)$", model_text, re.M)
    require(Counter(refs) == Counter(fields.keys()), "Model table references differ from table definitions")
    tags = [t for text in texts.values() for t in re.findall(r"^\s*lineageTag: (.+)$", text, re.M)]
    require(len(tags) == len(set(tags)), "Duplicated lineage tags")
    measures = {m for f in fields.values() for m in f["measure"]}
    require(sum(len(x["measure"]) for x in fields.values()) == len(measures), "Measure names must be unique")
    for name, text in texts.items():
        require(len(re.findall(r"^\s*dataType: dateTime$", text, re.M)) ==
                len(re.findall(r"^\s*dataType: dateTime\n\s*formatString: yyyy-MM-dd$", text, re.M)),
                f"{name}: date columns need an explicit ISO date format")
        require("variation Variation" not in text, f"{name}: automatic date variation is still present")
        if name.startswith("fact_simulated"):
            require('formatString: "$"' not in text, f"{name}: use an explicit USD currency label")
        for line in re.findall(r"^\tmeasure .*? = (.+)$", text, re.M):
            for match in DAX_REF.finditer(line):
                table, prop = match.group("table", "field")
                if table:
                    require(prop in fields[table.strip("'")]["column"] or prop in fields[table.strip("'")]["measure"],
                            f"{name}: unknown DAX reference {table}[{prop}]")
                else:
                    require(prop in measures, f"{name}: unknown DAX measure [{prop}]")
        sources = re.findall(r"^\t\tsourceColumn: (\w+)$", text, re.M)
        candidates = list(demo.glob(f"*/{name}.csv"))
        if candidates:
            require(len(candidates) == 1, f"{name}: ambiguous demo source")
            with candidates[0].open(encoding="utf-8-sig", newline="") as fp:
                reader = csv.DictReader(fp)
                headers = set(reader.fieldnames or ())
                rows = list(reader)
            require(rows or name == "price_comparison", f"{name}: header-only input in the public demo")
            if name in {"dim_market", "dim_category", "comparison_coverage"}:
                key = {"dim_market": "market", "dim_category": "category", "comparison_coverage": "comparison"}[name]
                values = [row[key] for row in rows]
                require(all(values) and len(values)==len(set(values)), f"{name}: blank or duplicate dimension keys")
            catalog = candidates[0].parent.name == "catalog"
            if catalog and {"market","snapshot","vintage"} <= headers:
                headers.add("cohort_key")
            require(set(sources) <= headers, f"{name}: missing CSV headers {set(sources)-headers}")
            for column, kind in re.findall(r"^\tcolumn (\w+)\n\t\tdataType: (\w+)", text, re.M):
                values = [r[column] for r in rows if r.get(column)]
                if kind == "int64":
                    require(all(re.fullmatch(r"-?[0-9]+", value) for value in values), f"{name}.{column}: expected whole numbers")
                elif kind == "double":
                    require(all(isfinite(float(value)) for value in values), f"{name}.{column}: expected finite numbers")
                elif kind == "dateTime":
                    for value in values:
                        date.fromisoformat(value)
        elif f"PortfolioTables[{name}]" in text:
            require(False, f"{name}: missing demo CSV; run python -m beauty.demo")
    expressions = (model/"expressions.tmdl").read_text(encoding="utf-8-sig")
    require('expression DemoRoot = "" meta' in expressions, "DemoRoot must be blank in source control")
    require(not re.search(r"(?i)[a-z]:[\\/]", expressions), "Named expressions contain a machine-specific path")
    rels = (model/"relationships.tmdl").read_text(encoding="utf-8-sig")
    keys = re.findall(r"relationship (.+)", rels)
    require(len(keys)==len(set(keys)), "Duplicate relationship IDs")
    for table, column in re.findall(r"(?:from|to)Column: ([^.\s]+)\.([^\s]+)", rels):
        require(column in fields[table]["column"], f"Unknown relationship field {table}.{column}")
    return fields


def validate_bindings(node, fields, aliases=None):
    if isinstance(node, dict):
        aliases = aliases or {}
        if "From" in node:
            aliases = {**aliases, **{item["Name"]: item["Entity"] for item in node["From"]}}
        for key, value in node.items():
            if key in {"Column", "Measure"} and isinstance(value, dict) and "Property" in value:
                source = value["Expression"]["SourceRef"]
                table = source["Entity"] if "Entity" in source else aliases[source["Source"]]
                require(value["Property"] in fields[table][key.lower()],
                        f"Visual references unknown {table}.{value['Property']}")
            validate_bindings(value, fields, aliases)
    elif isinstance(node, list):
        for item in node:
            validate_bindings(item, fields, aliases)


def validate_layout(report, fields):
    pages = report/"definition/pages"
    ordered = read_json(pages/"pages.json")
    page_ids = ordered["pageOrder"]
    require(len(page_ids)==len(set(page_ids))==10, "Expected ten unique pages")
    require(set(page_ids)=={p.name for p in pages.iterdir() if p.is_dir()}, "Page order and page folders differ")
    require(ordered["activePageName"] in page_ids, "Active page missing")
    visuals_seen = set()
    titles = []
    for page_id in page_ids:
        folder = pages/page_id
        page = read_json(folder/"page.json")
        require(page["name"]==page_id and page["width"]*9==page["height"]*16, f"{page_id}: ID or canvas invalid")
        visuals = []
        for path in sorted(folder.glob("visuals/*/visual.json")):
            visual = read_json(path)
            name = visual["name"]
            require(name==path.parent.name and name not in visuals_seen, f"Visual ID collision: {name}")
            visuals_seen.add(name)
            box = visual["position"]
            x,y,w,h = (box[k] for k in ("x","y","width","height"))
            require(0<=x<x+w<=page["width"] and 0<=y<y+h<=page["height"], f"Out of bounds: {name}")
            validate_bindings(visual, fields)
            context = visual["visual"]
            if context["visualType"] == "slicer":
                props = context["objects"]["data"][0]["properties"]
                require(props["mode"]["expr"]["Literal"]["Value"] == "'Dropdown'", f"{name}: expected dropdown slicer")
                require(h >= 100, f"{name}: slicer height too small")
            visuals.append((name,(x,y,x+w,y+h),box["tabOrder"]))
        require(visuals and len({v[2] for v in visuals})==len(visuals), f"{page_id}: empty page or duplicate tab order")
        for (a,(x1,y1,x2,y2),_), (b,(u1,v1,u2,v2),_) in combinations(visuals,2):
            require(min(x2,u2)<=max(x1,u1) or min(y2,v2)<=max(y1,v1), f"Overlap: {a} and {b}")
        titles.append((page["displayName"],len(visuals)))
    return titles


def validate_finance(demo):
    def read_rows(table):
        with (demo/"finance"/f"{table}.csv").open(encoding="utf-8-sig", newline="") as fp:
            return list(csv.DictReader(fp))
    def equivalent(row, expected, scope):
        require(row["evidence"]=="SIMULATED", f"{scope}: evidence label mismatch")
        for key, value in expected.items():
            raw = row[key]
            matches = isclose(float(raw),value,abs_tol=1e-8) if isinstance(value,(int,float)) and raw else raw == ("" if value is None else str(value))
            require(matches, f"{scope}: {key} mismatch")

    finance = read_rows("fact_simulated_finance")
    forecast_keys = {(r["scenario"], int(r["month"])):r for r in finance}
    require(len(finance)==len(forecast_keys)==36, "Forecast grain mismatch")
    d = Drivers()
    expected = {scenario:list(forecast(d,*drivers)) for scenario,drivers in SCENARIOS.items()}
    sku = read_rows("fact_simulated_sku")
    sku_index = {(r["scenario"],int(r["month"]),r["sku"]):r for r in sku}
    require(len(sku)==len(sku_index)==72, "SKU grain mismatch")
    for scenario, rows in expected.items():
        actual = [forecast_keys[scenario, month] for month,_,_ in rows]
        for (month,pnl,detail), row in zip(rows,actual,strict=True):
            equivalent(row,pnl,f"{scenario}/{month}")
            for sku_name, expected_sku in detail.items():
                equivalent(sku_index[scenario,month,sku_name],expected_sku,f"{scenario}/{month}/{sku_name}")
        for margin, profit in (("gross margin", "gross_profit"), ("operating margin", "operating_profit")):
            actual_margin = sum(float(r[profit]) for r in actual)/sum(float(r["net_revenue"]) for r in actual)
            expected_margin = sum(r[profit] for _,r,_ in rows)/sum(r["net_revenue"] for _,r,_ in rows)
            require(isclose(actual_margin,expected_margin), f"{scenario}: weighted {margin} mismatch")
    channel_rows = read_rows("fact_simulated_channel")
    require(len(channel_rows)==len(channels(d)), "Channel grain mismatch")
    for row in channel_rows:
        equivalent(row,channels(d)[row["channel"]],row["channel"])
    variance_rows = read_rows("fact_simulated_variance")
    v_index = {(int(r["month"]),r["metric"]):r for r in variance_rows}
    require(len(variance_rows)==len(v_index)==60, "Variance grain mismatch")
    ytd = Counter()
    for (month,budget,_),(_,bull,_) in zip(expected["Base"],expected["Bull"],strict=True):
        for metric,(delta,pct,status) in variance(budget,bull).items():
            ytd[metric] += delta
            equivalent(v_index[month,metric],{"budget":budget[metric],"simulated_actual":bull[metric],
                "variance":delta,"variance_pct":pct,"direction":status,"ytd_variance":ytd[metric]},f"variance/{month}/{metric}")
    pvm = read_rows("fact_simulated_pvm")
    require(len(pvm)==len({row["month"] for row in pvm})==12, "PVM monthly grain mismatch")
    for row in pvm:
        month = int(row["month"])
        delta = expected["Bull"][month-1][1]["net_revenue"]-expected["Base"][month-1][1]["net_revenue"]
        equivalent(row,{"total":delta,"residual":0},f"PVM/{month}")
        bridge = sum(float(row[k]) for k in ("price","volume","mix","new","removed"))
        require(isclose(bridge,delta,abs_tol=1e-8), f"PVM/{month}: components do not reconcile")
    promotions = read_rows("fact_simulated_promotion")
    require(len(promotions)==len({(r["discount"],r["uplift"]) for r in promotions})==35, "Promotion grain mismatch")
    for row in promotions:
        expected_promo = {key:value for key,value in promotion(d,float(row["discount"]),float(row["uplift"]),1500).items()
                          if key not in {"before","after"}}
        equivalent(row,expected_promo,f"promotion/{row['discount']}/{row['uplift']}")


def validate_schemas(report):
    from jsonschema import Draft7Validator
    from jsonschema.validators import validator_for
    from referencing import Registry, Resource
    from referencing.exceptions import Unretrievable
    from referencing.jsonschema import DRAFT202012

    def retrieve(uri):
        require(uri.startswith(("https://developer.microsoft.com/", "https://raw.githubusercontent.com/microsoft/")),
                f"Unexpected schema URL {uri}")
        with urlopen(uri, timeout=20) as stream:
            return Resource.from_contents(json.load(stream), default_specification=DRAFT202012)

    theme = read_json(PROJECT/"theme.json")
    with urlopen(theme["$schema"], timeout=20) as stream:
        schema = json.load(stream)
    Draft7Validator(schema).validate(theme)
    registered = next((report/"StaticResources/RegisteredResources").glob("*.json"))
    Draft7Validator(schema).validate(read_json(registered))
    print("Official theme schema passed for source and registered theme.", flush=True)

    registry = Registry(retrieve=retrieve)
    paths = sorted((report/"definition").rglob("*.json")) + list(PROJECT.glob("*.pbip")) + [report/"definition.pbir"]
    validated = 0
    for path in paths:
        document = read_json(path)
        if "$schema" in document:
            uri = document["$schema"]
            try:
                resource = registry.get_or_retrieve(uri)
                registry = resource.registry.with_resource(uri, resource.value)
                schema = resource.value.contents
                validator_for(schema)(schema, registry=registry).validate(document)
            except Unretrievable as error:
                raise ValueError(f"Microsoft PBIR schema unavailable for {path.name}: {uri} ({error.__cause__})") from error
            validated += 1
    return validated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", type=Path, default=ROOT/"output/demo")
    parser.add_argument("--schemas", action="store_true", help="Fetch declared JSON schemas and fail on unavailable schemas")
    args = parser.parse_args()
    report, model = project_paths()
    fields = validate_model(model,args.demo)
    pages = validate_layout(report,fields)
    validate_finance(args.demo)
    print("\n".join(f"{title}: {count} visuals" for title,count in pages))
    print(f"{len(fields)} tables, {sum(len(f['measure']) for f in fields.values())} measures, "
          f"{sum(count for _,count in pages)} visuals. Local structural and finance checks passed.")
    if args.schemas:
        try:
            print(f"Official PBIR schema check completed for {validate_schemas(report)} JSON files.")
        except (URLError, ValueError) as error:
            parser.exit(1, f"Schema validation incomplete: {error}\n")


if __name__ == "__main__":
    main()
