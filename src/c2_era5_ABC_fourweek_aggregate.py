"""Independent audit of four archived real ERA5 A/B/C seven-day windows.

This source-only audit checks 2,688 real BA-hours, unique exact UTC
timestamps, arithmetic, Census population source weight SHA256s, and
unapproved research status. No meteorological proxy is BA-model-ready.
"""
import argparse,csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from src.c2_era5_ABC_sevenday import WINDOWS,BAS,A_SHA,B_SHA,C_SHA

SOURCE_FILE="REAL_ERA5_ABC_SEVENDAY_672_BA_HOURS.csv"
SOURCE_META="REAL_ERA5_ABC_SEVENDAY_SOURCE_MANIFEST.json"
def audit(folders):
    if len(folders)!=4:raise ValueError("Exactly four original 7-day artifacts required")
    seen={};rows=[]
    for folder in folders:
        folder=Path(folder)
        m=json.loads((folder/SOURCE_META).read_text())
        start=m["UTC_window_start"]
        if start not in WINDOWS or start in seen:
            raise ValueError("Unexpected or duplicate preregistered source window")
        if (m.get("real_matched_BA_hours")!=672 or m.get("source_days")!=7 or
            m.get("A_B_C_source_weights_SHA256")!={"A":A_SHA,"B":B_SHA,"C":C_SHA} or
            m.get("geometry_approved") is not False or
            m.get("model_training_permitted") is not False or
            m.get("climate_change_attribution_done") is not False):
            raise ValueError("Source window quality or admission manifest failed")
        file=folder/SOURCE_FILE
        if hashlib.sha256(file.read_bytes()).hexdigest()!=m["actual_ERA5_CSV_SHA256"]:
            raise ValueError("Source hourly CSV SHA256 not reproducible")
        with file.open(newline="") as f:items=list(csv.DictReader(f))
        if len(items)!=672:raise ValueError("Original source seven-day hourly count incorrect")
        keys=set();begin=datetime.fromisoformat(start.replace("Z","+00:00"))
        for item in items:
            timestamp=datetime.fromisoformat(item["UTC_timestamp"].replace("Z","+00:00"))
            ba=item["BA"]
            key=(ba,timestamp)
            if ba not in BAS or key in keys:
                raise ValueError("Duplicate or invalid BA-hour key")
            keys.add(key)
            if (item["historical_BA_geography_approved"]!="False" or
                item["training_permitted"]!="False" or
                item["population_is_customer_weights"]!="False"):
                raise ValueError("False customer or training authorization")
            a=float(item["HIFLD_A_celsius"])
            b=float(item["TIGER_B_celsius"])
            c=float(item["population_C_celsius"])
            for keyname,expected in (("C_minus_B_celsius",c-b),
                                     ("C_minus_A_celsius",c-a),
                                     ("B_minus_A_celsius",b-a)):
                if abs(float(item[keyname])-expected)>2.1e-6:
                    raise ValueError("Real-source proxy temperature difference failed")
            rows.append({"source_window":start,**item})
        expected={(ba,begin+timedelta(hours=h)) for ba in BAS for h in range(168)}
        if keys!=expected:raise ValueError("Real UTC 7-day source not contiguous")
        seen[start]=m
    if set(seen)!=set(WINDOWS):raise ValueError("Missing preregistered season/year source window")
    summaries=[]
    for ba in BAS:
        vals=[float(r["C_minus_B_celsius"]) for r in rows if r["BA"]==ba]
        days=defaultdict(list)
        for r in rows:
            if r["BA"]==ba:days[r["UTC_timestamp"][:10]].append(float(r["C_minus_B_celsius"]))
        if len(vals)!=672 or len(days)!=28 or any(len(v)!=24 for v in days.values()):
            raise ValueError("Not four exact 7-day BA source windows")
        summaries.append({"BA":ba,"real_BA_hours":672,
            "mean_C_minus_B_c":round(statistics.mean(vals),6),
            "median_C_minus_B_c":round(statistics.median(vals),6),
            "min_C_minus_B_c":min(vals),"max_C_minus_B_c":max(vals),
            "hours_C_warmer_than_B":sum(x>0 for x in vals),
            "days_C_mean_warmer_than_B":sum(statistics.mean(x)>0 for x in days.values()),
            "historical_BA_geography_approved":False,"model_training_permitted":False})
    return sorted(rows,key=lambda r:(r["source_window"],r["UTC_timestamp"],r["BA"])),summaries

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-folders",nargs="+",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    rows,summary=audit(a.source_folders)
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    for name,records in (("REAL_ERA5_ABC_2688_BA_HOURS.csv",rows),
                         ("REAL_ERA5_ABC_FOUR_WEEK_BA_SUMMARY.csv",summary)):
        with (output/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    manifest={"real_BA_hours":len(rows),"observed_four_weeks":list(WINDOWS),
        "frozen_source_weight_SHA256":{"A":A_SHA,"B":B_SHA,"C":C_SHA},
        "observed_source":"ARCO ERA5 2m real reanalysis",
        "population_source":"Census CO-EST2025 ESTIMATESBASE2020",
        "summary":summary,
        "BA_geography_approved":False,"electric_demand_model_training_permitted":False,
        "hourly_rows_are_independent_trials":False}
    (output/"REAL_ERA5_ABC_4WEEK_PROVENANCE.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("REAL_ERA5_ABC_FOUR_WEEK_SUMMARY",json.dumps(manifest),flush=True)
if __name__=="__main__":main()
