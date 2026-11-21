"""Fail-closed C2 scientific admission from an actual published 23-year QA artifact.

This program does not fit a model, verify BA geography, or certify original
EIA source values. Only a source-authenticated ZIP with pinned JSON SHA
may be read. Every scientific gate remains CLOSED until separately audited.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

REAL_SEMANTIC_RUN=44861789787
REAL_SEMANTIC_ARTIFACT_ID=14692623744
REAL_SEMANTIC_MEMBER="C2_EIA_23_YEAR_REAL_SOURCE_SEMANTIC_QA.json"
REAL_SEMANTIC_JSON_SHA="b4abc2ac79ebf9e04c0f2b677b136f0d91d7aed5be4bb676c9dc99f54471fc61"
REQUIRED_GEO_EVIDENCE={
    "reports/E1_BA_GEOGRAPHY_INDEPENDENT_SOURCE_GATE_2026_11_14.md":
        ("~96.66%","~7.08%","NOT APPROVED"),
    "reports/C2_E1_VERIFIED_BA_UTILITY_GEO_JOIN_COVERAGE_AND_EIA861_SALES_NEXT_GATE_2026_11_15.md":
        ("1,418","979","GEO_LOAD_RELEVANCE=BLOCKED"),
}
REQUIRED_SOURCE_EVIDENCE={
    "reports/E1_FULL_2020_2025_REAL_ERA5_EIA930_SOURCE_DATA_FROZEN_QA.md":
        ("210,432","210,172","260","70","43629200989")
}

def summarize(semantic_artifact,repository_root):
    root=Path(repository_root)
    with zipfile.ZipFile(semantic_artifact) as z:
        if z.namelist()!=[REAL_SEMANTIC_MEMBER]:
            raise ValueError("Unexpected EIA CI published semantic artifact layout")
        raw=z.read(REAL_SEMANTIC_MEMBER)
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=REAL_SEMANTIC_JSON_SHA:
        raise ValueError("Original GitHub CI real-source semantic JSON changed")
    original=json.loads(raw)
    expected={
        "BA_years":23,"expected_hours":201672,"observed_hours":201671,
        "absent_time_keys":1,"null_demand_rows":210,
        "zero_demand_hours":1,"exploratory_low_positive_hours":2,
        "historical_BA_geography_approved":False,"model_training_permitted":False
    }
    for k,v in expected.items():
        if original.get(k)!=v:raise ValueError(f"EIA source evidence contract mismatch: {k}")
    actual=original.get("per_BA_year",[])
    if len(actual)!=23 or len({(r["ba"],r["year"]) for r in actual})!=23:
        raise ValueError("Original per-year EIA QA incomplete or duplicated")
    if sum(r["expected_hours"] for r in actual)!=201672:
        raise ValueError("Original annual EIA hours inconsistent")
    flags=original.get("review_rows",[])
    assert len(flags)==3
    if sorted((x["timestamp_utc"],x["reported_demand_mw"]) for x in flags)!=[
        ("2025-07-31T19:00:00Z",0.0),
        ("2025-07-31T21:00:00Z",273.0),
        ("2025-07-31T22:00:00Z",485.0)]:
        raise ValueError("Source-zero/low-positive research review values changed")
    for source,terms in {**REQUIRED_GEO_EVIDENCE,**REQUIRED_SOURCE_EVIDENCE}.items():
        report=(root/source).read_text(encoding="utf-8")
        if any(term not in report for term in terms):
            raise ValueError(f"Frozen evidence report requires independent refresh: {source}")
    blockers=[
        {"id":"GEO_HISTORICAL_BA_FOOTPRINT","cleared":False,
         "evidence":"2018 HIFLD candidates do not establish 2020–2025 BA operating area; CISO make_valid sensitivity ~7.08%, AZPS/SRP candidate area overlap ~96.66% of SRP"},
        {"id":"GEO_LOAD_RELEVANCE","cleared":False,
         "evidence":"1,418 utility-state association rows, 979 county matches; association count is not observed BA load/customer geography"},
        {"id":"LOAD_QUALITY_HOLDOUT_PROTOCOL","cleared":False,
         "evidence":"23/24 annual canonical source pass, AZPS2023 two original negatives; newest AZPS2025 genuine original 0 MW and two 273/485 MW exploratory review records"},
    ]
    return {
        "project":"C2",
        "decision":"SOURCE_PROVENANCE_VERIFIED_SCIENTIFIC_MODEL_ADMISSION_BLOCKED",
        "verified_observed_source":{"source":"GitHub Actions actual public EIA930 original raw HE with UTC-start SHA verification",
            "run_id":REAL_SEMANTIC_RUN,"artifact_id":REAL_SEMANTIC_ARTIFACT_ID,
            "source_semantic_JSON_sha256":digest,**{k:original[k] for k in expected},
            "old_archived_six_year_source_BA_hours":210432,
            "old_source_archive_is_not_model_ready":True,
            "source_canonical_years_pass":23,
            "source_canonical_years_fail":1},
        "independent_geography_and_load_relevance":{"HIFLD_vintage":2018,
            "CISO_original_invalid_geometry_repair_area_difference_pct_approx":7.08,
            "AZPS_SRP_candidate_polygon_SRP_area_overlap_pct_approx":96.66,
            "utility_BA_state_association_rows":1418,
            "county_matched_association_rows":979,
            "measured_customer_or_load_location_weights_available":False},
        "mandatory_scientific_gates":blockers,
        "all_mandatory_gates_cleared":False,
        "model_training_permitted":False,
        "forecast_skill_claims_permitted":False,
        "historical_anthropogenic_attribution_permitted":False,
        "future_SSP_PyPSA_stress_claims_permitted":False,
        "holdout_years":[2024,2025],
        "holdout_used_for_model_selection":False,
        "unreviewed_low_positive_threshold_is_official":False,
        "source_values_modified":False,
        "C1_frozen_untouched":True
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("real_semantic_artifact_zip",type=Path)
    p.add_argument("--repo-root",type=Path,default=Path("."))
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Scientific source admission result cannot be overwritten")
    d=summarize(a.real_semantic_artifact_zip,a.repo_root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({"decision":d["decision"],
                      "model_training_permitted":d["model_training_permitted"]},indent=2))

if __name__=="__main__":main()
