import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_cec_1306a_source_detail_aggregation import aggregate


class TestCEC1306ADetail(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.details = [
            dict(source_row_id="r1", year="2023", month="7", cec_county_number="1",
                 udc_id="u1", sector="residential", customer_class="res",
                 rate_class="tier1", naics="000000", gwh="2.5"),
            dict(source_row_id="r2", year="2023", month="7", cec_county_number="1",
                 udc_id="u1", sector="residential", customer_class="res",
                 rate_class="tier2", naics="000000", gwh="3.5"),
            dict(source_row_id="r3", year="2023", month="7", cec_county_number="1",
                 udc_id="u1", sector="commercial", customer_class="com",
                 rate_class="flat", naics="541110", gwh="4.0"),
        ]
        self.counties = [dict(cec_county_number="1", county_fips="06001", reviewed="True")]

    def write(self, schema_reviewed=True):
        def dump(name, rows):
            p = self.root / name
            with p.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            return p
        detail = dump("detail.csv", self.details)
        county = dump("county.csv", self.counties)
        manifest = self.root / "proof.json"
        manifest.write_text(json.dumps({
            "research_only": True, "training_permitted": False,
            "normalized_detail_schema_reviewed": schema_reviewed,
            "files": {key: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                            "source_release": "SYNTHETIC-ONLY"}
                      for key, p in (("detail", detail), ("cec_county_crosswalk", county))}
        }))
        return detail, county, manifest

    def test_distinct_filing_dimensions_may_aggregate_with_gwh_conservation(self):
        rows, proof = aggregate(*self.write())
        self.assertEqual(len(rows), 2)
        self.assertEqual(proof["original_detail_rows"], 3)
        self.assertAlmostEqual(proof["detail_gwh"], 10)
        self.assertAlmostEqual(proof["aggregated_gwh"], 10)
        self.assertFalse(proof["model_training_permitted"])
        self.assertFalse(proof["actual_CEC_official_schema_authenticated_by_this_script"])

    def test_duplicate_source_row_id_rejected(self):
        self.details[1]["source_row_id"] = "r1"
        with self.assertRaisesRegex(ValueError, "Duplicate/blank"):
            aggregate(*self.write())

    def test_missing_consumption_not_zero(self):
        self.details[0]["gwh"] = ""
        with self.assertRaisesRegex(ValueError, "cannot be treated as zero"):
            aggregate(*self.write())

    def test_unknown_county_not_allocated(self):
        self.details[0]["cec_county_number"] = "99"
        with self.assertRaisesRegex(ValueError, "Special/unmapped"):
            aggregate(*self.write())

    def test_source_hash_tampering_rejected(self):
        detail, county, manifest = self.write()
        detail.write_text(detail.read_text() + "new bytes")
        with self.assertRaisesRegex(ValueError, "SHA"):
            aggregate(detail, county, manifest)

    def test_unreviewed_source_schema_rejected(self):
        with self.assertRaisesRegex(ValueError, "field lineage"):
            aggregate(*self.write(schema_reviewed=False))

    def test_missing_naics_category_rejected(self):
        self.details[0]["naics"] = ""
        with self.assertRaisesRegex(ValueError, "filing category"):
            aggregate(*self.write())


if __name__ == "__main__":
    unittest.main()
