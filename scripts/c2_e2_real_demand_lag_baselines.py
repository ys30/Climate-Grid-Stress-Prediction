"""C-2 E2: observed 2024 CISO day/week lag demand-only reference forecasts.

Read a SHA-pinned annual EIA-930 UTC-start CSV; require every UTC hour.
Evaluate lag-24 and lag-168 on identical target hours. This is a retrospective
rolling-observation baseline, NOT a 24h/168h-ahead operational forecast and NOT
independent held-out model validation or weather/climate attribution.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.c2_e2_joint_coverage_gate import expected_hours, utc_hour
from scripts.c2_eia930_he_to_utc_start import he_to_start


def _percentile(values, p):
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return ordered[lo] + (pos - lo) * (ordered[hi] - ordered[lo])


def calculate(path: str | Path, *, ba: str, year: int) -> dict:
    path = Path(path)
    manifest_path = path.with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if manifest.get("sha256_csv") != sha:
        raise ValueError("EIA input SHA-256 differs from manifest")
    if (manifest.get("source_kind") != "derived_from_official_EIA_930_API"
            or manifest.get("clock_conversion") != "UTC_hour_ending_minus_one_hour"
            or manifest.get("target_year") != year):
        raise ValueError("EIA source lineage or UTC interval clock not verified")
    observed = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        cols = {"ba", "timestamp_utc", "demand_mw", "original_source_he_utc"}
        if not cols.issubset(reader.fieldnames or ()):
            raise ValueError("Missing required source columns")
        for row in reader:
            if row["ba"] != ba:
                raise ValueError("Wrong BA")
            ts = utc_hour(row["timestamp_utc"])
            if ts.year != year or ts in observed:
                raise ValueError("Out-of-year or duplicate UTC hour")
            if he_to_start(row["original_source_he_utc"]) != ts:
                raise ValueError("Hour-ending to UTC-start mismatch")
            demand = float(row["demand_mw"])
            if not math.isfinite(demand) or demand < 0:
                raise ValueError("Invalid demand MW")
            observed[ts] = demand

    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    n_expected = expected_hours(year)
    if len(observed) != n_expected or any(
        start + timedelta(hours=i) not in observed for i in range(n_expected)
    ):
        raise ValueError("Complete real UTC-year coverage required, no interpolation")

    # Common targets after a full 7d warmup. Both lags use prior observations.
    targets = [start + timedelta(hours=i) for i in range(168, n_expected)]
    true = [observed[t] for t in targets]
    threshold = _percentile(true, .9)
    result = {}
    for label, lag in (("lag24", 24), ("lag168", 168)):
        errors = [observed[t - timedelta(hours=lag)] - observed[t] for t in targets]
        peak_errors = [abs(err) for err, actual in zip(errors, true) if actual >= threshold]
        result[label] = {
            "lag_hours": lag, "n": len(errors),
            "mae_mw": sum(map(abs, errors)) / len(errors),
            "rmse_mw": math.sqrt(sum(err * err for err in errors) / len(errors)),
            "bias_mw": sum(errors) / len(errors),
            "top_decile_mae_mw": sum(peak_errors) / len(peak_errors),
        }
    return {
        "status": "real_EIA_demand_only_retrospective_rolling_lag_reference",
        "source_sha256": sha, "ba": ba, "year": year,
        "expected_source_hours": n_expected, "matched_target_hours": len(targets),
        "top_decile_actual_threshold_mw": threshold, "baselines": result,
        "limitations": [
            "Both references use actual prior observations, not fitted weather models.",
            "The 2024 target-year decile is descriptive, not a tuning objective.",
            "Operational forecast availability for 24h/168h horizons is not established.",
            "No weather, ERA5, climate counterfactual, or train/validation/test skill claims."
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    p.add_argument("--ba", required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error("Output exists: refuse overwrite")
    result = calculate(args.csv, ba=args.ba, year=args.year)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
