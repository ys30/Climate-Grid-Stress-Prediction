import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_bulk_quality_flags import COL, audit

class TestBulkQualityFlags(unittest.TestCase):
    FIELDS = list(COL.values())
    def write(self, folder, items):
        path = Path(folder) / 'bulk.csv'
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader();writer.writerows(items)
        return path
    def row(self, stamp='07/01/2025 01:00:00 AM', d='1,000',
            df='950', imputed='', adjusted=''):
        return dict(zip(self.FIELDS, ('SRP', stamp, d, df, imputed, adjusted)))
    def test_no_flags_clean(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row()]), 'SRP', 2025, 7)
            self.assertEqual(result['hourly_rows'], 1)
            self.assertEqual(result['flagged_days'], 0)
    def test_imputed_and_adjusted_are_numeric_side_series(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row(imputed='1,000', adjusted='980')]), 'SRP', 2025, 7)
            self.assertEqual(result['imputed_demand_hours'], 1)
            self.assertEqual(result['adjusted_differs_from_raw_hours'], 1)
            self.assertEqual(result['flagged_days'], 1)
    def test_adj_equal_not_change(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row(adjusted='1,000')]), 'SRP', 2025, 7)
            self.assertEqual(result['adjusted_reported_hours'], 1)
            self.assertEqual(result['adjusted_differs_from_raw_hours'], 0)
            self.assertEqual(result['flagged_days'], 0)
    def test_missing_forecast_not_zero_filled(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row(df='')]), 'SRP', 2025, 7)
            self.assertEqual(result['missing_d_or_df_hours'], 1)
            self.assertEqual(result['flagged_days'], 1)
    def test_gross_ratio_flag_only(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row(df='2500')]), 'SRP', 2025, 7)
            self.assertEqual(result['gross_df_d_ratio_flag_hours'], 1)
    def test_next_month_midnight_assigned_to_july(self):
        with tempfile.TemporaryDirectory() as folder:
            result = audit(self.write(folder, [self.row('08/01/2025 12:00:00 AM', imputed='1100')]), 'SRP', 2025, 7)
            self.assertEqual(result['flagged_dates_utc'], ['2025-07-31'])
    def test_duplicate_source_hour_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                audit(self.write(folder, [self.row(), self.row()]), 'SRP', 2025, 7)

if __name__ == '__main__':
    unittest.main()
