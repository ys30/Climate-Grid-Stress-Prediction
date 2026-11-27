#!/usr/bin/env python3
"""Strict, source-agnostic EIA SRP pilot quality gate. No empirical data fabricated."""
import argparse
import calendar
import csv
import datetime as dt
import json
from pathlib import Path

def gate(daily_path, excluded_path, manifest_path, *, ba='SRP', year=2025, month=7, min_days=25):
    with Path(daily_path).open(newline='', encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    with Path(excluded_path).open(newline='', encoding='utf-8-sig') as f:
        excluded=list(csv.DictReader(f))
    manifest=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    all_dates={dt.date(year,month,d).isoformat() for d in range(1,calendar.monthrange(year,month)[1]+1)}
    seen=set();complete=set();incomplete=set();errors=[]
    for category,values in [('complete',rows),('incomplete',excluded)]:
        for r in values:
            if r['ba']!=ba: continue
            day=r['date_utc']
            if day not in all_dates:
                errors.append(f'unexpected {ba} date in {category}: {day}')
                continue
            if day in seen:
                errors.append(f'duplicate classified date {ba} {day}')
                continue
            seen.add(day)
            if category=='complete':
                if int(r.get('paired_hours',0))!=24:
                    errors.append(f'false-complete day {day}: paired_hours !=24')
                else:complete.add(day)
            else:incomplete.add(day)
    expected=calendar.monthrange(year,month)[1]
    if not (0<=min_days<=expected):raise ValueError('min_days outside calendar month length')
    origin=manifest.get('origin','api')
    if origin not in ('api','bulk'):errors.append(f'unrecognized source origin: {origin}')
    if not any(x.get('ba')==ba and int(x.get('year',0))==year and int(x.get('month',0))==month for x in manifest.get('month_ba_manifest',[])):
        errors.append('source month absent from manifest')
    if len(complete)<min_days:errors.append(f'{len(complete)} complete days below minimum {min_days}')
    return {'passed':not errors,'ba':ba,'year':year,'month':month,'source_origin':origin,
            'calendar_days':expected,'complete_days':len(complete),
            'incomplete_days':len(incomplete),'wholly_missing_days':expected-len(seen),
            'coverage_fraction':len(complete)/expected,'minimum_complete_days':min_days,
            'errors':errors,'note':'Coverage gate only, not evidence of forecast skill or verified forecast vintage'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('daily_csv',type=Path);p.add_argument('excluded_csv',type=Path)
    p.add_argument('source_manifest',type=Path);p.add_argument('--ba',default='SRP')
    p.add_argument('--year',type=int,default=2025);p.add_argument('--month',type=int,default=7)
    p.add_argument('--min-days',type=int,default=25);p.add_argument('--output',type=Path)
    a=p.parse_args()
    result=gate(a.daily_csv,a.excluded_csv,a.source_manifest,ba=a.ba,year=a.year,month=a.month,min_days=a.min_days)
    content=json.dumps(result,indent=2)+'\n'
    print(content,end='')
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(content,encoding='utf-8')
    if not result['passed']:raise SystemExit(2)

if __name__=='__main__':main()
