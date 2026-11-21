"""SCE duplicate-row source guards; all fixtures are synthetic."""
import unittest
from scripts.c2_sce_2020q1_exact_duplicate_raw_row_probe import normalize_zip,normalize_numeric

class ExactSCEDuplicateGuards(unittest.TestCase):
    def test_zip_number_keeps_leading_zero(self):
        self.assertEqual(normalize_zip(1234),"01234")
        self.assertEqual(normalize_zip("09001"),"09001")
    def test_bad_zip_fails(self):
        for x in ("notZIP",123456,True):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):normalize_zip(x)
    def test_blank_not_true_zero(self):
        self.assertIsNone(normalize_numeric(None))
        self.assertIsNone(normalize_numeric(""))
        self.assertEqual(normalize_numeric(0),0)
    def test_numeric_source_values_remain_numeric(self):
        self.assertEqual(normalize_numeric("1,500"),1500.0)
        self.assertEqual(normalize_numeric(273),273)

if __name__=="__main__":unittest.main()
