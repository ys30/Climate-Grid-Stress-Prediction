#!/usr/bin/env python3
"""Fail-closed SHA-pinned 336-fit historical LOYO source admission audit."""
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
LOYO_SHA="41af7c24fd536c5d652f3cf39302499e9870c473d833fb98902375c91f31f0f1"
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def audit(protocol,loyo):
    p=json.loads(Path(protocol).read_text())
    if p["data"]["existing_LOYO_CSV_sha256"]!=LOYO_SHA or sha(loyo)!=LOYO_SHA:
        raise ValueError("Verified 336-fit LOYO source SHA mismatch")
    with Path(loyo).open(newline="") as f:rows=list(csv.DictReader(f))
    if len(rows)!=336:raise ValueError("Expected 336 real-source historical fits")
    groups=defaultdict(dict)
    for row in rows:
        key=tuple(row[k] for k in ("ba","season","target","variant"))
        if row["ba"] not in p["BA_codes"] or row["weather_mask_approved"]!="False" or row["causal"]!="False":
            raise ValueError("Unapproved geography/causal inference or BA code")
        name=row["omitted_year"]
        if name in groups[key]:raise ValueError("Repeated fit cohort")
        if name not in {"NONE","2020","2021","2022","2023","2024","2025"}:
            raise ValueError("Invalid omitted-year identifier")
        for k in ("cold_MW_per_C","warm_MW_per_C","rmse_MW","cold_delta_vs_full"):
            if not math.isfinite(float(row[k])):raise ValueError("Invalid fit number")
        groups[key][name]=row
    required={"NONE","2020","2021","2022","2023","2024","2025"}
    if len(groups)!=48 or any(set(v)!=required for v in groups.values()):
        raise ValueError("Incorrect 48×7 factorial grid")
    all_deltas=[]
    for g in groups.values():
        full=g["NONE"];base=float(full["cold_MW_per_C"])
        for year,row in g.items():
            if year=="NONE":continue
            if int(row["n_days"])>=int(full["n_days"]):
                raise ValueError("LOYO did not actually delete year observations")
            difference=float(row["cold_MW_per_C"])-base
            if abs(difference-float(row["cold_delta_vs_full"]))>1e-6:
                raise ValueError("LOYO coefficient difference does not reconcile")
            all_deltas.append(abs(difference))
    return {"status":"PASS_DESCRIPTIVE_ONLY","fits":336,"model_configs":48,
            "deletion_refits":288,"LOYO_csv_sha256":LOYO_SHA,
            "max_abs_cold_slope_deletion_change_MW_per_C":max(all_deltas),
            "heldout_predictions_evaluated":False,
            "untouched_2025_test_set":False,
            "weather_mask_approved":False,
            "formal_causal_and_future_model_training_permitted":False,
            "reason":"Model fitted only on retained years; deletion sensitivity is not held-out validation"}
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--protocol",required=True);a.add_argument("--loyo",required=True);a.add_argument("--out",required=True)
    x=a.parse_args()
    path=Path(x.out)
    if path.exists():raise FileExistsError(path)
    result=audit(x.protocol,x.loyo)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
