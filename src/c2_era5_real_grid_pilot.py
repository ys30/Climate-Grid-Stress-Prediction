"""Fetch real ARCO ERA5 hourly temperature at a small subset of grid cells.

This is a smoke test for weights-to-Zarr connectivity, NOT an estimate of
full-BA exposure. The subset is deliberately too small for model input.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
from collections import defaultdict
from src.c2_era5_public_probe import STORE,VARIABLE,sample_record

def select_cells(rows,per_ba=3):
    grouped=defaultdict(list)
    for row in rows:
        if row.get("research_status")!="exploratory_unapproved_geometry":
            raise ValueError("Expected unapproved experimental weights")
        grouped[row["ba"]].append(row)
    if set(grouped)!={"AZPS","BPAT","CISO","SRP"}:raise ValueError("Four BAs required")
    result=[]
    for ba,items in sorted(grouped.items()):
        weights=[float(x["weight"]) for x in items]
        if abs(sum(weights)-1)>1e-6:raise ValueError("All original weights must sum to 1")
        top=sorted(items,key=lambda x:-float(x["weight"]))[:per_ba]
        for row in top:
            result.append({"ba":ba,"latitude":float(row["latitude"]),
               "longitude_0_360":float(row["longitude_0_360"]),
               "original_full_polygon_weight":float(row["weight"]),
               "partial_pilot_not_BA_exposure":True})
    return result

def run(weights_path,at,output):
    import xarray as xr
    with open(weights_path,newline="") as f:
        selected=select_cells(list(csv.DictReader(f)))
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    observations=[]
    for r in selected:
        s=sample_record(ds,at,r["latitude"],r["longitude_0_360"])
        observations.append({**r,**s})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"real_era5_grid_sample_NOT_BA_EXPOSURE.json").write_text(json.dumps(observations,indent=2)+"\n")
    sha=hashlib.sha256(Path(weights_path).read_bytes()).hexdigest()
    report={"era5_store":STORE,"weight_input_sha256":sha,
       "utc_sample_time":at,"BAs":sorted({r["ba"] for r in observations}),
       "actual_source_cells":len(observations),
       "pilot_only":True,"full_area_weather_exposure_computed":False,
       "historical_BA_geometry_approved":False,"weather_demand_joined":False,
       "no_training_executed":True}
    (out/"pilot_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print("ERA5_GRID_PILOT",json.dumps(report))
    for r in observations:
        print("REAL_GRID_CELL",json.dumps({k:r[k] for k in ("ba","latitude","longitude_0_360","temperature_celsius","original_full_polygon_weight")}))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weights",required=True)
    p.add_argument("--time",default="2023-07-01T12:00:00Z")
    p.add_argument("--out",default="outputs/e1_real_grid_pilot")
    a=p.parse_args()
    run(a.weights,a.time,a.out)
if __name__=="__main__":main()
