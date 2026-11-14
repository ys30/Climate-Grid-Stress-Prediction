import unittest
from src.c2_topology_sensitivity import assess
class Tests(unittest.TestCase):
    def test_make_valid_not_approved(self):
        src={"type":"FeatureCollection","features":[]}
        for i,ba in enumerate(("AZPS","BPAT","CISO","SRP")):
            x=-118+i*2
            src["features"].append({"type":"Feature","properties":{"ba":ba},
                "geometry":{"type":"Polygon","coordinates":[[[x,35],[x+.4,35.4],
                    [x+.4,35],[x,35.4],[x,35]]]}})
        summary,derived=assess(src)
        self.assertEqual(len(summary),4)
        self.assertTrue(all(not row["geom_repair_approved"] for row in summary))
        self.assertTrue(all(not f["properties"]["geometry_approved"] for f in derived["features"]))
if __name__=="__main__":unittest.main()
