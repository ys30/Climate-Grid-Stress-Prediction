import unittest
from src.c2_era5_public_probe import normalize_lon
class Tests(unittest.TestCase):
    def test_western_longitude(self):
        self.assertEqual(normalize_lon(-112),248)
        self.assertEqual(normalize_lon(248),248)
    def test_bad_longitudes(self):
        with self.assertRaises(ValueError):normalize_lon(-999)
if __name__=="__main__":unittest.main()
