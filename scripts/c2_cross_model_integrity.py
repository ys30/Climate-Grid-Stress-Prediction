#!/usr/bin/env python3
"""Fail-closed cross-estimator consistency gate for pre-labeled C2 event pairs."""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

REQUIRED = ('ba','date','target','estimator','event_category','episode_id','actual_mw','calendar_pred_mw','weather_pred_mw')

def validate(path):
    path=Path(path)
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    by_day=defaultdict(list)
    by_episode=defaultdict(set)
    counts=defaultdict(int)
    issues=[]
    with path.open(newline='',encoding='utf-8-sig') as fh:
        reader=csv.DictReader(fh)
        missing=set(REQUIRED)-set(reader.fieldnames or ())
        if missing:
            raise ValueError('Missing columns: '+', '.join(sorted(missing)))
        n=0
        for line,r in enumerate(reader,2):
            n+=1
            try:
                import datetime
                day=datetime.date.fromisoformat(r['date'])
                actual=float(r['actual_mw'])
                preds=[float(r[c]) for c in ('calendar_pred_mw','weather_pred_mw')]
                if not all(math.isfinite(v) for v in [actual]+preds):
                    raise ValueError('nonfinite numeric value')
                key=(r['ba'].strip(),day.isoformat(),r['target'].strip(),r['event_category'].strip())
                model=r['estimator'].strip()
                ep=r['episode_id'].strip()
                if not all([key[0],key[2],key[3],model,ep]):
                    raise ValueError('blank key')
                if model in [x[0] for x in by_day[key]]:
                    raise ValueError('duplicate estimator for BA/date/target/category')
                by_day[key].append((model,actual,ep))
                by_episode[(key[0],key[2],key[3],model,ep)].add(day)
                counts[model]+=1
            except (ValueError,TypeError,KeyError) as err:
                issues.append({'line':line,'issue':str(err)})
    if not n:
        issues.append({'issue':'empty input'})
    for key,obs in by_day.items():
        if len({v[1] for v in obs})>1:
            issues.append({'key':str(key),'issue':'actual_mw differs across estimators'})
        if len({v[2] for v in obs})>1:
            issues.append({'key':str(key),'issue':'episode_id differs across estimators'})
    for key,dates in by_episode.items():
        ss=sorted(dates)
        if len({d.year for d in ss})>1:
            issues.append({'key':str(key),'issue':'episode crosses calendar year'})
        if len(ss)<2:
            issues.append({'key':str(key),'issue':'singleton episode'})
        if any((b-a).days!=1 for a,b in zip(ss,ss[1:])):
            issues.append({'key':str(key),'issue':'episode has date gap'})
    return {'input_sha256':sha,'rows':n,'day_keys':len(by_day),
            'model_rows':dict(sorted(counts.items())),'passed':not issues,'issues':issues}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input_csv',type=Path)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    result=validate(args.input_csv)
    output=json.dumps(result,indent=2)+'\n'
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(output,encoding='utf-8')
    print(output,end='')
    raise SystemExit(0 if result['passed'] else 2)

if __name__=='__main__':
    main()
