#!/usr/bin/env python3
"""Rerun SHA-verified BPAT EIA-930 hourly extract from archived original ZIP."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

SOURCE_SHA = "4c61e2a2b587c580f50e28483542608a88e8fe3d54ed13141073353ea7eef916"
GZIP_SHA = "88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
ANNUAL = {2020: 8784, 2021: 8760, 2022: 8760, 2023: 8760, 2024: 8784, 2025: 8760}
NEST = "inputs/C2_2020_2025_72_Month_Original_Source_Archive.zip"
INNER = "C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"
COLUMNS = ("timestamp_utc_start", "EIA930_original_demand_mw",
           "EIA930_demand_missing", "EIA930_anomaly_candidate_not_confirmed")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main(source, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError("Do not overwrite a source evidence package")
    if digest(source.read_bytes()) != SOURCE_SHA:
        raise ValueError("Original ZIP SHA-256 differs from pinned source")
    with zipfile.ZipFile(source) as z:
        with zipfile.ZipFile(io.BytesIO(z.read(NEST))) as orig:
            gz = orig.read(INNER)
    if digest(gz) != GZIP_SHA:
        raise ValueError("Original source gzip SHA-256 mismatch")
    with gzip.GzipFile(fileobj=io.BytesIO(gz)) as f:
        source_rows = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", newline=""))
        rows = [{k: row[k] for k in COLUMNS} for row in source_rows if row["ba"] == "BPAT"]
    counts = Counter(int(row["timestamp_utc_start"][:4]) for row in rows)
    if dict(counts) != ANNUAL or len(rows) != 52608:
        raise ValueError("BPAT source reporting-year UTC hour count is not expected")
    if len({row["timestamp_utc_start"] for row in rows}) != len(rows):
        raise ValueError("Duplicated BPAT UTC source hour")
    if any(float(row["EIA930_original_demand_mw"]) <= 0
           or row["EIA930_demand_missing"] != "False"
           or row["EIA930_anomaly_candidate_not_confirmed"] != "False"
           for row in rows):
        raise ValueError("BPAT source has nonpositive or missing/anomaly candidate hour")
    destination.mkdir(parents=True)
    csv_path = destination / "BPAT_2020_2025_EIA930_AUTHENTIC_HOURLY_START_UTC.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    result = {"source_original_sha256": SOURCE_SHA, "source_hourly_gzip_sha256": GZIP_SHA,
              "output_csv_sha256": digest(csv_path.read_bytes()),
              "annual_UTC_hour_counts": dict(sorted(counts.items())),
              "BPAT_observed_hours": len(rows), "FERC714_hourly_acquired": False,
              "EIA_FERC_source_area_equivalence_verified": False,
              "model_training_permitted": False}
    (destination/"MANIFEST.json").write_text(json.dumps(result, indent=2)+"\n")
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source-zip", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(main(args.source_zip, args.out), indent=2))
