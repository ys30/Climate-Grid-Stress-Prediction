"""C-2 E2: provenance-gated EIA-930 × ERA5 hourly BA proxy join.

Requires:
- EIA CSV produced by c2_eia930_he_to_utc_start.py and its SHA manifest;
- ERA5 proxy CSV with columns ba,timestamp_utc,temperature_c and a separate
  .manifest.json containing SHA256 and *explicit* weather construction provenance.

No ERA5 acquisition, regridding, population weighting, interpolation or
source-observation inference is performed here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from scripts.c2_e2_joint_coverage_gate import utc_hour


def _read_verified(path, *, expected_kind):
    p = Path(path)
    manifest_path = p.with_suffix(".manifest.json")
    if not manifest_path.exists():
        raise ValueError(f"Missing manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if manifest.get("sha256_csv") != sha:
        raise ValueError(f"SHA-256 mismatch for {p}")
    if manifest.get("source_kind") != expected_kind:
        raise ValueError(f"Unexpected source_kind for {p}")
    with p.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Empty source CSV")
        records = list(reader)
    return records, manifest, sha


def join(eia_csv, weather_csv, output_csv, *, ba, year):
    if not 2020 <= year <= 2025:
        raise ValueError("Year outside registered E2 cohort")
    target = Path(output_csv)
    if any(Path(p).resolve() == target.resolve() for p in (eia_csv, weather_csv)):
        raise ValueError("Output cannot overwrite input")
    if target.exists() or target.with_suffix(".manifest.json").exists():
        raise FileExistsError("Output or manifest already exists")

    eia_rows, em, ehash = _read_verified(
        eia_csv, expected_kind="derived_from_official_EIA_930_API")
    weather_rows, wm, whash = _read_verified(
        weather_csv, expected_kind="ERA5_BA_geographic_proxy")
    if em.get("target_year") != year or em.get("clock_conversion") != "UTC_hour_ending_minus_one_hour":
        raise ValueError("EIA time convention not proved for selected year")
    for field in ("retrieval_timestamp_utc", "era5_dataset", "era5_variables",
                  "spatial_method", "geometry_source", "time_reference"):
        if not wm.get(field):
            raise ValueError(f"Weather provenance missing {field}")
    if wm["time_reference"] != "UTC_interval_start":
        raise ValueError("Weather clock must explicitly be UTC interval-start")
    if wm["spatial_method"] not in ("unweighted_grid_mean", "single_gridcell"):
        raise ValueError("Only declared geography-only BA weather proxies admitted")
    # The manifest distinguishes proxy weather from independent measured load.
    if wm.get("is_measured_county_load_weighted") is not False:
        raise ValueError("Weather proxy must explicitly reject measured county-load-weight claim")

    demand = {}
    seen_eia_hours = set()
    missing_source_demand_hours = 0
    required_eia = {"ba", "timestamp_utc", "demand_mw", "original_source_he_utc"}
    if eia_rows and not required_eia.issubset(eia_rows[0]):
        raise ValueError("EIA file missing required columns")
    from scripts.c2_eia930_he_to_utc_start import he_to_start
    for row in eia_rows:
        if row["ba"] != ba:
            raise ValueError("Wrong EIA BA")
        t = utc_hour(row["timestamp_utc"])
        if t.year != year or t in seen_eia_hours:
            raise ValueError("Invalid year or duplicate EIA hour")
        seen_eia_hours.add(t)
        if he_to_start(row["original_source_he_utc"]) != t:
            raise ValueError("EIA HE clock mismatch")
        original = row["demand_mw"]
        if original is None or original.strip() == "":
            missing_source_demand_hours += 1
            continue  # Never impute an official null-demand source hour.
        value = float(original)
        if not math.isfinite(value) or value < 0:
            raise ValueError("Invalid EIA demand MW")
        demand[t] = value

    weather = {}
    required_weather = {"ba", "timestamp_utc", "temperature_c"}
    if weather_rows and not required_weather.issubset(weather_rows[0]):
        raise ValueError("Weather file missing required columns")
    for row in weather_rows:
        if row["ba"] != ba:
            raise ValueError("Wrong weather BA")
        t = utc_hour(row["timestamp_utc"])
        if t.year != year or t in weather:
            raise ValueError("Invalid year or duplicate weather hour")
        value = float(row["temperature_c"])
        if not math.isfinite(value) or not -100 < value < 70:
            raise ValueError("Invalid temperature proxy °C")
        weather[t] = value

    if not demand or not weather:
        raise ValueError("Empty real-data side; no simulated input permitted")
    shared = sorted(demand.keys() & weather.keys())
    # Do not fill gaps. Full completeness adjudication remains a separate gate.
    if not shared:
        raise ValueError("No overlapping source hours")
    report = {"status": "hourly_proxy_join_only_not_predictive_validation",
              "ba": ba, "year": year, "eia_hours": len(demand),
              "weather_hours": len(weather), "shared_hours": len(shared),
              "source_null_demand_hours_excluded": missing_source_demand_hours,
              "unmatched_eia_hours": len(demand) - len(shared),
              "unmatched_weather_hours": len(weather) - len(shared),
              "eia_sha256": ehash, "weather_sha256": whash,
              "weather_spatial_method": wm["spatial_method"],
              "weather_geometry_source": wm["geometry_source"],
              "claim_guard": "Geographic proxy, not observed county or load-weighted temperature"}
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".partial")
    if tmp.exists():
        raise FileExistsError("Stale partial output")
    try:
        with tmp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["ba", "timestamp_utc", "demand_mw", "temperature_c"])
            writer.writeheader()
            for t in shared:
                writer.writerow({"ba": ba, "timestamp_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "demand_mw": demand[t], "temperature_c": weather[t]})
        report["sha256_csv"] = hashlib.sha256(tmp.read_bytes()).hexdigest()
        tmp.replace(target)
        manifest = {**report, "source_kind": "EIA930_ERA5_BA_proxy_joint",
                    "claim_status": "joint_coverage_must_pass_before_model_training"}
        target.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                                         encoding="utf-8")
    finally:
        if tmp.exists():
            tmp.unlink()
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("eia_csv")
    p.add_argument("weather_csv")
    p.add_argument("output_csv")
    p.add_argument("--ba", required=True)
    p.add_argument("--year", required=True, type=int)
    a = p.parse_args()
    print(json.dumps(join(a.eia_csv, a.weather_csv, a.output_csv, ba=a.ba, year=a.year),
                     indent=2))


if __name__ == "__main__":
    main()
