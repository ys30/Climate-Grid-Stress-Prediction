#!/usr/bin/env python3
"""Source-only four-BA extreme-spike neighborhood QA. Never clean automatically."""
import argparse,gzip,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_MEMBER='results/C2_2020_2025_DUAL_VINTAGE_QUARANTINE_NOT_MODEL.csv.gz'
SOURCE_SHA='2e61b850272495e9e1644f23d06a3bb1c3aa93229229974a0ac7aa00432eec4c'
MEMBER_SHA='5a7fc7bf030cdac33131c480ca0c145db0b942db050e09bf1c5d1396994dbee1'

def hashbytes(b):
    return hashlib.sha256(b).hexdigest()

def run(source,out):
    source,out=Path(source),Path(out)
    if out.exists():raise FileExistsError(out)
    if hashbytes(source.read_bytes())!=SOURCE_SHA:
        raise ValueError('Unexpected source ZIP hash')
    with zipfile.ZipFile(source) as z:
        if z.testzip():raise ValueError('CRC failed')
        member=z.read(SOURCE_MEMBER)
    if hashbytes(member)!=MEMBER_SHA:
        raise ValueError('Unexpected source member hash')
    df=pd.read_csv(io.BytesIO(gzip.decompress(member)))
    if len(df)!=210432 or df.duplicated(['ba','utc_start']).any():
        raise ValueError('Unexpected source cohort')
    df['utc']=pd.to_datetime(df.utc_start,utc=True)
    items=[];stats=[]
    for ba,b in df.groupby('ba'):
        b=b.sort_values('utc').reset_index(drop=True)
        vals=b.old_bulk_demand_mw.astype(float)
        context=pd.concat([vals.shift(h) for h in list(range(-12,-2))+list(range(3,13))],axis=1)
        med=context.median(axis=1)
        nref=context.notna().sum(axis=1)
        ratio=vals/med
        screen=(nref>=14)&(med>0)&(vals>=10000)&(ratio>=3)
        b['ref_median_mw']=med;b['ratio']=ratio;b['screen']=screen
        for i,row in b.loc[screen].iterrows():
            window=b.iloc[max(0,i-2):min(len(b),i+3)]
            api=bool(row.api_source_checked)
            same=(api and pd.notna(row.new_api_demand_mw) and
                  float(row.old_bulk_demand_mw)==float(row.new_api_demand_mw))
            items.append(dict(ba=ba,hour_utc=row.utc.isoformat(),
                old_bulk_mw=row.old_bulk_demand_mw,
                local_20hour_reference_median_mw=row.ref_median_mw,
                ratio_to_reference=row.ratio,
                source_flagged=bool(row.original_anomaly_candidate),
                neighboring_source_flagged_within_2h=bool(window.original_anomaly_candidate.any()),
                api_source_checked=api,api_numeric_equal=same if api else None,
                source_status=row.source_status,
                operator_verified=False,automatic_delete_approved=False))
        stats.append(dict(ba=ba,source_hours=len(b),
            source_flagged_hours=int(b.original_anomaly_candidate.sum()),
            screened_extreme_hours=int(screen.sum()),
            unflagged_screened_hours=int((screen&~b.original_anomaly_candidate).sum()),
            screened_hours_with_API_checked=int((screen & b.api_source_checked).sum()),
            screened_hours_with_API_unavailable=int((screen & ~b.api_source_checked).sum())))
    out.mkdir(parents=True)
    a=pd.DataFrame(items).sort_values(['ba','hour_utc'])
    s=pd.DataFrame(stats)
    a.to_csv(out/'FOUR_BA_FAMILY_SCREEN_REVIEW_HOURS.csv',index=False)
    s.to_csv(out/'FOUR_BA_FAMILY_SCREEN_SOURCE_QA.csv',index=False)
    result=dict(source_zip_sha256=hashbytes(source.read_bytes()),
        source_member_gzip_sha256=hashbytes(member),
        method='20 reference UTC hours at offsets [-12,-3] and [3,12]; >=14 valid; >=10000MW and >=3x reference',
        scope='source-only candidate screen, not an error classifier or correction',
        source_rows=len(df),total_screened_hours=len(a),
        total_unflagged_screened=int((~a.source_flagged).sum()),
        source_counts=stats,operator_verified=False,
        geography_approved=False,model_training_allowed=False)
    for f in out.glob('*.csv'):
        result[f.name+'_sha256']=hashbytes(f.read_bytes())
    (out/'SOURCE_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-zip',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.source_zip,args.out),indent=2))
