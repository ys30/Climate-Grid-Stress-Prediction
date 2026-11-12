import unittest
class TestAreaAggregate(unittest.TestCase):
    def test_hourly_weighted_kelvin_conversion(self):
        import numpy as np,xarray as xr
        from src.c2_era5_area_aggregate import aggregate
        ba=("AZPS","BPAT","CISO","SRP")
        ds=xr.Dataset({"2m_temperature":(("time","latitude","longitude"),
                 np.array([[[300.,302.]],[[301.,303.]]]))},
               coords={"time":np.array(["2023-07-01T00:00:00","2023-07-01T01:00:00"],dtype="datetime64[ns]"),
                       "latitude":[35.],"longitude":[248.,248.25]})
        ds["2m_temperature"].attrs["units"]="K"
        w={b:[(35.,248.,.5),(35.,248.25,.5)] for b in ba}
        rows,qa=aggregate(ds,w)
        self.assertEqual(len(rows),8)
        self.assertEqual(len(qa),0)
        self.assertAlmostEqual(rows[0]["temperature_2m_c"],27.85,places=5)
    def test_partial_cells_do_not_get_silently_renormalized(self):
        import numpy as np,xarray as xr
        from src.c2_era5_area_aggregate import aggregate
        ds=xr.Dataset({"2m_temperature":(("time","latitude","longitude"),
                  np.array([[[300.,float("nan")]]]))},
               coords={"time":np.array(["2023-07-01T00:00:00"],dtype="datetime64[ns]"),
                       "latitude":[35.],"longitude":[248.,248.25]})
        ds["2m_temperature"].attrs["units"]="K"
        rows,qa=aggregate(ds,{b:[(35.,248.,.5),(35.,248.25,.5)]
                            for b in ("AZPS","BPAT","CISO","SRP")})
        self.assertEqual(rows,[])
        self.assertEqual(len(qa),4)
if __name__=="__main__":unittest.main()
