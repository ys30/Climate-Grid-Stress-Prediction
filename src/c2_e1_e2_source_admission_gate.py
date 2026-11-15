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

PUDL_VERSIONED_PARQUET_SHA={
 "core_eia861__yearly_balancing_authority.parquet":
  "0fdb3930b3fbec15845242d1fbd96182bc015dfaf9ba23a04ebb646886d9ea4d",
 "out_eia861__yearly_balancing_authority_service_territory.parquet":
  "a50f78de5c7a70ec510a9de241872955e737d73e15a48842ede80c5c610b6791"}

def verify_stable_pudl(versioned_folder,crosswalk_folder):
    """Compare every BA-year-FIPS member and identity, not just summary flags."""
    source=Path(versioned_folder)
    info=json.loads((source/"PUDL_FIXED_RELEASE_V2026_10_PROVENANCE.json").read_text())
    if (info.get("pudl_fixed_release")!="v2026.10.0"
        or info.get("nightly_derived_snapshot_SHA256")!=FROZEN_COUNTY_CSV_SHA
        or info.get("source_release_pin_verified") is not True
        or info.get("all_BA_ID_and_county_memberships_equal") is not True
        or info.get("year_BA_slots_compared")!=24
        or info.get("total_year_BA_membership_agreements")!=24
        or info.get("total_year_BA_identity_agreements")!=24
        or info.get("year_BA_differences")!=[]
        or info.get("operational_BA_geography_approved") is not False
        or info.get("model_training_permitted") is not False):
        raise ValueError("Versioned PUDL source match flags inconsistent")
    originals=info.get("versioned_original_parquet",{})
    if set(originals)!=set(PUDL_VERSIONED_PARQUET_SHA):
        raise ValueError("Two original stable PUDL Parquet source objects required")
    for name,expected in PUDL_VERSIONED_PARQUET_SHA.items():
        entry=originals[name]
        if (entry.get("raw_sha256")!=expected
          or entry.get("versioned_url")!="s3://pudl.catalyst.coop/v2026.10.0/"+name
          or not isinstance(entry.get("raw_bytes"),int)
          or entry["raw_bytes"]<=0):
            raise ValueError("Incorrect official PUDL tagged source digest")
    original=Path(crosswalk_folder)/"2020_2025_EIA861_fourBA_yearly_county_FIPS_memberships_UNAPPROVED.csv"
    if sha(original)!=FROZEN_COUNTY_CSV_SHA:
        raise ValueError("Unverified old snapshot county CSV")
    with original.open(newline="",encoding="utf-8") as f:
        old=list(csv.DictReader(f))
    source_csv=source/"PUDL_v2026_10_YEAR_BA_COUNTY_MEMBERSHIPS.csv"
    with source_csv.open(newline="",encoding="utf-8") as f:
        current=list(csv.DictReader(f))
    old_map={(int(x["year"]),x["eia930_BA_code"],x["county_id_fips"],
             str(x["EIA861_balancing_authority_id"]))
             for x in old}
    new_map={(int(x["year"]),x["BA"],x["county_id_fips"],str(x["BA_ID"]))
             for x in current}
    if len(old_map)!=1110 or len(old)!=1110 or len(current)!=1110 or old_map!=new_map:
        raise ValueError("Upstream stable Parquet membership not identical to 1110 source rows")
    if any(x.get("model_training_permitted")!="False" for x in current):
        raise ValueError("Versioned PUDL counties must remain an unapproved proxy")
    comparison=source/"PUDL_2026_10_VS_NIGHTLY_SNAPSHOT_24_BA_YEAR_AUDIT.csv"
    with comparison.open(newline="",encoding="utf-8") as f:
        diagnostic=list(csv.DictReader(f))
    expected={(y,ba) for y in range(2020,2026) for ba in BAS}
    keys={(int(x["year"]),x["BA"]) for x in diagnostic}
    if len(diagnostic)!=24 or keys!=expected or any(
        x["identical_BA_ID"]!="True" or x["identical_county_membership"]!="True"
        for x in diagnostic):
        raise ValueError("Original 24 BA/year independent comparison not all matched")
    return {"upstream_stable_release_verified":True,
            "stable_release":"v2026.10.0",
            "full_original_parquet_sha256":PUDL_VERSIONED_PARQUET_SHA,
            "BA_year_slots_exactly_matched":24,
            "BA_year_county_memberships_exactly_matched":1110,
            "frozen_versioned_membership_csv_sha256":sha(source_csv),
            "frozen_original_24_slot_comparison_sha256":sha(comparison),
            "geographical_electricity_load_coverage_certified":False}

