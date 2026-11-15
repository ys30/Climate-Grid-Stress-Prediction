"""C2 E1 seven-day actual ARCO ERA5 sensitivity under A/B/C spatial proxies.

Strict source-only experiment: 2018 HIFLD area A, 2024 TIGER EIA861
county-area B, 2020 Census estimate-base county-population C. Never fit
EIA930 demand and never admit geographic masks as BA operating boundaries.
"""
import argparse,csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_ABC_four_day import normalize_day,BAS,A_SHA,B_SHA,C_SHA
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_public_probe import STORE

WINDOWS={
    "2023-01-15T00:00:00Z":"winter2023",
    "2023-07-01T00:00:00Z":"summer2023",
    "2025-01-15T00:00:00Z":"winter2025",
    "2025-07-01T00:00:00Z":"summer2025",
}
def check_start(start):
    if start not in WINDOWS:raise ValueError("Only preregistered four real seven-day UTC windows")
    return datetime.fromisoformat(start.replace("Z","+00:00"))

def summarize(rows):
    if len(rows)!=7*24*4:raise ValueError("Require 672 real BA-hour source records")
    result=[];daily=[]
    for ba in BAS:
        samples=[r for r in rows if r["BA"]==ba]
        if len(samples)!=168:raise ValueError("Incomplete hourly BA exposure")
        values=[float(r["C_minus_B_celsius"]) for r in samples]
        by_day=defaultdict(list)
        for r in samples:
            by_day[r["UTC_timestamp"][:10]].append(float(r["C_minus_B_celsius"]))
        if len(by_day)!=7 or any(len(v)!=24 for v in by_day.values()):
            raise ValueError("Missing real 24-hour day in BA")
        for day,v in sorted(by_day.items()):
            daily.append({"BA":ba,"UTC_day":day,"hours":24,
                "mean_C_minus_B_c":round(statistics.mean(v),6),
                "hours_C_warmer_than_B":sum(x>0 for x in v),
                "geometry_approved":False,"model_training_permitted":False})
        means=[statistics.mean(v) for v in by_day.values()]
        result.append({"BA":ba,"observed_UTC_hours":168,
            "mean_C_minus_B_c":round(statistics.mean(values),6),
            "median_C_minus_B_c":round(statistics.median(values),6),
            "minimum_C_minus_B_c":min(values),
            "maximum_C_minus_B_c":max(values),
            "hours_C_warmer_than_B":sum(v>0 for v in values),
            "days_C_mean_warmer_than_B":sum(x>0 for x in means),
            "geometry_approved":False,
            "model_training_permitted":False})
    return result,daily

def run(start,af,bf,cf,cm,out):
    begin=check_start(start)
    hashes={tag:hashlib.sha256(Path(f).read_bytes()).hexdigest()
            for tag,f in zip("ABC",(af,bf,cf))}
    if hashes!={"A":A_SHA,"B":B_SHA,"C":C_SHA}:
        raise ValueError("A/B/C source weight SHA256 drift")
    manifest=json.loads(Path(cm).read_text())
    if (manifest.get("weight_csv_sha256")!=C_SHA or
        manifest.get("census2020_variable")!="ESTIMATESBASE2020" or
        manifest.get("population_is_original_decennial_PL_P1_001N") is not False or
        manifest.get("actual_customers_or_load_distribution_observed") is not False or
        manifest.get("county_proxy_geography_approved") is not False or
        manifest.get("model_training_permitted") is not False):
        raise ValueError("Unapproved Census population estimate-base source not verified")
    groups={}
    for tag,f in zip("ABC",(af,bf,cf)):
        source=load_exploratory_weights(f)
        groups.update({tag+"_"+ba:source[ba] for ba in BAS})
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    csvpath=output/"REAL_ERA5_ABC_SEVENDAY_672_BA_HOURS.csv"
    allrows=[]
    with csvpath.open("w",newline="") as file:
        writer=None
        for d in range(7):
            date=(begin+timedelta(days=d)).strftime("%Y-%m-%dT00:00:00Z")
            raw,source=calculate_24(ds,groups,date)
            if (source.get("row_count")!=288 or
                source.get("contiguous_UTC_hours_verified") is not True or
                source.get("historical_geography_admitted") is not False):
                raise ValueError("Day source incomplete or falsely approved")
            joined=normalize_day(raw,date)
            if len(joined)!=96:raise ValueError("Missing 24 h x four BA")
            if writer is None:
                writer=csv.DictWriter(file,fieldnames=list(joined[0]))
                writer.writeheader()
            writer.writerows(joined);file.flush()
            allrows.extend(joined)
            print("REAL_ERA5_ABC_SEVENDAY_DAY",json.dumps({
                "day":date,"actual_matched_BA_hours":len(joined),
                "common_ERA5_grid_cells_per_hour":source["source_grid_cells_per_hour"],
                "model_training_permitted":False}),flush=True)
    expected={(ba,begin+timedelta(hours=h))
              for ba in BAS for h in range(168)}
    observed={(r["BA"],datetime.fromisoformat(r["UTC_timestamp"].replace("Z","+00:00")))
              for r in allrows}
    if len(observed)!=672 or observed!=expected:
        raise ValueError("Exact BA×UTC hour coverage incomplete")
    result,daily=summarize(allrows)
    for file,records in (("REAL_ERA5_ABC_SEVENDAY_BA_SUMMARY.csv",result),
                         ("REAL_ERA5_ABC_SEVENDAY_DAILY_SUMMARY.csv",daily)):
        with (output/file).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    meta={"UTC_window_start":start,"selected_window":WINDOWS[start],
        "source_days":7,"real_matched_BA_hours":len(allrows),
        "source":"public genuine Google ARCO ERA5 hourly 2m temperature",
        "A_B_C_source_weights_SHA256":hashes,
        "C_population_source":"CO-EST2025 ESTIMATESBASE2020, not actual customers",
        "county_polygon_vintage":2024,"year_vintage_mismatch_acknowledged":True,
        "actual_ERA5_CSV_SHA256":hashlib.sha256(csvpath.read_bytes()).hexdigest(),
        "BA_summary":result,"BA_daily_summary_rows":len(daily),
        "geometry_approved":False,"model_training_permitted":False,
        "climate_change_attribution_done":False,
        "hourly_rows_not_independent_statistical_units":True}
    (output/"REAL_ERA5_ABC_SEVENDAY_SOURCE_MANIFEST.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("REAL_ERA5_ABC_7DAY_SUMMARY",json.dumps(meta),flush=True)
    return meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True)
    p.add_argument("--A",required=True);p.add_argument("--B",required=True)
    p.add_argument("--C",required=True);p.add_argument("--C-manifest",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.start,a.A,a.B,a.C,a.C_manifest,a.out)
if __name__=="__main__":main()
