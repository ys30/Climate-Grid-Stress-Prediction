"""Reconcile 810 processed PUDL 2020–23 null sales cells to pinned raw EIA861.

All four source artifacts use exact checked SHA256. The raw workbook year
headers certify RES/COM/IND/TRANSPORT/TOTAL (not OTHER). '.' is NEVER zero.
"""
import argparse,csv,hashlib,io,json,zipfile
from collections import Counter
from pathlib import Path

SRC={
 "exact":("C2_E1_468_EXACT_ORIGINAL_SALES_ROWS.csv","eda59eaa015fd0cf4eaedb73cb73bda06a1c1fd13d6ba7e72adbd249c8b0ba91"),
 "candidate":("C2_E1_2020_2023_ORIGINAL_SALES_CANDIDATE_EXCEL_ROWS.csv","1527647b41c22e1e80b9bfd997276fd3c63b9a73b27924439e739f6cd5caf415"),
 "processed":("C2_E1_MISSING_MWH_SAME_FILING_1321_ROWS.csv","6e1e43eeec3b6f0bfb73b5eb25241b8d3e5a3fbf4acdfb9485800fa923bc6300"),
 "header":("C2_E1_ORIGINAL_2020_2023_EXACT_SALES_HEADER_INVENTORY.csv","11ec32b75414a443048d4045e8dbfa56e843dae76db9b362641c811bd67f9b94")}
CLASSES={"residential":(9,10,11),"commercial":(12,13,14),
         "industrial":(15,16,17),"transportation":(18,19,20)}
NAMES={"residential":"RESIDENTIAL","commercial":"COMMERCIAL",
       "industrial":"INDUSTRIAL","transportation":"TRANSPORTATION"}

def read(zippath,key):
    name,sha=SRC[key]
    with zipfile.ZipFile(zippath) as z:raw=z.read(name)
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Pinned input SHA256 mismatch for "+key)
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def validate_headers(data):
    by={(int(r["year"]),int(r["excel_column_1based"])):json.loads(r["first_9_source_rows_json"]) for r in data}
    for year in range(2020,2024):
        if any("OTHER" in json.dumps(v[:3]).upper() for (y,_),v in by.items() if y==year):
            raise ValueError("Unexpected source OTHER column")
        for cls,ids in CLASSES.items():
            first=by[year,ids[0]+1]
            if NAMES[cls] not in first[0].upper() or "REVENUES" not in first[1].upper():
                raise ValueError("Wrong year-specific raw revenue heading")
            if "SALES" not in by[year,ids[1]+1][1].upper() or "MEGAWATTHOURS" not in by[year,ids[1]+1][2].upper():
                raise ValueError("Wrong year-specific raw sales MWh heading")
            if "CUSTOMERS" not in by[year,ids[2]+1][1].upper():
                raise ValueError("Wrong year-specific customer heading")
        if "TOTAL" not in by[year,22][0].upper():
            raise ValueError("Expected source TOTAL not found")

def analyze(exact,candidate,processed):
    key=lambda r:(str(r["year"]),str(int(r["utility_id_eia"])),r["state"],r["BA"])
    indexes={}
    for r in candidate:
        k=(key(r),str(r["excel_row"]),r["raw_row_sha256"])
        if k in indexes:raise ValueError("Duplicate candidate")
        indexes[k]=r
    raw={}
    for r in exact:
        k=key(r)
        match=indexes.get((k,str(r["source_excel_row"]),r["source_raw_row_sha256"]))
        if match is None:raise ValueError("Unverified exact original raw row")
        if k in raw:raise ValueError("Multiple strict rows for source group")
        raw[k]=match
    if len(raw)!=468:raise ValueError("Not 468 exact raw groups")
    evidence=[]
    for p in processed:
        if not 2020<=int(p["year"])<=2023:continue
        k=key(p)
        if k not in raw:raise ValueError("Processed null with no strict original row")
        match=raw[k]
        vals=json.loads(match["raw_values_json"])
        if len(vals)!=24:raise ValueError("Unexpected raw sales workbook column count")
        cls=p["customer_class"]
        if cls=="other":
            revenue=sales=customers="NO_ORIGINAL_COLUMN"
            col="";classification="other_sector_not_in_original_report"
        elif cls in CLASSES:
            ids=CLASSES[cls]
            revenue,sales,customers=[vals[i] for i in ids]
            col=ids[1]+1
            classification="literal_dot_original_sales" if sales=="." else "UNEXPECTED_RAW_SALES_VALUE"
        else:raise ValueError("Unknown class")
        if classification=="UNEXPECTED_RAW_SALES_VALUE":raise ValueError("Processed null has unexpected raw sales value")
        evidence.append({
            "year":p["year"],"BA":p["BA"],"state":p["state"],"utility_id_eia":p["utility_id_eia"],
            "customer_class":cls,"original_workbook":match["archive_member"],
            "original_sheet":match["sheet"],"original_excel_row":match["excel_row"],
            "original_excel_sales_column":col,"original_revenue_cell":revenue,
            "original_sales_cell":sales,"original_customers_cell":customers,
            "raw_sales_classification":classification,
            "original_row_sha256":match["raw_row_sha256"],
            "original_dot_equals_numeric_zero":False,"model_training_permitted":False})
    if len(evidence)!=810:raise ValueError("Not 810 PUDL null rows")
    counter=Counter(r["raw_sales_classification"] for r in evidence)
    if counter!=Counter({"other_sector_not_in_original_report":468,"literal_dot_original_sales":342}):
        raise ValueError("Original-source null mechanism differs")
    return evidence

def write(path,items):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)

def main():
    p=argparse.ArgumentParser()
    for k in SRC:p.add_argument("--"+k,required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args();o=Path(a.out);o.mkdir(parents=True,exist_ok=True)
    validate_headers(read(a.header,"header"))
    evidence=analyze(read(a.exact,"exact"),read(a.candidate,"candidate"),read(a.processed,"processed"))
    write(o/"C2_E1_810_ORIGINAL_SALES_CELL_LINEAGE.csv",evidence)
    rows=[]
    for (year,cls,status),n in sorted(Counter((r["year"],r["customer_class"],r["raw_sales_classification"]) for r in evidence).items()):
        rows.append(dict(year=year,customer_class=cls,source_status=status,source_rows=n))
    write(o/"C2_E1_2020_23_ORIGINAL_CELL_LINEAGE_YEAR_CLASS_SUMMARY.csv",rows)
    (o/"C2_E1_EXACT_CELL_LINEAGE_PROVENANCE.json").write_text(json.dumps({
        "original_eia861_zenodo_doi":"10.5281/zenodo.23241340",
        "source_artifact_member_SHA256":{k:v[1] for k,v in SRC.items()},
        "verified_processed_null_sector_records":810,
        "other_absent_raw_sector_column":468,"original_literal_dot_MWh_sales_cell":342,
        "other_nonzero_MWh_inferred":False,"dot_treated_as_zero":False,
        "source_quality_gate_scope":"E1 original 2020-2023 annual EIA861 category-null lineage only",
        "geographic_BA_load_relevance_approved":False,
        "model_training_permitted":False,"sealed_2024_2025_hourly_demand_used":False},indent=2)+"\n")
    print("VERIFIED 810 ORIGINAL CELL LINEAGE: 468 OTHER ABSENT + 342 RAW MWh '.'")
if __name__=="__main__":main()
