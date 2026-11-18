"""C-2 E2: fail-closed joint EIA-930 × weather BA-hour coverage gate.

Input is a *previously sourced and joined* CSV. This module does not download data,
impute observations, infer BA geography, or establish empirical prediction skill.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED = ("ba", "timestamp_utc", "demand_mw", "temperature_c")
DEFAULT_BAS = ("CISO", "AZPS", "BPAT", "SRP")
SPLITS = {"train": (2020, 2021, 2022), "validation": (2023,), "test": (2024, 2025)}


def utc_hour(value: str) -> datetime:
    if not value or not (value.endswith("Z") or value.endswith("+00:00")):
        raise ValueError("timestamp_utc must explicitly declare UTC (Z or +00:00)")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() != timedelta(0):
        raise ValueError("timestamp_utc must use UTC offset zero")
    if parsed.minute or parsed.second or parsed.microsecond:
        raise ValueError("timestamp_utc must be exactly hourly UTC interval-start")
    return parsed.astimezone(timezone.utc)


def finite_number(value: str, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric and nonblank") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def expected_hours(year: int) -> int:
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    return int((end - start).total_seconds() // 3600)


def audit(path: str | Path, bas=DEFAULT_BAS, completeness=0.98) -> dict:
    if not 0 < completeness <= 1:
        raise ValueError("completeness must be between 0 and 1")
    requested = set(bas)
    observed = defaultdict(set)
    invalid = defaultdict(int)
    duplicate = defaultdict(int)
    rows = defaultdict(int)
    example_errors = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            ba = (row["ba"] or "").strip()
            if ba not in requested:
                continue
            try:
                ts = utc_hour((row["timestamp_utc"] or "").strip())
            except ValueError as exc:
                # A row with no reliable UTC hour cannot be assigned to a year.
                raise ValueError(f"line {line_number}, BA {ba}: {exc}") from exc
            key = (ba, ts.year)
            rows[key] += 1
            if ts in observed[key]:
                duplicate[key] += 1
                if len(example_errors) < 10:
                    example_errors.append(f"duplicate: {ba} {ts.isoformat()} line {line_number}")
                continue
            observed[key].add(ts)
            try:
                demand = finite_number(row["demand_mw"], "demand_mw")
                finite_number(row["temperature_c"], "temperature_c")
                if demand < 0:
                    raise ValueError("demand_mw cannot be negative")
            except ValueError as exc:
                invalid[key] += 1
                if len(example_errors) < 10:
                    example_errors.append(f"{ba} {ts.isoformat()}: {exc}")

    years = sorted({*range(2020, 2026), *(year for _, year in rows)})
    table = []
    year_pass = {}
    for ba in sorted(requested):
        for year in years:
            key = (ba, year)
            unique = len(observed[key])
            good = unique - invalid[key]
            expected = expected_hours(year)
            coverage = good / expected
            passed = coverage >= completeness and duplicate[key] == 0 and invalid[key] == 0 and unique <= expected
            year_pass[key] = passed
            table.append({"ba": ba, "year": year, "expected_hours": expected,
                          "rows": rows[key], "unique_hours": unique, "valid_joint_hours": good,
                          "invalid_joint_rows": invalid[key], "duplicate_hours": duplicate[key],
                          "coverage": round(coverage, 6), "pass": passed})

    split_eligibility = {}
    for ba in sorted(requested):
        split_eligibility[ba] = {
            name: all(year_pass.get((ba, y), False) for y in ys)
            for name, ys in SPLITS.items()
        }
        split_eligibility[ba]["three_complete_annual_cycles"] = (
            sum(year_pass.get((ba, y), False) for y in years) >= 3
        )
        split_eligibility[ba]["predeclared_2020_2025_split"] = all(
            split_eligibility[ba][name] for name in SPLITS
        )

    return {"status": "coverage_audit_only_not_model_validation",
            "input": str(path), "required_columns": REQUIRED,
            "coverage_threshold": completeness, "yearly": table,
            "split_eligibility": split_eligibility,
            "errors_sample": example_errors,
            "caveats": [
                "This CSV is not verified by the audit as authentic EIA-930 or ERA5.",
                "Cross-source timestamps, weather geometry, demand semantics and revisions require external provenance.",
                "Passing coverage does not validate temporal leakage, forecasting skill, or climate attribution.",
            ]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Sourced, joined BA × UTC hour input CSV")
    parser.add_argument("--output", help="Write report JSON; otherwise print to stdout")
    parser.add_argument("--min-completeness", type=float, default=0.98)
    args = parser.parse_args()
    result = audit(args.csv, completeness=args.min_completeness)
    formatted = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(formatted + "\n", encoding="utf-8")
    else:
        print(formatted)


if __name__ == "__main__":
    main()
