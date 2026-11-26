#!/usr/bin/env python3
"""Candidate-to-BA code cross-check from fixed-release PUDL annual summary.

This PUDL-derived table may include imputed DEMAND in its annual summary.
Only respondent identity metadata is used; annual demand values are NEVER used
as an independent measured validation source.
"""
import argparse
import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path

VERSION="v2026.10.0"
BUCKET="pudl.catalyst.coop"
TABLE="out_ferc714__summarized_demand"
FIELDS=("respondent_id_ferc714","report_date","respondent_name_ferc714",
        "eia_code","respondent_type","balancing_authority_id_eia",
        "balancing_authority_code_eia","balancing_authority_name_eia",
        "utility_id_eia")


def source_url(transport):
    if transport=="s3":
        return "s3://"+BUCKET+"/"+VERSION+"/"+TABLE+".parquet"
    if transport=="https":
        return "https://s3.us-west-2.amazonaws.com/"+BUCKET+"/"+VERSION+"/"+TABLE+".parquet"
    raise ValueError("Invalid fixed-version source transport")


def inspect_rows(rows):
    """Reject malformed/duplicate annual identifiers; missing years remain explicit."""
    observed=[]
    seen=set()
    for vals in rows:
        if len(vals)!=len(FIELDS):
            raise ValueError("Unexpected summary record schema width")
        item=dict(zip(FIELDS,vals))
        if item["balancing_authority_code_eia"]!="BPAT":
            continue
        if item["respondent_type"]!="balancing_authority":
            raise ValueError("BPAT code linked to a non-BA respondent in curated summary")
        rid=item["respondent_id_ferc714"]
        if not isinstance(rid,int) or isinstance(rid,bool) or rid<=0:
            raise ValueError("Invalid positive PUDL FERC respondent ID")
        dt=item["report_date"]
        if isinstance(dt, (date,datetime)):
            year=dt.year
        else:
            try:
                year=date.fromisoformat(str(dt)[:10]).year
            except ValueError as exc:
                raise ValueError("Invalid annual report_date") from exc
        if not 2020<=year<=2025:
            raise ValueError("Source row year outside 2020-2025 cohort")
        key=(rid,year)
        if key in seen:
            raise ValueError("Duplicate respondent-year in annual linkage source")
        seen.add(key)
        observed.append(item)
    if not observed:
        raise ValueError("No BPAT code linkage in published summary table")
    return observed


def run(out, transport="https", connector=None):
    import duckdb
    out=Path(out)
    if out.exists():
        raise FileExistsError("Refuse to overwrite evidence")
    out.mkdir(parents=True)
    url=source_url(transport)
    proof={"status":"QUERY_FAILED","release":VERSION,"source_table":TABLE,
           "derived_PUDL_identity_not_operator_original":True,
           "original_parquet_sha_verified":False,
           "respondent_identity_independently_approved":False,
           "hourly_load_verified":False,"model_training_permitted":False,
           "source_url":url}
    try:
        con=connector if connector is not None else duckdb.connect()
        proof["stage"]="httpfs_load"
        con.execute("INSTALL httpfs; LOAD httpfs;")
        if transport=="s3":
            proof["stage"]="s3_config"
            con.execute("CREATE SECRET (TYPE s3, PROVIDER config, REGION 'us-west-2', URL_STYLE 'path')")
        projection=", ".join(FIELDS)
        sql=("SELECT "+projection+" FROM read_parquet('"+url+"') "
             "WHERE balancing_authority_code_eia='BPAT' "
             "AND report_date>=DATE '2020-01-01' AND report_date<DATE '2026-01-01' "
             "ORDER BY report_date, respondent_id_ferc714")
        proof["stage"]="remote_identity_query"
        proof["sql"]=sql
        # Capture all returned BPAT rows from published curated annual summary.
        rows=con.execute(sql).fetchall()
        validated=inspect_rows(rows)
        ids=sorted({str(row["respondent_id_ferc714"]) for row in validated})
        proof["candidate_respondent_ids"]=ids
        proof["rows_returned"]=len(validated)
        proof["status"]="PUDL_DERIVED_BPAT_LINKAGE_CANDIDATE"
        path=out/"PUDL_BPAT_FERC714_YEARLY_RESPONDENT_LINKS.csv"
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(validated)
        proof["derived_csv_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
        return proof
    except Exception as e:
        proof["status"]="QUERY_FAILED"
        proof["error_stage"]=proof.get("stage","unknown")
        proof["error_class"]=type(e).__name__
        proof["error_message"]=str(e)[:700]
        raise
    finally:
        (out/"PUDL_FERC714_BPAT_CURATED_IDENTITY_PROVENANCE.json").write_text(
            json.dumps(proof,indent=2,default=str)+"\n",encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--transport",choices=("s3","https"),default="https")
    a=p.parse_args()
    print(json.dumps(run(a.out,a.transport),default=str))


if __name__=="__main__":
    main()
