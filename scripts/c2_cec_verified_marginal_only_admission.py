"""Verify official CEC county and agency XLSX schema from SHA-pinned GitHub CI.

Only certifies two separately aggregated published worksheets. It never
pretends either worksheet contains joint COUNTY×AGENCY electricity data,
and does not claim that unpublished QFER 1306A records are available.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

ARTIFACT_RUN_ID=44872398200
ARTIFACT_ID=14695445486
MEMBER="C2_CEC_QFER_OFFICIAL_ANNUAL_WORKBOOK_SCHEMA.json"
PINNED_SCHEMA_JSON_SHA256="19dd37863086d4981290a9e15130ae5c77ca9071b23c3edb09d1723ca99250ec"
PINNED_COUNTY_XLSX_SHA256="142a104d6deebc5c789c1dfcc51387f8681891e4e300f787510cf8b7c23d67ca"
PINNED_AGENCY_XLSX_SHA256="b2a8a8d5863cca938ce3cf6c41c6ff941c20640a977952e75e449732f19460c2"
COUNTY_FIELDS=["YEAR","COUNTY_NUM","COUNTY_NAME","SECTOR","RNR","GWH"]
AGENCY_FIELDS=["YEAR","PLANNING_AREA","AGENCY_NAME","AGENCY_TYPE","SECTOR","RNR","GWH"]

def _fields(part):
    tabs=part.get("sheets",[])
    if len(tabs)!=1 or not tabs[0].get("preview_first_12_rows_first_30_cells"):
        raise ValueError("CEC original Excel sheet preview incomplete")
    head=tabs[0]["preview_first_12_rows_first_30_cells"][0]["cells"]
    return [x["value"] for x in head]

def verify(original_zip,expected_schema_sha=PINNED_SCHEMA_JSON_SHA256):
    with zipfile.ZipFile(original_zip) as z:
        if z.namelist()!=[MEMBER]:
            raise ValueError("CEC provenance ZIP layout changed")
        payload=z.read(MEMBER)
    actual=hashlib.sha256(payload).hexdigest()
    if actual!=expected_schema_sha:raise ValueError("Original CEC source schema SHA changed")
    data=json.loads(payload)
    county=data["county_annual"];agency=data["utility_annual"]
    if county["actual_download_sha256"]!=PINNED_COUNTY_XLSX_SHA256:
        raise ValueError("County source XLSX original SHA changed")
    if agency["actual_download_sha256"]!=PINNED_AGENCY_XLSX_SHA256:
        raise ValueError("Utility source XLSX original SHA changed")
    if _fields(county)!=COUNTY_FIELDS or _fields(agency)!=AGENCY_FIELDS:
        raise ValueError("Actual CEC source columns differ from verified schema")
    if data["file_level_joint_county_utility_allocation_established"] is not False:
        raise ValueError("Unverified joint CEC source allocation claim")
    if data["model_training_permitted"] is not False:
        raise ValueError("CEC source metadata cannot authorize C2 training")
    return {
        "decision":"OFFICIAL_CEC_TWO_ANNUAL_MARGINAL_FILES_VERIFIED_NO_JOINT_AGENCY_COUNTY_ALLOCATION",
        "verified_original_CI_run":ARTIFACT_RUN_ID,
        "verified_original_CI_artifact":ARTIFACT_ID,
        "source_schema_sha256":actual,
        "county_workbook_sha256":county["actual_download_sha256"],
        "agency_workbook_sha256":agency["actual_download_sha256"],
        "county_workbook_columns":COUNTY_FIELDS,
        "agency_workbook_columns":AGENCY_FIELDS,
        "county_excel_dimension":county["sheets"][0]["sheet_dimension_claim"],
        "agency_excel_dimension":agency["sheets"][0]["sheet_dimension_claim"],
        "joint_county_agency_columns_present_in_either_file":False,
        "CEC_1306A_original_report_asks_reporting_county":True,
        "original_filing_joint_data_publicly_obtained":False,
        "actual_meter_level_county_allocation_available":False,
        "EIA930_CISO_reporting_scope_matched_to_CEC_consumption":False,
        "GEO_LOAD_RELEVANCE_cleared":False,
        "GEO_HISTORICAL_BA_FOOTPRINT_cleared":False,
        "model_training_permitted":False,
        "C1_frozen_untouched":True
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError("Refuse to overwrite existing CEC provenance evidence")
    result=verify(args.artifact)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"decision":result["decision"],"model_training_permitted":False}))

if __name__=="__main__":main()
