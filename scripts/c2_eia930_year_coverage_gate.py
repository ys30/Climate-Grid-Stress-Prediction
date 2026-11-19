"""Strict EIA-930-only UTC interval-start coverage audit before ERA5 joins.

Input: one BA/year converted CSV and SHA manifest from
scripts/c2_eia930_he_to_utc_start.py. This does not establish source
measurement accuracy or forecast skill, and does not impute missing hours.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.c2_e2_joint_coverage_gate import utc_hour, expected_hours


def audit_file(path: str | Path, *, year: int, ba: str, min_coverage: float = 0.98) -> dict:
    source = Path(path)
    if not 0 < min_coverage <= 1:
        raise ValueError("min_coverage must be in (0, 1]")
    if not 2020 <= year <= 2025:
        raise ValueError("Only registered 2020-2025 cohort years supported")
    manifest_path = source.with_suffix(".manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError("Converted-data manifest required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    file_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if manifest.get("sha256_csv") != file_hash:
        raise ValueError("Converted CSV does not match SHA-256 manifest")
    if manifest.get("source_kind") != "derived_from_official_EIA_930_API":
        raise ValueError("Source lineage is not verified as EIA-930 intake")
    if manifest.get("target_year") != year:
        raise ValueError("Manifest target year differs from selected year")
    if manifest.get("clock_conversion") != "UTC_hour_ending_minus_one_hour":
        raise ValueError("EIA hour-ending conversion proof missing")
    actual = set()
    duplicate = 0
    invalid = 0
    out_of_period = 0
    wrong_ba = 0
    source_he_mismatch = 0
    rows = 0
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = {"ba", "timestamp_utc", "demand_mw", "original_source_he_utc"}
        if not columns.issubset(reader.fieldnames or ()):
            raise ValueError(f"Missing columns: {sorted(columns-set(reader.fieldnames or []))}")
        for record in reader:
            rows += 1
            ts = utc_hour(record["timestamp_utc"])
            if record["ba"] != ba:
                wrong_ba += 1
            if ts < start or ts >= end:
                out_of_period += 1
            if ts in actual:
                duplicate += 1
            actual.add(ts)
            try:
                value = float(record["demand_mw"])
                if not math.isfinite(value) or value < 0:
                    invalid += 1
            except (TypeError, ValueError):
                invalid += 1
            try:
                from scripts.c2_eia930_he_to_utc_start import he_to_start
                if he_to_start(record["original_source_he_utc"]) != ts:
                    source_he_mismatch += 1
            except (TypeError, ValueError):
                source_he_mismatch += 1
    expected = expected_hours(year)
    present = sum(1 for ts in actual if start <= ts < end)
    missing = expected - present
    # Source timestamps may exist even where EIA reported a null demand.
    # Do not report all present timestamps as valid measured-demand coverage.
    valid = max(0, present - invalid)
    coverage = valid / expected
    source_hour_coverage = present / expected
    # Even when coverage >= threshold, anomalies and null values fail closed.
    passed = (coverage >= min_coverage and missing >= 0 and duplicate == 0
              and invalid == 0 and out_of_period == 0 and wrong_ba == 0
              and source_he_mismatch == 0 and rows == len(actual))
    return {
        "status": "EIA_only_coverage_audit_not_ERA5_or_prediction_validation",
        "ba": ba, "year": year, "source_sha256": file_hash,
        "expected_hours": expected, "rows": rows, "unique_in_year": present,
        "missing_hours": missing, "missing_demand_rows": invalid,
        "valid_demand_hours": valid, "source_hour_coverage": round(source_hour_coverage, 8),
        "duplicate_hours": duplicate, "invalid_rows": invalid,
        "out_of_period_rows": out_of_period, "wrong_ba_rows": wrong_ba,
        "source_he_mismatch_rows": source_he_mismatch,
        "coverage": round(coverage, 8), "coverage_threshold": min_coverage,
        "pass": passed,
        "caveat": "Passing year completeness does not validate ERA5 matching or EIA measurement semantics"
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--ba", required=True)
    p.add_argument("--min-coverage", type=float, default=0.98)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = audit_file(args.csv, year=args.year, ba=args.ba,
                        min_coverage=args.min_coverage)
    result = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            p.error("Audit report exists; refuse overwrite")
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    if not report["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
