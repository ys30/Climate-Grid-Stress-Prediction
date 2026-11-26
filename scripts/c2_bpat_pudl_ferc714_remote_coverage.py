#!/usr/bin/env python3
"""Lightweight PUDL v2026.10.0 FERC714 BPAT respondent discovery.

Runs read-only DuckDB range queries against public fixed-version S3 Parquet.
Produces *derived query evidence*, NOT immutable original full Parquet bytes.
No BPA identity autoapproval; no EIA930 numeric validation is claimed.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

VERSION="v2026.10.0"
BASE="s3://pudl.catalyst.coop/"+VERSION+"/"
RESP=BASE+"core_ferc714__respondent_id.parquet"
HOUR=BASE+"core_ferc714__hourly_planning_area_demand.parquet"
HTTPS_BASE="https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/"+VERSION+"/"


def store_csv(path, records, names):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=names)
        writer.writeheader()
        writer.writerows(records)
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def query(con, sql, params=None):
    return con.execute(sql, params or []).fetchall()


def run(out, reviewed_respondent_id=None, transport="s3"):
    import duckdb
    if transport not in ("s3", "https"):
        raise ValueError("Only fixed-release s3 or https transport is permitted")
    respondent_uri = RESP if transport == "s3" else HTTPS_BASE + "core_ferc714__respondent_id.parquet"
    hourly_uri = HOUR if transport == "s3" else HTTPS_BASE + "core_ferc714__hourly_planning_area_demand.parquet"
    out=Path(out)
    if out.exists():
        raise FileExistsError("Refuse to overwrite independent source discovery")
    out.mkdir(parents=True)
    proof={"release":VERSION,
           "transport":transport,
           "respondent_uri":respondent_uri,
           "hourly_uri":hourly_uri,
           "read_only_source_type":"PUDL-curated public S3 Parquet remote query",
           "full_original_parquet_bytes_downloaded":False,
           "original_parquet_sha256_verified":False,
           "bpa_original_xlsx_verified":False,
           "respondent_identity_approved":False,
           "EIA930_comparison_completed":False,
           "model_training_permitted":False}
    try:
        con=duckdb.connect()
        con.execute("INSTALL httpfs; LOAD httpfs;")
        # Path-style is required because pudl.catalyst.coop has multiple dots.
        if transport == "s3":
            con.execute("CREATE SECRET (TYPE s3, PROVIDER config, REGION 'us-west-2', URL_STYLE 'path')")
        # Keep a deterministic query string and record it with the results.
        sql=("SELECT respondent_id_ferc714, respondent_name_ferc714, "
             "respondent_id_ferc714_csv, respondent_id_ferc714_xbrl, eia_code "
             "FROM read_parquet('"+respondent_uri+"') "
             "WHERE regexp_matches(upper(coalesce(respondent_name_ferc714,'')),"
             "'BONNEVILLE|(^|[^A-Z])BPA([^A-Z]|$)') "
             "ORDER BY respondent_id_ferc714")
        proof["candidate_sql"]=sql
        cols=["respondent_id_ferc714","respondent_name_ferc714",
              "respondent_id_ferc714_csv","respondent_id_ferc714_xbrl","eia_code"]
        data=[dict(zip(cols,row)) for row in query(con,sql)]
        if not data:
            raise ValueError("No BPA respondent candidate in pinned PUDL release")
        ids=[str(row["respondent_id_ferc714"]) for row in data]
        if len(set(ids))!=len(ids):
            raise ValueError("Nonunique BPA respondent identifiers")
        proof["bpa_candidate_count"]=len(data)
        proof["candidate_csv_sha256"]=store_csv(out/"BPA_FERC714_RESPONDENT_CANDIDATES.csv",data,cols)
        proof["candidates"]=data
        if reviewed_respondent_id is None:
            proof["status"]="RESPONDENT_REVIEW_REQUIRED"
            return proof
        # Explicit reviewer ID is necessary but not sufficient for independent
        # BA identity approval. This still performs source-only coverage queries.
        if str(reviewed_respondent_id) not in ids:
            raise ValueError("Explicit reviewed ID absent from source candidates")
        proof["reviewed_candidate_id_for_diagnostic_only"]=reviewed_respondent_id
        hourly_sql=("SELECT year(datetime_utc) AS utc_year, "
                    "count(*) AS source_hour_rows, "
                    "count(DISTINCT datetime_utc) AS unique_utc_hours, "
                    "count(*) FILTER (WHERE demand_mwh IS NULL) AS null_demand_rows, "
                    "min(datetime_utc) AS first_utc, max(datetime_utc) AS last_utc "
                    "FROM read_parquet('"+hourly_uri+"') "
                    "WHERE respondent_id_ferc714=? AND datetime_utc >= TIMESTAMP '2020-01-01' "
                    "AND datetime_utc < TIMESTAMP '2026-01-01' "
                    "GROUP BY 1 ORDER BY 1")
        proof["hourly_coverage_sql"]=hourly_sql
        rows=query(con,hourly_sql,[reviewed_respondent_id])
        fields=["utc_year","source_hour_rows","unique_utc_hours","null_demand_rows","first_utc","last_utc"]
        records=[dict(zip(fields,[str(x) if x is not None else "" for x in row])) for row in rows]
        proof["hourly_coverage_csv_sha256"]=store_csv(out/"BPA_FERC714_2020_2025_HOURLY_COVERAGE.csv",records,fields)
        proof["hourly_coverage"]=records
        proof["status"]="SOURCE_COVERAGE_CANDIDATE_NOT_IDENTITY_CERTIFIED"
        return proof
    finally:
        (out/"BPA_FERC714_PUDL_REMOTE_QUERY_PROVENANCE.json").write_text(
            json.dumps(proof,indent=2,default=str)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--reviewed-respondent-id",type=int)
    parser.add_argument("--transport",choices=("s3","https"),default="s3")
    args=parser.parse_args()
    result=run(args.out,args.reviewed_respondent_id,args.transport)
    print(json.dumps({"status":result["status"],"candidate_count":result["bpa_candidate_count"],
                      "model_training_permitted":False}))


if __name__=="__main__":
    main()
