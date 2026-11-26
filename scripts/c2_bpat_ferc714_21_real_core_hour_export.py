#!/usr/bin/env python3
"""Export respondent 21 from pinned PUDL core FERC714 without imputation.

Returns derived source rows with provenance, NOT upstream full-Parquet original SHA
or independent BPA operator XLSX certification.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

RELEASE="v2026.10.0"
TABLE="core_ferc714__hourly_planning_area_demand"
FIELDS=("respondent_id_ferc714","report_date","datetime_utc","demand_mwh")
SOURCE_PREFIX={
    "s3": f"s3://pudl.catalyst.coop/{RELEASE}/",
    "https": f"https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/{RELEASE}/",
}

def uri(transport):
    if transport not in SOURCE_PREFIX:
        raise ValueError("Only approved fixed-release S3/HTTPS transport")
    return SOURCE_PREFIX[transport]+TABLE+".parquet"

def hashfile(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def normalized_hour(value):
    if isinstance(value,str):
        stamp=datetime.fromisoformat(value.replace("Z","+00:00"))
    elif isinstance(value,datetime):
        stamp=value
    else:
        raise ValueError("Non-datetime FERC UTC source hour")
    if stamp.tzinfo is not None:
        stamp=stamp.astimezone(timezone.utc)
    if stamp.minute or stamp.second or stamp.microsecond:
        raise ValueError("Non-hourly PUDL normalized time")
    return stamp.replace(tzinfo=timezone.utc)

def normalize_row(row):
    if len(row)!=4:
        raise ValueError("Core FERC714 wrong field count")
    respondent,report,stamp,mwh=row
    if respondent!=21:
        raise ValueError("Unexpected respondent, expected PUDL 21")
    if isinstance(report,(date,datetime)):
        date_str=report.date().isoformat() if isinstance(report,datetime) else report.isoformat()
    elif isinstance(report,str):
        date_str=date.fromisoformat(report[:10]).isoformat()
    else:
        raise ValueError("Invalid report date")
    if not 2020<=int(date_str[:4])<=2025:
        raise ValueError("Unexpected reporting year")
    hour=normalized_hour(stamp)
    if mwh is None:
        value=""
    else:
        numeric=float(mwh)
        if not math.isfinite(numeric) or numeric<0:
            raise ValueError("Nonfinite or negative observed core demand")
        value=format(numeric,".15g")
    return [str(respondent),date_str,hour.isoformat(),value]

def export(out,transport="https",connector=None):
    out=Path(out)
    if out.exists():
        raise FileExistsError("Refuse overwrite of original-source extract")
    out.mkdir(parents=True)
    provenance={
        "status":"FAILED","release":RELEASE,"source_table":TABLE,
        "transport":transport,"source_uri":uri(transport),
        "full_original_parquet_sha_verified":False,
        "BPA_operator_original_XLSX_verified":False,
        "FERC_EIA_planning_area_equivalence_verified":False,
        "model_training_permitted":False,
    }
    csvpath=out/"PUDL_FERC714_BPA_RESPONDENT21_2020_2025_CORE_HOURLY.csv"
    try:
        if connector is None:
            import duckdb
            con=duckdb.connect()
        else:
            con=connector
        provenance["stage"]="duckdb_httpfs"
        con.execute("INSTALL httpfs; LOAD httpfs;")
        if transport=="s3":
            provenance["stage"]="anonymous_s3"
            con.execute("CREATE SECRET (TYPE s3, PROVIDER config, REGION 'us-west-2', URL_STYLE 'path')")
        sql=("SELECT respondent_id_ferc714, report_date, datetime_utc, demand_mwh "
             "FROM read_parquet('"+uri(transport)+"') "
             "WHERE respondent_id_ferc714=21 AND report_date >= DATE '2020-01-01' "
             "AND report_date < DATE '2026-01-01' "
             "ORDER BY report_date, datetime_utc")
        provenance["sql"]=sql
        provenance["stage"]="read_core_hourly"
        result=con.execute(sql)
        annual=Counter();missing=Counter();spill=Counter();seen=set();total=0
        with csvpath.open("w",newline="",encoding="utf-8") as f:
            writer=csv.writer(f)
            writer.writerow(FIELDS)
            while True:
                batch=result.fetchmany(10000)
                if not batch:
                    break
                for original in batch:
                    row=normalize_row(original)
                    year=int(row[1][:4]);stamp=row[2]
                    if stamp in seen:
                        raise ValueError("Duplicate normalized UTC hour across report years")
                    seen.add(stamp)
                    writer.writerow(row)
                    annual[year]+=1
                    missing[year]+=int(row[3]=="")
                    spill[year]+=int(int(stamp[:4])!=year)
                    total+=1
        if total==0:
            raise ValueError("No real respondent 21 core hourly source rows returned")
        provenance.update({
            "status":"CORE_SOURCE_HOURLY_EXTRACTED_UNAPPROVED",
            "rows":total,"report_year_rows":dict(sorted(annual.items())),
            "missing_demand_by_report_year":dict(sorted(missing.items())),
            "utc_year_spillover_by_report_year":dict(sorted(spill.items())),
            "unique_utc_hours":len(seen),
            "derived_core_hourly_csv_sha256":hashfile(csvpath),
            "derived_core_hourly_csv_bytes":csvpath.stat().st_size,
            "six_year_coverage_independently_confirmed":False,
        })
        return provenance
    except Exception as exc:
        provenance.update({
            "status":"FAILED","error_class":type(exc).__name__,
            "error_stage":provenance.get("stage","unknown"),
            "error_message":str(exc)[:600],
        })
        raise
    finally:
        (out/"PUDL_FERC714_BPA21_CORE_HOURLY_SOURCE_PROVENANCE.json").write_text(
            json.dumps(provenance,indent=2)+"\n",encoding="utf-8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--transport",choices=["s3","https"],default="https")
    args=parser.parse_args()
    print(json.dumps(export(args.out,args.transport),indent=2))

if __name__=="__main__":
    main()
