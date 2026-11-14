import unittest
from datetime import datetime,timedelta
import numpy as np
import xarray as xr
from src.c2_era5_24h_exploratory import calculate_24
class Test24(unittest.TestCase):
    def test_24_complete_hourly_samples(self):
        timestamps=np.array([np.datetime64("2023-07-01T00:00:00")+np.timedelta64(i,"h") for i in range(24)])
        ds=xr.Dataset({"2m_temperature":(("time","latitude","longitude"),
                np.full((24,1,1),300.))},
             coords={"time":timestamps,"latitude":[35.],"longitude":[248.]})
        ds["2m_temperature"].attrs["units"]="K"
        groups={ba:[(35.,248.,1.)] for ba in ("AZPS","BPAT","CISO","SRP")}
        rows,meta=calculate_24(ds,groups,"2023-07-01T00:00:00Z")
        self.assertEqual(len(rows),96)
        self.assertEqual(meta["hours"],24)
        self.assertFalse(meta["historical_geography_admitted"])
    def test_noncontiguous_time_refused(self):
        timestamps=np.array([np.datetime64("2023-07-01T00:00:00")+np.timedelta64(i,"h") for i in range(25) if i!=12])
        ds=xr.Dataset({"2m_temperature":(("time","latitude","longitude"),
                np.full((24,1,1),300.))},
             coords={"time":timestamps,"latitude":[35.],"longitude":[248.]})
        ds["2m_temperature"].attrs["units"]="K"
        groups={ba:[(35.,248.,1.)] for ba in ("AZPS","BPAT","CISO","SRP")}
        with self.assertRaises(ValueError):
            calculate_24(ds,groups,"2023-07-01T00:00:00Z")
if __name__=="__main__":unittest.main()
