import unittest
from src.c2_era5_AB_fourmonth_aggregate import reconcile
class Tests(unittest.TestCase):
    def test_requires_immutable_independent_four_source_months(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            reconcile([])
if __name__=="__main__":unittest.main()
