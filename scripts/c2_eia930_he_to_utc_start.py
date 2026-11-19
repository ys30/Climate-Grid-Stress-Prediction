"""Convert EIA-930 raw UTC hour-ending (HE) labels to UTC interval starts.

Authoritative source: https://www.eia.gov/electricity/930-content/about.html
An EIA hourly reading labeled 01:00 covers [00:00, 01:00).
This script ONLY accepts raw CSV produced by c2_eia930_raw_api_intake.py.
It does not fill gaps, assert BA geographic coverage, or join ERA5 weather.

IMPORTANT: For a complete calendar year of UTC interval-start hours, source
hour-ending labels must include Jan 1 01:00 through NEXT Jan 1 00:00.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE_COLUMNS = ("ba", "source_period_utc", "measurement_type",
                  "reported_demand_mw", "source")
SOURCE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}(?::00(?::00)?)?(?:Z)?$")
HOUR = timedelta(hours=1)


def parse_source_he(label: str) -> datetime:
    """Strict UTC HE source timestamp; no local timezone or fractional hours."""
    if not isinstance(label, str) or not SOURCE_PATTERN.fullmatch(label):
        raise ValueError("EIA source period must be YYYY-MM-DDTHH, optionally :00[:00] or Z")
    naive = label.removesuffix("Z")
    timestamp = datetime.fromisoformat(naive).replace(tzinfo=timezone.utc)
    if timestamp.minute or timestamp.second or timestamp.microsecond:
        raise ValueError("non-hourly EIA source HE timestamp")
    return timestamp


def he_to_start(label: str) -> datetime:
    return parse_source_he(label) - HOUR


def convert(raw_csv: str | Path, output_csv: str | Path, *, target_year: int | None = None) -> dict:
    raw = Path(raw_csv)
    target = Path(output_csv)
    if target.exists() or target.with_suffix(".manifest.json").exists():
        raise FileExistsError("Refuse to overwrite prior processed data or manifest")
    if raw.resolve() == target.resolve():
        raise ValueError("Input and output must differ")
    source_manifest = raw.with_suffix(".manifest.json")
    if not source_manifest.exists():
        raise FileNotFoundError("Pinned raw intake manifest is required")
    provenance = json.loads(source_manifest.read_text(encoding="utf-8"))
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    if provenance.get("sha256_csv") != digest or provenance.get("clock_status") != "source_label_unconverted":
        raise ValueError("Raw CSV hash or unconverted EIA source status does not match manifest")
    if provenance.get("source_kind") != "official_EIA_930_API":
        raise ValueError("Cannot assume EIA HE convention for a different source")
    if target_year is not None and not 2019 <= target_year <= 2026:
        raise ValueError("target_year outside preregistered intake year bounds")
    output = []
    source_null_demand = 0
    source_invalid_numeric = 0
    unique = set()
    with raw.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not set(SOURCE_COLUMNS).issubset(reader.fieldnames or ()):
            raise ValueError("Missing expected raw EIA source columns")
        for line, record in enumerate(reader, 2):
            ba = record["ba"]
            if ba != provenance["ba"] or record["measurement_type"] != "D":
                raise ValueError(f"BA / demand type mismatch on source line {line}")
            ts = he_to_start(record["source_period_utc"])
            if target_year is not None and ts.year != target_year:
                continue
            key = (ba, ts)
            if key in unique:
                raise ValueError(f"duplicate BA and UTC interval-start at line {line}")
            unique.add(key)
            original = record["reported_demand_mw"]
            if original is None or original == "":
                source_null_demand += 1
                value = ""
            else:
                try:
                    demand = float(original)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"invalid demand on line {line}") from exc
                if not math.isfinite(demand) or demand < 0:
                    # Retain source anomaly so downstream annual QA can report
                    # its timestamp and explicitly deny normal eligibility.
                    source_invalid_numeric += 1
                value = original
            output.append({"ba": ba,
                           "timestamp_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "demand_mw": value,
                           "original_source_he_utc": record["source_period_utc"]})
    if not output:
        raise ValueError("No usable source hours after year filter")
    output.sort(key=lambda r: (r["ba"], r["timestamp_utc"]))
    # Do not make a completeness claim. A separate coverage gate is mandatory.
    manifest = {"source_kind": "derived_from_official_EIA_930_API",
                "input_sha256": digest, "target_year": target_year,
                "clock_conversion": "UTC_hour_ending_minus_one_hour",
                "reference": "https://www.eia.gov/electricity/930-content/about.html",
                "row_count": len(output), "source_null_demand_rows": source_null_demand,
                "source_invalid_numeric_rows": source_invalid_numeric,
                "source_provenance": str(source_manifest),
                "claim_status": "HE_clock_transformed_only_no_joint_weather_or_skill"}
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".partial")
    if tmp.exists():
        raise FileExistsError("Stale partial output requires manual inspection")
    try:
        with tmp.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(output[0]))
            writer.writeheader()
            writer.writerows(output)
        manifest["sha256_csv"] = hashlib.sha256(tmp.read_bytes()).hexdigest()
        tmp.replace(target)
        target.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                                        encoding="utf-8")
    finally:
        if tmp.exists():
            tmp.unlink()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--year", type=int, help="Select interval-start UTC calendar year")
    args = parser.parse_args()
    print(json.dumps(convert(args.raw_csv, args.output_csv, target_year=args.year), indent=2))


if __name__ == "__main__":
    main()
