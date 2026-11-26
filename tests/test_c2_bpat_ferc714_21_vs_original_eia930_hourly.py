"""Local source-only FERC/EIA comparisons on simulated FERC rows; no claimed FERC observations."""
import csv,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.c2_bpat_ferc714_21_vs_original_eia930_hourly import (
    read_ferc,calculate,utc,YEARS
)

class TestFERCRealInputAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.file=Path(self.tmp.name)/"FERC_SYNTHETIC_NOT_REAL.csv"
        self.rows=[{"respondent_id_ferc714":"21","report_date":"2020-12-31",
                    "datetime_utc":"2021-01-01T00:00:00+00:00","demand_mwh":"7000"}]
        self.write()
    def write(self):
        with self.file.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(self.rows[0]))
            w.writeheader();w.writerows(self.rows)
    def test_reporting_year_is_preserved_across_UTC_boundary(self):
        f,c,n,s=read_ferc(self.file)
        self.assertEqual(c[2020],1);self.assertEqual(s[2020],1)
        self.assertNotIn(2021,c)
    def test_duplicate_UTC_hour_fails_closed(self):
        self.rows.append(self.rows[0].copy());self.write()
        with self.assertRaisesRegex(ValueError,"Duplicate FERC"):read_ferc(self.file)
    def test_unapproved_respondent_fails_closed(self):
        self.rows[0]["respondent_id_ferc714"]="22";self.write()
        with self.assertRaisesRegex(ValueError,"respondent"):read_ferc(self.file)
    def test_missing_value_is_not_imputed(self):
        self.rows[0]["demand_mwh"]="";self.write()
        f,c,n,s=read_ferc(self.file)
        self.assertIsNone(list(f.values())[0]);self.assertEqual(n[2020],1)
    def test_nonhourly_time_fails_closed(self):
        self.rows[0]["datetime_utc"]="2021-01-01T00:30:00+00:00";self.write()
        with self.assertRaisesRegex(ValueError,"Non-hour"):read_ferc(self.file)
    def test_no_source_url_fails_closed(self):
        f,c,n,s=read_ferc(self.file)
        with self.assertRaisesRegex(ValueError,"source URL"):
            calculate({},f,c,n,s,"eia_sha","ferc_sha","")
    def test_preliminary_shift_is_not_optimized(self):
        f,c,n,s=read_ferc(self.file)
        e={datetime(2021,1,1,tzinfo=timezone.utc):7000}
        r=calculate(e,f,c,n,s,"eia","ferc","https://example.org/synthetic.csv")
        x=r["annual_diagnostics"][0]
        self.assertEqual(x["zero_shift_matched_hours"],1)
        self.assertEqual(x["zero_shift_mae_mw"],0)
        self.assertFalse(x["FERC_complete_source_hours"])
        self.assertFalse(r["automatically_select_best_shift"])
        self.assertFalse(r["model_training_permitted"])
    def test_timezone_convert_to_UTC(self):
        self.assertEqual(utc("2020-12-31T16:00:00-08:00"),
                         datetime(2021,1,1,tzinfo=timezone.utc))

if __name__=="__main__":unittest.main()
