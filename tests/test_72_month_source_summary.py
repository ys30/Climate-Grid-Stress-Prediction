import unittest,calendar
from src.c2_72_month_source_summary import reconcile,SOURCE_WEIGHTS_SHA
class Tests(unittest.TestCase):
    def all_months(self):
        items=[]
        for y in range(2020,2026):
            for m in range(1,13):
                days=calendar.monthrange(y,m)[1]
                slots=days*24*4
                items.append({"utc_start":f"{y}-{m:02d}-01T00:00:00+00:00",
                 "days":days,"hours_per_BA":days*24,
                 "source_BA_hour_slots":slots,"weather_source_rows":slots,
                 "all_weather_hours_present":True,
                 "BAs":["AZPS","BPAT","CISO","SRP"],
                 "weights_sha256":SOURCE_WEIGHTS_SHA,
                 "source_missing_demand_hours":0,"paired_source_rows":slots,
                 "missing_demand_BA_hours":[],
                 "no_imputation":True,"historical_geometry_approved":False,
                 "training_or_validation_permitted":False,
                 "eia_candidate_anomaly_flags_in_window":0})
        return items
    def test_leap_years_and_full_six_calendar_years(self):
        months,gaps,qa=reconcile(self.all_months())
        self.assertEqual(len(months),72)
        self.assertEqual(qa["total_real_ERA5_BA_hours"],
          4*24*(366+365+365+365+366+365))
        self.assertEqual(len(qa["yearly_source_quality"]),6)
        self.assertTrue(all(not x["training_permitted"] for x in qa["yearly_source_quality"]))
        self.assertEqual(sum(x["observed_weather_BA_hours"] for x in qa["yearly_source_quality"]),qa["total_real_ERA5_BA_hours"])
        self.assertFalse(qa["training_permitted"])
        self.assertFalse(qa["BA_geography_historical_approval"])
    def test_missing_month_never_passes(self):
        with self.assertRaisesRegex(ValueError,"Expected 72"):
            reconcile(self.all_months()[:-1])
    def test_demand_gap_accounted_without_imputation(self):
        items=self.all_months()
        items[0]["source_missing_demand_hours"]=1
        items[0]["paired_source_rows"]-=1
        items[0]["missing_demand_BA_hours"]=[{"ba":"SRP","utc":"2020-01-05T00:00:00+00:00"}]
        rows,gaps,report=reconcile(items)
        self.assertEqual(len(gaps),1)
        self.assertEqual(report["total_missing_original_demand_BA_hours"],1)
    def test_falsely_authorized_geography_blocked(self):
        items=self.all_months()
        items[5]["historical_geometry_approved"]=True
        with self.assertRaisesRegex(ValueError,"permission"):
            reconcile(items)
if __name__=="__main__":unittest.main()
