"""Source-only E1 sensitivity: effects of unknown additional EIA-861 bundled MWh.

Requires the immutable 24-row observed sales result; does not estimate missing
MWh or spatially disaggregate utility sales. Never admits E2 model fitting.
"""
import argparse,csv,hashlib,json
from pathlib import Path

SOURCE_SHA="2b437b6288e1d8221aa555c63aadfbf16d033406b4ac5ee6c70bff0d497987c0"
BAS=("AZPS","BPAT","CISO","SRP")
PERIODS={"train_validation_2020_2023":set(range(2020,2024)),
         "source_2020_2025":set(range(2020,2026))}

def analyze(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError("Pinned actual annual EIA861 sales result digest mismatch")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    keys={(int(r["year"]),r["BA"]) for r in rows}
    expected={(year,ba) for year in range(2020,2026) for ba in BAS}
    if len(rows)!=24 or keys!=expected:
        raise ValueError("Incomplete or duplicate true 24 BA-year result")
    scenarios=[];thresholds=[]
    for period,years in PERIODS.items():
        for ba in BAS:
            source=[r for r in rows if r["BA"]==ba and int(r["year"]) in years]
            d=sum(float(r["selected_observed_bundled_sales_mwh"]) for r in source)
            n=sum(float(r["county_matched_sales_mwh"]) for r in source)
            if not 0<n<=d:raise ValueError("Actual source energy accounting invalid")
            for x in (0,0.01,0.025,0.05,0.10,0.25):
                u=x*d
                scenarios.append({"period":period,"BA":ba,"actual_selected_sales_mwh":int(d),
                    "actual_matched_sales_mwh":int(n),"hypothetical_extra_MWh_over_actual":x,
                    "hypothetical_extra_mwh":round(u,2),
                    "conditional_worst_case_pct":round(100*n/(d+u),5),
                    "conditional_best_case_pct":round(100*(n+u)/(d+u),5),
                    "actual_baseline_pct":round(100*n/d,5),
                    "missing_MWh_actually_observed":False,"model_training_permitted":False})
            for target in (.99,.975,.95,.90):
                u=max(0,n/target-d)
                thresholds.append({"period":period,"BA":ba,"target_pct":round(100*target,3),
                    "extra_all_unmatched_MWh_to_reach_or_fall_below_target":round(u,2),
                    "extra_MWh_over_observed_pct":round(100*u/d,5),
                    "observed_already_at_or_below_target":n/d<=target,
                    "is_hypothetical_not_measured":True})
    assert len(scenarios)==48 and len(thresholds)==32
    return scenarios,thresholds

def save(path,rows):
    with Path(path).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--annual",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    scenarios,thresholds=analyze(a.annual)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    save(out/"C2_E1_48_MWH_HYPOTHETICAL_BOUNDS.csv",scenarios)
    save(out/"C2_E1_32_MWH_COVERAGE_THRESHOLDS.csv",thresholds)
    (out/"C2_E1_MWH_BOUNDS_PROVENANCE.json").write_text(json.dumps({
       "pinned_real_sales_annual_result_sha256":SOURCE_SHA,
       "uncounted_original_mwh_rows":1321,
       "actual_missing_mwh_sum_known":False,
       "is_conditional_sensitivity_not_absolute_bound":True,
       "model_training_permitted":False,
       "2024_2025_test_demand_used":False},indent=2)+"\n")
if __name__=="__main__":main()
