"""Auditable source-only 2020Q1 ZIP electricity demand sample inventory.

Three separate electric utilities; no county-level allocations or BA demand
validation. A genuine source record requires public downloaded original bytes,
not a source-page link or a completed synthetic unit test.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone

SOURCE_URLS={
 "SDGE":"https://energydata.sdge.com/downloadEnergyUsageFile?name=SDGE-ELEC-2020-Q1.csv",
 "SDGE_HASH":"https://energydata.sdge.com/downloadEnergyUsageFile?name=SDGE-ELEC-2020-Q1-HASH.txt",
 "SCE":"https://www.sce.com/sites/default/files/inline-files/SCE_2020_Q1_ElectricUsageByZip.xlsx",
 "PGE":"https://pge-energydatarequest.com/public_datasets/download?file=PGE_2020_Q1_ElectricUsageByZip.zip&type=electric"
}
def hash_bytes(b):return hashlib.sha256(b).hexdigest()

def inspect_csv(blob):
    sample=blob[:100000].decode("utf-8-sig",errors="replace")
    if "<html" in sample[:1000].lower() or "<!doctype" in sample[:1000].lower():
        raise ValueError("Source returned HTML rather than electricity CSV")
    try:dialect=csv.Sniffer().sniff(sample[:5000],delimiters=",;\t|")
    except csv.Error:dialect=csv.excel
    stream=io.StringIO(blob.decode("utf-8-sig",errors="replace"))
    rd=csv.reader(stream,dialect)
    preview=[]
    for _ in range(8):
        try:preview.append(next(rd)[:40])
        except StopIteration:break
    if not preview:raise ValueError("Empty CSV source")
    rows=list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig",errors="replace")),dialect=dialect))
    if not rows:raise ValueError("SDGE source CSV has no records")
    header=list(rows[0].keys())
    required={"ZipCode","Month","Year","CustomerClass","Combined","TotalCustomers","TotalkWh","AveragekWh"}
    if not required.issubset(header):raise ValueError("SDGE original columns differ")
    if any(r["Year"]!="2020" or r["Month"] not in ("1","2","3") for r in rows):
        raise ValueError("SDGE original 2020Q1 period mismatch")
    return {"format":"CSV","actual_data_rows":len(rows),"first_eight_rows":preview,
            "header_fields":header,
            "period_month_rows":dict(Counter(r["Month"] for r in rows)),
            "customer_class_source_rows":dict(Counter(r["CustomerClass"] for r in rows)),
            "combined_privacy_source_rows":dict(Counter(r["Combined"] for r in rows)),
            "positive_reported_kwh_rows":sum(float(r["TotalkWh"])>0 for r in rows),
            "ZIP_merged_to_other_ZIP_source_rows_not_resolved":True,
            "joint_ZIP_county_observed":False,"total_use_inferred_mwh":None}

def inspect_excel(blob):
    if not zipfile.is_zipfile(io.BytesIO(blob)):raise ValueError("SCE file not a real XLSX ZIP")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if "xl/workbook.xml" not in z.namelist():
            raise ValueError("SCE XLSX missing workbook.xml")
        xmlns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            x=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for entry in x.findall(xmlns+"si"):
                shared.append("".join(t.text or "" for t in entry.iter(xmlns+"t")))
        sheet_paths=sorted(x for x in z.namelist() if
                           re.fullmatch(r"xl/worksheets/sheet\d+\.xml",x))
        sheet_previews=[]
        for sheet_path in sheet_paths[:6]:
            root=ET.fromstring(z.read(sheet_path))
            found=[]
            for row in root.findall(".//"+xmlns+"sheetData/"+xmlns+"row")[:18]:
                values=[]
                for cell in row.findall(xmlns+"c")[:18]:
                    v=cell.find(xmlns+"v")
                    if v is not None and v.text is not None:
                        value=shared[int(v.text)] if cell.attrib.get("t")=="s" else v.text
                        values.append({"cell":cell.attrib.get("r"),"value":str(value)[:100]})
                if values:found.append({"row":row.attrib.get("r"),"values":values})
            sheet_previews.append({"sheet_member":sheet_path,"preview":found})
        return {"format":"XLSX","workbook_members":len(z.namelist()),
                "contains_shared_strings":"xl/sharedStrings.xml" in z.namelist(),
                "source_sheet_previews":sheet_previews,
                "source_numeric_interpretation_not_yet_approved":True,
                "joint_ZIP_county_observed":False,"total_use_inferred_mwh":None}

def inspect_pge(blob):
    if not zipfile.is_zipfile(io.BytesIO(blob)):raise ValueError("PGE public response is not ZIP")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=z.namelist()
        if not names:raise ValueError("PGE ZIP has no members")
        return {"format":"ZIP","archive_members":names[:50],
                "source_column_values_not_yet_semantically_verified":True,
                "joint_ZIP_county_observed":False,"total_use_inferred_mwh":None}

def audit(files):
    result={}
    for util in ("PGE","SCE","SDGE"):
        path=Path(files[util])
        blob=path.read_bytes()
        if len(blob)<128:raise ValueError(util+" original file too small/missing")
        result[util]={"source_url":SOURCE_URLS[util],
                      "response_sha256":hash_bytes(blob),"response_bytes":len(blob),
                      "original_source_verified":False,
                      "full_2020_2023_CEC_or_CISO_linkage_approved":False}
        try:
            check={"PGE":inspect_pge,"SCE":inspect_excel,"SDGE":inspect_csv}[util](blob)
        except ValueError as exc:
            result[util]["source_format_error"]=str(exc)
            result[util]["response_head_preview"]=blob[:240].decode("utf-8",errors="replace")
            result[util]["source_download_unverified"]=True
        else:
            result[util].update(check)
            result[util]["original_source_verified"]=True
    hashfile=Path(files["SDGE_HASH"])
    h=hashfile.read_bytes()
    if len(h)<8:raise ValueError("SDGE source hash text missing")
    result["SDGE"]["publisher_hash_file_original_sha256"]=hash_bytes(h)
    result["SDGE"]["publisher_hash_file_preview"]=h.decode("utf-8",errors="replace")[:1000]
    digest_match=re.search(r"\b([0-9A-Fa-f]{128})\b",h.decode("utf-8",errors="replace"))
    if not digest_match:raise ValueError("Missing publisher SHA512 in original SDGE hash file")
    actual_sha512=hashlib.sha512(Path(files["SDGE"]).read_bytes()).hexdigest()
    if actual_sha512.lower()!=digest_match.group(1).lower():
        raise ValueError("SDGE original CSV bytes do not match published SHA512")
    result["SDGE"]["original_csv_sha512"]=actual_sha512
    result["SDGE"]["publisher_hash_algorithm_and_digest_matched"]=True
    verified=sum(bool(v["original_source_verified"]) for v in result.values())
    if verified<2:
        raise ValueError("Fewer than two independently valid original utility source formats")
    return {"status":"PARTIAL_GENUINE_2020Q1_SOURCE_VERIFICATION_NO_COUNTY_MODEL_ADMISSION",
            "period":"2020 Q1","utility_count":3,
            "verified_original_utility_count":verified,
            "all_three_original_utility_files_verified":verified==3,
            "source_only":True,
            "county_metered_MWh_verified":False,"ZIP_to_county_mapping_applied":False,
            "privacy_merged_ZIP_handling_verified":False,"historical_CISO_membership_verified":False,
            "model_training_permitted":False,"C1_modified":False,
            "utility_files":result}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("PGE","SCE","SDGE","SDGE_HASH"):
        ap.add_argument("--"+key.lower().replace("_","-"),type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError("No overwrite of original source audit")
    data=audit({k:getattr(args,k.lower()) for k in ("PGE","SCE","SDGE","SDGE_HASH")})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"status":data["status"],"utilities":list(data["utility_files"]), "verified":data["verified_original_utility_count"],
                      "model_training_permitted":False}))

if __name__=="__main__":main()
