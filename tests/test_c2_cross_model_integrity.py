import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_cross_model_integrity import validate, REQUIRED

class TestCrossModelIntegrity(unittest.TestCase):
    def check(self,modify=None):
        rows=[]
        for day in ('2025-07-01','2025-07-02'):
            for model in ('Ridge','Huber'):
                row=dict(ba='SRP',date=day,target='peak',estimator=model,
                    event_category='high_load',episode_id='ep1',actual_mw='1000',
                    calendar_pred_mw='900',weather_pred_mw='950')
                rows.append(row)
        if modify: modify(rows)
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'sample.csv'
            with file.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=(*REQUIRED, 'source_flag'))
                writer.writeheader()
                writer.writerows(rows)
            return validate(file)
    def test_valid(self):
        r=self.check();self.assertTrue(r['passed']);self.assertEqual(r['rows'],4)
    def test_actual_mismatch(self):
        r=self.check(lambda a:a[1].update(actual_mw='1100'));self.assertFalse(r['passed'])
    def test_episode_mismatch(self):
        r=self.check(lambda a:a[1].update(episode_id='x'));self.assertFalse(r['passed'])
    def test_duplicate(self):
        r=self.check(lambda a:a.append(dict(a[0])));self.assertFalse(r['passed'])
    def test_gap(self):
        r=self.check(lambda a:[x.update(date='2025-07-04') for x in a[2:]]);self.assertFalse(r['passed'])
    def test_missing_estimator_pair(self):
        r=self.check(lambda a:a.pop(1));self.assertFalse(r['passed'])
        self.assertTrue(any('missing estimator' in x['issue'] for x in r['issues']))
    def test_entire_estimator_missing(self):
        r=self.check(lambda a:a.__setitem__(slice(None),[x for x in a if x["estimator"]=="Ridge"]))
        self.assertFalse(r["passed"])
        self.assertTrue(any("missing required estimator" in x["issue"] for x in r["issues"]))
    def test_source_flag_mismatch(self):
        r=self.check(lambda a:a[0].update(source_flag='yes'))
        self.assertFalse(r['passed'])
        self.assertTrue(any('source_flag differs' in x['issue'] for x in r['issues']))
    def test_unknown_source_flag(self):
        r=self.check(lambda a:a[0].update(source_flag='unknown'))
        self.assertFalse(r['passed'])
    def test_nonfinite(self):
        r=self.check(lambda a:a[0].update(actual_mw='nan'));self.assertFalse(r['passed'])

if __name__=='__main__':
    unittest.main()
