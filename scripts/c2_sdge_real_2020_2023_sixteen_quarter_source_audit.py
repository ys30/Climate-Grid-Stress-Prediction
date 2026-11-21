"""Independent public SDG&E 2020–2023 original 16-quarter source integrity.

Original quarterly CSV and corresponding publisher SHA512 sidecar are
mandatory for EVERY quarter. Source-only privacy and completeness audit;
NEVER infer county load, undo Combined privacy suppression, model or fit
2024–25 sealed EIA-930 demand observations.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re
from collections import Counter
from pathlib import Path

YEARS=range(2020,2024)
QUARTERS=range(1,5)
FIELDS=["ZipCode","Month","Year","CustomerClass","Combined",
        "TotalCustomers","TotalkWh","AveragekWh"]
HASH_PATTERN=re.compile(r"\b([0-9A-Fa-f]{128})\b")

def inspect_one(path,sidecar,year,quarter):
    data=Path(path).read_bytes()
    if len(data)<100 or data[:32].lower().lstrip().startswith((b"<html",b"<!doctype")):
        raise ValueError(f"{year}Q{quarter}: download not original CSV")
    digest=hashlib.sha512(data).hexdigest()
    sidecar_content=Path(sidecar).read_text("utf-8",errors="replace")
    published=HASH_PATTERN.findall(sidecar_content)
    if len(published)!=1 or published[0].lower()!=digest:
        raise ValueError(f"{year}Q{quarter}: official source SHA512 missing or mismatch")
    with open(path,encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        if rdr.fieldnames!=FIELDS:
            raise ValueError(f"{year}Q{quarter}: source column schema drift {rdr.fieldnames}")
        rows=list(rdr)
    if not rows:raise ValueError(f"{year}Q{quarter}: no original rows")
    expected={str(x) for x in range((quarter-1)*3+1,quarter*3+1)}
    months=Counter();combined=Counter();states=Counter();classes=Counter();negative_groups=Counter()
    keys=set();duplicate_keys=0
    for r in rows:
        if r["Year"]!=str(year) or r["Month"] not in expected:
            raise ValueError(f"{year}Q{quarter}: original calendar period mismatch")
        zipcode=r["ZipCode"].strip()
        if not re.fullmatch(r"\d{5}",zipcode):
            raise ValueError(f"{year}Q{quarter}: bad original ZIP field")
        m=r["Month"]; months[m]+=1
        key=(zipcode,m,r["CustomerClass"])
        if key in keys:duplicate_keys+=1
        keys.add(key)
        c=r["Combined"].strip().upper()
        if c not in ("Y","N"):raise ValueError(f"{year}Q{quarter}: unknown Combined value")
        combined[c]+=1;classes[r["CustomerClass"]]+=1
        val=r["TotalkWh"].strip()
        if not val:states["blank"]+=1
        else:
            try:x=float(val)
            except ValueError:states["non_numeric"]+=1
            else:
                if not math.isfinite(x):states["nonfinite"]+=1
                elif x<0:
                    states["negative"]+=1
                    negative_groups[(m,r["CustomerClass"],c)]+=1
                elif x==0:states["literal_zero"]+=1
                else:states["positive"]+=1
    if set(months)!=expected:raise ValueError(f"{year}Q{quarter}: missing original month")
    return {"year":year,"quarter":quarter,"raw_CSV_SHA256":hashlib.sha256(data).hexdigest(),
       "original_publisher_SHA512":digest,"publisher_hash_matched":True,
       "source_rows":len(rows),"month_row_counts":dict(sorted(months.items())),
       "privacy_Combined_counts":dict(combined),"customer_class_row_counts":dict(classes),
       "kwh_value_states":dict(states),
       "negative_kwh_original_class_combined_month":[{"month":int(key[0]),"customer_class":key[1],"combined":key[2],"rows":count} for key,count in sorted(negative_groups.items())],
       "duplicate_ZIP_month_class_extra_rows":duplicate_keys,
       "reporting_ZIP_aggregate_is_observed_county_load":False}

def run(directory):
    directory=Path(directory);quarterly=[]
    for y in YEARS:
        for q in QUARTERS:
            base=f"SDGE-ELEC-{y}-Q{q}"
            quarterly.append(inspect_one(
                directory/f"{base}.csv",directory/f"{base}-HASH.txt",y,q))
    if len(quarterly)!=16 or len({(r["year"],r["quarter"]) for r in quarterly})!=16:
        raise ValueError("Expected 16 distinct source quarters")
    known=next(r for r in quarterly if r["year"]==2020 and r["quarter"]==1)
    if known["source_rows"]!=1719 or known["privacy_Combined_counts"]!={"Y":1421,"N":298}:
        raise ValueError("2020Q1 previously independently pinned original quarter differs")
    combined=Counter();kwh=Counter();negative_by_class_combined=Counter()
    for r in quarterly:
        combined.update(r["privacy_Combined_counts"])
        kwh.update(r["kwh_value_states"])
        for group in r["negative_kwh_original_class_combined_month"]:
            negative_by_class_combined[(group["customer_class"],group["combined"])]+=group["rows"]
    if kwh["negative"]!=50 or sum(negative_by_class_combined.values())!=50:
        raise ValueError("Original 50 negative kWh rows changed or classification incomplete")
    return {"status":"REAL_SDGE_16_QUARTER_ORIGINAL_PUBLISHER_HASH_VERIFIED",
        "quarters":16,"years":[2020,2021,2022,2023],
        "raw_source_records":sum(r["source_rows"] for r in quarterly),
        "combined_flags":dict(combined),
        "kwh_value_states":dict(kwh),
        "negative_source_class_combined_groups":[{"customer_class":k[0],"combined":k[1],"rows":count} for k,count in sorted(negative_by_class_combined.items())],
        "negative_kwh_as_meter_errors_proven":False,\n        "quarterly_original_provenance":quarterly,
        "publisher_SHA512_all_quarters_valid":True,
        "privacy_Combined_mapped_to_original_physical_ZIP":False,
        "ZIP_to_county_allocation_performed":False,
        "actual_county_electricity_MWh_verified":False,
        "historical_CISO_BA_geography_authorized":False,
        "model_training_permitted":False,"sealed_2024_2025_hourly_demand_used":False,
        "C1_frozen_untouched":True}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--directory",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError("Refuse to overwrite verified source audit")
    r=run(args.directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:r[k] for k in ("quarters","raw_source_records","combined_flags",
        "kwh_value_states","model_training_permitted")},indent=2))

if __name__=="__main__":main()
