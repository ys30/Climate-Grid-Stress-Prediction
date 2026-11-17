"""Audit original raw 2020-2023 EIA861 Excel sales rows behind processed nulls.

Matches source candidate groups by year, utility EIA ID, exact state and BA
tokens. A match is a *candidate*, not verified class-cell lineage; never
interpret literal '.' as numeric zero.
"""
import argparse,csv,hashlib,io,json,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path

DOI="10.5281/zenodo.23241340"
MD5S={2020:"ef71e150dd76b2fbce8504ce7159358e",
      2021:"c088fae5dca1c1c38a11094a2a096735",
      2022:"8a88824bec4b2aecdc04b0b62fa41452",
      2023:"7472a6617cc00ff4ae10440f7ef12805"}
DERIVED_SHA="6e1e43eeec3b6f0bfb73b5eb25241b8d3e5a3fbf4acdfb9485800fa923bc6300"
DERIVED_MEMBER="C2_E1_MISSING_MWH_SAME_FILING_1321_ROWS.csv"
BAS={"AZPS","BPAT","CISO","SRP"}

def get_keys(artifact_zip):
    with zipfile.ZipFile(artifact_zip) as z:content=z.read(DERIVED_MEMBER)
    if hashlib.sha256(content).hexdigest()!=DERIVED_SHA:
        raise ValueError("Original grouped null-row artifact member digest mismatch")
    rows=list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    rows=[r for r in rows if 2020<=int(r["year"])<=2023]
    if len(rows)!=810:raise ValueError("Expected 810 original processed null sales sector rows")
    keys=defaultdict(list)
    for r in rows:
        key=(int(r["year"]),str(r["utility_id_eia"]),r["state"],r["BA"])
        keys[key].append(r["customer_class"])
    return keys,rows

def strval(v):
    if v is None:return ""
    if isinstance(v,float) and v.is_integer():return str(int(v))
    return str(v).strip()

def audit(artifact_zip,archive_paths,output):
    keys,rows=get_keys(artifact_zip)
    candidates=[];archive_meta=[]
    for year,path in sorted(archive_paths.items()):
        p=Path(path);b=p.read_bytes()
        if hashlib.md5(b).hexdigest()!=MD5S[year]:
            raise ValueError(f"Pinned {year} original EIA861 raw ZIP MD5 mismatch")
        archive_meta.append({"year":year,"original_zip_md5":MD5S[year],
                             "zip_sha256":hashlib.sha256(b).hexdigest()})
        relevant={(u,st,ba) for y,u,st,ba in keys if y==year}
        by_util=defaultdict(set)
        for u,st,ba in relevant:by_util[u].add((st,ba))
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names=[n for n in z.namelist() if n.lower().endswith((".xlsx",".xlsm")) and
                   ("sales" in n.lower() or "ult_cust" in n.lower())]
            if not names:raise ValueError(f"No 2020-23 raw Sales Excel workbook for year {year}")
            import openpyxl
            for filename in names:
                book=openpyxl.load_workbook(io.BytesIO(z.read(filename)),read_only=True,data_only=True)
                for sheet in book.worksheets:
                    for index,row in enumerate(sheet.iter_rows(values_only=True),1):
                        cells=[strval(v) for v in row]
                        # EIA utility ID must be in an early column; do not
                        # match incidental references in free-text cells.
                        utilmatch=next((v for v in cells[:6] if v in by_util),None)
                        if utilmatch is None:continue
                        for st,ba in by_util[utilmatch]:
                            if st not in cells or ba not in cells:continue
                            # Keep raw candidate row verbatim so reviewers can
                            # later confirm year-specific column header mapping.
                            candidates.append({"year":year,"utility_id_eia":utilmatch,
                                "state":st,"BA":ba,"archive_member":filename,
                                "sheet":sheet.title,"excel_row":index,
                                "raw_row_sha256":hashlib.sha256(
                                    json.dumps(cells,ensure_ascii=False).encode()).hexdigest(),
                                "literal_dot_cells":sum(x=="." for x in cells),
                                "raw_values_json":json.dumps(cells,ensure_ascii=False),
                                "is_verified_per_sector_raw_lineage":False})
                book.close()
    groupcount=Counter((int(r["year"]),r["utility_id_eia"],r["state"],r["BA"]) for r in rows)
    candidate_by_key=defaultdict(list)
    for r in candidates:
        candidate_by_key[(r["year"],r["utility_id_eia"],r["state"],r["BA"])].append(r)
    summary=[]
    for key,count in sorted(groupcount.items()):
        source_candidates=candidate_by_key[key]
        summary.append({"year":key[0],"utility_id_eia":key[1],"state":key[2],"BA":key[3],
           "processed_null_sector_rows":count,"candidate_original_sales_rows":len(source_candidates),
           "original_source_candidate_found":bool(source_candidates),
           "raw_excel_sector_cell_lineage_confirmed":False,
           "model_training_permitted":False})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    def write(name,records,fields):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
    write("C2_E1_2020_2023_RAW_SALES_CANDIDATE_GROUPS.csv",summary,list(summary[0]))
    fields=list(candidates[0]) if candidates else [
        "year","utility_id_eia","state","BA","archive_member","sheet",
        "excel_row","raw_row_sha256","literal_dot_cells","raw_values_json",
        "is_verified_per_sector_raw_lineage"]
    write("C2_E1_2020_2023_ORIGINAL_SALES_CANDIDATE_EXCEL_ROWS.csv",candidates,fields)
    (out/"C2_E1_ORIGINAL_2020_2023_SOURCE_PROVENANCE.json").write_text(json.dumps({
        "tagged_pudl_release":"v2026.10.0","pinned_eia861_original_zenodo_doi":DOI,
        "raw_zip_digests":archive_meta,"processed_null_rows":len(rows),
        "source_utility_ba_state_year_groups":len(summary),
        "candidate_groups_found":sum(r["original_source_candidate_found"] for r in summary),
        "candidate_raw_excel_rows":len(candidates),
        "raw_class_cell_lineage_proven":False,
        "sealed_2024_2025_hourly_demand_used":False,
        "model_training_permitted":False},indent=2)+"\n")
    return summary,candidates

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--derived-artifact",required=True)
    for year in MD5S:p.add_argument(f"--raw-{year}",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    archives={y:getattr(args,f"raw_{y}") for y in MD5S}
    groups,candidates=audit(args.derived_artifact,archives,args.out)
    print(json.dumps({"groups":len(groups),"raw_candidates":len(candidates),
        "groups_with_candidates":sum(g["original_source_candidate_found"] for g in groups)}))
if __name__=="__main__":main()
