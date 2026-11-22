import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from c2_ba_hourly_join_audit import audit, parse_utc_hour

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, field, rows):
        p = self.root / name
        with p.open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['ba', 'utc_start', field])
            w.writerows(rows)
        return p

    def test_utc_only(self):
        for x in ['2020-01-01T00:00:00', '2020-01-01T00:00:00-07:00', '2020-01-01T00:30:00Z']:
            with self.assertRaises(ValueError):
                parse_utc_hour(x)
        self.assertEqual(parse_utc_hour('2020-01-01T00:00:00Z').hour, 0)

    def test_missing_is_not_zero_and_leap_year(self):
        d = self.write('d.csv', 'demand_mw', [['CISO','2020-01-01T00:00:00Z','0']])
        w = self.write('w.csv', 'weather_value', [['CISO','2020-01-01T00:00:00Z','']])
        res = audit(d, w, ['CISO'], 2020, 2020)
        self.assertEqual(res['ba_years'][0]['expected_hours'], 8784)
        self.assertEqual(res['ba_years'][0]['demand_valid_hours'], 1)
        self.assertEqual(res['ba_years'][0]['paired_valid_hours'], 0)
        self.assertFalse(res['model_training_permitted'])

    def test_duplicate_is_invalid(self):
        rows = [['SRP','2021-03-14T10:00:00Z','1']]
        d = self.write('d.csv','demand_mw',rows + rows)
        w = self.write('w.csv','weather_value',rows)
        res = audit(d,w,['SRP'],2021,2021)
        self.assertEqual(res['ba_years'][0]['duplicate_rows'],1)
        self.assertEqual(res['ba_years'][0]['paired_valid_hours'],0)

if __name__ == '__main__':
    unittest.main()
