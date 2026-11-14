import unittest
from src.c2_era5_calendar_month_source import month_days
class Tests(unittest.TestCase):
    def test_feb_leap_and_nonleap(self):
        self.assertEqual(month_days(2020,2),29)
        self.assertEqual(month_days(2024,2),29)
        self.assertEqual(month_days(2025,2),28)
    def test_other_month_lengths(self):
        self.assertEqual(month_days(2023,4),30)
        self.assertEqual(month_days(2023,10),31)
    def test_invalid_dates_blocked(self):
        with self.assertRaises(ValueError):month_days(2027,2)
        with self.assertRaises(ValueError):month_days(2024,13)
if __name__=="__main__":unittest.main()
