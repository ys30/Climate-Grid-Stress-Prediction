"""Compare frozen C-2 source-missing totals with newer EIA API audit vintage.

This is a cross-vintage ACCOUNTING comparison, not row-level revision
confirmation. AZPS 2023 canonical annual gate fails and is excluded from
the new audited missing-hour denominator; do not subtract totals as fixes.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

BAS=("AZPS","BPAT","CISO","SRP")
OLD_MISSING={"AZPS":26,"BPAT":0,"CISO":109,"SRP":125}
OLD_HOURS=210432
OLD_MISSING_TOTAL=260
FROZEN_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
NEW_GATE_STATUS="artifact_hash_and_annual_gate_pass"


def compare(waves,diagnostic):
    seen=set()
    missing_by_ba={ba:0 for ba in BAS}
    included_by_ba={ba:[] for ba in BAS}
    rows=[]
    for wave,path in waves.items():
        d=json.loads(Path(path).read_text())
        if not isinstance(d.get("cohorts"),list):
            raise ValueError(f"{wave} does not contain cohort audits")
        for entry in d["cohorts"]:
            ba=entry["ba"];year=entry["year"]
            if ba not in BAS or year not in range(2020,2026) or (ba,year) in seen:
                raise ValueError("Unexpected/duplicate EIA annual cohort")
            seen.add((ba,year))
            ok=entry.get("gate_pass") is True and entry.get("status")==NEW_GATE_STATUS
            if ok:
                n=entry.get("missing_demand_rows")
                h=entry.get("expected_hours")
                v=entry.get("valid_demand_hours")
                absent=entry.get("missing_hours")
                valid_keys=entry.get("unique_hours")
                if (any(type(x) is not int for x in (n,h,v,absent,valid_keys))
                    or min(n,h,v,absent,valid_keys)<0
                    or h-valid_keys!=absent or valid_keys-v!=n):
                    raise ValueError("Yearly source missing count does not reconcile")
                # Explicit demand blanks and missing UTC timestamp keys are
                # disjoint failure classes, even when annual source gate passes.
                missing_by_ba[ba]+=n
                included_by_ba[ba].append(year)
            rows.append({"ba":ba,"year":year,"strict_canonical_pass":ok,
                         "new_missing_demand_rows":entry.get("missing_demand_rows") if ok else None})
    # The only separate pilot is CISO 2024: complete, 100% verified source.
    if ("CISO",2024) in seen:
        raise ValueError("Separate CISO pilot duplicated")
    seen.add(("CISO",2024))
    rows.append({"ba":"CISO","year":2024,"strict_canonical_pass":True,
                 "new_missing_demand_rows":0})
    included_by_ba["CISO"].append(2024)
    expected={(ba,y) for ba in BAS for y in range(2020,2026)}
    if seen!=expected:
        raise ValueError("EIA cohort coverage is incomplete")
    status=json.loads(Path(diagnostic).read_text())
    if (status.get("source_gate_pass") is not False
        or status.get("annual_audit_pass") is not False
        or status.get("invalid_numeric_rows")!=2
        or status.get("missing_demand_rows")!=0
        or status.get("expected_hours")!=8760
        or len(status.get("anomalies_max20",[]))!=2):
        raise ValueError("AZPS2023 separately authenticated source anomaly status missing")
    failures=[(r["ba"],r["year"]) for r in rows if not r["strict_canonical_pass"]]
    if failures!=[("AZPS",2023)]:
        raise ValueError("New BA-year strict gate outcome differs from authenticated evidence")
    old_total=sum(OLD_MISSING.values())
    new_total=sum(missing_by_ba.values())
    if old_total!=OLD_MISSING_TOTAL or new_total!=210:
        raise ValueError("Unexplained change in frozen or newer missing totals")
    return {
        "status":"DIFFERENT_SOURCE_VINTAGES_NOT_HOUR_LEVEL_REVISIONS",
        "frozen_six_year_archive":{"ba_hours":OLD_HOURS,"missing_hours":OLD_MISSING_TOTAL,
                                  "inner_gzip_sha256":FROZEN_SHA,
                                  "per_ba_missing":OLD_MISSING,
                                  "BA_years_in_source_archive":24},
        "newer_independent_year_gates":{"BA_years_pass":23,
            "BA_years_fail":1,"missing_in_23_passing_BA_years":new_total,
            "per_ba_missing_in_passing_years":missing_by_ba,
            "included_BA_years":included_by_ba,
            "AZPS_2023_status":"source present, strict QA fails (2 negative, 0 null)",
            "AZPS_2023_invalid_demand_hours":2},
        "comparability":{
            "raw_total_difference_missing":old_total-new_total,
            "interpretation":"NOT 50 repaired source hours; different vintage and one BA-year excluded",
            "same_BA_year_sample":False,
            "same_source_revision_vintage":False,
            "per_hour_disagreements_verified":False,
            "record_level_revision_audit_needed":True,
            "source_model_training_permitted":False,
        },
        "per_year_new_audit":sorted(rows,key=lambda x:(x["ba"],x["year"]))
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wave1",type=Path,default=Path("docs/E2_WAVE1_VERIFIED_STATUS.json"))
    p.add_argument("--wave2",type=Path,default=Path("docs/E2_WAVE2_VERIFIED_STATUS.json"))
    p.add_argument("--wave3",type=Path,default=Path("docs/E2_WAVE3_VERIFIED_STATUS.json"))
    p.add_argument("--azps2023",type=Path,default=Path("docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json"))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=compare({"wave1":a.wave1,"wave2":a.wave2,"wave3":a.wave3},a.azps2023)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({"status":d["status"],
                      "new_audit_missing_in_passing_years":210,
                      "model_training_permitted":False},indent=2))

if __name__=="__main__":
    main()
