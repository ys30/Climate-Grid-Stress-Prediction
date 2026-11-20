"""Pair one authenticated EIA-930 CISO day and public ARCO ERA5 grid day.

Inputs are the existing independently verified Actions ZIPs. This code
does not substitute a single ERA5 grid cell for CISO BA-wide exposure.
"""
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path

EIA_CSV="utc_start/eia930_CISO_2024_start.csv"
EIA_MANIFEST="utc_start/eia930_CISO_2024_start.manifest.json"
ARCO_CSV="arco_2024_02_01_sacramento_single_gridcell.csv"
ARCO_MANIFEST="arco_2024_02_01_sacramento_single_gridcell.manifest.json"
EIA_SHA="375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c"
ARCO_SHA="5f3b5cbce41c0f60d75af9401cdac25b9c7262c088ed6e4fc8f4785d632f48fd"


def read_verified(zpath,csv_name,manifest_name,expected_sha):
    with zipfile.ZipFile(zpath) as z:
        data=z.read(csv_name)
        manifest=json.loads(z.read(manifest_name))
    sha=hashlib.sha256(data).hexdigest()
    if sha!=expected_sha or manifest.get("sha256_csv")!=sha:
        raise ValueError("Source byte SHA mismatch; no join")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    return rows,manifest


def pair(eia_zip,arco_zip,output):
    output=Path(output)
    if output.exists() or output.with_suffix(".manifest.json").exists():
        raise FileExistsError("Do not overwrite prior paired-vintage evidence")
    eia,em=read_verified(eia_zip,EIA_CSV,EIA_MANIFEST,EIA_SHA)
    arco,wm=read_verified(arco_zip,ARCO_CSV,ARCO_MANIFEST,ARCO_SHA)
    if em.get("target_year")!=2024 or em.get("clock_conversion")!="UTC_hour_ending_minus_one_hour":
        raise ValueError("Unverified EIA UTC hour-ending conversion")
    if wm.get("source_kind")!="public_ARCO_ERA5_Zarr_one_gridcell" or wm.get("ba_exposure_qualified") is not False:
        raise ValueError("Unqualified or mislabeled ARCO source")
    if wm.get("clock")!="UTC_instantaneous_valid_time_not_EIA_hour_ending":
        raise ValueError("ARCO weather time reference not established")
    e={}
    for r in eia:
        t=r["timestamp_utc"]
        if t.startswith("2024-02-01T"):
            if t in e or r["ba"]!="CISO" or not r["demand_mw"].strip():
                raise ValueError("Missing or duplicate CISO load day")
            e[t]=r
    w={}
    for r in arco:
        t=r["timestamp_utc"]
        if t in w: raise ValueError("Duplicate ARCO time")
        w[t]=r
    from datetime import datetime,timedelta,timezone
    first=datetime(2024,2,1,tzinfo=timezone.utc)
    expected={(first+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(24)}
    if set(e)!=expected or set(w)!=expected:
        raise ValueError("Expected complete common 24 UTC hours, no filling")
    rows=[{"timestamp_utc":t,"ciso_demand_mw":e[t]["demand_mw"],
           "sacramento_grid_t2m_c":w[t]["temperature_c"],
           "original_eia_hour_ending_utc":e[t]["original_source_he_utc"]}
           for t in sorted(expected)]
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    report={
        "status":"OBSERVED_SAME_UTC_HOUR_DIAGNOSTIC_NOT_CISO_BA_WEATHER_EXPOSURE",
        "hours":24,"year":2024,"date":"2024-02-01",
        "eia_2024_csv_sha256":EIA_SHA,"arco_gridday_csv_sha256":ARCO_SHA,
        "joined_csv_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "eia_evidence":"GitHub Actions 44427373589; artifact 14486655626",
        "arco_evidence":"GitHub Actions 44678645391; artifact 14605122303",
        "weather_grid":"38.5N 121.5W; point gridcell only",
        "eia_clock":"UTC interval start from source HE -1 hour",
        "era5_clock":"original UTC instantaneous validity timestamp; not shifted",
        "spatial_limitation":"Single gridpoint is not established CISO BA weather exposure",
        "model_skill_computed":False,"causal_claim":False
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("eia_artifact_zip",type=Path)
    p.add_argument("arco_artifact_zip",type=Path)
    p.add_argument("output_csv",type=Path)
    a=p.parse_args()
    print(json.dumps(pair(a.eia_artifact_zip,a.arco_artifact_zip,a.output_csv),indent=2))


if __name__=="__main__":
    main()
