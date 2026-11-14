import unittest
from src.c2_exploratory_grid_weights import calculate
class Tests(unittest.TestCase):
    def polygon(self,ba,x,y):
        return {"type":"Feature","properties":{"ba":ba,"geometry_approved":False,
           "source_approved":False},"geometry":{"type":"Polygon","coordinates":[[
           [x,y],[x+0.35,y],[x+0.35,y+0.35],[x,y+0.35],[x,y]]]}}
    def test_weights_and_overlap_are_provisional(self):
        geo={"type":"FeatureCollection","features":[
            self.polygon("AZPS",-112.,34.),
            self.polygon("SRP",-111.8,34.),
            self.polygon("BPAT",-120.,45.),
            self.polygon("CISO",-118.,37.)]}
        w,summary,overlaps=calculate(geo)
        self.assertEqual(len(summary),4)
        self.assertTrue(all(r["research_status"]=="exploratory_unapproved_geometry" for r in w))
        self.assertTrue(any(r["intersection_km2"]>0 for r in overlaps))
        self.assertTrue(all(abs(r["weight_sum"]-1)<1e-7 for r in summary))
    def test_approved_sources_not_accidentally_accepted(self):
        ft=self.polygon("AZPS",-112.,34.)
        ft["properties"]["geometry_approved"]=True
        with self.assertRaises(ValueError):calculate({"type":"FeatureCollection","features":[
          ft,self.polygon("SRP",-111.,34.),self.polygon("BPAT",-120.,45.),
          self.polygon("CISO",-118.,37.)]})
if __name__=="__main__":unittest.main()
