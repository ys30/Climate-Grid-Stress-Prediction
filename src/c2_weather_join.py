"""C2 E1 join contract: EIA-930 reported BA demand x audited UTC weather exposure.

Input weather table must have independently verified BA-representative exposure
(e.g. ERA5 grid-area weighted), not illustrative single-city-point values.
This script only makes a complete-case join; it does not fetch weather or fit a model.
"""
import argparse,csv,json,math
from datetime import datetime,timezone
from pathlib import Path

DEMAND_COLS={"year","ba","timestamp_utc_start","raw_demand_mw","quarantine","model_eligible"}
WEATHER_COLS={"ba","timestamp_utc_start","temperature_2m_c","exposure_method","source_dataset"}

def utc_hour(value):
    stamp=datetime.fromisoformat(value.replace("Z","+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds()!=0:
        raise ValueError("UTC-aware source timestamps required")
    if stamp.minute or stamp.second or stamp.microsecond:
        raise ValueError("Hourly interval start required")
    return stamp.astimezone(timezone.utc).isoformat()

def read_rows(path,columns):
    with open(path,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not columns.issubset(reader.fieldnames or []):
            raise ValueError("Missing columns "+repr(columns-set(reader.fieldnames or [])))
        return list(reader)

def join(demand,weather):
    wx={}
    for x in weather:
        key=(x["ba"],utc_hour(x["timestamp_utc_start"]))
        if key in wx:raise ValueError("Duplicate weather BA-hour key")
        if x["exposure_method"] not in ("ba_area_weighted_era5","ba_load_weighted_era5"):
            raise ValueError("Unsupported weather exposure method (point stations not admissible)")
        if x["source_dataset"]!="ERA5":raise ValueError("Only audited ERA5 exposure is admissible")
        try:
            v=float(x["temperature_2m_c"])
            if not math.isfinite(v):raise ValueError()
        except ValueError:
            raise ValueError("Non-finite ERA5 temperature") from None
        wx[key]=v
    out=[];seen=set()
    audit={"demand_rows":len(demand),"eligible_rows":0,"quarantined":0,
           "missing_weather":0,"joined_rows":0,"excluded_missing_demand":0}
    for d in demand:
        key=(d["ba"],utc_hour(d["timestamp_utc_start"]))
        if key in seen:raise ValueError("Duplicate demand BA-hour key")
        seen.add(key)
        if d["quarantine"]=="True" or d["model_eligible"]!="True":
            audit["quarantined"]+=1
            continue
        try:
            load=float(d["raw_demand_mw"])
            if not math.isfinite(load) or load<0:raise ValueError()
        except ValueError:
            audit["excluded_missing_demand"]+=1
            continue
        audit["eligible_rows"]+=1
        if key not in wx:
            audit["missing_weather"]+=1
            continue
        stamp=datetime.fromisoformat(key[1])
        out.append({"year":int(d["year"]),"ba":d["ba"],"timestamp_utc_start":key[1],
                    "demand_mw":load,"temperature_2m_c":wx[key],
                    "utc_hour":stamp.hour,"utc_day_of_week":stamp.weekday(),
                    "utc_day_of_year":stamp.timetuple().tm_yday,
                    "weather_exposure_verified":True})
    audit["joined_rows"]=len(out)
    audit["complete_case_only"]=True
    audit["raw_data_imputed"]=False
    audit["trained_model"]=False
    return out,audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",required=True)
    p.add_argument("--weather",required=True)
    p.add_argument("--out",default="outputs/e1_join")
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    rows,qa=join(read_rows(a.demand,DEMAND_COLS),read_rows(a.weather,WEATHER_COLS))
    cols=["year","ba","timestamp_utc_start","demand_mw","temperature_2m_c",
          "utc_hour","utc_day_of_week","utc_day_of_year","weather_exposure_verified"]
    with (out/"complete_case_weather_demand.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    (out/"join_manifest.json").write_text(json.dumps(qa,indent=2)+"\n")
    print(json.dumps(qa,indent=2))
if __name__=="__main__":main()