def make_gate(abc,census,crosswalk,versioned_pudl):
    evidence={"ERA5_AB_C":verify_abc(abc),"Census_population":verify_census(census),
              "EIA861_BA_county":verify_crosswalk(crosswalk),
              "PUDL_v2026_10_stable_source":verify_stable_pudl(versioned_pudl,crosswalk)}
    evidence["EIA861_BA_county"]["upstream_parquet_source"]="PUDL v2026.10.0 tagged source, two original Parquet SHA256 verified"
    evidence["EIA861_BA_county"]["upstream_stable_release_verified"]=True
    blockers=[
      {"id":"GEO_HISTORICAL_BA_FOOTPRINT","cleared":False,
       "why":"HIFLD 2018/whole-county TIGER 2024 proxies do not establish operating BA geography in 2020–2025",
       "required_evidence":"Independent dated BA/utility mapping and explicit reviewed spatial estimand"},
      {"id":"GEO_LOAD_RELEVANCE","cleared":False,
       "why":"Area and resident population weighting are not independently verified utility customers/BA load weighting",
       "required_evidence":"Validated utility-to-BA locations, customers or demand weights and uncertainty tests"},
      {"id":"PROVENANCE_PUDL_RELEASE","cleared":True,
       "why":"Upstream PUDL v2026.10.0 original Parquet SHA256 verified; all 24 BA-year identities and 1110 county FIPS entries match frozen nightly snapshot",
       "required_evidence":"Satisfied: tagged v2026.10.0 plus 2 pinned Parquet SHA256 values"},
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
      "independently_validated":evidence,"admission_checks":blockers,
      "mandatory_blockers":[x for x in blockers if not x["cleared"]],
      "explanation":"Source QA PASS does not imply BA geography/admission PASS."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--abc-audit",required=True)
    p.add_argument("--population",required=True)
    p.add_argument("--crosswalk",required=True)
    p.add_argument("--versioned-pudl",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    gate=make_gate(args.abc_audit,args.population,args.crosswalk,args.versioned_pudl)
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"C2_E1_E2_FROZEN_SOURCE_AND_MODEL_ADMISSION_GATE.json").write_text(
       json.dumps(gate,indent=2,sort_keys=True)+"\n")
    report=["# C2 E1 → E2 audited source ledger and admission decision","",
       "**Verified source evidence:** 2,688 actual ERA5 proxy BA-hour rows, pinned A/B/C weights, official county population estimate base, six-year EIA861 BA-county snapshot.","",
       "**E2 weather–demand model admission: BLOCKED**. Source QA success is not proof these BA geographies represent loads.","",
       "## Mandatory independent admission criteria"]
    for entry in gate["admission_checks"]:
        report.append("- **"+entry["id"]+"** — "+("CLEARED" if entry["cleared"] else "BLOCKED")+" — "+entry["why"]+"; needs: "+entry["required_evidence"])
    report+=["","## Evidence detail","",
        "```json",json.dumps(gate["independently_validated"],indent=2),"```",
        "","No original missing EIA930 load has been imputed; no E2 model fit, ALL/NAT attribution or SSP/PyPSA stress output is authorized.",""]
    (dest/"C2_E1_E2_ADMISSION_GATE_SOURCE_LEDGER.md").write_text("\n".join(report))
    print("C2_E1_E2_SOURCE_QA_AND_ADMISSION",json.dumps(gate),flush=True)
if __name__=="__main__":main()
