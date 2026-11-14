import hashlib
import unittest
from src.c2_ba_era5_weights import validate_meta

class GeographyAdmissionTests(unittest.TestCase):
    def setUp(self):
        raw=b'{"type":"FeatureCollection","features":[]}'
        self.raw=raw
        self.meta={
            "source_url":"https://example.org/geometry",
            "source_vintage":"2018",
            "license":"research",
            "geometry_sha256":hashlib.sha256(raw).hexdigest(),
            "code_crosswalk_reviewed":True,
        }
    def test_no_auto_admit_without_four_independent_reviews(self):
        with self.assertRaisesRegex(ValueError,"historical_vintage_reviewed"):
            validate_meta(self.meta,self.raw)
    def test_flags_without_documented_evidence_are_not_enough(self):
        for k in ("historical_vintage_reviewed","spatial_overlap_reviewed",
                  "topology_repair_reviewed","exposure_interpretation_reviewed"):
            self.meta[k]=True
        with self.assertRaisesRegex(ValueError,"historical_vintage_review_reference"):
            validate_meta(self.meta,self.raw)
    def test_documented_all_gates_accepted_by_metadata_layer(self):
        for k in ("historical_vintage","spatial_overlap",
                  "topology_repair","exposure_interpretation"):
            self.meta[k+"_reviewed"]=True
            self.meta[k+"_review_reference"]="scientific review reference "+k
        validate_meta(self.meta,self.raw)
if __name__=="__main__":
    unittest.main()
