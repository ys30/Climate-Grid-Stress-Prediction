"""Inspect official CEC QFER annual XLSX schema without inventing county×utility cells.

Source-only spreadsheet structure review using Python standard-library
ZIP/XML. The inventory is not a data extraction/BA crosswalk, and matching
'county' plus 'utility' strings in workbook labels does NOT certify joint
county-by-utility reported sales. No geography/model gate is changed.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path

NS={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p":"http://schemas.openxmlformats.org/package/2006/relationships"}
MAX_CELLS=30
MAX_ROWS=12

def sha256(data):return hashlib.sha256(data).hexdigest()

def inspect_xlsx(path, *, source_url):
    path=Path(path)
    raw=path.read_bytes()
    if len(raw)<512:raise ValueError("Not a nonempty original XLSX")
    if raw[:2]!=b"PK":raise ValueError("Original CEC source is not ZIP/XLSX")
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
            raise ValueError("No spreadsheet workbook + relationships")
        book=ET.fromstring(z.read("xl/workbook.xml"))
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets={}
        for r in rels.findall("p:Relationship",NS):
            dest=r.attrib.get("Target","")
            if dest.startswith("/"): full=dest.lstrip("/")
            elif dest.startswith("xl/"):full=dest
            else: full="xl/"+dest.lstrip("/")
            targets[r.attrib["Id"]]=full
        strings=[]
        if "xl/sharedStrings.xml" in names:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("x:si",NS):
                strings.append("".join(t.text or "" for t in si.findall(".//x:t",NS)))
        sheets=[]
        for sheet in book.findall("x:sheets/x:sheet",NS):
            rid=sheet.attrib.get("{"+NS["r"]+"}id")
            member=targets.get(rid)
            if not member or member not in names:raise ValueError("Unresolved original workbook sheet")
            tree=ET.fromstring(z.read(member))
            dim=tree.find("x:dimension",NS)
            preview=[]
            for row in tree.findall("x:sheetData/x:row",NS)[:MAX_ROWS]:
                values=[]
                for cell in row.findall("x:c",NS)[:MAX_CELLS]:
                    typ=cell.attrib.get("t")
                    value=cell.find("x:v",NS)
                    inline=cell.find("x:is",NS)
                    s=value.text if value is not None else None
                    if typ=="s" and s is not None:
                        idx=int(s);s=strings[idx] if 0<=idx<len(strings) else None
                    elif typ=="inlineStr" and inline is not None:
                        s="".join(t.text or "" for t in inline.findall(".//x:t",NS))
                    if s is not None:
                        values.append({"cell":cell.attrib.get("r"),"value":str(s)[:160]})
                if values:preview.append({"row":int(row.attrib.get("r","0")),"cells":values})
            sheets.append({"name":sheet.attrib["name"],
                "sheet_dimension_claim":dim.attrib.get("ref") if dim is not None else None,
                "preview_first_12_rows_first_30_cells":preview,
                "joint_county_utility_measurement_verified":False})
    return {"source_url":source_url,"actual_download_sha256":sha256(raw),
        "source_bytes":len(raw),"original_workbook_intact":True,
        "inventory_is_not_joint_county_by_utility_extraction":True,
        "historical_CISO_operational_BA_scope_verified":False,
        "year_2025_coverage_verified":False,
        "model_training_permitted":False,"sheets":sheets}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--county-annual",type=Path,required=True)
    p.add_argument("--utility-annual",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Cannot overwrite existing source evidence")
    report={"status":"OFFICIAL_CEC_ANNUAL_XLSX_SCHEMA_INVENTORY_NOT_GEO_ADMISSION",
       "retrieved_date_is_download_time_not_source_publication":True,
       "CEC_reporting_source":"California Energy Commission QFER 1306A Schedule 1",
       "county_annual":inspect_xlsx(a.county_annual,source_url=
           "https://www.energy.ca.gov/filebrowser/download/8144?fid=8144"),
       "utility_annual":inspect_xlsx(a.utility_annual,source_url=
           "https://www.energy.ca.gov/filebrowser/download/8168?fid=8168"),
       "file_level_joint_county_utility_allocation_established":False,
       "actual_meter_county_allocation_established":False,
       "GEO_LOAD_RELEVANCE_cleared":False,
       "CISO_EIA930_and_CEC_reporting_scope_equal_established":False,
       "model_training_permitted":False,
       "C1_source_modified":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],
       "county_sheets":len(report["county_annual"]["sheets"]),
       "utility_sheets":len(report["utility_annual"]["sheets"]),
       "model_training_permitted":False},indent=2))

if __name__=="__main__":main()
