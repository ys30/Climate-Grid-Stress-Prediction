"""Compare archived RAW EIA-930 balance hourly demand (NOT PUDL-imputed)."""
import argparse,csv,hashlib,io,json,urllib.request,zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path

SOURCES={
  "2025-06-archive":("15568995","691d52a09eff623571a4f18d504c0d25"),
  "2025-11-v53":("17688027","122e5d253321b7baef657a4880f9a579"),
  "2026-09-v92":("22215263","1b4acef4e1ec596cf92e7658f9be64c7")}
FIRST=datetime(2023,2,26,20,tzinfo=timezone.utc)
HOURS=11
FORMAT="%m/%d/%Y %I:%M:%S %p"
ORIGINAL={"2023-02-26T22:00:00Z":2958,
          "2023-02-26T23:00:00Z":68520,
          "2023-02-27T00:00:00Z":45097,
          "2023-02-27T01:00:00Z":27030,
          "2023-02-27T02:00:00Z":3578}

def get_zip(label,download_dir):
    record,expected_md5=SOURCES[label]
    path=Path(download_dir)/(record+"-2023half1.zip")
    if not path.exists():
        url=f"https://zenodo.org/records/{record}/files/eia930-2023half1.zip?download=1"
        req=urllib.request.Request(url,headers={"User-Agent":"C2-EIA930-vintage-audit/1.0"})
        with urllib.request.urlopen(req,timeout=180) as response:
            raw=response.read()
        if hashlib.md5(raw).hexdigest()!=expected_md5:
            raise ValueError("Pinned raw ZIP MD5 mismatch before save: "+label)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
    raw=path.read_bytes()
    if hashlib.md5(raw).hexdigest()!=expected_md5:
        raise ValueError("Pinned raw ZIP MD5 mismatch: "+label)
    return raw

def archived_balance_digest(raw):
    """Hash uncompressed raw source balance CSV, distinguishing ZIP metadata from data changes."""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names=[n for n in archive.namelist() if n.lower().endswith("-balance.csv")]
        if len(names)!=1:
            raise ValueError("Raw archive must have one balance CSV")
        with archive.open(names[0]) as f:
            sha=hashlib.sha256()
            size=0
            while True:
                chunk=f.read(1024*1024)
                if not chunk:
                    break
                sha.update(chunk)
                size+=len(chunk)
        if size==0:
            raise ValueError("Raw balance CSV is empty")
        return {"filename":names[0],"balance_csv_sha256":sha.hexdigest(),"uncompressed_bytes":size}

def read_srp(raw):
    found={}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names=[n for n in archive.namelist() if n.lower().endswith("-balance.csv")]
        if len(names)!=1:
            raise ValueError("Raw archive must have one balance CSV")
        with archive.open(names[0]) as stream:
            reader=csv.DictReader(io.TextIOWrapper(stream,encoding="utf-8-sig",newline=""))
            required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("Not a raw EIA-930 balance CSV")
            for row in reader:
                if (row.get("Balancing Authority") or "").strip()!="SRP":continue
                ending=datetime.strptime(row["UTC Time at End of Hour"].strip(),FORMAT).replace(tzinfo=timezone.utc)
                start=ending-timedelta(hours=1)
                if start<FIRST or start>=FIRST+timedelta(hours=HOURS):continue
                key=start.strftime("%Y-%m-%dT%H:%M:%SZ")
                if key in found:raise ValueError("Duplicate SRP UTC hour-ending source")
                value=row["Demand (MW)"].strip()
                found[key]=None if not value else float(value)
    return found

def compare(snapshots):
    values={label:read_srp(raw) for label,raw in snapshots.items()}
    rows=[]
    for offset in range(HOURS):
        start=FIRST+timedelta(hours=offset)
        end=start+timedelta(hours=1)
        key=start.strftime("%Y-%m-%dT%H:%M:%SZ")
        a=values["2025-11-v53"].get(key)
        b=values["2026-09-v92"].get(key)
        orig=ORIGINAL.get(key)
        early=values.get("2025-06-archive",{}).get(key)
        rows.append({"utc_interval_start":key,"utc_hour_ending":end.strftime("%Y-%m-%dT%H:%M:%SZ"),
          "pudl_2025june_demand_mw":early,
          "pudl_2025v53_demand_mw":a,"pudl_2026v92_demand_mw":b,
          "june_to_nov_demand_changed":early!=a if early is not None and a is not None else None,
          "project_source_panel_demand_mw":orig,
          "historic_vintage_value_changed":a!=b if a is not None and b is not None else None,
          "matches_existing_project_source_v53":a==orig if a is not None and orig is not None else None,
          "matches_existing_project_source_v92":b==orig if b is not None and orig is not None else None})
    paired=[r for r in rows if r["historic_vintage_value_changed"] is not None]
    early_paired=[r for r in rows if r["june_to_nov_demand_changed"] is not None]
    return rows,{"n_hours":HOURS,"n_paired":len(paired),
      "earliest_archive_comparison_available":"2025-06-archive" in snapshots,
      "n_june_nov_paired":len(early_paired),
      "n_changed_demand_hours_june_to_nov":sum(r["june_to_nov_demand_changed"] for r in early_paired),
      "all_hours_present_in_three_sources":len(early_paired)==HOURS and len(paired)==HOURS,
      "n_changed_original_demand_hours":sum(r["historic_vintage_value_changed"] for r in paired),
      "all_hours_present_in_both_sources":all(
         r["pudl_2025v53_demand_mw"] is not None and r["pudl_2026v92_demand_mw"] is not None for r in rows),
      "original_source_values_modified":False,"E2_training_permitted":False,
      "source_archive_hash_difference_alone_proves_hourly_revision":False,
      "sources":{k:{"zenodo_record":SOURCES[k][0],"pinned_zip_md5":SOURCES[k][1],
         "download_zip_sha256":hashlib.sha256(v).hexdigest(),
         **archived_balance_digest(v)} for k,v in snapshots.items()},
      "original_balance_files_identical":archived_balance_digest(snapshots["2025-11-v53"])["balance_csv_sha256"]==archived_balance_digest(snapshots["2026-09-v92"])["balance_csv_sha256"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cache",default="inputs/pudl_vintages")
    p.add_argument("--out",default="outputs/srp_vintage")
    args=p.parse_args()
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    snapshots={}
    for name in SOURCES:
        try:
            snapshots[name]=get_zip(name,args.cache)
        except Exception as exc:
            # Upload the failure evidence from Actions even when a remote archive
            # is unreachable or no longer matches its published checksum.
            issue={
                "stage":"download_or_archive_hash_verification",
                "failed_vintage":name,
                "source_record":SOURCES[name][0],
                "exception_type":type(exc).__name__,
                "reason":str(exc)[:400],
                "archives_verified_before_failure":list(snapshots),
                "E2_training_permitted":False
            }
            (dest/"C2_SRP_VINTAGE_FETCH_FAILURE_QA.json").write_text(
                json.dumps(issue,indent=2)+"\n")
            raise
    rows,report=compare(snapshots)
    with (dest/"C2_SRP_2023_FEB_THREE_SOURCE_VINTAGES.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (dest/"C2_SRP_2023_FEB_VINTAGE_QA.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PUDL_EIA930_VINTAGE_COMPARE",json.dumps(report),flush=True)
    if not report["all_hours_present_in_three_sources"]:
        raise SystemExit("Missing SRP original source hour in at least one of three historical archives")

if __name__=="__main__":main()
