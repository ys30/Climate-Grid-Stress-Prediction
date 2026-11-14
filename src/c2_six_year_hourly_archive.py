"""Archive the actual 2020–2025 public source-hour EIA930/ERA5 panel.

This is a strictly *non-model* provisional-geography data artifact.
Original EIA demand gaps are empty, NEVER imputed. Separately track candidate
anomalies. Integrity manifests and actual data SHA-256 support reproducibility.
"""
import argparse,csv,gzip,hashlib,io,json
from pathlib import Path
from src.c2_72_month_source_summary import reconcile
from src.c2_full_source_event_audit import check_rows,FILENAME

COLUMNS=("year","month","ba","timestamp_utc_start",
         "EIA930_original_demand_mw","ERA5_2m_candidate_area_temperature_c",
         "EIA930_demand_missing","EIA930_anomaly_candidate_not_confirmed",
         "geometry_historically_approved","model_training_eligible")

def transform_row(row,year,month):
    if row.get("train_or_validate_eligible")!="False":
        raise ValueError("Cannot archive as provisional data with training permission")
    if row.get("historical_BA_area_approved")!="False":
        raise ValueError("Historical BA geography has not been independently approved")
    missing=row["source_missing_demand"]=="True"
    if missing and row.get("demand_mw_raw"):
        raise ValueError("Original missing demand must remain empty")
    return {"year":year,"month":month,"ba":row["ba"],
        "timestamp_utc_start":row["timestamp_utc_start"],
        "EIA930_original_demand_mw":row.get("demand_mw_raw",""),
        "ERA5_2m_candidate_area_temperature_c":row["temperature_c_experimental_area"],
        "EIA930_demand_missing":str(missing),
        "EIA930_anomaly_candidate_not_confirmed":row["demand_spike_candidate"],
        "geometry_historically_approved":"False",
        "model_training_eligible":"False"}

def archive(root,out_dir):
    root=Path(root);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    manifests=sorted(root.rglob("seasonal_source_audit.json"))
    if len(manifests)!=72:raise ValueError("Require 72 original month artifacts")
    all_metadata=[json.loads(path.read_text()) for path in manifests]
    _,_,totals=reconcile(all_metadata)
    selected=sorted(zip(manifests,all_metadata),key=lambda p:p[1]["utc_start"])
    target=out/"C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"
    records=0;received_ba={};source_files=[]
    with target.open("wb") as bf:
        with gzip.GzipFile(fileobj=bf,mode="wb",filename="",compresslevel=8,mtime=0) as gf:
            with io.TextIOWrapper(gf,encoding="utf-8",newline="") as writer_file:
                writer=csv.DictWriter(writer_file,fieldnames=COLUMNS,lineterminator="\n")
                writer.writeheader()
                for manifest_path,meta in selected:
                    src=manifest_path.parent/FILENAME
                    if not src.exists():raise ValueError("Archived month lacks exact-hour source CSV "+str(src))
                    raw=src.read_bytes()
                    source_files.append({"month":meta["utc_start"][:7],
                         "source_csv_sha256":hashlib.sha256(raw).hexdigest(),
                         "EIA930_input_sha256s":meta["eia_original_sources"]})
                    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
                    check_rows(rows,meta) # exact BA × UTC hour and anomaly counter
                    year=int(meta["utc_start"][:4]);month=int(meta["utc_start"][5:7])
                    for r in sorted(rows,key=lambda z:(z["ba"],z["timestamp_utc_start"])):
                        data=transform_row(r,year,month)
                        writer.writerow(data)
                        records+=1
                        received_ba[data["ba"]]=received_ba.get(data["ba"],0)+1
    if records!=totals["total_real_ERA5_BA_hours"]:
        raise ValueError("Archived actual source rows do not match 72-month manifest")
    if sorted(received_ba)!=["AZPS","BPAT","CISO","SRP"]:
        raise ValueError("Four BA actual-source archive incomplete")
    compressed_sha=hashlib.sha256(target.read_bytes()).hexdigest()
    manifest={"file":target.name,
        "compressed_csv_sha256":compressed_sha,
        "rows":records,
        "observed_BA_hour_counts":received_ba,
        "observed_EIA_demand_weather_pairs":totals["total_observed_EIA_ERA5_pairs"],
        "missing_raw_EIA_demand_hours":totals["total_missing_original_demand_BA_hours"],
        "original_EIA930_demand_anomaly_candidates":totals["total_original_demand_anomaly_candidates"],
        "all_month_sources_verified":72,
        "source_weights_sha256":"e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3",
        "input_source_csvs":source_files,
        "original_EIA_demand_imputed":False,
        "ERA5_2m_grid_source":"public ARCO-ERA5 0.25-degree hourly reanalysis",
        "BA_geometry_vintage":"2018 source-derived candidate",
        "historical_geography_approved":False,
        "training_or_attribution_authorized":False,
        "description":"Real hourly observed weather and load; BA region mask not scientifically approved for demand/weather modeling."}
    (out/"C2_SOURCE_HOURLY_ARCHIVE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    (out/"SHA256SUMS.txt").write_text(compressed_sha+"  "+target.name+"\n")
    print("REAL_ERA5_EIA930_SIX_YEAR_ARCHIVE",json.dumps({
        "rows":records,"per_BA":received_ba,
        "observed_pairs":manifest["observed_EIA_demand_weather_pairs"],
        "missing_source_demand":manifest["missing_raw_EIA_demand_hours"],
        "candidate_anomalies":manifest["original_EIA930_demand_anomaly_candidates"],
        "gzip_sha256":compressed_sha,
        "model_eligible":False}))
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    archive(a.inputs,a.out)
if __name__=="__main__":main()
