"""Aggregate independent C-2 EIA-only annual gates over the fixed 24 BA-years.

No downloader, no weather join, no output overwrite. Missing files are reported
as failures, not silently skipped. Writes a single reproducible JSON summary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from scripts.c2_eia930_year_coverage_gate import audit_file

BAS = ("AZPS", "BPAT", "CISO", "SRP")
YEARS = tuple(range(2020, 2026))


def inventory(root: Path, *, bas=BAS, years=YEARS) -> dict:
    reports = []
    for ba in bas:
        for year in years:
            p = root / "utc_start" / f"eia930_{ba}_{year}_start.csv"
            try:
                result = audit_file(p, year=year, ba=ba)
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                result = {"ba": ba, "year": year, "pass": False,
                          "error": f"{type(exc).__name__}: {exc}",
                          "status": "missing_or_unverified_source"}
            reports.append(result)
    total = len(reports)
    eligible = sum(r["pass"] for r in reports)
    return {"status": "EIA_only_annual_coverage_inventory_not_joint_ERA5_validation",
            "total_ba_years": total, "passing_ba_years": eligible,
            "failing_ba_years": total - eligible,
            "all_pass": eligible == total,
            "years": reports}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error("Output exists; refuse overwrite")
    result = inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"EIA annual coverage: {result['passing_ba_years']}/{result['total_ba_years']} passed; report {args.output}")
    if not result["all_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
