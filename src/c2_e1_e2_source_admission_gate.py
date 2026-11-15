"""Reproducible source-evidence ledger and fail-closed E2 admission for Project C-2.

Never infer historical BA operating-area validity or model permission from
successful weather-proxy experiments. Verify actual archived source files and
emit machine-readable reasons blocking E2 model training.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timedelta

BAS=("AZPS","BPAT","CISO","SRP")
EXPECTED_WINDOWS=("2023-01-15T00:00:00Z","2023-07-01T00:00:00Z",
                  "2025-01-15T00:00:00Z","2025-07-01T00:00:00Z")
FROZEN_WEIGHTS={
 "A":"e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3",
 "B":"6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8",
 "C":"741d9e1b1101b6a018311803dee6e42fda8b5dacf26ccf40e876171383335361"}
FROZEN_COUNTY_CSV_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"
FROZEN_POPULATION_CSV_SHA="ee8fbfcaa6aca125669a2214aeadc349bfea17ed72eb29aa29cb9a845eaa9097"
FROZEN_CENSUS_ORIGINAL_SHA="4f5a499d851e2cb48fd7a5405e5a9235453a8a66933657aacd10df0e264f35d5"
ABC_FILE="REAL_ERA5_ABC_2688_BA_HOURS.csv"
ABC_META="REAL_ERA5_ABC_4WEEK_PROVENANCE.json"

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_abc(artifact_folder):
    base=Path(artifact_folder)
    meta=json.loads((base/ABC_META).read_text())
    if (meta.get("real_BA_hours")!=2688 or
        meta.get("frozen_source_weight_SHA256")!=FROZEN_WEIGHTS or
        meta.get("observed_four_weeks")!=list(EXPECTED_WINDOWS) or
        meta.get("BA_geography_approved") is not False or
        meta.get("electric_demand_model_training_permitted") is not False or
        meta.get("hourly_rows_are_independent_trials") is not False):
        raise ValueError("Four-week original source manifest is incompatible")
    with (base/ABC_FILE).open(newline="",encoding="utf-8") as f:
        records=list(csv.DictReader(f))
    if len(records)!=2688:raise ValueError("Source audit has incomplete actual ERA5 BA-hour rows")
    seen=set()
    for row in records:
        label=row.get("source_window")
        if label not in EXPECTED_WINDOWS:raise ValueError("Unexpected source UTC week")
        dt=datetime.fromisoformat(row["UTC_timestamp"].replace("Z","+00:00"))
        begin=datetime.fromisoformat(label.replace("Z","+00:00"))
        if not begin<=dt<begin+timedelta(days=7):
            raise ValueError("Weather outside frozen selected window")
        ba=row["BA"]
        key=(label,ba,dt)
        if ba not in BAS or key in seen:
            raise ValueError("Duplicate/unknown source BA-hour")
        seen.add(key)
        if (row.get("historical_BA_geography_approved")!="False" or
            row.get("training_permitted")!="False" or
            row.get("population_is_customer_weights")!="False"):
            raise ValueError("A/B/C candidate source falsely authorized")
        A=float(row["HIFLD_A_celsius"]);B=float(row["TIGER_B_celsius"])
        C=float(row["population_C_celsius"])
        for field,value in (("B_minus_A_celsius",B-A),
                            ("C_minus_B_celsius",C-B),
                            ("C_minus_A_celsius",C-A)):
            if abs(float(row[field])-value)>2.1e-6:
                raise ValueError("Incorrect source temperature differences")
    expected={(window,ba,
              datetime.fromisoformat(window.replace("Z","+00:00"))+timedelta(hours=h))
              for window in EXPECTED_WINDOWS for ba in BAS for h in range(168)}
    if seen!=expected:raise ValueError("Missing real hourly ERA5 BA key")
    return {"source_hourly_records_verified":len(seen),
            "four_UTC_windows_verified":len(EXPECTED_WINDOWS),
            "source_ABC_original_csv_sha256":sha(base/ABC_FILE),
            "frozen_AB_C_weight_sha256":FROZEN_WEIGHTS,
            "weather_spatial_sensitivity_observed":True,
            "historical_BA_operating_geography_approved":False}

def verify_census(population_folder):
    base=Path(population_folder)
    provenance=json.loads((base/"C2_PROXY_C_POPULATION_SOURCE_PROVENANCE.json").read_text())
    if (provenance.get("census2020_variable")!="ESTIMATESBASE2020" or
        provenance.get("population_is_original_decennial_PL_P1_001N") is not False or
        provenance.get("county_proxy_geography_approved") is not False or
        provenance.get("actual_customers_or_load_distribution_observed") is not False or
        provenance.get("model_training_permitted") is not False):
        raise ValueError("Census estimates-base source misclassified")
    if (provenance.get("weight_csv_sha256")!=FROZEN_WEIGHTS["C"] or
        provenance.get("census2020_raw_population_csv_sha256")!=FROZEN_POPULATION_CSV_SHA or
        provenance.get("EIA861_yearly_membership_input_sha256")!=FROZEN_COUNTY_CSV_SHA or
        provenance.get("population_source_states",[{}])[0].get("source_file_sha256")!=FROZEN_CENSUS_ORIGINAL_SHA):
        raise ValueError("Census data or experimental weights not source pinned")
    data=base/"CENSUS2020_ESTIMATES_BASE_COUNTY_POPULATION_SOURCE.csv"
    if sha(data)!=FROZEN_POPULATION_CSV_SHA:raise ValueError("Population original-derived CSV SHA mismatch")
    with data.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    if len(rows)!=182 or len({r["county_id_fips"] for r in rows})!=182:
        raise ValueError("Expected 182 unique source Census county FIPS")
    for row in rows:
        if (len(row["county_id_fips"])!=5 or
            not row["county_id_fips"].isdigit() or
            not row["census2020_estimates_base_population"].isdigit()):
            raise ValueError("Invalid original Census county record")
    return {"Census_source_counties_verified":len(rows),
           "Census_estimate_base_original_file_sha256":FROZEN_CENSUS_ORIGINAL_SHA,
           "actual_customer_weather_weighting_source_present":False,
           "population_is_utility_load":False}

def verify_crosswalk(crosswalk_folder):
    path=Path(crosswalk_folder)/"2020_2025_EIA861_fourBA_yearly_county_FIPS_memberships_UNAPPROVED.csv"
    if sha(path)!=FROZEN_COUNTY_CSV_SHA:
        raise ValueError("Frozen EIA861 annual county membership artifact differs")
    with path.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    if len(rows)!=1110:raise ValueError("Annual county membership source count differs")
    slots=defaultdict(set);keys=set()
    for row in rows:
        y=int(row["year"]);ba=row["eia930_BA_code"];fips=row["county_id_fips"]
        key=(y,ba,fips)
        if y not in range(2020,2026) or ba not in BAS or len(fips)!=5 or not fips.isdigit() or key in keys:
            raise ValueError("Duplicate or invalid original BA/annual county FIPS")
        if row["model_ready"]!="False":raise ValueError("Unapproved county mask may not be trained")
        slots[(y,ba)].add(fips);keys.add(key)
    if len(slots)!=24:raise ValueError("Not 24 years x four BA exact source slots")
    if any(slots[(2020,ba)]!=slots[(year,ba)]
           for ba in BAS for year in range(2021,2026)):
        raise ValueError("Annual original BA county membership not stable as documented")
    return {"years":list(range(2020,2026)),
      "annual_BA_year_slots":24,
      "source_BA_county_rows":len(rows),
      "snapshot_csv_sha256":FROZEN_COUNTY_CSV_SHA,
      "upstream_parquet_source":"PUDL nightly (MUTABLE; not release-pinned)",
      "upstream_stable_release_verified":False,
      "historic_operating_area_certification":False}

def make_gate(abc,census,crosswalk):
    evidence={"ERA5_AB_C":verify_abc(abc),"Census_population":verify_census(census),
              "EIA861_BA_county":verify_crosswalk(crosswalk)}
    blockers=[
      {"id":"GEO_HISTORICAL_BA_FOOTPRINT","cleared":False,
       "why":"HIFLD 2018/whole-county TIGER 2024 proxies do not establish operating BA geography in 2020–2025",
       "required_evidence":"Independent dated BA/utility mapping and explicit reviewed spatial estimand"},
      {"id":"GEO_LOAD_RELEVANCE","cleared":False,
       "why":"Area and resident population weighting are not independently verified utility customers/BA load weighting",
       "required_evidence":"Validated utility-to-BA locations, customers or demand weights and uncertainty tests"},
      {"id":"PROVENANCE_PUDL_RELEASE","cleared":False,
       "why":"Archived EIA861 county CSV is SHA-pinned, but its upstream PUDL yearly Parquet source was mutable nightly",
       "required_evidence":"Stable tagged PUDL data release and immutable upstream parquet digest"},
      {"id":"LOAD_QUALITY_HOLDOUT_PROTOCOL","cleared":False,
       "why":"260 original demand gaps and 70 source anomaly candidates require final exception and chronological holdout rules",
       "required_evidence":"Frozen anomaly decisions, no imputation and sealed 2024–25 test protocol"}]
    return {"project":"C2","source_only_evidence_verified":True,
      "observed_real_ERA5_AB_C_pairs":2688,
      "scientific_weather_proxy_validation":False,
      "approved_historical_BA_geography":False,
      "model_training_permitted":False,"forecast_skill_claims_permitted":False,
      "anthropogenic_attribution_permitted":False,
      "future_SSP_PyPSA_stress_claims_permitted":False,
      "independently_validated":evidence,"mandatory_blockers":blockers,
      "explanation":"Source QA PASS does not imply BA geography/admission PASS."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--abc-audit",required=True)
    p.add_argument("--population",required=True)
    p.add_argument("--crosswalk",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    gate=make_gate(args.abc_audit,args.population,args.crosswalk)
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"C2_E1_E2_FROZEN_SOURCE_AND_MODEL_ADMISSION_GATE.json").write_text(
       json.dumps(gate,indent=2,sort_keys=True)+"\n")
    report=["# C2 E1 → E2 audited source ledger and admission decision","",
       "**Verified source evidence:** 2,688 actual ERA5 proxy BA-hour rows, pinned A/B/C weights, official county population estimate base, six-year EIA861 BA-county snapshot.","",
       "**E2 weather–demand model admission: BLOCKED**. Source QA success is not proof these BA geographies represent loads.","",
       "## Mandatory independent admission criteria"]
    for entry in gate["mandatory_blockers"]:
        report.append("- **"+entry["id"]+"** — "+entry["why"]+"; needs: "+entry["required_evidence"])
    report+=["","## Evidence detail","",
        "```json",json.dumps(gate["independently_validated"],indent=2),"```",
        "","No original missing EIA930 load has been imputed; no E2 model fit, ALL/NAT attribution or SSP/PyPSA stress output is authorized.",""]
    (dest/"C2_E1_E2_ADMISSION_GATE_SOURCE_LEDGER.md").write_text("\n".join(report))
    print("C2_E1_E2_SOURCE_QA_AND_ADMISSION",json.dumps(gate),flush=True)
if __name__=="__main__":main()
