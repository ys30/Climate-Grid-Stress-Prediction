"""Read ONLY header information from pinned original 2020–23 EIA861 Sales workbooks.

Used to map 810 derived null class rows to original year-specific triples,
without guessing column indices or training any model.
"""
import argparse,hashlib,io,csv,json,zipfile
from pathlib import Path
MD5={2020:"ef71e150dd76b2fbce8504ce7159358e",2021:"c088fae5dca1c1c38a11094a2a096735",2022:"8a88824bec4b2aecdc04b0b62fa41452",2023:"7472a6617cc00ff4ae10440f7ef12805"}
def inventory(year,archive):
    data=Path(archive).read_bytes()
    if hashlib.md5(data).hexdigest()!=MD5[year]:raise ValueError("Pinned raw annual archive MD5 mismatch")
    import openpyxl
    filename=f"Sales_Ult_Cust_{year}.xlsx"
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name=next((x for x in z.namelist() if x.endswith(filename)),None)
        if name is None:raise ValueError("Missing exact raw Sales workbook")
        wb=openpyxl.load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
        ws=wb["States"]
        rows=list(next(iter([list(r) for r in ws.iter_rows(min_row=1,max_row=9,values_only=True)]),[])) if False else [
          ["" if c is None else str(c) for c in row]
          for row in ws.iter_rows(min_row=1,max_row=9,values_only=True)]
        result=[dict(year=year,archive=name,sheet="States",excel_column_1based=i+1,
           first_9_source_rows_json=json.dumps([row[i] if i<len(row) else "" for row in rows],ensure_ascii=False))
          for i in range(max(len(row) for row in rows))]
        wb.close()
        return result
def main():
    p=argparse.ArgumentParser()
    for y in MD5:p.add_argument(f"--raw-{y}",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args();output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for y in MD5:rows.extend(inventory(y,getattr(a,f"raw_{y}")))
    with (output/"C2_E1_ORIGINAL_2020_2023_EXACT_SALES_HEADER_INVENTORY.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (output/"PROVENANCE.json").write_text(json.dumps({
      "PUDL_v2026_10_eia861_raw_zenodo":"23241340","annual_original_zip_md5":MD5,
      "source_excel_columns_audited":len(rows),"sector_mapping_approved":False,
      "model_training_permitted":False,"sealed_hourly_demand_used":False},indent=2)+"\n")
if __name__=="__main__":main()
