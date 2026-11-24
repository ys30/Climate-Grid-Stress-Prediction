import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_cec_joint_geo_source_gate import inspect


class CECJointGeoGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tables = {
            "membership_1305": [
                {"year": "2023", "month": "7", "ba": "CISO", "udc_id": "u1"},
                {"year": "2023", "month": "7", "ba": "AZPS", "udc_id": "u2"},
                {"year": "2023", "month": "7", "ba": "SRP", "udc_id": "u2"},
            ],
            "county_consumption_1306A": [
                {"year": "2023", "month": "7", "county_fips": "06001", "udc_id": "u1",
                 "sector": "residential", "gwh": "10"},
                {"year": "2023", "month": "7", "county_fips": "04013", "udc_id": "u2",
                 "sector": "residential", "gwh": "20"},
                {"year": "2023", "month": "7", "county_fips": "06013", "udc_id": "u3",
                 "sector": "commercial", "gwh": "5"},
            ],
            "udc_eia_crosswalk": [
                {"udc_id": "u1", "eia_utility_id": "100", "reviewed": "True"},
                {"udc_id": "u2", "eia_utility_id": "200", "reviewed": "True"},
                {"udc_id": "u3", "eia_utility_id": "300", "reviewed": "False"},
            ],
        }

    def write(self, bad_manifest=False):
        paths = {}
        config = {"research_only": True, "training_permitted": False, "files": {}}
        for key, rows in self.tables.items():
            path = self.root / (key + ".csv")
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            paths[key] = path
            config["files"][key] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_release": "SYNTHETIC-TEST-ONLY",
                "source_kind": "official_original" if key != "udc_eia_crosswalk" else "reviewed_crosswalk"
            }
        if bad_manifest:
            config["files"]["membership_1305"]["sha256"] = "0" * 64
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps(config))
        return [paths[k] for k in ("membership_1305", "county_consumption_1306A",
                                  "udc_eia_crosswalk")] + [manifest]

    def test_conditional_join_never_approves_model(self):
        result = inspect(*self.write())
        self.assertEqual(result["consumption_rows_by_source_association_status"], {
            "conditional_unique_source_association": 1,
            "membership_unavailable": 1,
            "udc_multi_BA_nonexclusive": 1,
        })
        self.assertEqual(result["candidate_consumption_gwh"], 10)
        self.assertFalse(result["historical_BA_footprint_approved"])
        self.assertFalse(result["load_weighted_exposure_approved"])
        self.assertFalse(result["model_training_permitted"])

    def test_changed_source_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            inspect(*self.write(bad_manifest=True))

    def test_missing_gwh_cannot_be_zero_imputed(self):
        self.tables["county_consumption_1306A"][0]["gwh"] = ""
        with self.assertRaisesRegex(ValueError, "never treat missing as zero"):
            inspect(*self.write())

    def test_invalid_fips_rejected(self):
        self.tables["county_consumption_1306A"][0]["county_fips"] = "0601"
        with self.assertRaisesRegex(ValueError, "county FIPS"):
            inspect(*self.write())

    def test_duplicate_membership_rejected(self):
        self.tables["membership_1305"].append(self.tables["membership_1305"][0].copy())
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            inspect(*self.write())

    def test_no_actual_public_data_fabrication(self):
        self.assertFalse(inspect(*self.write())["cec_public_joint_release_verified_by_this_script"])


if __name__ == "__main__":
    unittest.main()
