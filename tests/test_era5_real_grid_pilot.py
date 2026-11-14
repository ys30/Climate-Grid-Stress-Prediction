import unittest
from src.c2_era5_real_grid_pilot import select_cells
class Tests(unittest.TestCase):
    def test_only_unapproved_grid_weights_can_be_sampled(self):
        rows=[{"ba":ba,"weight":"1","latitude":"35","longitude_0_360":"248",
            "research_status":"exploratory_unapproved_geometry"}
            for ba in ["AZPS","BPAT","CISO","SRP"]]
        cells=select_cells(rows)
        self.assertEqual(len(cells),4)
        self.assertTrue(all(x["partial_pilot_not_BA_exposure"] for x in cells))
        rows[0]["research_status"]="approved"
        with self.assertRaises(ValueError):select_cells(rows)
if __name__=="__main__":unittest.main()
