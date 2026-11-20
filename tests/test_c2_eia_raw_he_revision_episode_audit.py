"""Synthetic-only forensic HE/UTC-start and source revision episode contracts."""
import csv,hashlib,io,json,tempfile,unittest,zipfile
from pathlib import Path
from scripts.c2_eia_raw_he_revision_episode_audit import episodes,verify_one

class RawHEVintageTests(unittest.TestCase):
    def test_contiguous_spans_and_gap(self):
        spans=episodes(["2025-07-26T08:00:00Z","2025-07-26T07:00:00Z",
                        "2025-07-26T10:00:00Z"])
        self.assertEqual([x["hours"] for x in spans],[2,1])
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            episodes(["2025-07-26T07:00:00Z"]*2)

    def fixture(self):
        root=tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        file=Path(root.name)/"source.zip"
        ba,year="AZPS",2025
        columns_raw=["ba","source_period_utc","measurement_type","reported_demand_mw","source"]
        columns_new=["ba","timestamp_utc","demand_mw","original_source_he_utc"]
        raw=[{"ba":ba,"source_period_utc":"2025-07-31T20","measurement_type":"D",
              "reported_demand_mw":"0","source":"EIA API electricity/rto/region-data"}]
        new=[{"ba":ba,"timestamp_utc":"2025-07-31T19:00:00Z",
              "demand_mw":"0","original_source_he_utc":"2025-07-31T20"}]
        def encoded(rows,keys):
            stream=io.StringIO()
            w=csv.DictWriter(stream,fieldnames=keys);w.writeheader();w.writerows(rows)
            return stream.getvalue().encode()
        r=encoded(raw,columns_raw);s=encoded(new,columns_new)
        with zipfile.ZipFile(file,"w") as z:
            for name,data in [(f"raw/eia930_{ba}_{year}_he.csv",r),
                              (f"utc_start/eia930_{ba}_{year}_start.csv",s)]:
                z.writestr(name,data)
                z.writestr(name.replace(".csv",".manifest.json"),json.dumps({
                    "sha256_csv":hashlib.sha256(data).hexdigest()}))
        changed=[{"timestamp_utc":"2025-07-31T19:00:00Z",
                  "new_api_eia930_demand_mw":"0",
                  "frozen_eia930_demand_mw":"6569",
                  "classification":"numeric_changed"}]
        return file,changed

    def test_raw_he_exactly_reproduces_new_zero(self):
        path,changed=self.fixture()
        out=verify_one(path,"AZPS",2025,changed)
        self.assertEqual(out["raw_to_shifted_mismatches"],0)
        self.assertEqual(out["nonidentical_rows_checked"],1)
        self.assertFalse(out["source_mechanism_established"])

    def test_fake_new_converted_value_rejected(self):
        path,changed=self.fixture()
        changed[0]["new_api_eia930_demand_mw"]="5"
        out=verify_one(path,"AZPS",2025,changed)
        self.assertEqual(out["raw_to_shifted_mismatches"],1)

if __name__=="__main__": unittest.main()
