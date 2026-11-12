"""E0 official six-month CSV source gate; raw reported hourly BA demand only."""
import argparse,csv,hashlib,json
from datetime import datetime,timedelta,timezone
from io import StringIO
from pathlib import Path
from urllib.request import Request,urlopen
BAS=("AZPS","BPAT","CISO","SRP")
TIME_FORMAT="%m/%d/%Y %I:%M:%S %p"
BASE="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
REQUIRED=("Balancing Authority","UTC Time at End of Hour","Demand (MW)")

def extract_text(text,start,end):
    first=datetime.fromisoformat(start.replace("Z","+00:00"))
    last=datetime.fromisoformat(end.replace("Z","+00:00"))
    if first.tzinfo is None or last.tzinfo is None:
        raise ValueError("Specify timezone-aware UTC start and end")
    first,last=first.astimezone(timezone.utc),last.astimezone(timezone.utc)
    expected=set()
    t=first
    while t<=last:
        for ba in BAS: expected.add((t,ba))
        t+=timedelta(hours=1)
    reader=csv.DictReader(StringIO(text))
    if not set(REQUIRED).issubset(reader.fieldnames or []):
        raise ValueError("Unexpected EIA-930 balance CSV header")
    rows={}
    duplicated=0
    blanks=0
    for row in reader:
        ba=row["Balancing Authority"].strip()
        if ba not in BAS: continue
        stamp=datetime.strptime(row["UTC Time at End of Hour"].strip(),TIME_FORMAT).replace(tzinfo=timezone.utc)
        interval_start=stamp-timedelta(hours=1)
        key=(interval_start,ba)
        if key not in expected: continue
        if key in rows: duplicated+=1
        raw=row["Demand (MW)"].strip()
        if not raw:
            blanks+=1
            rows[key]=None
            continue
        try:
            v=float(raw)
            if not 0<=v<float("inf"):raise ValueError("Invalid finite nonnegative demand")
            rows[key]=v
        except ValueError: rows[key]=None;blanks+=1
    missing=len(expected-set(rows))
    clean=[(t,ba,v) for (t,ba),v in sorted(rows.items()) if v is not None]
    return {"expected_rows":len(expected),"observed_keys":len(rows),
            "valid_rows":len(clean),"missing_keys":missing,"duplicate_keys":duplicated,
            "blank_or_invalid":blanks,"coverage_complete":not(missing or duplicated or blanks) and len(clean)==len(expected)},clean

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--half",default="2024_Jul_Dec")
    p.add_argument("--start",default="2024-07-01T00:00:00+00:00")
    p.add_argument("--end",default="2024-07-01T23:00:00+00:00")
    p.add_argument("--out",default="outputs/e0")
    a=p.parse_args()
    if not all(c.isalnum() or c=="_" for c in a.half):raise ValueError("Unsafe half-year name")
    url=BASE+f"EIA930_BALANCE_{a.half}.csv"
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=180) as response:
        raw=response.read()
    if len(raw)<1000: raise ValueError("Unexpectedly small official EIA CSV")
    report,rows=extract_text(raw.decode("utf-8-sig"),a.start,a.end)
    report.update({"source_url":url,"source_sha256":hashlib.sha256(raw).hexdigest(),
                   "source_bytes":len(raw),"source_clock":"hour-ending UTC to interval start (-1h)",
                   "status":"raw_observed_demand_intake_not_prediction_or_outage_validation"})
    (out/"official_source_report.json").write_text(json.dumps(report,indent=2)+"\n")
    with (out/"verified_hourly_demand.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["timestamp_utc_start","ba","demand_mw"])
        for t,ba,v in rows:w.writerow([t.isoformat(),ba,v])
    print(json.dumps(report,indent=2))
    if not report["coverage_complete"]:raise SystemExit("Source completeness gate did not pass")
if __name__=="__main__":main()
