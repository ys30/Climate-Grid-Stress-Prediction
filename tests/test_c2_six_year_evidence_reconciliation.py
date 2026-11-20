"""Contract tests for two independent evidence denominators in C-2."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_six_year_evidence_reconciliation import summarize


class SixYearReconciliationTests(unittest.TestCase):
    def test_real_frozen_reports_reconcile_without_training_admission(self):
        files={wave:Path(f"docs/E2_{wave.upper()}_VERIFIED_STATUS.json")
               for wave in ("wave1","wave2","wave3")}
        result=summarize(files,frozen_report_path=Path(
            "reports/E1_FULL_2020_2025_REAL_ERA5_EIA930_SOURCE_DATA_FROZEN_QA.md"))
        frozen=result["frozen_source_scope"]
        source=result["newer_EIA_strict_source_gate"]
        self.assertEqual(frozen["era5_eia930_BA_hour_records"],210432)
        self.assertEqual(frozen["nonmissing_original_demand"]+frozen["missing_original_demand"],210432)
        self.assertEqual(frozen["source_BA_year_groups_present"],24)
        self.assertEqual(source["passed_BA_year_groups"],23)
        self.assertEqual(source["failed_BA_year_groups"],[{"ba":"AZPS","year":2023}])
        self.assertFalse(result["scientific_admission"]["model_training_permitted"])
        self.assertTrue(source["distinct_from_source_group_presence"])

    def test_cannot_count_noncanonical_azps_as_strict_QA_pass(self):
        sources={wave:Path(f"docs/E2_{wave.upper()}_VERIFIED_STATUS.json")
                 for wave in ("wave1","wave2","wave3")}
        with tempfile.TemporaryDirectory() as root:
            changed={}
            for name,path in sources.items():
                d=json.loads(path.read_text())
                if name=="wave3":
                    for entry in d["cohorts"]:
                        if entry["ba"]=="AZPS" and entry["year"]==2023:
                            entry["gate_pass"]=True
                            entry["status"]="artifact_hash_and_annual_gate_pass"
                p=Path(root)/(name+".json")
                p.write_text(json.dumps(d))
                changed[name]=p
            with self.assertRaisesRegex(ValueError,"Canonical QA outcome changed"):
                summarize(changed,frozen_report_path=Path(
                    "reports/E1_FULL_2020_2025_REAL_ERA5_EIA930_SOURCE_DATA_FROZEN_QA.md"))


if __name__=="__main__":
    unittest.main()
