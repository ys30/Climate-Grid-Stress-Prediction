#!/usr/bin/env python3
"""Audit EIA-930 six-month BALANCE source quality flags, without exclusions.

The EIA (Imputed) and (Adjusted) fields are supplemental numeric series,
not boolean labels. Empty means no such reported value.
"""
import argparse
import csv
import datetime as dt
import json
import math
from collections import Counter
from pathlib import Path

COL = {
    'ba': 'Balancing Authority',
    'period': 'UTC Time at End of Hour',
    'demand': 'Demand (MW)',
    'forecast': 'Demand Forecast (MW)',
    'imputed': 'Demand (MW) (Imputed)',
    'adjusted': 'Demand (MW) (Adjusted)',
}
FORMATS = ('%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %H:%M:%S',
           '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S')

def parse_stamp(value):
    for fmt in FORMATS:
        try:
            date = dt.datetime.strptime(value.strip(), fmt)
            if date.minute != 0 or date.second != 0:
                break
            return date
        except ValueError:
            continue
    raise ValueError('invalid UTC hourly-ending timestamp: ' + repr(value))

def parse_num(value):
    raw = (value or '').strip().replace(',', '')
    if not raw or raw.upper() in ('NA', 'N/A', '-'):
        return None
    number = float(raw)
    if not math.isfinite(number):
        raise ValueError('non-finite numeric value')
    return number

def audit(raw_csv, ba, year, month):
    period_start = dt.datetime(year, month, 1)
    period_end = dt.datetime(year + (month == 12), month % 12 + 1, 1)
    counter = Counter()
    affected_days = set()
    observed_hours = set()
    with Path(raw_csv).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        needed = {COL[k] for k in ('ba', 'period', 'demand', 'forecast')}
        missing = needed - set(reader.fieldnames or [])
        if missing:
            raise ValueError('BALANCE missing required columns: ' + repr(sorted(missing)))
        available = set(reader.fieldnames or [])
        has_imputed = COL['imputed'] in available
        has_adjusted = COL['adjusted'] in available
        for lineno, row in enumerate(reader, 2):
            if (row[COL['ba']] or '').strip() != ba:
                continue
            stamp = parse_stamp(row[COL['period']])
            if not period_start < stamp <= period_end:
                continue
            if stamp in observed_hours:
                raise ValueError(f'duplicate {ba} UTC end-hour at line {lineno}')
            observed_hours.add(stamp)
            d = parse_num(row[COL['demand']])
            forecast = parse_num(row[COL['forecast']])
            imputed = parse_num(row[COL['imputed']]) if has_imputed else None
            adjusted = parse_num(row[COL['adjusted']]) if has_adjusted else None
            counter['rows'] += 1
            flag = False
            if d is None or forecast is None:
                counter['missing_d_or_df_hours'] += 1
                flag = True
            if imputed is not None:
                counter['imputed_demand_hours'] += 1
                flag = True
            if adjusted is not None:
                counter['adjusted_reported_hours'] += 1
                if d is not None and abs(adjusted - d) > 1e-6:
                    counter['adjusted_differs_from_raw_hours'] += 1
                    flag = True
            if d is not None and forecast is not None and d > 0:
                ratio = forecast / d
                if ratio < 0.5 or ratio > 2.0:
                    counter['gross_df_d_ratio_flag_hours'] += 1
                    flag = True
            if flag:
                affected_days.add((stamp - dt.timedelta(hours=1)).date().isoformat())
    return {
        'ba': ba, 'year': year, 'month': month,
        'source_file': Path(raw_csv).name,
        'hourly_rows': counter['rows'],
        'has_imputed_column': has_imputed,
        'has_adjusted_column': has_adjusted,
        'missing_d_or_df_hours': counter['missing_d_or_df_hours'],
        'imputed_demand_hours': counter['imputed_demand_hours'],
        'adjusted_reported_hours': counter['adjusted_reported_hours'],
        'adjusted_differs_from_raw_hours': counter['adjusted_differs_from_raw_hours'],
        'gross_df_d_ratio_flag_hours': counter['gross_df_d_ratio_flag_hours'],
        'flagged_days': len(affected_days),
        'flagged_dates_utc': sorted(affected_days),
        'interpretation': 'Diagnostic only: these flags do not automatically exclude scored hours.',
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('raw_bulk_csv', type=Path)
    p.add_argument('output_json', type=Path)
    p.add_argument('--ba', default='SRP')
    p.add_argument('--year', type=int, default=2025)
    p.add_argument('--month', type=int, default=7)
    a = p.parse_args()
    result = audit(a.raw_bulk_csv, a.ba, a.year, a.month)
    a.output_json.parent.mkdir(parents=True, exist_ok=True)
    a.output_json.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
