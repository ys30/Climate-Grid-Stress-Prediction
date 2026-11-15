"""Independently verify four seven-day original ERA5 A/B source artifacts.

Four selected weeks are a designed weather spatial-sensitivity diagnostic,
not 28 independent weeks, an authorized BA weather exposure, or model data.
"""
import argparse,csv,json,statistics
from pathlib import Path
from datetime import datetime,timedelta

BAS=("AZPS","BPAT","CISO","SRP")
EXPECTED=("2023-01-15T00:00:00Z","2023-07-01T00:00:00Z",
          "2025-01-15T00:00:00Z","2025-07-01T00:00:00Z")
A_SHA="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"
B_SHA="6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8"
DATA="REAL_ERA5_7DAY_HIFLD_Census_AB_HOURLY_UNAPPROVED.csv"
META="REAL_ERA5_7DAY_AB_SOURCE_MANIFEST.json"

def reconcile(folders):
    by_start={};output=[]
    for path in folders:
        path=Path(path)
        meta=json.loads((path/META).read_text())
        start=meta["source_start_UTC"]
        if start not in EXPECTED or start in by_start:raise ValueError("Unexpected or duplicated source week")
        if meta.get("days")!=7 or meta.get("observed_BA_hours")!=672:
            raise ValueError("Missing 7day source-hour accounting")
        if (meta.get("HIFLD_A_weights_SHA256")!=A_SHA or
            meta.get("Census_B_weights_SHA256")!=B_SHA):
            raise ValueError("Source BA geometry weights changed")
        if (meta.get("official_historical_BA_geography_approved") is not False or
            meta.get("model_training_permitted") is not False or
            meta.get("anthropogenic_climate_attribution_performed") is not False):
            raise ValueError("Real ERA5 source proxy must remain unapproved")
        with (path/DATA).open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
        if len(rows)!=672:raise ValueError("Not exactly 672 BA hours in source CSV")
        begin=datetime.fromisoformat(start.replace("Z","+00:00"))
        observed=set()
        for r in rows:
            stamp=datetime.fromisoformat(r["timestamp_utc_start"].replace("Z","+00:00"))
            key=(r["ba"],stamp)
            if key in observed:raise ValueError("Duplicate BA-UTC source key")
            observed.add(key)
            if r["historical_geography_approved"]!="False" or r["training_permitted"]!="False":
                raise ValueError("False row-level geography/model authorization")
            d=float(r["Census_minus_HIFLD_celsius"])
            calculated=float(r["Census_2024_county_proxy_celsius"])-float(r["HIFLD_2018_candidate_celsius"])
            if abs(d-calculated)>0.000002:raise ValueError("Source temperature difference inconsistent")
            output.append({"source_start_UTC":start,**r})
        expect={(ba,begin+timedelta(hours=h)) for ba in BAS for h in range(168)}
        if observed!=expect:raise ValueError("Incomplete exact BA hourly source coverage")
        by_start[start]=meta
    if set(by_start)!=set(EXPECTED):raise ValueError("Require four original verified seasonal weekly windows")
    statistics_out=[]
    for ba in BAS:
        values=[float(r["Census_minus_HIFLD_celsius"]) for r in output if r["ba"]==ba]
        if len(values)!=672:raise ValueError("Missing BA real source window")
        statistics_out.append({"ba":ba,"observed_hours":len(values),
            "mean_B_minus_A_celsius":round(statistics.mean(values),6),
            "median_B_minus_A_celsius":round(statistics.median(values),6),
            "min_B_minus_A_celsius":min(values),
            "max_B_minus_A_celsius":max(values),
            "negative_hours":sum(v<0 for v in values),
            "positive_hours":sum(v>0 for v in values),
            "historical_geography_approved":False,
            "model_training_permitted":False})
    return sorted(output,key=lambda r:(r["source_start_UTC"],r["timestamp_utc_start"],r["ba"])),statistics_out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-folders",required=True,nargs="+")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    rows,stats=reconcile(a.source_folders)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for name,data in (("REAL_ERA5_2688_BA_HOURLY_AB.csv",rows),
                      ("REAL_ERA5_2688_BA_AB_SUMMARY.csv",stats)):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    metadata={"source_days":list(EXPECTED),"source_seven_day_windows":4,
        "actual_BA_hour_comparisons":len(rows),"source_HIFLD_weights_sha256":A_SHA,
        "source_Census_weights_sha256":B_SHA,"per_BA":stats,
        "real_source":"public hourly ARCO ERA5 2m temperature reanalysis",
        "independent_hour_assumption":False,
        "historical_BA_geography_approved":False,
        "demand_model_training_permitted":False,
        "anthropogenic_climate_attribution_performed":False}
    (out/"REAL_ERA5_4WEEK_AB_PROVENANCE.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print("REAL_ERA5_4WEEK_AB_SUMMARY",json.dumps(metadata),flush=True)
if __name__=="__main__":main()
