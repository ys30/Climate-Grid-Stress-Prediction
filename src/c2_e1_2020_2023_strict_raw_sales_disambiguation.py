"""Fail-closed exact original EIA-861 Sales line disambiguation (2020-2023).

Reads provenance-only original candidate CSVs; does not call sector-level sales
cells structural, impute MWh, open 2024-25 demand, or permit E2 training.
"""
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

CANDIDATE_SHA="1527647b41c22e1e80b9bfd997276fd3c63b9a73b27924439e739f6cd5caf415"
GROUP_SHA="ac59f6534934f60b2a00660edb8395cd908c147d70ae34b7594874fefb9768e7"
KEY=("year","utility_id_eia","state","BA")

def rows(path,expected):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("Original archived candidate input SHA256 mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def strict(r):
    a=json.loads(r["raw_values_json"]);y=int(r["year"])
    return (r["archive_member"]==f"Sales_Ult_Cust_{y}.xlsx"
        and r["sheet"]=="States" and len(a)>=9
        and a[0]==str(y) and a[1]==str(int(r["utility_id_eia"]))
        and a[3]=="A" and a[4].lower()=="bundled" and a[5]=="O"
        and a[6]==r["state"] and a[8]==r["BA"])

def reconcile(candidates,groups):
    index=defaultdict(list)
    for r in candidates:index[tuple(r[k] for k in KEY)].append(r)
    outputs=[]
    for group in groups:
        k=tuple(group[x] for x in KEY)
        candidates_for_group=index[k]
        if len(candidates_for_group)!=int(group["candidate_original_sales_rows"]):
            raise ValueError("Original candidate count differs from archived evidence")
        eligible=[r for r in candidates_for_group if strict(r)]
        if len(eligible)!=1:
            raise ValueError("No unique original bundled observed States row: "+str(k))
        r=eligible[0];a=json.loads(r["raw_values_json"])
        outputs.append({"year":k[0],"utility_id_eia":k[1],"state":k[2],"BA":k[3],
          "processed_null_class_records":int(group["processed_null_sector_rows"]),
          "broad_candidate_rows":len(candidates_for_group),
          "exact_original_rows":1,"excluded_nonmatching_candidate_rows":len(candidates_for_group)-1,
          "source_workbook":r["archive_member"],"source_sheet":r["sheet"],
          "source_excel_row":r["excel_row"],"source_utility_name":a[2],
          "original_part":a[3],"original_service_type":a[4],"original_data_type":a[5],
          "original_ownership":a[7],"source_raw_row_sha256":r["raw_row_sha256"],
          "sector_cell_lineage_verified":False,"missing_MWh_imputed":False,
          "model_training_permitted":False})
    if len(outputs)!=468 or sum(r["processed_null_class_records"] for r in outputs)!=810:
        raise ValueError("Unexpected historical source accounting")
    if sum(r["excluded_nonmatching_candidate_rows"] for r in outputs)!=93:
        raise ValueError("Unexpected excluded original candidate count")
    return outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",required=True)
    p.add_argument("--groups",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args();out=Path(x.out);out.mkdir(parents=True,exist_ok=True)
    result=reconcile(rows(x.candidates,CANDIDATE_SHA),rows(x.groups,GROUP_SHA))
    with (out/"C2_E1_468_EXACT_ORIGINAL_SALES_ROWS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    (out/"C2_E1_EXACT_ORIGINAL_SALES_PROVENANCE.json").write_text(json.dumps({
        "candidate_sha256":CANDIDATE_SHA,"group_sha256":GROUP_SHA,
        "source_groups":468,"disambiguated_to_one_original_row":468,
        "eliminated_nontarget_candidates":93,"processed_null_sector_rows":810,
        "raw_sector_cells_proven_structural_zero":False,
        "model_training_permitted":False,"test_hourly_demand_used":False},indent=2)+"\n")
    print("Verified 468 of 468 unique raw bundled observed States rows; 93 nontarget candidates excluded")
if __name__=="__main__":main()
