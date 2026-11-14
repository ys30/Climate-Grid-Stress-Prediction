import unittest
import numpy as np
import xarray as xr
from src.c2_era5_full_grid_one_hour import compute_from_loaded_grid,load_exploratory_weights
class TestFullGrid(unittest.TestCase):
    def test_full_weight_sum_and_actual_grid_extraction(self):
        arr=np.array([[299.,301.],[302.,304.]])
        grid=xr.DataArray(arr,coords={"latitude":[35.,35.25],"longitude":[248.,248.25]},
                          dims=("latitude","longitude"),attrs={"units":"K"})
        groups={ba:[(35.,248.,.25),(35.,248.25,.75)] for ba in ("AZPS","BPAT","CISO","SRP")}
        res=compute_from_loaded_grid(grid,groups)
        self.assertEqual(len(res),4)
        self.assertAlmostEqual(res[0]["weighted_temperature_celsius"],27.35,places=5)
        self.assertFalse(res[0]["historical_weather_exposure_approved"])
    def test_missing_grid_raises(self):
        grid=xr.DataArray([[float("nan")]],coords={"latitude":[35.],"longitude":[248.]},
                         dims=("latitude","longitude"),attrs={"units":"K"})
        with self.assertRaises(ValueError):
            compute_from_loaded_grid(grid,{"AZPS":[(35.,248.,1.)]})
if __name__=="__main__":unittest.main()
