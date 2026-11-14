import unittest
from shapely.geometry import box,mapping
from src.c2_hifld_vs_county_spatial_overlap import compare,BAS
class TestSpatialOverlap(unittest.TestCase):
    def f(self,ba,poly):
        return {"type":"Feature","properties":{"ba":ba,"geometry_approved":False,"source_approved":False},
                "geometry":mapping(poly)}
    def test_identical_masks_have_jaccard_one(self):
        feats=[self.f(ba,box(-113,33,-112,34)) for ba in BAS]
        geo={"type":"FeatureCollection","features":feats}
        res=compare(geo,geo)
        self.assertEqual(len(res),4)
        self.assertTrue(all(abs(x["spatial_jaccard_intersection_over_union"]-1)<1e-6 for x in res))
        self.assertTrue(all(not x["model_ready"] for x in res))
    def test_no_overlap_zero_jaccard(self):
        a={"features":[self.f(ba,box(-113,33,-112,34)) for ba in BAS]}
        b={"features":[self.f(ba,box(-110,33,-109,34)) for ba in BAS]}
        self.assertTrue(all(x["spatial_jaccard_intersection_over_union"]==0 for x in compare(a,b)))
if __name__=="__main__":unittest.main()
