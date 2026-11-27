import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_coverage_scorecard import build_summary

class TestEia930Coverage(unittest.TestCase):
    def write(self,path,rows,fields):
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    def setup_files(self,td,good,bad):
        daily=Path(td)/'daily.csv';excluded=Path(td)/'excluded.csv'
        self.write(daily,good,['ba','date_utc','signed_peak_error_mw'])
        self.write(excluded,bad,['ba','date_utc'])
        return daily,excluded
    def test_missing_whole_day_distinct_from_incomplete(self):
        with tempfile.TemporaryDirectory() as td:
            files=self.setup_files(td,[dict(ba='SRP',date_utc='2024-01-01',signed_peak_error_mw='-10')],
                [dict(ba='SRP',date_utc='2024-01-02')])
            row=build_summary(*files,['SRP'],2024,2024)[0]
            self.assertEqual(row['calendar_days'],366)
            self.assertEqual(row['complete_days'],1)
            self.assertEqual(row['incomplete_days'],1)
            self.assertEqual(row['wholly_missing_days'],364)
            self.assertAlmostEqual(row['peak_mae_mw'],10)
            self.assertEqual(row['underforecast_fraction'],1)
    def test_missing_all_days_not_full(self):
        with tempfile.TemporaryDirectory() as td:
            row=build_summary(*self.setup_files(td,[],[]),['SRP'],2025,2025)[0]
            self.assertEqual(row['wholly_missing_days'],365)
            self.assertIsNone(row['peak_mae_mw'])
            self.assertEqual(row['status'],'PARTIAL')
    def test_duplicate_date_fails(self):
        with tempfile.TemporaryDirectory() as td:
            a=dict(ba='SRP',date_utc='2025-01-01',signed_peak_error_mw='-5')
            files=self.setup_files(td,[a,a],[])
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                build_summary(*files,['SRP'],2025,2025)
    def test_good_and_bad_same_day_fails(self):
        with tempfile.TemporaryDirectory() as td:
            files=self.setup_files(td,[dict(ba='SRP',date_utc='2025-01-01',signed_peak_error_mw='0')],
                [dict(ba='SRP',date_utc='2025-01-01')])
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                build_summary(*files,['SRP'],2025,2025)

if __name__=='__main__':
    unittest.main()
