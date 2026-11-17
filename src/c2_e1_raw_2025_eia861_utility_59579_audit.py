"""Inspect the exact PUDL v2026.10.0 pinned 2025 raw EIA-861 archive.

Find utility 59579 in original spreadsheets (no model fitting, no inference
that derived sales nulls are automatically empty original reported cells).
"""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path

RAW_MD5="dff89c8f144a4497057ff7dad93e1944"
DOI="10.5281/zenodo.23241340"
TARGET_ID="59579"

def inspect(archive,out):
    raw=Path(archive).read_bytes()
    if hashlib.md5(raw).hexdigest()!=RAW_MD5:
        raise ValueError("Pinned 2025 EIA861 raw Zenodo ZIP MD5 mismatch")
    import openpyxl
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    inventory=[];matches=[];errors=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for item in z.infolist():
            if item.is_dir():continue
            low=item.filename.lower()
            if low.endswith((".xlsx",".xlsm")):
                try:
                    book=openpyxl.load_workbook(io.BytesIO(z.read(item)),read_only=True,data_only=True)
                    for sheet in book.worksheets:
                        header=[]
                        count=0
                        targetrows=0
                        for idx,row in enumerate(sheet.iter_rows(values_only=True),1):
                            count+=1
                            # The utility EIA ID is typically among the leading columns;
                            # keep matches as candidates, never infer column mapping.
                            cells=[str(c).strip() if c is not None else "" for c in row]
                            if idx<=8:header.append(cells[:16])
                            found=any(re.fullmatch(r"59579(?:\.0)?",v) for v in cells[:10])
                            if found:
                                targetrows+=1
                                matches.append({"archive_member":item.filename,"sheet":sheet.title,
                                    "excel_row":idx,"raw_values_json":json.dumps(cells,ensure_ascii=False),
                                    "is_verified_raw_sales_row":("sales" in low or "sales" in sheet.title.lower())})
                        inventory.append({"archive_member":item.filename,"sheet":sheet.title,
                            "row_count":count,"matches_59579_in_first_10_cells":targetrows,
                            "header_sample_json":json.dumps(header,ensure_ascii=False)})
                    book.close()
                except Exception as exc:errors.append({"file":item.filename,"error":str(exc)})
            else:
                inventory.append({"archive_member":item.filename,"sheet":"NON_OPENPYXL",
                    "row_count":None,"matches_59579_in_first_10_cells":None,
                    "header_sample_json":""})
    if not inventory:raise ValueError("No raw archive members inspected")
    def write(name,items,fields):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(items)
    write("C2_E1_RAW_2025_WORKBOOK_SHEET_INVENTORY.csv",inventory,
          ["archive_member","sheet","row_count","matches_59579_in_first_10_cells","header_sample_json"])
    write("C2_E1_59579_2025_ORIGINAL_EXCEL_CANDIDATE_ROWS.csv",matches,
          ["archive_member","sheet","excel_row","raw_values_json","is_verified_raw_sales_row"])
    (out/"C2_E1_RAW_2025_ARCHIVE_PROVENANCE.json").write_text(json.dumps({
        "pudl_release":"v2026.10.0","tagged_raw_eia861_zenodo_doi":DOI,
        "archive":"eia861-2025.zip","archive_md5":RAW_MD5,
        "archive_sha256":hashlib.sha256(raw).hexdigest(),
        "workbook_sheets_inspected":sum(1 for a in inventory if a["sheet"]!="NON_OPENPYXL"),
        "candidate_rows_with_59579":len(matches),
        "candidate_rows_in_sales_named_sources":sum(x["is_verified_raw_sales_row"] for x in matches),
        "unreadable_members":errors,"source_only":True,"raw_cell_to_derived_class_lineage_verified":False,
        "model_training_permitted":False,"sealed_2024_2025_EIA930_demand_used":False
    },indent=2)+"\n")
    print(json.dumps({"candidate_raw_rows":len(matches),
      "sales_named_candidate_rows":sum(x["is_verified_raw_sales_row"] for x in matches),
      "unreadable":errors}))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--out",required=True)
    x=p.parse_args();inspect(x.archive,x.out)
if __name__=="__main__":main()
