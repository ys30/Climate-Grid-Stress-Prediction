"""C-2 explicit 4-BA × year EIA-930 intake orchestration.

Runs only when invoked manually with EIA_API_KEY. Never embeds API secrets or
commits source data; does not assert coverage or make modeling-ready panel.
Each BA/year is independently source-pinned. Aborts on any failure.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from scripts.c2_eia930_raw_api_intake import ALLOWED_BAS, collect, save
from scripts.c2_eia930_he_to_utc_start import convert


def run(outdir: Path, bas: tuple[str, ...], years: tuple[int, ...], key: str,
        *, dry_run: bool = False) -> dict:
    if not key and not dry_run:
        raise ValueError("EIA_API_KEY required; no unauthenticated or simulated retrieval")
    if not bas or not years or len(set(bas)) != len(bas) or len(set(years)) != len(years):
        raise ValueError("BA/year list must be nonempty and unique")
    if any(ba not in ALLOWED_BAS for ba in bas):
        raise ValueError("Unknown balancing authority")
    if any(y not in range(2020, 2026) for y in years):
        raise ValueError("Research inventory restricted to 2020–2025")
    jobs = []
    for ba in bas:
        for year in years:
            raw = outdir / "raw" / f"eia930_{ba}_{year}_he.csv"
            converted = outdir / "utc_start" / f"eia930_{ba}_{year}_start.csv"
            # Preflight all paths to avoid partial campaign caused by existing files.
            jobs.append({"ba": ba, "year": year, "raw": raw, "converted": converted})
    if not dry_run:
        for job in jobs:
            for p in (job["raw"], job["raw"].with_suffix(".manifest.json"),
                      job["converted"], job["converted"].with_suffix(".manifest.json")):
                if p.exists():
                    raise FileExistsError(f"Existing output; start a new vintage directory: {p}")
    planned = [{"ba": j["ba"], "year": j["year"], "raw": str(j["raw"]),
                "utc_start": str(j["converted"])} for j in jobs]
    if dry_run:
        return {"status": "dry_run_no_network_no_data", "jobs": planned}
    completed = []
    for job in jobs:
        ba, year = job["ba"], job["year"]
        start, end = f"{year}-01-01T00", f"{year + 1}-01-01T00"
        rows = collect(key, ba, start, end)
        raw_manifest = save(rows, job["raw"], ba=ba, start=start, end=end)
        time_manifest = convert(job["raw"], job["converted"], target_year=year)
        completed.append({"ba": ba, "year": year,
                          "raw_sha256": raw_manifest["sha256_csv"],
                          "clocked_sha256": time_manifest["sha256_csv"],
                          "raw_rows": raw_manifest["row_count"],
                          "clocked_rows": time_manifest["row_count"]})
    return {"status": "source_retrieval_and_HE_conversion_only",
            "completed": completed,
            "not_established": ["year completeness", "ERA5 matching", "forecast model skill"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--bas", nargs="+", default=sorted(ALLOWED_BAS))
    p.add_argument("--years", nargs="+", type=int, default=list(range(2020, 2026)))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    result = run(args.outdir, tuple(args.bas), tuple(args.years),
                 os.environ.get("EIA_API_KEY", ""), dry_run=args.dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
