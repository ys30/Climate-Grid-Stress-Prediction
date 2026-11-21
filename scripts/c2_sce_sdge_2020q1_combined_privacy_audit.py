"""Source-only 2020-Q1 SCE+SDGE Combined/zero provenance audit.

No county allocation, no treatment of Combined=Y as physical zero,
no inference that kWh reported at a merged recipient ZIP belongs there.
This is an original utility published-record quality assessment only.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
from openpyxl import load_workbook

SCE_SHA="0d814db6abdb342171899eb57201cb3d3c62767b48cb2ce89aec537e2342431b"
SDGE_SHA="350a0f8e9610dc4347f1705cfeb1ccf06ce1fc4ea528e8f5b88c49cc32b550e7"
SDGE_PUBLISHER_SHA512="a877c771fa7c8804e0e03b30248c11e7eedb8595aa7338cb33327441db713873380c1e4e2f7bdc5fc4b98fe62c02ba58c5eb6273944c1efd2b7189e75113925a"

def hashfile(path,algorithm="sha256"):
    h=hashlib.new(algorithm)
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def asnum(value):
    if value is None or str(value).strip()=="":
        return "blank"
    try:
        n=float(str(value).replace(",",""))
    except (TypeError,ValueError):
        return "non_numeric"
    if not math.isfinite(n):return "nonfinite"
    if n<0:return "negative"
    return "zero" if n==0 else "positive"

def summarize_records(utility,items):
    strata=defaultdict(lambda:{"rows":0,"zip_codes":set(),"kwh_state":Counter(),
                               "accounts_state":Counter(),"duplicate_zip_month_class":0})
    keys=set();duplicate_keys=Counter();duplicate_samples=[];total=0;invalid_period=0
    for r in items:
        total+=1
        zip_code=str(r["zip"]).strip()
        month=str(r["month"]).strip()
        year=str(r["year"]).strip()
        clazz=str(r["class"]).strip()
        combined=str(r["combined"]).strip().upper()
        if not re.fullmatch(r"\d{5}",zip_code):raise ValueError(f"{utility} invalid 5-digit ZIP: {zip_code!r}")
        if year!="2020" or month not in {"1","2","3"}:invalid_period+=1
        if combined not in {"Y","N"}:raise ValueError(f"{utility} unknown Combined code: {combined!r}")
        key=(zip_code,month,clazz)
        if key in keys:
            duplicate_keys[key]+=1
            if len(duplicate_samples)<8:
                duplicate_samples.append({"zip":zip_code,"month":month,"class":clazz,
                                          "combined":combined,
                                          "kwh_state":asnum(r["kwh"]),
                                          "accounts_state":asnum(r["accounts"])})
        keys.add(key)
        bucket=strata[(month,clazz,combined)]
        bucket["rows"]+=1
        bucket["zip_codes"].add(zip_code)
        bucket["kwh_state"][asnum(r["kwh"])]+=1
        bucket["accounts_state"][asnum(r["accounts"])]+=1
    if invalid_period:raise ValueError("Outside original Q1 2020 period")
    if not total:raise ValueError("Empty real electricity data")
    out=[]
    for (month,clazz,combined),v in sorted(strata.items()):
        out.append({"utility":utility,"month":int(month),"customer_class":clazz,
            "combined":combined,"records":v["rows"],"distinct_reported_zip":len(v["zip_codes"]),
            "kwh_state_counts":dict(v["kwh_state"]),"accounts_state_counts":dict(v["accounts_state"]),
            "reported_zero_kwh_is_true_zero_verified":False,
            "combined_record_zip_allocation_approved":False})
    return {"utility":utility,"rows":total,"distinct_ZIP_month_class_keys":len(keys),
            "extra_duplicate_ZIP_month_class_rows":sum(duplicate_keys.values()),
            "duplicate_ZIP_month_class_samples":duplicate_samples,
            "ZIP_month_class_unique_source_grain_verified":len(duplicate_keys)==0,
            "aggregation_at_assumed_ZIP_month_class_grain_permitted":False,
            "strata":out,"combined_Y_rows":sum(x["records"] for x in out if x["combined"]=="Y"),
            "combined_N_rows":sum(x["records"] for x in out if x["combined"]=="N")}

def sce_records(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    if len(wb.worksheets)!=1:raise ValueError("SCE original workbook sheet count changed")
    sh=wb.worksheets[0]
    rows=sh.iter_rows(values_only=True)
    next(rows);next(rows)
    header=[str(x).replace("\n"," ").strip() if x is not None else "" for x in next(rows)[:8]]
    expected=["Zip Code","Month","Year","Customer Class","Combined","TotalAccounts","TotalkWh","AveragekWh"]
    if header!=expected:raise ValueError(f"SCE original column schema differs: {header}")
    for row in rows:
        if not row or row[0] is None:continue
        zip_code=str(row[0]).split(".")[0].zfill(5)
        yield {"zip":zip_code,"month":str(row[1]),"year":str(row[2]),
               "class":str(row[3]),"combined":str(row[4]),
               "accounts":row[5],"kwh":row[6]}

def sdge_records(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        expected=["ZipCode","Month","Year","CustomerClass","Combined","TotalCustomers","TotalkWh","AveragekWh"]
        if reader.fieldnames!=expected:
            raise ValueError("SDGE original 2020Q1 source fields changed")
        for row in reader:
            yield {"zip":row["ZipCode"],"month":row["Month"],"year":row["Year"],
                   "class":row["CustomerClass"],"combined":row["Combined"],
                   "accounts":row["TotalCustomers"],"kwh":row["TotalkWh"]}

def run(sce,sdge,hashfile_sdge):
    if hashfile(sce)!=SCE_SHA:raise ValueError("SCE SHA256 changed")
    if hashfile(sdge)!=SDGE_SHA:raise ValueError("SDGE SHA256 changed")
    publisher=Path(hashfile_sdge).read_text(encoding="utf-8",errors="replace")
    match=re.search(r"\b([0-9A-Fa-f]{128})\b",publisher)
    if not match or match.group(1).lower()!=hashfile(sdge,"sha512") or match.group(1).lower()!=SDGE_PUBLISHER_SHA512:
        raise ValueError("Original SDGE publisher SHA512 mismatch")
    a=summarize_records("SCE",sce_records(sce))
    b=summarize_records("SDGE",sdge_records(sdge))
    if b["rows"]!=1719 or b["combined_Y_rows"]!=1421 or b["combined_N_rows"]!=298:
        raise ValueError("SDGE independently pinned Q1 source row/Combined contract changed")
    return {"status":"OBSERVED_UTILITY_ZIP_COMBINED_PRIVACY_PROVENANCE_ONLY",
            "verified_original_run_reference":44917907054,
            "actual_original_SCE_SHA256":SCE_SHA,"actual_original_SDGE_SHA256":SDGE_SHA,
            "SDGE_publisher_SHA512_verified":True,
            "period":"2020Q1","utilities":[a,b],
            "combined_Y_is_not_proof_of_consumption_zero":True,
            "privacy_suppressed_cells_reconstructed":False,
            "county_specific_MWh_observed":False,
            "ZIP_to_county_weights_calibrated":False,
            "historic_CISO_BA_utility_member_crosswalk_verified":False,
            "model_training_permitted":False,
            "C1_untouched":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sce",required=True,type=Path)
    p.add_argument("--sdge",required=True,type=Path)
    p.add_argument("--sdge-hash",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError("No overwrite")
    result=run(args.sce,args.sdge,args.sdge_hash)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"SCE_rows":result["utilities"][0]["rows"],
                      "SDGE_rows":result["utilities"][1]["rows"],
                      "SDGE_combined_Y":result["utilities"][1]["combined_Y_rows"],
                      "model_training_permitted":False}))

if __name__=="__main__":main()
