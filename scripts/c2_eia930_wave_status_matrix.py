#!/usr/bin/env python3
"""Reconcile published EIA-930 Wave 1–3 verification metadata.

Source-only evidence. No EIA raw files, hourly ERA5 joins, or model fitting.
"""
import argparse
import csv
import json
from pathlib import Path

BAS = ("CISO", "AZPS", "BPAT", "SRP")
YEARS = tuple(range(2020, 2026))

def reconcile(documents):
    observed = {}
    for document in documents:
        if not isinstance(document.get("cohorts"), list):
            raise ValueError("Missing cohorts array")
        for row in document["cohorts"]:
            key = (row["ba"], int(row["year"]))
            if key in observed:
                raise ValueError(f"BA-year claimed by multiple sources: {key}")
            observed[key] = (row, document)
    output = []
    for ba in BAS:
        for year in YEARS:
            value = observed.get((ba, year))
            if value is None:
                status = "unlisted_in_status_files"
                row, source = {}, {}
            else:
                row, source = value
                status = "sha_and_annual_gate_verified" if (
                    row.get("gate_pass") is True and
                    row.get("status") == "artifact_hash_and_annual_gate_pass" and
                    row.get("csv_sha256") and row.get("raw_sha256")
                ) else row.get("status", "not_verified")
            output.append({
                "ba": ba, "year": year, "source_status": status,
                "source_verified": status == "sha_and_annual_gate_verified",
                "valid_demand_hours": row.get("valid_demand_hours"),
                "expected_hours": row.get("expected_hours"),
                "missing_demand_rows": row.get("missing_demand_rows"),
                "artifact_id": row.get("artifact_id"),
                "source_run_id": source.get("run_id"),
                "raw_sha256": row.get("raw_sha256"),
                "csv_sha256": row.get("csv_sha256"),
                "era5_join_verified": False,
                "model_training_permitted": False
            })
    return output

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path, help="Saved Wave 1–3 verified status JSON files")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    docs = [json.loads(p.read_text(encoding="utf-8")) for p in args.files]
    rows = reconcile(docs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    n = sum(r["source_verified"] for r in rows)
    print(f"{n}/{len(rows)} BA-years source-verified; ERA5 joint gate remains BLOCKED")

if __name__ == "__main__":
    main()
