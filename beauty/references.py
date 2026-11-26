"""Import documented external observations and validate their analytical units."""
import csv
from datetime import date
from math import isfinite
from urllib.parse import urlsplit

FIELDS = ("organization title publication_date measurement_period geography metric value units "
          "url access_date limitations").split()
SERIES = {
    "fx_usd_per_cad": ("Canada", "USD per CAD"),
    "cpi_us": ("US", "index (1982-84=100)"),
}

def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value > 0

def period(metric, value):
    day = date.fromisoformat(value + "-01" if metric == "cpi_us" else value)
    canonical = day.isoformat()
    if value != (canonical[:7] if metric == "cpi_us" else canonical):
        raise ValueError(f"Invalid period for {metric}: {value!r}")
    if metric == "fx_usd_per_cad" and day.weekday() >= 5:
        raise ValueError("FX observation must be dated on a business day")
    return day

def load(cursor, path, config):
    reference = {metric: dict(config.get(metric, {})) for metric in SERIES}
    for metric, entries in reference.items():
        for day, value in entries.items():
            period(metric, day)
            if not positive(value):
                raise ValueError(f"{metric} requires positive finite values")
    seen = set()
    if path:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames != FIELDS:
                raise ValueError("Benchmark headers do not match template")
            for line, record in enumerate(reader, 2):
                try:
                    row = {key: (record.get(key) or "").strip() for key in FIELDS}
                    url = urlsplit(row["url"])
                    if None in record or not all(row.values()) or url.scheme != "https" or not url.hostname or url.username:
                        raise ValueError("Required fields and a public HTTPS source URL are required")
                    publication = date.fromisoformat(row["publication_date"])
                    access = date.fromisoformat(row["access_date"])
                    value = float(row["value"])
                    if publication > access or not isfinite(value):
                        raise ValueError("Access must follow publication and values must be finite")
                    metric, measurement = row["metric"], row["measurement_period"]
                    if metric in SERIES:
                        day = period(metric, measurement)
                        if (row["geography"], row["units"]) != SERIES[metric] or not positive(value) or day > publication:
                            raise ValueError(f"Invalid geography, units, value, or publication date for {metric}")
                        key = (metric, measurement)
                        if key in seen or (measurement in reference[metric] and reference[metric][measurement] != value):
                            raise ValueError(f"Duplicate or conflicting observation for {metric} {measurement}")
                        seen.add(key)
                        reference[metric][measurement] = value
                    row["publication_date"], row["access_date"], row["value"] = publication.isoformat(), access.isoformat(), value
                    cursor.execute("INSERT INTO fact_industry_benchmark VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                   [row[key] for key in FIELDS])
                except ValueError as error:
                    raise ValueError(f"{path.name}:{line}: {error}") from error
    return reference
