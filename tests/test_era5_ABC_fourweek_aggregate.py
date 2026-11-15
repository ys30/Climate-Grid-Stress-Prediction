import unittest
from src.c2_era5_ABC_fourweek_aggregate import audit
class TestSourceAudit(unittest.TestCase):
    def test_missing_four_week_source_fails_closed(self):
        with self.assertRaises(ValueError):audit([])
if __name__=="__main__":unittest.main()
