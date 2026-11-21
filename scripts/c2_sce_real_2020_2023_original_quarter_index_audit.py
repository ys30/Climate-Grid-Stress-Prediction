"""Source-authenticated annual SCE public ZIP electric quarterly index and raw XLSX QA.

The official SCE page supplies distinct historical 2020–2023 download
hrefs. Never guess a legacy URL, treat a privacy-merged ZIP as physical
load, overwrite original data, or infer CISO BA membership. Only source
metadata (not customer or ZIP rows) is retained.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,urllib.parse
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

INDEX="https://www.sce.com/regulatory/regulatory-information/energy-data-reports-compliances"
FILE_RE=re.compile(r"SCE_(202[0-3])_Q([1-4])_ElectricUsageByZip\.xlsx",re.I)
EXPECTED={(y,q) for y in range(2020,2024) for q in range(1,5)}
FIRST_SHA="0d814db6abdb342171899eb57201cb3d3c62767b48cb2ce89aec537e2342431b"

def source_links(html,base=INDEX):
    soup=BeautifulSoup(html,"html.parser")
    links={}
    for a in soup.find_all("a",href=True):
        href=urllib.parse.urljoin(base,a["href"])
        decoded=urllib.parse.unquote(urllib.parse.urlsplit(href).path)
        m=FILE_RE.search(decoded)
        if not m:
            # Official 2022 Q2 link is mislabeled SCE_2002_Q2 (publisher typo).
            if "SCE_2002_Q2_ElectricUsageByZip.xlsx" in decoded:
                key=(2022,2)
                if key in links and links[key]!=href:
                    raise ValueError("Conflicting official SCE 2022Q2 links")
                links[key]=href
            continue
        key=(int(m[1]),int(m[2]))
        if key in links and links[key]!=href:
            raise ValueError(f"Ambiguous official SCE quarterly href {key}")
        if urllib.parse.urlsplit(href).hostname not in {"www.sce.com","sce.com"}:
            raise ValueError("Unexpected offsite SCE electricity XLSX href")
        links[key]=href
    if set(links)!=EXPECTED:
        raise ValueError(f"Official SCE source index incomplete or changed; missing={sorted(EXPECTED-set(links))}, excess={sorted(set(links)-EXPECTED)}")
    return links

def source_workbook_info(raw,year,quarter):
    if not raw.startswith(b"PK"):
        raise ValueError(f"{year}Q{quarter} server returned non-XLSX content")
    wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    if len(wb.worksheets)!=1:raise ValueError("SCE historical workbook has multiple sheets")
    sheet=wb.worksheets[0]
    hdrs=[]
    for idx,row in enumerate(sheet.iter_rows(max_row=12,values_only=True),start=1):
        vals=[str(v).strip() if v is not None else "" for v in row[:12]]
        if "Zip Code" in vals and "TotalkWh" in vals:
            hdrs.append({"row":idx,"columns":vals})
    if len(hdrs)!=1:raise ValueError(f"{year}Q{quarter} lacks unique recognizable source header")
    # Confirm the year IN the downloaded workbook, independently of its typo URL.
    header_idx=hdrs[0]["row"]
    columns=hdrs[0]["columns"]
    year_index=next((i for i,h in enumerate(columns) if h.strip().lower()=="year"),None)
    if year_index is None:raise ValueError("No original internal reporting year field")
    sample=[]
    for original_row in sheet.iter_rows(min_row=header_idx+1,max_row=header_idx+45,values_only=True):
        if len(original_row)>year_index and original_row[year_index] is not None:
            v=str(original_row[year_index]).strip()
            if v.endswith(".0"):v=v[:-2]
            sample.append(v)
    if not sample or any(v!=str(year) for v in sample):
        raise ValueError(f"Source workbook internal year differs from {year}Q{quarter}: {sample[:10]}")
    return {"source_header":hdrs[0],"sheet_name":sheet.title,
            "internal_year_sample_count":len(sample),
            "internal_year_sample_confirmed":True,
            "official_filename_2002_Q2_typo":(year,quarter)==(2022,2),
            "claimed_rows":sheet.max_row,"claimed_columns":sheet.max_column,
            "actual_zip_level_kwh_sum_reproduced":False}

def collect(index_html,download):
    links=source_links(index_html)
    result=[]
    for year,quarter in sorted(links):
        url=links[(year,quarter)]
        try:
            blob=download(url)
            detail=source_workbook_info(blob,year,quarter)
            digest=hashlib.sha256(blob).hexdigest()
            if (year,quarter)==(2020,1) and digest!=FIRST_SHA:
                raise ValueError("Original SCE 2020 Q1 pinned source SHA drift")
            result.append({"year":year,"quarter":quarter,"source_url":url,
                           "http_original_source_sha256":digest,"response_bytes":len(blob),
                           "status":"AUTHENTIC_XLSX_STRUCTURE_VERIFIED",**detail})
        except Exception as exc:
            result.append({"year":year,"quarter":quarter,"source_url":url,
                           "status":"SOURCE_NOT_VERIFIED","error":str(exc)[:300]})
    succeeded=sum(x["status"]=="AUTHENTIC_XLSX_STRUCTURE_VERIFIED" for x in result)
    return {"status":"REAL_SCE_16_QUARTER_SOURCE_AUDIT" if succeeded==16
             else "SCE_SOURCE_INCOMPLETE_RESEARCH_NOT_APPROVED",
            "official_SCE_index":INDEX,"quarter_count_expected":16,
            "quarter_count_verified":succeeded,
            "all_2020_2023_original_sources_verified":succeeded==16,
            "source_metadata_only":True,
            "Combined_source_recipient_ZIP_located":False,
            "ZIP_to_county_allocation_performed":False,
            "CISO_BA_membership_verified":False,
            "model_training_permitted":False,"C1_untouched":True,
            "quarters":result}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Do not overwrite original source audit")
    session=requests.Session()
    session.headers.update({"User-Agent":"Climate-Grid-Stress-Prediction-source-audit/1.0"})
    def fetch(url):
        res=session.get(url,timeout=90)
        res.raise_for_status()
        return res.content
    html=fetch(INDEX).decode("utf-8",errors="replace")
    result=collect(html,fetch)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+chr(10))
    print(json.dumps({"quarters_verified":result["quarter_count_verified"],
                      "model_training_permitted":False}))
    if not result["all_2020_2023_original_sources_verified"]:
        raise SystemExit("Some authentic SCE quarters failed; audit JSON retained without claiming success")

if __name__=="__main__":main()
