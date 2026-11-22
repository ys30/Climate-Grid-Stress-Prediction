#!/usr/bin/env python3
"""Audit BA demand × weather-proxy UTC hourly coverage; never fit a model.

Inputs are separately sourced CSVs. Required demand columns: ba,utc_start,demand_mw.
Required weather columns: ba,utc_start,weather_value. A weather_value represents
an explicitly documented proxy, not a verified load-weighted exposure.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

UTC = dt.timezone.utc

def parse_utc_hour(s):
    if not s.endswith('Z') and not s.endswith('+00:00'):
        raise ValueError('timestamps must explicitly specify UTC (+00:00 or Z)')
    t = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if t.utcoffset() != dt.timedelta(0) or any((t.minute, t.second, t.microsecond)):
        raise ValueError('not an exact UTC hour')
    return t

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load(path, field, bas, start_year, end_year):
    records, errors = {}, []
    duplicates = defaultdict(int)
    poisoned_keys = set()
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        needed = {'ba', 'utc_start', field}
        if not needed.issubset(set(reader.fieldnames or [])):
            raise ValueError(f'{path}: missing required columns {sorted(needed - set(reader.fieldnames or []))}')
        for line, row in enumerate(reader, 2):
            ba = (row['ba'] or '').strip().upper()
            if ba not in bas:
                continue
            try:
                time = parse_utc_hour((row['utc_start'] or '').strip())
            except ValueError as e:
                errors.append({'line': line, 'reason': str(e), 'ba': ba})
                continue
            if not start_year <= time.year <= end_year:
                continue
            key = (ba, time)
            if key in records:
                duplicates[(ba, time.year)] += 1
                poisoned_keys.add(key)
                records[key] = None
                continue
            try:
                val = float(row[field]) if row[field] and row[field].strip() else None
                if val is not None and (not math.isfinite(val) or (field == 'demand_mw' and val < 0)):
                    raise ValueError('nonfinite or negative demand')
            except ValueError:
                val = None
            records[key] = None if key in poisoned_keys else val
    return records, duplicates, errors

def audit(demand_file, weather_file, bas, start_year=2020, end_year=2025, min_fraction=0.98):
    demand, ddups, derr = load(demand_file, 'demand_mw', bas, start_year, end_year)
    weather, wdups, werr = load(weather_file, 'weather_value', bas, start_year, end_year)
    years = []
    for ba in bas:
        for year in range(start_year, end_year + 1):
            t = dt.datetime(year, 1, 1, tzinfo=UTC)
            stop = dt.datetime(year + 1, 1, 1, tzinfo=UTC)
            expected = int((stop - t).total_seconds() // 3600)
            demand_ok = weather_ok = paired = 0
            while t < stop:
                dv, wv = demand.get((ba, t)), weather.get((ba, t))
                demand_ok += dv is not None
                weather_ok += wv is not None
                paired += dv is not None and wv is not None
                t += dt.timedelta(hours=1)
            dups = ddups[(ba, year)] + wdups[(ba, year)]
            fraction = paired / expected
            years.append({'ba': ba, 'year': year, 'expected_hours': expected,
                          'demand_valid_hours': demand_ok, 'weather_valid_hours': weather_ok,
                          'paired_valid_hours': paired, 'paired_fraction': round(fraction, 8),
                          'duplicate_rows': dups,
                          'coverage_pass': fraction >= min_fraction and dups == 0 and not derr and not werr})
    return {'status': 'INVENTORY_ONLY_NO_MODEL_PERMISSION',
            'demand_sha256': sha256(demand_file), 'weather_sha256': sha256(weather_file),
            'utc_input_errors': {'demand': derr[:100], 'weather': werr[:100],
                                 'demand_count': len(derr), 'weather_count': len(werr)},
            'required_external_gates': ['EIA930_SOURCE_AND_CLOCK_VERIFIED',
                                        'ERA5_PROXY_PROVENANCE_VERIFIED',
                                        'CHRONOLOGICAL_SPLIT_FROZEN',
                                        'NO_TEST_YEAR_MODEL_SELECTION',
                                        'BA_DEFINITION_STABILITY_VERIFIED'],
            'model_training_permitted': False, 'ba_years': years}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--demand', type=Path, required=True)
    p.add_argument('--weather', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--bas', default='CISO,AZPS,BPAT,SRP')
    p.add_argument('--start-year', type=int, default=2020)
    p.add_argument('--end-year', type=int, default=2025)
    p.add_argument('--min-fraction', type=float, default=0.98)
    a = p.parse_args()
    if a.start_year > a.end_year or not 0 < a.min_fraction <= 1:
        p.error('invalid year range or coverage fraction')
    bas = list(dict.fromkeys(x.strip().upper() for x in a.bas.split(',') if x.strip()))
    if not bas:
        p.error('empty BA cohort')
    result = audit(a.demand, a.weather, bas, a.start_year, a.end_year, a.min_fraction)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Inventory written to {a.out}; training permission remains FALSE.')

if __name__ == '__main__':
    main()
