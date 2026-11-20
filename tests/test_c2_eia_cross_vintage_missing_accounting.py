"""Cross-vintage audit contracts: never treat noncomparable missing totals as fixes."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_eia_cross_vintage_missing_accounting import compare


class MissingByVintageTests(unittest.TestCase):
    def paths(self):
        return {key:Path("docs")/f"E2_{key.upper()}_VERIFIED_STATUS.json"
                for key in ("wave1","wave2","wave3")}

    def test_two_different_source_vintages_must_not_be_conflated(self):
        d=compare(self.paths(),Path("docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json"))
        self.assertEqual(d["frozen_six_year_archive"]["missing_hours"],260)
        new=d["newer_independent_year_gates"]
        self.assertEqual(new["BA_years_pass"],23)
        self.assertEqual(new["missing_in_23_passing_BA_years"],210)
        self.assertEqual(new["per_ba_missing_in_passing_years"],
                         {"AZPS":25,"BPAT":49,"CISO":13,"SRP":123})
        self.assertEqual(new["AZPS_2023_invalid_demand_hours"],2)
        self.assertFalse(d["comparability"]["same_BA_year_sample"])
        self.assertFalse(d["comparability"]["per_hour_disagreements_verified"])
        self.assertFalse(d["comparability"]["source_model_training_permitted"])

    def test_azps2023_negative_rows_must_not_be_mislabeled_missing(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path("docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json")
            doc=json.loads(source.read_text())
            doc["missing_demand_rows"]=2
            path=Path(root)/"fake.json"
            path.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,"AZPS2023"):
                compare(self.paths(),path)

    def test_annual_duplicate_records_fail(self):
        with tempfile.TemporaryDirectory() as root:
            files={}
            for name,path in self.paths().items():
                data=json.loads(path.read_text())
                if name=="wave3":
                    data["cohorts"].append(dict(data["cohorts"][0]))
                output=Path(root)/f"{name}.json"
                output.write_text(json.dumps(data))
                files[name]=output
            with self.assertRaisesRegex(ValueError,"duplicate"):
                compare(files,Path("docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json"))


if __name__=="__main__":
    unittest.main()
