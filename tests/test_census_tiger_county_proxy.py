import unittest,tempfile,csv,os
from pathlib import Path
from shapely.geometry import box
from src.c2_census_tiger_county_proxy import source_memberships,build_county_features,BAS
class TestCensusCountyProxy(unittest.TestCase):
    def test_four_BA_union_and_nonexclusive_overlap(self):
        geom={"04013":box(-113,32,-112,33),"04015":box(-112,32,-111,33),
              "53001":box(-120,45,-119,46),"06001":box(-119,34,-118,35)}
        membership={"AZPS":{"04013","04015"},"SRP":{"04013"},
                    "BPAT":{"53001"},"CISO":{"06001"}}
        features,summary=build_county_features(membership,geom)
        self.assertEqual(len(features["features"]),4)
        self.assertEqual(sum(x["counties"] for x in summary),5)
        self.assertTrue(all(x["properties"]["geometry_approved"] is False for x in features["features"]))
    def test_vintage_and_model_flags_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"source.csv"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=["year","eia930_BA_code","county_id_fips","model_ready"])
                w.writeheader()
                for ba in BAS:
                    w.writerow({"year":2024,"eia930_BA_code":ba,
                       "county_id_fips":"04013","model_ready":"False"})
            self.assertEqual(len(source_memberships(p)),4)
            txt=p.read_text().replace("False","True")
            p.write_text(txt)
            with self.assertRaises(ValueError):source_memberships(p)
if __name__=="__main__":unittest.main()
