"""Source-vintage EIA-930 revision windows in candidate civil-time zones.

The chosen IANA zones are geographical hypotheses, NOT confirmed BA/EIA
reporting timezones or proof of re-submission mechanism. Input values remain
unmodified and model eligibility remains false.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timedelta,timezone,time
from pathlib import Path
from zoneinfo import ZoneInfo
from collections import Counter

EXPECTED_SHA="6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480"
ZONE_HYPOTHESES={"AZPS":"America/Phoenix","BPAT":"America/Los_Angeles"}
TARGET={("AZPS","2025"),("BPAT","2021"),("BPAT","2023")}

def civil_day_utc_bounds(local_date, zone):
    """Return UTC interval for a whole local civil date, including DST 23/25h."""
    start_local=datetime.combine(local_date,time.min,tzinfo=zone)
    end_local=datetime.combine(local_date+timedelta(days=1),time.min,tzinfo=zone)
    start=start_local.astimezone(timezone.utc)
    end=end_local.astimezone(timezone.utc)
    length=int((end-start)/timedelta(hours=1))
    if length not in (23,24,25):
        raise ValueError("Unexpected local civil day length")
    return start,end,length


def classify_civil_day(first,last,n,zone):
    """Exact UTC interval equality, not wall-clock hour-count inference."""
    local=first.astimezone(zone)
    start,end,expected=civil_day_utc_bounds(local.date(),zone)
    return (n==expected and first==start and
            last+timedelta(hours=1)==end),expected


def audit(source:Path,expected_sha=EXPECTED_SHA):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=expected_sha:
        raise ValueError("Original comparison CSV changed; SHA mismatch")
    with source.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
    episodes=[]
    for ba,year in sorted(TARGET):
        entries=sorted(((datetime.fromisoformat(r["timestamp_utc"].replace("Z","+00:00")),r)
                        for r in rows if r["ba"]==ba and r["year"]==year
                        and r["classification"]!="both_null"),key=lambda t:t[0])
        if len({t for t,_ in entries})!=len(entries):
            raise ValueError("Duplicate UTC source disagreement")
        spans=[]
        for t,r in entries:
            if not spans or t-spans[-1][-1][0]!=timedelta(hours=1):spans.append([])
            spans[-1].append((t,r))
        zone=ZoneInfo(ZONE_HYPOTHESES[ba])
        for seq in spans:
            first,last=seq[0][0],seq[-1][0]
            lf,ll=first.astimezone(zone),last.astimezone(zone)
            midnight=lf.hour==0 and lf.minute==0
            full,expected_local_hours=classify_civil_day(first,last,len(seq),zone)
            episodes.append({"ba":ba,"year":int(year),
                "start_utc":first.isoformat().replace("+00:00","Z"),
                "end_utc":last.isoformat().replace("+00:00","Z"),
                "hours":len(seq),"classes":dict(Counter(r["classification"] for _,r in seq)),
                "hypothetical_iana_zone":ZONE_HYPOTHESES[ba],
                "hypothetical_local_start":lf.isoformat(),
                "hypothetical_local_end":ll.isoformat(),
                "hypothetical_local_calendar_midnight_start":midnight,
                "hypothetical_one_full_civil_day":full,
                "hypothetical_civil_day_expected_hours":expected_local_hours,
                "DST_23_25_hour_calendar_explicitly_supported":True,
                "actual_BA_reporting_timezone_verified":False,
                "daily_resubmission_causality_established":False})
    return {"source":"Original SHA-verified 23-BA-year old/new changed rows",
            "source_sha256":expected_sha,
            "total_nonidentical_hours":sum(x["hours"] for x in episodes),
            "number_of_episodes":len(episodes),
            "complete_hypothetical_local_days":sum(x["hypothetical_one_full_civil_day"] for x in episodes),
            "local_time_is_exploratory_hypothesis_only":True,
            "official_submission_vintage_or_change_log_obtained":False,
            "model_training_permitted":False,
            "episodes":episodes}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Output exists; no overwrite")
    d=audit(a.source)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({"episodes":d["number_of_episodes"],
                      "full_hypothetical_local_days":d["complete_hypothetical_local_days"],
                      "model_training_permitted":False}))

if __name__=="__main__":main()
