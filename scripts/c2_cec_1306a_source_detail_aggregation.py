#!/usr/bin/env python3
"""Normalize source-authenticated CEC 1306A-like DETAIL rows without inventing data.

Input is a researcher-defined normalized schema, NOT a claim that official
published CEC 1306A files have these fields or are publicly accessible.
The result is a candidate input for c2_cec_joint_geo_source_gate.py only.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


FIELDS = ("source_row_id", "year", "month", "cec_county_number", "udc_id",
          "sector", "customer_class", "rate_class", "naics", "gwh")
OUT = ("year", "month", "cec_county_number", "county_fips",
       "udc_id", "sector", "gwh")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def aggregate(detail, county_map, manifest):
    meta = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if meta.get("training_permitted") is not False or meta.get("research_only") is not True:
        raise ValueError("Source detail normalization must forbid training")
    inputs = {"detail": detail, "cec_county_crosswalk": county_map}
    for name, path in inputs.items():
        entry = meta.get("files", {}).get(name, {})
        if (not isinstance(entry.get("sha256"), str)
                or entry["sha256"] != sha(path)
                or not str(entry.get("source_release") or "").strip()):
            raise ValueError("Missing or changed source SHA or release: " + name)
    if meta.get("normalized_detail_schema_reviewed") is not True:
        raise ValueError("Original-to-normalized field lineage has not been reviewed")
    with Path(county_map).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not {"cec_county_number", "county_fips", "reviewed"} <= set(reader.fieldnames or []):
            raise ValueError("Missing county crosswalk fields")
        mapping = {}
        observed_fips = set()
        for r in reader:
            county = r["cec_county_number"].strip()
            fips = r["county_fips"].strip()
            if (not county.isdigit() or county != str(int(county))
                    or not 1 <= int(county) <= 58
                    or len(fips) != 5 or not fips.startswith("06")
                    or not fips.isdigit() or r["reviewed"] != "True"):
                raise ValueError("Unapproved or non-CA county-number mapping")
            if county in mapping or fips in observed_fips:
                raise ValueError("Nonunique reviewed county crosswalk")
            mapping[county] = fips
            observed_fips.add(fips)
    grouped = defaultdict(list)
    seen_ids = set()
    count = 0
    with Path(detail).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not set(FIELDS) <= set(reader.fieldnames or []):
            raise ValueError("Missing normalized raw-detail dimensions")
        for r in reader:
            rid = r["source_row_id"].strip()
            if not rid or rid in seen_ids:
                raise ValueError("Duplicate/blank original source-row identifier")
            seen_ids.add(rid)
            year, month = int(r["year"]), int(r["month"])
            if year not in range(2020, 2026) or month not in range(1, 13):
                raise ValueError("Invalid source date")
            county = r["cec_county_number"].strip()
            if county not in mapping:
                raise ValueError("Special/unmapped original CEC county number")
            dims = [r[x].strip() for x in
                    ("udc_id", "sector", "customer_class", "rate_class", "naics")]
            if any(not x for x in dims):
                raise ValueError("Undefined original filing category: cannot silently collapse")
            try:
                value = float(r["gwh"])
            except (ValueError, TypeError) as e:
                raise ValueError("Missing/non-numeric GWh cannot be treated as zero") from e
            if not math.isfinite(value) or value < 0:
                raise ValueError("Invalid original energy")
            key = (year, month, county, mapping[county], dims[0], dims[1])
            grouped[key].append(value)
            count += 1
    if not count:
        raise ValueError("Empty original source detail")
    totals = []
    for key, vals in sorted(grouped.items()):
        totals.append({**dict(zip(OUT[:6], map(str, key))),
                       "gwh": format(math.fsum(vals), ".12g")})
    original_total = math.fsum(x for values in grouped.values() for x in values)
    aggregated_total = math.fsum(float(x["gwh"]) for x in totals)
    if not math.isclose(original_total, aggregated_total, rel_tol=1e-10, abs_tol=1e-8):
        raise ValueError("Source GWh not conserved after aggregation")
    return totals, {
        "original_detail_rows": count,
        "normalized_month_county_udc_sector_rows": len(totals),
        "detail_gwh": original_total,
        "aggregated_gwh": aggregated_total,
        "conservation_verified": True,
        "source_detail_sha256": sha(detail),
        "source_county_crosswalk_sha256": sha(county_map),
        "actual_CEC_official_schema_authenticated_by_this_script": False,
        "historical_operational_BA_geography_approved": False,
        "hourly_load_geography_approved": False,
        "model_training_permitted": False,
    }


def main():
    p = argparse.ArgumentParser()
    for arg in ("detail", "county_map", "manifest", "out"):
        p.add_argument("--" + arg.replace("_", "-"), required=True, type=Path)
    a = p.parse_args()
    out = a.out
    if out.exists():
        raise FileExistsError("Refuse overwrite of independently audited normalization")
    rows, proof = aggregate(a.detail, a.county_map, a.manifest)
    out.mkdir(parents=True)
    with (out / "CEC_1306A_CANDIDATE_MONTHLY_COUNTY_UDC_SECTOR.csv").open(
            "w", newline="", encoding="utf-8") as stream:
        w = csv.DictWriter(stream, fieldnames=OUT)
        w.writeheader()
        w.writerows(rows)
    proof["normalized_csv_sha256"] = sha(
        out / "CEC_1306A_CANDIDATE_MONTHLY_COUNTY_UDC_SECTOR.csv")
    (out / "UNAPPROVED_1306A_AGGREGATION_MANIFEST.json").write_text(
        json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
