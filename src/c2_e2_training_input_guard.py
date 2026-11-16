"""C-2 fail-closed preflight for source-only quarantine exports.

Science admission is blocked. Validate candidate inputs; never unlock model fitting.
"""
import argparse,csv,json
from pathlib import Path

EXPECTED_FIELDS=('year','ba','timestamp_utc_start','raw_demand_mw','quarantine',
                 'reason','source_candidate_eligible','model_eligible')
REQUIRED_DENIALS=('model_training_permitted','historical_BA_geography_approved',
                  'load_relevance_approved','training_executed','imputation_performed')

def verify(source_csv,source_manifest):
    with open(source_manifest,encoding='utf-8') as f: meta=json.load(f)
    if not isinstance(meta,dict):raise ValueError('Not a JSON object manifest')
    for field in REQUIRED_DENIALS:
        if meta.get(field) is not False:
            raise ValueError(f'Unsafe/missing negative scientific admission assertion: {field}')
    seen=set();counted=0;candidates=0;quarantined=0
    with open(source_csv,newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not set(EXPECTED_FIELDS).issubset(reader.fieldnames):
            raise ValueError('Source CSV does not carry complete source-vs-model gate fields')
        for row in reader:
            counted+=1
            key=(row['year'],row['ba'],row['timestamp_utc_start'])
            if key in seen:raise ValueError(f'Duplicate BA/source-hour observation: {key}')
            seen.add(key)
            if row['model_eligible']!='False':
                raise ValueError(f'Unsafe E2 model eligibility in candidate source CSV: {key}')
            if row['quarantine'] not in ('True','False') or row['source_candidate_eligible'] not in ('True','False'):
                raise ValueError(f'Unrecognized source-only flag: {key}')
            if row['source_candidate_eligible']==row['quarantine']:
                raise ValueError(f'Conflicting quarantine and source-only eligibility: {key}')
            if not row['raw_demand_mw']:raise ValueError(f'Blank observed raw demand: {key}')
            candidates+=row['source_candidate_eligible']=='True'
            quarantined+=row['quarantine']=='True'
    if counted!=meta.get('raw_observed_points'):
        raise ValueError('Observed row count disagrees with source manifest')
    if candidates!=meta.get('source_candidate_eligible_observed_points'):
        raise ValueError('Candidate row count disagrees with source manifest')
    if quarantined!=meta.get('quarantined_candidate_points'):
        raise ValueError('Quarantine row count disagrees with source manifest')
    if meta.get('model_eligible_observed_points')!=0:
        raise ValueError('Nonzero model-eligible count despite scientific gate')
    return {'source_rows_checked':counted,'source_candidate_passed':candidates,
            'source_quarantined':quarantined,'model_eligible_rows':0,
            'training_permitted':False,'decision':'SOURCE_QA_ONLY_MODEL_BLOCKED'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-csv',required=True)
    p.add_argument('--source-manifest',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    result=verify(a.source_csv,a.source_manifest)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    raise SystemExit('C2 E2 formal training admission remains BLOCKED (preflight source QA verified)')

if __name__=='__main__':main()
