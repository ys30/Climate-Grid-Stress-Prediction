#!/usr/bin/env python3
"""C2 EIA D/DF BA-year daily coverage and retrospective aggregate benchmark.

Consumes the outputs of c2_eia930_day_ahead_benchmark.py, including the
excluded-day table. A day absent from BOTH tables is counted as wholly missing.
Never labels historical DF a verified issue-time forecast vintage.
"""
import argparse
import calendar
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

def load_rows(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def build_summary(daily_csv, excluded_csv, bas, start_year, end_year):
    if start_year>end_year:
        raise ValueError('Invalid year range')
    good=load_rows(daily_csv)
    dropped=load_rows(excluded_csv)
    known=set()
    by_good=defaultdict(list)
    bad=set()
    for r in good:
        key=(r['ba'],r['date_utc'])
        if key in known:
            raise ValueError('Duplicate BA/date across daily output')
        known.add(key)
        by_good[(r['ba'],int(r['date_utc'][:4]))].append(r)
    for r in dropped:
        key=(r['ba'],r['date_utc'])
        if key in known or key in bad:
            raise ValueError('Duplicate BA/date in output/exclusions')
        bad.add(key)
    result=[]
    for ba in bas:
        for year in range(start_year,end_year+1):
            num_days=366 if calendar.isleap(year) else 365
            dates={ (dt.date(year,1,1)+dt.timedelta(days=i)).isoformat() for i in range(num_days) }
            # Only requested calendar years are scored.
            completed=[r for r in by_good[(ba,year)] if r['date_utc'] in dates]
            complete_dates={r['date_utc'] for r in completed}
            invalid_days={date for b,date in bad if b==ba and date in dates}
            absent=dates-complete_dates-invalid_days
            n=len(completed)
            if n:
                errors=[float(r['signed_peak_error_mw']) for r in completed]
                abs_err=[abs(v) for v in errors]
                metrics={'peak_mae_mw':sum(abs_err)/n,
                         'peak_mean_bias_mw':sum(errors)/n,
                         'underforecast_fraction':sum(v<0 for v in errors)/n}
            else:
                metrics={'peak_mae_mw':None,'peak_mean_bias_mw':None,
                         'underforecast_fraction':None}
            result.append({'ba':ba,'year':year,'calendar_days':num_days,
                           'complete_days':n,'incomplete_days':len(invalid_days),
                           'wholly_missing_days':len(absent),
                           'coverage_fraction':n/num_days,**metrics,
                           'status':'FULL' if n==num_days else 'PARTIAL'})
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('daily_csv',type=Path)
    p.add_argument('excluded_csv',type=Path)
    p.add_argument('output_json',type=Path)
    p.add_argument('--start-year',type=int,default=2023)
    p.add_argument('--end-year',type=int,default=2025)
    p.add_argument('--ba',action='append',required=True)
    a=p.parse_args()
    result=build_summary(a.daily_csv,a.excluded_csv,a.ba,a.start_year,a.end_year)
    a.output_json.parent.mkdir(parents=True,exist_ok=True)
    a.output_json.write_text(json.dumps({'rows':result,
       'status':'COMPLETE' if all(r['status']=='FULL' for r in result) else 'INCOMPLETE',
       'interpretation':'Historical reported EIA DF vs D, not independently verified issue-time vintage.'},
       indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ba_years':len(result),'all_full':all(r['status']=='FULL' for r in result)},indent=2))

if __name__=='__main__':
    main()
