"""Read 2020–23 authentic SCE monthly ZIP cells from 16 SHA-pinned XLSX.

Source-only privacy, negative/blank cell and duplicated-key examination,
never a measured county load or EIA-930 BA hourly demand model.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,re,urllib.parse
from collections import Counter
from pathlib import Path
import requests
from openpyxl import load_workbook

EXPECTED={(year,q) for year in range(2020,2024) for q in range(1,5)}
def numeric_state(v):
    if v is None or str(v).strip()=="":return "blank"
    try:x=float(str(v).replace(",",""))
    except (ValueError,TypeError):return "non_numeric"
    if not math.isfinite(x):return "nonfinite"
    return "negative" if x<0 else "zero" if x==0 else "positive"

def parse(raw,year,q):
    book=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    if len(book.worksheets)!=1:raise ValueError("SCE workbook multi-sheet drift")
    sh=book.worksheets[0]
    schema=None
    for row_index,record in enumerate(sh.iter_rows(max_row=25,values_only=True),start=1):
        h=[re.sub("[^a-z0-9]","",str(x).lower()) for x in record[:12]]
        required=("zipcode","month","year","customerclass","combined","totalaccounts","totalkwh","averagekwh")
        if all(x in h for x in required):
            schema=(row_index,{k:h.index(k) for k in required});break
    if schema is None:raise ValueError(f"SCE {year}Q{q} actual column dictionary drift")
    head,index=schema;combined=Counter();state=Counter();classes=Counter();months=Counter();keys=set()
    duplicates=0;rows=0;combined_states=Counter()
    expected_months={str(x) for x in range(3*(q-1)+1,3*q+1)}
    for record in sh.iter_rows(min_row=head+1,values_only=True):
        zip_v=record[index["zipcode"]] if len(record)>index["zipcode"] else None
        if zip_v is None:continue
        z=str(zip_v).strip().replace(".0","")
        if not re.fullmatch("[0-9]{1,5}",z):raise ValueError("SCE ZIP format drift")
        z=z.zfill(5)
        vyear=str(record[index["year"]]).strip().replace(".0","")
        mon=str(record[index["month"]]).strip().replace(".0","")
        if vyear!=str(year) or mon not in expected_months:
            raise ValueError(f"SCE {year}Q{q} actual record year/month out of scope: {vyear}/{mon}")
        c=str(record[index["combined"]]).strip().upper()
        if c not in ("Y","N"):raise ValueError("SCE unknown privacy merged source code")
        clazz=str(record[index["customerclass"]]).strip()
        key=(z,mon,clazz)
        if key in keys:duplicates+=1
        keys.add(key)
        kwh_state=numeric_state(record[index["totalkwh"]])
        combined[c]+=1;state[kwh_state]+=1;classes[clazz]+=1;months[mon]+=1
        combined_states[(c,kwh_state)]+=1
        rows+=1
    if not rows or set(months)!=expected_months:raise ValueError("SCE monthly source coverage incomplete")
    return {"year":year,"quarter":q,"data_rows":rows,"unique_ZIP_month_class_keys":len(keys),
       "duplicate_ZIP_month_class_extra_rows":duplicates,
       "privacy_Combined_source_rows":dict(combined),
       "kwh_original_value_states":dict(state),
       "original_customer_class_source_rows":dict(classes),
       "original_month_source_rows":dict(months),
       "Combined_and_kwh_state_rows":[{"combined":k[0],"kwh_state":k[1],"rows":v}
          for k,v in sorted(combined_states.items())],
       "source_ZIP_recipient_physical_location_verified":False}

def evaluate(manifest,fetch):
    quarters=manifest.get("quarters",[])
    if len(quarters)!=16 or {(r["year"],r["quarter"]) for r in quarters}!=EXPECTED:
        raise ValueError("SCE original SHA manifest missing one or more quarters")
    if not manifest.get("all_2020_2023_original_sources_verified",False):
        raise ValueError("SCE source manifest not scientifically accepted")
    output=[];total=Counter()
    for r in sorted(quarters,key=lambda x:(x["year"],x["quarter"])):
        url=r["source_url"]
        if urllib.parse.urlsplit(url).hostname not in ("sce.com","www.sce.com"):
            raise ValueError("Untrusted SCE source download hostname")
        data=fetch(url)
        sha=hashlib.sha256(data).hexdigest()
        if sha!=r["http_original_source_sha256"]:
            raise ValueError(f"Observed original SCE {r['year']}Q{r['quarter']} SHA256 differs")
        result=parse(data,r["year"],r["quarter"])
        result["original_source_sha256"]=sha
        result["original_source_url"]=url
        output.append(result)
        total.update(result["kwh_original_value_states"])
    return {"decision":"SCE_ORIGINAL_16Q_SOURCE_ROWS_PROFILE_VERIFIED_NO_COUNTY_LOAD",
      "original_CI_manifest_run":45043217550,
      "original_CI_manifest_artifact":14762472124,
      "verified_2020_2023_quarters":len(output),
      "original_publisher_source_sha256_all_16_confirmed":True,
      "source_rows":sum(x["data_rows"] for x in output),
      "total_extra_duplicate_ZIP_month_class_rows":sum(x["duplicate_ZIP_month_class_extra_rows"] for x in output),
      "original_kwh_cell_states":dict(total),
      "quarters":output,
      "ZIP_privacy_merged_geography_identified":False,
      "county_MWh_estimates_calculated":False,
      "model_training_permitted":False,
      "C1_untouched":True}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pinned-manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError("No overwrite")
    manifest=json.loads(args.pinned_manifest.read_text())
    with requests.Session() as ses:
        def fetch(url):
            response=ses.get(url,timeout=80);response.raise_for_status()
            return response.content
        result=evaluate(manifest,fetch)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"quarters":result["verified_2020_2023_quarters"],
        "source_rows":result["source_rows"],
        "duplicate_rows":result["total_extra_duplicate_ZIP_month_class_rows"],
        "kwh_states":result["original_kwh_cell_states"]}))
if __name__=="__main__":main()
