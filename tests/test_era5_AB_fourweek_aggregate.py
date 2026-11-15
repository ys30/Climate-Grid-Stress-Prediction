import unittest
from src.c2_era5_AB_fourweek_aggregate import reconcile
class TestFourWeek(unittest.TestCase):
    def test_missing_original_weeks_fails_closed(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            reconcile([])
if __name__=="__main__":unittest.main()
