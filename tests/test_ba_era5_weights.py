import unittest,hashlib,json
from src.c2_ba_era5_weights import cell_centers,validate_meta,build_weights
class Tests(unittest.TestCase):
    def test_grid_alignment(self):
        self.assertEqual(cell_centers(-110.1,-109.6),[-110.,-109.75])
    def test_provenance_rejected_on_hash_mismatch(self):
        with self.assertRaises(ValueError):
            validate_meta({"source_url":"test","source_vintage":"2025",
                "license":"open","geometry_sha256":"wrong","code_crosswalk_reviewed":True},b"geometry")
    def test_synthetic_polygons_only_as_unit_fixture(self):
        geo={"type":"FeatureCollection","features":[]}
        for i,ba in enumerate(("AZPS","BPAT","CISO","SRP")):
            lon=-119+i*2
            geo["features"].append({"type":"Feature","properties":{"ba":ba},
                "geometry":{"type":"Polygon","coordinates":[[[lon,35],[lon+.4,35],
                         [lon+.4,35.4],[lon,35.4],[lon,35]]]}})
        rows,summary=build_weights(geo,{})
        self.assertEqual(len(summary),4)
        self.assertTrue(all(abs(s["weight_sum"]-1)<1e-9 for s in summary))
        self.assertTrue(all(r["intersection_area_m2"]>0 for r in rows))
if __name__=="__main__":unittest.main()
