"""C2 E1: reclassify real PUDL EIA861 missing MWh source records, without imputation.
Input: successful Actions run 44038797725 source detail; NO E2 training.
"""
import csv,hashlib,json,argparse
from pathlib import Path
from collections import defaultdict
SOURCE_SHA256="b7f3e7d1d1ddc9258b9f8461324c269d2a92c3758b623b92740532143eddffc4"
EXPECTED={"other":709,"transportation":386,"industrial":127,"commercial":52,"residential":47}
BAS={"AZPS","BPAT","CISO","SRP"}

def analyze(source):
    raw=Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Original real EIA861 missing-sales source hash differs")
    data=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    missing=defaultdict(int);observed=defaultdict(int)
    for r in data:
        ba=r["BA"];yr=int(r["year"]);cls=r["customer_class"];stage=r["classification"]
        if ba not in BAS or not 2020<=yr<=2025:raise ValueError("Unexpected BA-year")
        n=int(r["source_rows"])
        if n<0:raise ValueError("Negative source row counts")
        if stage=="04_eligible_bundled_missing_mwh":missing[ba,yr,cls]+=n
        elif stage=="05_selected_nonmissing_mwh":observed[ba,yr,cls]+=n
    totals={cls:sum(n for (ba,yr,c),n in missing.items() if c==cls) for cls in EXPECTED}
    if totals!=EXPECTED:raise ValueError("Original PUDL source classification count drift")
    detail=[{"BA":ba,"year":yr,"customer_class":cls,
         "missing_sales_mwh_records":missing[ba,yr,cls],
         "nonmissing_sales_mwh_records":observed[ba,yr,cls],
         "other_is_proven_structural_zero":False}
      for ba in sorted(BAS) for yr in range(2020,2026) for cls in EXPECTED]
    summary=[]
    for ba in sorted(BAS):
      for period,years in (("2020_2023",range(2020,2024)),("2024_2025",range(2024,2026)),("2020_2025",range(2020,2026))):
        counts={cls:sum(missing[ba,yr,cls] for yr in years) for cls in EXPECTED}
        summary.append({"BA":ba,"period":period,"missing_total":sum(counts.values()),
          "other_historical_placeholder_candidate":counts["other"],
          "transportation_missing":counts["transportation"],
          "industrial_commercial_residential_missing":sum(counts[c] for c in ("industrial","commercial","residential")),
          "non_other_missing":sum(v for c,v in counts.items() if c!="other"),
          "unknown_MWh_not_imputed":True,"model_training_permitted":False})
    return detail,summary

def save(path,rows):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();details,summary=analyze(a.source);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    save(out/"C2_120_BA_YEAR_CLASS_RECORDS.csv",details)
    save(out/"C2_12_BA_PERIOD_MISSINGNESS.csv",summary)
    (out/"PROVENANCE.json").write_text(json.dumps({"source_sha256":SOURCE_SHA256,
       "other_historical_category_candidates":709,"non_other_missing_records":612,
       "actual_missing_MWh_quantified":False,"2024_2025_EIA930_demand_test_used":False,
       "E2_training_permitted":False},indent=2)+"\n")
if __name__=="__main__":main()
