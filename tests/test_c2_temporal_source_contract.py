"""Contract tests for EIA-930 chronological gate: examples are synthetic, not observations."""
import unittest
from src.c2_temporal_gate import BAS, SPLITS, evaluate, _expected_hours

def annual_rows():
    rows=[]
    for years in SPLITS.values():
        for year in years:
            hours=_expected_hours(year)
            for ba in BAS:
                rows.append({"year":str(year),"ba":ba,"expected_hours":str(hours),
                             "observed_keys":str(hours),"valid_values":str(hours),
                             "blank_or_invalid":"0","missing_hour_keys":"0",
                             "duplicate_keys":"0","valid_coverage_ratio":"1.0"})
    return rows

class TestTemporalSourceContract(unittest.TestCase):
    def test_complete_synthetic_counts_still_do_not_authorize_model(self):
        result=evaluate(annual_rows())
        self.assertTrue(result["coverage_only_source_gate_passed"])
        self.assertFalse(result["empirical_model_training_permitted"])
        self.assertTrue(result["time_holdout_locked"])

    def test_duplicate_annual_key_fails(self):
        rows=annual_rows()
        with self.assertRaisesRegex(ValueError,"Duplicate BA/year"):
            evaluate(rows+[dict(rows[0])])

    def test_leap_year_and_count_consistency(self):
        rows=annual_rows()
        self.assertEqual(_expected_hours(2024),8784)
        bad=[dict(r) for r in rows]
        x=next(r for r in bad if r["year"]=="2024")
        x["expected_hours"]="8760"
        with self.assertRaisesRegex(ValueError,"leap-year"):
            evaluate(bad)

        bad=[dict(r) for r in rows]
        bad[0]["valid_values"]=str(int(bad[0]["valid_values"])-1)
        with self.assertRaisesRegex(ValueError,"arithmetic"):
            evaluate(bad)

    def test_nonfinite_ratio_and_corrupt_missing_fail(self):
        rows=annual_rows()
        bad=[dict(r) for r in rows]
        bad[0]["valid_coverage_ratio"]="nan"
        with self.assertRaisesRegex(ValueError,"ratio"):
            evaluate(bad)
        bad=[dict(r) for r in rows]
        bad[0]["missing_hour_keys"]="1"
        with self.assertRaisesRegex(ValueError,"arithmetic"):
            evaluate(bad)

    def test_noncomplete_year_does_not_open_model_gate(self):
        rows=annual_rows()
        rows=[r for r in rows if not (r["year"]=="2025" and r["ba"]=="SRP")]
        result=evaluate(rows)
        self.assertFalse(result["test"]["admitted"])
        self.assertFalse(result["coverage_only_source_gate_passed"])
        self.assertFalse(result["empirical_model_training_permitted"])

if __name__=="__main__":
    unittest.main()
