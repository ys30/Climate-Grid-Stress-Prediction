"""Never infer county-by-agency CEC sales from marginal XLSX source sheets."""
import hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
from scripts.c2_cec_verified_marginal_only_admission import (
    MEMBER,verify,PINNED_COUNTY_XLSX_SHA256,PINNED_AGENCY_XLSX_SHA256,
    COUNTY_FIELDS,AGENCY_FIELDS
)

class RealCECMarginsTest(unittest.TestCase):
    def make(self,agency_header=None):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder=Path(temp.name)
        def tab(headers,ref):
            return {"sheet_dimension_claim":ref,
                "preview_first_12_rows_first_30_cells":[{"row":1,
                    "cells":[{"cell":f"A{i}","value":name} for i,name in enumerate(headers)]}]}
        data={"county_annual":{"actual_download_sha256":PINNED_COUNTY_XLSX_SHA256,
                "sheets":[tab(COUNTY_FIELDS,"A1:F14169")]},
              "utility_annual":{"actual_download_sha256":PINNED_AGENCY_XLSX_SHA256,
                "sheets":[tab(agency_header or AGENCY_FIELDS,"A1:G11460")]},
              "file_level_joint_county_utility_allocation_established":False,
              "model_training_permitted":False}
        payload=json.dumps(data).encode()
        archive=folder/"evidence.zip"
        with zipfile.ZipFile(archive,"w") as z:z.writestr(MEMBER,payload)
        return archive,hashlib.sha256(payload).hexdigest()

    def test_verified_two_margins_still_cannot_admit_spatial_model(self):
        p,h=self.make()
        d=verify(p,expected_schema_sha=h)
        self.assertFalse(d["joint_county_agency_columns_present_in_either_file"])
        self.assertFalse(d["original_filing_joint_data_publicly_obtained"])
        self.assertFalse(d["model_training_permitted"])

    def test_modified_source_schema_fails_closed(self):
        p,h=self.make(agency_header=AGENCY_FIELDS+["COUNTY"])
        with self.assertRaisesRegex(ValueError,"columns differ"):
            verify(p,expected_schema_sha=h)

    def test_hash_mismatch_fails(self):
        p,_=self.make()
        with self.assertRaisesRegex(ValueError,"SHA"):
            verify(p,expected_schema_sha="0"*64)

if __name__=="__main__":unittest.main()
