"""Build a noncanonical AZPS 2023 sensitivity input, never rewrite EIA originals.

A precise, preregistered exclusion of TWO authenticated negative EIA values.
Output is not eligible for canonical source gate; no interpolation or zeros.
Both original and diagnostic manifest hash must match byte-for-byte.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA = "fdbb0f8692dc201e0e2f36ee72c7a831255fa86d01800ba639adb61e6dd0054f"
FLAGS = {
    "2023-12-19T20:00:00Z": "-21897",
    "2023-12-28T21:00:00Z": "-10944",
}
SOURCE = "derived_from_official_EIA_930_API"
OUTPUT_KIND = "EIA930_AZPS2023_NONCANONICAL_EXCLUDED_NEGATIVE_SENSITIVITY"


def build(source_csv: Path, diagnostic_json: Path, output_csv: Path) -> dict:
    source_csv, diagnostic_json, output_csv = map(Path, (source_csv, diagnostic_json, output_csv))
    if any(p.resolve() == output_csv.resolve() for p in (source_csv, diagnostic_json)):
        raise ValueError("Output must differ from inputs")
    if output_csv.exists() or output_csv.with_suffix(".manifest.json").exists():
        raise FileExistsError("Sensitivity output already exists; no overwrite")
    original_manifest = json.loads(source_csv.with_suffix(".manifest.json").read_text())
    sha = hashlib.sha256(source_csv.read_bytes()).hexdigest()
    if sha != SOURCE_SHA or sha != original_manifest.get("sha256_csv"):
        raise ValueError("Wrong or modified AZPS 2023 source CSV; SHA pin mismatch")
    if original_manifest.get("source_kind") != SOURCE or original_manifest.get("target_year") != 2023:
        raise ValueError("Source lineage/year not authenticated")
    if original_manifest.get("clock_conversion") != "UTC_hour_ending_minus_one_hour":
        raise ValueError("Source clock is not certified")
    diagnostic = json.loads(diagnostic_json.read_text())
    if (diagnostic.get("utc_start_sha256") != SOURCE_SHA
        or diagnostic.get("source_gate_pass") is not False
        or diagnostic.get("invalid_numeric_rows") != 2
        or diagnostic.get("annual_audit_pass") is not False):
        raise ValueError("Independent diagnosis must document exactly two invalid values")
    anomalies = diagnostic.get("anomalies_max20", [])
    if {x["timestamp_utc"]: x["reported_demand_mw"] for x in anomalies} != FLAGS:
        raise ValueError("Pinned negative-value evidence differs from diagnosis")
    with source_csv.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = ["ba", "timestamp_utc", "demand_mw", "original_source_he_utc"]
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError("Source missing required original columns")
        retained = []
        excluded = []
        seen = set()
        for r in reader:
            t = r["timestamp_utc"]
            if r["ba"] != "AZPS" or t in seen or not t.startswith("2023-"):
                raise ValueError("Wrong BA, timestamp or duplicate")
            seen.add(t)
            if t in FLAGS:
                if r["demand_mw"] != FLAGS[t]:
                    raise ValueError("Actual source anomaly differs from registered value")
                excluded.append({"timestamp_utc": t, "reported_demand_mw": r["demand_mw"]})
                continue
            try:
                v = float(r["demand_mw"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Unexpected missing or nonnumeric demand at {t}") from exc
            if not math.isfinite(v) or v < 0:
                raise ValueError(f"Unexpected extra abnormal demand at {t}")
            retained.append({k: r[k] for k in required})
    if len(retained) != 8758 or len(excluded) != 2 or len(seen) != 8760:
        raise ValueError("Unexpected cohort shape; requires full 8760 source rows")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    temp = output_csv.with_suffix(output_csv.suffix + ".partial")
    if temp.exists():
        raise FileExistsError("Existing partial output requires manual inspection")
    try:
        with temp.open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=required)
            w.writeheader()
            w.writerows(retained)
        new_sha = hashlib.sha256(temp.read_bytes()).hexdigest()
        temp.replace(output_csv)
    finally:
        if temp.exists():
            temp.unlink()
    manifest = {
        "source_kind": OUTPUT_KIND,
        "canonical_source_gate_pass": False,
        "status": "NONCANONICAL_SENSITIVITY_ONLY_NOT_SOURCE_GATE_PASS",
        "ba": "AZPS", "year": 2023,
        "source_sha256": sha, "derived_sha256": new_sha,
        "diagnostic_sha256": hashlib.sha256(diagnostic_json.read_bytes()).hexdigest(),
        "retained_real_hourly_rows": len(retained),
        "excluded_real_hourly_rows": excluded,
        "method": "exact authenticated negative-value exclusions; no interpolation, zero replacement or smoothing",
        "warning": "Do not pass this derived file as canonical EIA source or claim AZPS 2023 source gate passed"
    }
    output_csv.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_csv", type=Path)
    p.add_argument("diagnostic_json", type=Path)
    p.add_argument("output_csv", type=Path)
    a = p.parse_args()
    result = build(a.source_csv, a.diagnostic_json, a.output_csv)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
