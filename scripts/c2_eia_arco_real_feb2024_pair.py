"""Join SHA-pinned real CISO EIA 2024 and February public ARCO ERA5 ZIPs.

This is an hourly *source-clock* diagnostic. A near-Sacramento single
gridpoint MUST NOT be used as a qualified CISO BA-wide temperature proxy.
"""
from __future__ import annotations
import argparse,calendar,csv,hashlib,io,json,math,zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path

EIA_SHA="375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c"
WEATHER_SHA="b572cfd5c2c5df6025f6e4f54b4e4ec97ab261c8c0d53dae1ec18e37b98c9a75"


def read(zpath,csvname,manifestname,expected_sha):
    with zipfile.ZipFile(zpath) as archive:
        raw=archive.read(csvname)
        manifest=json.loads(archive.read(manifestname))
    if hashlib.sha256(raw).hexdigest()!=expected_sha or manifest.get("sha256_csv")!=expected_sha:
        raise ValueError("Input archive SHA or source manifest mismatch")
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))),manifest


def join(eia_zip,weather_zip,output):
    output=Path(output)
    if output.exists() or output.with_suffix(".manifest.json").exists():
        raise FileExistsError("Never overwrite observed paired data or manifest")
    eia,em=read(eia_zip,"utc_start/eia930_CISO_2024_start.csv",
                "utc_start/eia930_CISO_2024_start.manifest.json",EIA_SHA)
    weather,wm=read(weather_zip,"arco_2024_02_sacramento_single_gridcell.csv",
                    "arco_2024_02_sacramento_single_gridcell.manifest.json",WEATHER_SHA)
    if em.get("target_year")!=2024 or em.get("clock_conversion")!="UTC_hour_ending_minus_one_hour":
        raise ValueError("EIA time provenance missing")
    if wm.get("source_kind")!="public_ARCO_ERA5_Zarr_single_gridcell_month":
        raise ValueError("Weather source identity mismatch")
    if wm.get("clock")!="UTC_instantaneous_valid_time_not_EIA_hour_ending":
        raise ValueError("ERA5 UTC validity definition absent")
    if wm.get("is_CISO_BA_weather_exposure") is not False or wm.get("eia_join_executed") is not False:
        raise ValueError("Only unqualified one-cell weather is eligible for this diagnostic")
    first=datetime(2024,2,1,tzinfo=timezone.utc)
    expected=[(first+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
              for i in range(calendar.monthrange(2024,2)[1]*24)]
    loads={}
    for r in eia:
        ts=r["timestamp_utc"]
        if ts.startswith("2024-02-"):
            if ts in loads or r["ba"]!="CISO":
                raise ValueError("Duplicate/wrong EIA BA hour")
            label=datetime.strptime(r["original_source_he_utc"],"%Y-%m-%dT%H")
            if (label-timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")!=ts:
                raise ValueError("EIA original HE + UTC-start clock disagreement")
            value=float(r["demand_mw"])
            if not math.isfinite(value) or value<0:
                raise ValueError("Missing or invalid EIA demand")
            loads[ts]=r
    if set(loads)!=set(expected):
        raise ValueError("EIA lacks one or more 696 real February UTC hours")
    if len(weather)!=len(expected) or [r["timestamp_utc"] for r in weather]!=expected:
        raise ValueError("ERA5 lacks a continuous complete February UTC timeline")
    rows=[]
    for wr in weather:
        ts=wr["timestamp_utc"]
        temperature=float(wr["temperature_c"])
        if not math.isfinite(temperature) or not -100<temperature<70:
            raise ValueError("Invalid original ERA5 grid temperature")
        er=loads[ts]
        rows.append({"timestamp_utc":ts,"ciso_demand_mw":er["demand_mw"],
                     "sacramento_grid_t2m_c":wr["temperature_c"],
                     "original_eia_hour_ending_utc":er["original_source_he_utc"]})
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    report={"source_kind":"EIA930_ARCO_ERA5_FEB2024_SINGLE_GRIDCELL_DIAGNOSTIC",
            "matched_hours":len(rows),"year":2024,"month":2,
            "eia_source_sha256":EIA_SHA,"weather_source_sha256":WEATHER_SHA,
            "joined_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
            "ciso_ba_weather_proxy_qualified":False,
            "model_validation_performed":False,"causal_attribution_performed":False,
            "claim_status":"UTC matching of authentic sources only; no BA-wide spatial exposure"}
    output.with_suffix(".manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("eia_zip",type=Path)
    p.add_argument("weather_zip",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    print(json.dumps(join(a.eia_zip,a.weather_zip,a.output),indent=2))

if __name__=="__main__":
    main()
