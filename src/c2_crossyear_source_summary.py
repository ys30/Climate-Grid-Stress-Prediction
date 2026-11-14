"""Compile independently verified annual two-day E1 source audit manifests.

No extrapolation from audited hours to yearly weather availability, and no
authorization for training from historical provisional BA geography.
"""
import argparse,csv,json
from pathlib import Path
from collections import Counter

EXPECTED=tuple(range(2020,2026))
def combine(manifests):
    seen={};rows=[]
    for report in manifests:
        when=report.get("utc_start","")
        year=int(when[:4])
        if year not in EXPECTED or year in seen:raise ValueError("Duplicate or unsupported study year")
        if report.get("BAs")!=["AZPS","BPAT","CISO","SRP"]:
            raise ValueError("BA scope changed between year audits")
        if report.get("historical_geometry_approved") is not False:
            raise ValueError("Geography must remain unapproved")
        if report.get("training_or_validation_permitted") is not False:
            raise ValueError("Model use is not permitted in raw-source audit")
        if report.get("no_imputation") is not True:
            raise ValueError("Imputation prohibited")
        if report.get("days")!=2 or report.get("hours_per_BA")!=48:
            raise ValueError("Each year must use exactly two UTC days")
        if report.get("paired_source_rows")!=192 or report.get("weather_source_rows")!=192:
            raise ValueError("Each year must have exactly 192 source rows")
        if report.get("all_source_hours_present") is not True:
            raise ValueError("Source hour coverage failed")
        seen[year]=report
        rows.append({"year":year,"utc_start":when,"hours_per_BA":48,
                     "observed_source_pairs":192,
                     "source_quarantine_flags":report["eia_candidate_anomaly_flags_in_window"],
                     "complete_pairing":True,"model_eligible":False})
    if set(seen)!=set(EXPECTED):
        raise ValueError("Require six separately verified annual audits")
    hashes={r["weights_sha256"] for r in seen.values()}
    if len(hashes)!=1:raise ValueError("Source geometry weight version mismatch")
    summary={"years":list(EXPECTED),"year_count":6,
             "observed_hours_per_BA_across_sampled_windows":288,
             "real_source_pairs_total":sum(r["observed_source_pairs"] for r in rows),
             "area_weight_sha256":next(iter(hashes)),
             "annual_full_weather_data_verified":False,
             "training_authorized":False,"geometry_historical_approval":False,
             "causal_attribution_performed":False}
    return sorted(rows,key=lambda x:x["year"]),summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifests",nargs="+",required=True)
    p.add_argument("--out",default="outputs/e1_crossyear_summary")
    a=p.parse_args()
    records=[json.loads(Path(x).read_text()) for x in a.manifests]
    rows,summary=combine(records)
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    with (output/"crossyear_two_day_source_summary.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (output/"crossyear_source_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("C2_CROSSYEAR_SOURCE_SUMMARY",json.dumps(summary))
if __name__=="__main__":main()
