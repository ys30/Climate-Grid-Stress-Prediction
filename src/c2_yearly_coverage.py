"""E0 calendar-year EIA-930 raw-demand inventory using both official half-year CSVs.

Year-specific source snapshots are provenance-verified by SHA256. Report missing
BA-hour rows; never impute and never call reporting QA an outage validation.
"""
import argparse,csv,hashlib,json,subprocess,tempfile
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path

BAS=("AZPS","BPAT","CISO","SRP")
REQUIRED={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
SOURCE="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_"
FMT="%m/%d/%Y %I:%M:%S %p"

def expected_hours(year):
    first=datetime(year,1,1,tzinfo=timezone.utc)
    last=datetime(year+1,1,1,tzinfo=timezone.utc)
    return int((last-first).total_seconds()//3600)

def analyze_files(files,year):
    """Stream rows from official unmodified CSVs, checking duplicates and source categories."""
    first=datetime(year,1,1,tzinfo=timezone.utc)
    last=datetime(year+1,1,1,tzinfo=timezone.utc)
    stats={ba:{"observed_keys":0,"valid_values":0,"blank_or_invalid":0,
               "duplicate_keys":0,"min_mw":None,"max_mw":None} for ba in BAS}
    seen=set()
    for name in files:
        with open(name,newline="",encoding="utf-8-sig") as stream:
            reader=csv.DictReader(stream)
            if not REQUIRED.issubset(reader.fieldnames or []):
                raise ValueError(f"Official demand columns absent from {name}")
            for row in reader:
                ba=(row.get("Balancing Authority") or "").strip()
                if ba not in BAS:continue
                try:
                    end=datetime.strptime(row["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)
                except (ValueError,AttributeError) as exc:
                    raise ValueError(f"Malformed official time in {name}") from exc
                t=end-timedelta(hours=1)
                if not first<=t<last:continue
                key=(ba,t)
                st=stats[ba]
                if key in seen:
                    st["duplicate_keys"]+=1
                    continue
                seen.add(key)
                st["observed_keys"]+=1
                raw=(row.get("Demand (MW)") or "").strip()
                try:
                    val=float(raw)
                    if not 0<=val<float("inf"):raise ValueError()
                except ValueError:
                    st["blank_or_invalid"]+=1
                    continue
                st["valid_values"]+=1
                st["min_mw"]=val if st["min_mw"] is None else min(st["min_mw"],val)
                st["max_mw"]=val if st["max_mw"] is None else max(st["max_mw"],val)
    expected=expected_hours(year)
    rows=[]
    for ba in BAS:
        item=stats[ba]
        item.update({"year":year,"ba":ba,"expected_hours":expected,
                     "missing_hour_keys":expected-item["observed_keys"],
                     "valid_coverage_ratio":round(item["valid_values"]/expected,6),
                     "complete":item["valid_values"]==expected and item["duplicate_keys"]==0})
        rows.append(item)
    return rows

def sha256_file(file):
    digest=hashlib.sha256()
    with open(file,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),""):digest.update(chunk)
    return digest.hexdigest()

def run(years,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    all_rows=[];sources=[];failures=[]
    with tempfile.TemporaryDirectory() as root:
        for year in years:
            inputs=[]
            print(f"BEGIN YEAR {year}",flush=True)
            for part in ("Jan_Jun","Jul_Dec"):
                url=f"{SOURCE}{year}_{part}.csv"
                dest=Path(root)/f"{year}_{part}.csv"
                try:
                    subprocess.run(["curl","--fail","--location","--silent","--show-error",
                                    "--connect-timeout","15","--max-time","150",
                                    "--retry","1","--output",str(dest),url],
                                   check=True,timeout=180)
                    print(f"DOWNLOADED {year} {part}: {dest.stat().st_size} bytes",flush=True)
                    if dest.stat().st_size<1000:raise ValueError("Unexpectedly small CSV")
                    sources.append({"year":year,"half":part,"url":url,"bytes":dest.stat().st_size,
                                    "sha256":sha256_file(dest)})
                    inputs.append(dest)
                except Exception as exc:
                    failures.append({"year":year,"half":part,"error_type":type(exc).__name__,
                                     "message":str(exc)[:250]})
            if len(inputs)==2:
                try:
                    all_rows.extend(analyze_files(inputs,year))
                    print(f"AUDITED YEAR {year}: {len(all_rows)} total BA rows",flush=True)
                except (ValueError,KeyError) as exc:
                    failures.append({"year":year,"error_type":type(exc).__name__,
                                     "message":str(exc)[:250]})
    columns=["year","ba","expected_hours","observed_keys","valid_values","missing_hour_keys",
             "blank_or_invalid","duplicate_keys","valid_coverage_ratio","complete","min_mw","max_mw"]
    with (out/"annual_ba_coverage.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(all_rows)
    report={"status":"observational_source_coverage_only_no_attribution_or_forecast",
            "years_requested":years,"source_files":sources,"rows_audited":len(all_rows),
            "download_or_parsing_failures":failures,
            "full_years_all_four_bas":[year for year in years if
              sum(x["complete"] for x in all_rows if x["year"]==year)==len(BAS)],
            "clock":"EIA-930 end-hour UTC converted to UTC interval-start (-1 h)",
            "no_imputation":True}
    (out/"annual_coverage_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"rows_audited":len(all_rows),"failures":failures,
                      "full_years_all_four_bas":report["full_years_all_four_bas"],
                      "coverage":all_rows},indent=2))
    if failures:raise SystemExit("One or more official sources unavailable or unparseable")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--years",nargs="+",type=int,default=[2023,2024])
    p.add_argument("--out",default="outputs/e0_years")
    a=p.parse_args()
    if any(y<2015 or y>2026 for y in a.years):raise ValueError("Invalid EIA-930 year")
    run(a.years,a.out)
