"""Reconcile C2 frozen six-year source archive with newer strict EIA annual gates.

Different units of verification must never be silently merged:
* '24/24 source groups present' means 24 BA-year groups are archived.
* '23/24 strict annual QA passes' means AZPS 2023 still fails canonical QA.
* '210432 real BA-hour source rows' includes unapproved geographic exposure.
No model-admission or BA exposure approval is inferred from these.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_BAS = {"AZPS", "BPAT", "CISO", "SRP"}
YEARS = set(range(2020, 2026))


def summarize(wave_files, *, frozen_report_path):
    report_text = Path(frozen_report_path).read_text(encoding="utf-8")
    required_proofs = (
        "210,432", "210,172", "260", "70",
        "model_training_eligible=False",
        "43629200989", "14127710411",
        "88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac",
    )
    # Match frozen E1 source report, not a newly synthesized source panel.
    if any(token not in report_text for token in required_proofs):
        raise ValueError("Frozen 2020–25 source evidence summary is incomplete")
    seen = {}
    runs = {}
    for wave_name, path in wave_files.items():
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        entries = data.get("cohorts")
        if not isinstance(entries, list):
            raise ValueError(f"{wave_name}: missing audited cohort evidence")
        runs[wave_name] = data.get("run_id")
        for entry in entries:
            ba, year = entry.get("ba"), entry.get("year")
            if ba not in REQUIRED_BAS or year not in YEARS:
                raise ValueError("Unexpected BA/year in strict QA")
            key = (ba, year)
            if key in seen:
                raise ValueError("Duplicate BA-year across audit waves")
            passed = entry.get("gate_pass") is True and entry.get("status") == "artifact_hash_and_annual_gate_pass"
            seen[key] = {"pass": passed, "status": entry.get("status"),
                         "coverage": entry.get("coverage")}

    # CISO 2024 was validated separately from these three expansion waves.
    separate = ("CISO", 2024)
    if separate in seen:
        raise ValueError("CISO 2024 counted twice")
    seen[separate] = {"pass": True, "status": "independently_verified_original_pilot",
                      "eia_utc_sha256": "375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c"}
    expected = {(ba, y) for ba in REQUIRED_BAS for y in YEARS}
    if set(seen) != expected:
        raise ValueError(f"Missing strict QA groups: {sorted(expected-set(seen))}")

    passed = sum(int(v["pass"]) for v in seen.values())
    failed = sorted((ba, year) for (ba, year), item in seen.items() if not item["pass"])
    if passed != 23 or failed != [("AZPS", 2023)]:
        raise ValueError("Canonical QA outcome changed: independently review, do not infer model approval")
    return {
        "project": "C2",
        "status": "SIX_YEAR_SOURCE_VERIFIED_MODEL_ADMISSION_BLOCKED",
        "frozen_source_scope": {
            "era5_eia930_BA_hour_records": 210432,
            "nonmissing_original_demand": 210172,
            "missing_original_demand": 260,
            "source_anomaly_candidates_not_confirmed_errors": 70,
            "source_BA_year_groups_present": 24,
            "weather_geography": "2018_HIFLD_unapproved_repaired_candidate",
            "archive_run_id": 43629200989,
            "archive_artifact_id": 14127710411,
            "inner_gzip_sha256": "88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac",
        },
        "newer_EIA_strict_source_gate": {
            "total_BA_year_groups": 24,
            "passed_BA_year_groups": passed,
            "failed_BA_year_groups": [{"ba": ba, "year": year} for ba, year in failed],
            "wave_run_ids": runs,
            "distinct_from_source_group_presence": True,
            "azps2023_noncanonical_sensitivity_does_not_waive_source_gate": True,
        },
        "scientific_admission": {
            "historical_BA_geography_approved": False,
            "load_relevant_weather_exposure_approved": False,
            "load_anomaly_and_holdout_protocol_approved": False,
            "model_training_permitted": False,
            "forecast_skill_claims_permitted": False,
            "anthropogenic_climate_attribution_permitted": False,
            "future_SSP_PyPSA_claims_permitted": False,
        },
        "meaning": "Sources present is not strict annual QA or geography/model admission",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wave1", type=Path, default=Path("docs/E2_WAVE1_VERIFIED_STATUS.json"))
    p.add_argument("--wave2", type=Path, default=Path("docs/E2_WAVE2_VERIFIED_STATUS.json"))
    p.add_argument("--wave3", type=Path, default=Path("docs/E2_WAVE3_VERIFIED_STATUS.json"))
    p.add_argument("--frozen-report", type=Path,
                   default=Path("reports/E1_FULL_2020_2025_REAL_ERA5_EIA930_SOURCE_DATA_FROZEN_QA.md"))
    p.add_argument("--output", type=Path, required=True)
    a=p.parse_args()
    result=summarize({"wave1":a.wave1,"wave2":a.wave2,"wave3":a.wave3},
                     frozen_report_path=a.frozen_report)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"strict_QA_passed":23,
                      "training":False},indent=2))


if __name__=="__main__":
    main()
