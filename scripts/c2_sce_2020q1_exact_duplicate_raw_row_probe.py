"""Exact raw-row SCE 2020 Q1 duplicated ZIP×month×class investigation.

Only public utility quarterly aggregate XLSX, source SHA-pinned.
Never select one record silently, assume Combined reports represent
metered physical zero, or infer ZIP/county load weights.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import defaultdict,Counter
from pathlib import Path
from openpyxl import load_workbook

SOURCE_SHA256="0d814db6abdb342171899eb57201cb3d3c62767b48cb2ce89aec537e2342431b"
EXPECTED_HEADER=("Zip Code","Month","Year","Customer Class","Combined","TotalAccounts","TotalkWh","AveragekWh")
EXPECTED_EXTRA_DUPLICATE_ROWS=15

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def normalize_zip(v):
    if isinstance(v,bool):raise ValueError("Boolean ZIP invalid")
    s=str(v).strip()
    if s.endswith(".0"):s=s[:-2]
    if not s.isdigit() or len(s)>5:raise ValueError("Cannot establish 5-digit ZIP source identity")
    return s.zfill(5)

def normalize_numeric(v):
    if v is None:return None
    if isinstance(v,(int,float)) and math.isfinite(v):return v
    s=str(v).strip()
    if not s:return None
    try:
        n=float(s.replace(",",""))
    except ValueError:return s
    return n if math.isfinite(n) else s

def probe(path):
    if sha(path)!=SOURCE_SHA256:raise ValueError("Actual SCE original SHA256 changed")
    wb=load_workbook(path,read_only=True,data_only=True)
    if len(wb.worksheets)!=1:raise ValueError("Unexpected SCE sheet count")
    sh=wb.worksheets[0]
    header=tuple(str(x).strip() if x is not None else "" for x in
                 next(sh.iter_rows(min_row=3,max_row=3,values_only=True))[:8])
    if header!=EXPECTED_HEADER:raise ValueError("Original SCE column layout changed")
    keyed=defaultdict(list);all_rows=0
    for row_index,row in enumerate(sh.iter_rows(min_row=4,values_only=True),start=4):
        if not row or row[0] is None:continue
        cells=list(row[:8])
        key=(normalize_zip(cells[0]),str(cells[1]),str(cells[3]).strip())
        payload=(key[0],str(cells[1]),str(cells[2]),
                 str(cells[3]).strip(),str(cells[4]).strip().upper(),
                 normalize_numeric(cells[5]),normalize_numeric(cells[6]),
                 normalize_numeric(cells[7]))
        keyed[key].append((row_index,payload))
        all_rows+=1
    duplicates=[]
    for (zip_code,month,clazz),rows in sorted(keyed.items()):
        if len(rows)<2:continue
        unique={x[1] for x in rows}
        duplicates.append({
          "zip":zip_code,"month":int(month),"customer_class":clazz,
          "original_Excel_row_numbers":[r for r,_ in rows],
          "source_row_multiplicity":len(rows),
          "original_rows_exactly_identical":len(unique)==1,
          "distinct_raw_payloads":len(unique),
          "all_records_combined_Y":all(p[4]=="Y" for _,p in rows),
          "all_records_kwh_blank":all(p[6] is None for _,p in rows),
          "all_records_accounts_blank":all(p[5] is None for _,p in rows),
          "all_records_average_kwh_blank":all(p[7] is None for _,p in rows),
          "safe_to_assign_county_MWh":False,
          "safe_to_sum_unreviewed_duplicates":False})
    extra=sum(x["source_row_multiplicity"]-1 for x in duplicates)
    if all_rows!=9324 or extra!=EXPECTED_EXTRA_DUPLICATE_ROWS:
        raise ValueError("Pinned SCE original source count or extra duplicate contract changed")
    return {
      "decision":"AUTHENTIC_SCE_DUPLICATE_KEYS_CLASSIFIED_SOURCE_ONLY",
      "actual_SCE_SHA256":SOURCE_SHA256,
      "observed_rows":all_rows,
      "unique_ZIP_month_class_keys":len(keyed),
      "duplicated_keys":len(duplicates),
      "extra_duplicate_rows":extra,
      "all_duplicate_groups_exactly_identical":all(x["original_rows_exactly_identical"] for x in duplicates),
      "duplicate_groups_all_Combined_Y":all(x["all_records_combined_Y"] for x in duplicates),
      "duplicate_groups_all_kwh_blank":all(x["all_records_kwh_blank"] for x in duplicates),
      "duplicate_groups_all_accounts_blank":all(x["all_records_accounts_blank"] for x in duplicates),
      "duplicate_groups_all_average_blank":all(x["all_records_average_kwh_blank"] for x in duplicates),
      "duplicate_groups":duplicates,
      "source_aggregation_permitted":False,
      "physical_consumer_county_allocation_approved":False,
      "2024_2025_hourly_holdout_used":False,
      "model_training_permitted":False,
      "C1_untouched":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sce",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("No audit overwrite")
    d=probe(a.sce)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({k:d[k] for k in (
      "observed_rows","duplicated_keys","extra_duplicate_rows",
      "all_duplicate_groups_exactly_identical","model_training_permitted")},indent=2))

if __name__=="__main__":main()
