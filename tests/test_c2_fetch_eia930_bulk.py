import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_fetch_eia930_bulk import csv_to_month
from scripts.c2_verify_eia930_source import verify
from scripts.c2_eia930_day_ahead_benchmark import read_pairs

class TestEiaBulkAdapter(unittest.TestCase):
    HEADERS=['Balancing Authority','UTC Time at End of Hour','Demand (MW)','Demand Forecast (MW)']
    def fixture(self,root,change=None):
        data=[
          dict(zip(self.HEADERS,['SRP','07/01/2025 01:00:00 AM','1,100','1,050'])),
          dict(zip(self.HEADERS,['SRP','07/01/2025 02:00:00 AM','1101','1051'])),
          dict(zip(self.HEADERS,['SRP','08/01/2025 12:00:00 AM','1200','1150'])),
          dict(zip(self.HEADERS,['SRP','08/01/2025 01:00:00 AM','1201','1151'])),
          dict(zip(self.HEADERS,['AZPS','07/01/2025 01:00:00 AM','2100','2050'])),
        ]
        if change: change(data)
        path=Path(root)/'bulk.csv'
        with path.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=self.HEADERS)
            writer.writeheader();writer.writerows(data)
        return path
    def test_month_end_and_source_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'normalized'
            meta=csv_to_month(self.fixture(td),out)
            self.assertEqual(meta['origin'],'bulk')
            self.assertEqual(meta['row_count'],6)
            self.assertEqual(len(meta['original_bulk_sha256']),64)
            self.assertTrue(verify(out/'eia930_D_DF_hourly.csv',out/'source_manifest.json')['passed'])
    def test_no_hallucinated_day(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'normalized'
            csv_to_month(self.fixture(td),out)
            days,excluded,_=read_pairs(out/'eia930_D_DF_hourly.csv',{'SRP'})
            self.assertEqual(days,[])
            self.assertEqual(len(excluded),2)
    def test_original_bulk_tampering_fails_verifier(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'normalized'
            csv_to_month(self.fixture(td),out)
            original=out/'EIA930_BALANCE_original.csv'
            original.write_text(original.read_text().replace('1,100','9,999'))
            result=verify(out/'eia930_D_DF_hourly.csv',out/'source_manifest.json')
            self.assertFalse(result['passed'])
            self.assertTrue(any('original bulk source SHA-256 mismatch' in issue for issue in result['issues']))
    def test_duplicate_source_hour_fails(self):
        with tempfile.TemporaryDirectory() as td:
            def duplicate(rows):rows.append(dict(rows[0]))
            with self.assertRaisesRegex(ValueError,'duplicate'):
                csv_to_month(self.fixture(td,duplicate),Path(td)/'out')
    def test_unsupported_header_fails(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'bad.csv'
            file.write_text('invalid,columns\n1,2\n')
            with self.assertRaisesRegex(ValueError,'Unsupported BALANCE schema'):
                csv_to_month(file,Path(td)/'out')
    def test_iso_utc_source_format_is_supported(self):
        with tempfile.TemporaryDirectory() as td:
            def convert(rows):
                rows[0]['UTC Time at End of Hour']='2025-07-01 01:00:00'
                rows[1]['UTC Time at End of Hour']='2025-07-01T02:00:00'
            out=Path(td)/'normalized'
            csv_to_month(self.fixture(td,convert),out)
            report=verify(out/'eia930_D_DF_hourly.csv',out/'source_manifest.json')
            self.assertTrue(report['passed'],report['issues'])
    def test_subhourly_utc_timestamp_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            def change(rows):
                rows[0]['UTC Time at End of Hour']='07/01/2025 01:15:00 AM'
            with self.assertRaisesRegex(ValueError,'non-hourly'):
                csv_to_month(self.fixture(td,change),Path(td)/'normalized')
    def test_existing_output_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            file=self.fixture(td)
            out=Path(td)/'out'
            csv_to_month(file,out)
            with self.assertRaisesRegex(ValueError,'already exists'):
                csv_to_month(file,out)
if __name__=='__main__':
    unittest.main()
