"""Regression tests for C2 retrospective paired persistent-event audit."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"c2_episode_tail_audit.py"
spec=importlib.util.spec_from_file_location("c2_episode_tail_audit",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
FIELDS=("ba","date","target","estimator","event_category","episode_id",
        "actual_mw","calendar_pred_mw","weather_pred_mw","source_flag")

class TestEpisodeTailAudit(unittest.TestCase):
    def make_csv(self,rows,root):
        path=Path(root)/"rows.csv"
        with open(path,"w",newline="",encoding="utf-8") as f:
            wr=csv.DictWriter(f,fieldnames=FIELDS)
            wr.writeheader()
            wr.writerows(rows)
        return path

    def rows(self):
        return [dict(ba="SRP",date=f"2025-07-{d:02d}",target="peak",
            estimator="Huber",event_category="observed_high_demand",
            episode_id="a",actual_mw=1000,calendar_pred_mw=800,
            weather_pred_mw=900,source_flag="1" if d==1 else "")
            for d in (1,2)]

    def test_expected_paired_error_direction_and_flag(self):
        with tempfile.TemporaryDirectory() as td:
            src=self.make_csv(self.rows(),td)
            m=mod.audit(src,Path(td)/"out",bootstrap=10)
            self.assertEqual(m["episodes"],1)
            self.assertEqual(m["source_flagged_rows"],1)
            with open(Path(td)/"out"/"episode_duration_metrics.csv",newline="") as f:
                r=list(csv.DictReader(f))[0]
            self.assertAlmostEqual(float(r["delta_mae_mw"]),-100)
            self.assertAlmostEqual(float(r["weather_underforecast_rate"]),1)
            self.assertEqual(r["duration"],"2-3d")
            self.assertEqual(r["interval_type"],"withheld_fewer_than_8_episodes")
            self.assertEqual(r["delta_mae_bootstrap_p025_mw"],"")

    def test_reject_gap(self):
        rows=self.rows()
        rows[1]["date"]="2025-07-03"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"Noncontiguous"):
                mod.build_episodes(mod.parse_rows(self.make_csv(rows,td)))

    def test_reject_cross_year(self):
        rows=self.rows()
        rows[0]["date"]="2024-12-31"
        rows[1]["date"]="2025-01-01"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"crosses year"):
                mod.build_episodes(mod.parse_rows(self.make_csv(rows,td)))

    def test_reject_duplicate_keys(self):
        rows=self.rows()+[dict(self.rows()[0],episode_id="another")]
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"duplicate"):
                mod.parse_rows(self.make_csv(rows,td))

    def test_reject_singleton(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"Singleton"):
                mod.build_episodes(mod.parse_rows(self.make_csv(self.rows()[:1],td)))

    def test_reject_nan(self):
        rows=self.rows()
        rows[0]["actual_mw"]="nan"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"nonfinite"):
                mod.parse_rows(self.make_csv(rows,td))

    def test_eight_episode_interval_and_reproducibility(self):
        rows=[]
        for e in range(8):
            for d in (1,2):
                rows.append(dict(self.rows()[0],date=f"2025-07-{2*e+d:02d}",
                    episode_id=f"e{e}",source_flag="",weather_pred_mw=str(900+e)))
        with tempfile.TemporaryDirectory() as td:
            eps=mod.build_episodes(mod.parse_rows(self.make_csv(rows,td)))
            a=mod.describe(eps,bootstrap=30,seed=43)
            b=mod.describe(eps,bootstrap=30,seed=43)
            self.assertEqual(a,b)
            self.assertEqual(a[0]["episodes"],8)
            self.assertEqual(a[0]["days"],16)
            self.assertEqual(a[0]["interval_type"],"descriptive_episode_cluster_bootstrap")

if __name__=="__main__":
    unittest.main()
