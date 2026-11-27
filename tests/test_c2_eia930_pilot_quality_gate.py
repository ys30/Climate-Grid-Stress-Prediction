import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_pilot_quality_gate import gate

class TestPilotQualityGate(unittest.TestCase):
    def fixture(self,dir,complete=31,incomplete=0):
        folder=Path(dir)
        full=folder/'daily.csv';bad=folder/'excluded.csv';manifest=folder/'manifest.json'
        with full.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['ba','date_utc','paired_hours'])
            writer.writeheader()
            for n in range(1,complete+1):
                writer.writerow({'ba':'SRP','date_utc':f'2025-07-{n:02d}','paired_hours':24})
        with bad.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['ba','date_utc','paired_hours'])
            writer.writeheader()
            for n in range(complete+1,complete+incomplete+1):
                writer.writerow({'ba':'SRP','date_utc':f'2025-07-{n:02d}','paired_hours':23})
        manifest.write_text(json.dumps({'origin':'bulk','month_ba_manifest':[{'ba':'SRP','year':2025,'month':7}]}))
        return full,bad,manifest
    def test_complete_month(self):
        with tempfile.TemporaryDirectory() as d:
            r=gate(*self.fixture(d))
            self.assertTrue(r['passed']);self.assertEqual(r['complete_days'],31)
            self.assertEqual(r['wholly_missing_days'],0)
            self.assertTrue(r['full_month_research_ready'])
            self.assertEqual(r['admission'],'FULL_MONTH')
    def test_coverage_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            r=gate(*self.fixture(d,24,7))
            self.assertFalse(r['passed']);self.assertEqual(r['incomplete_days'],7)
            self.assertEqual(r['admission'],'REJECTED')
    def test_whole_missing_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            r=gate(*self.fixture(d,25,1))
            self.assertTrue(r['passed']);self.assertEqual(r['wholly_missing_days'],5)
            self.assertFalse(r['full_month_research_ready'])
            self.assertEqual(r['admission'],'PILOT_ACCEPTED_PARTIAL')
    def test_pilot_accepted_but_partial_month_is_not_research_ready(self):
        with tempfile.TemporaryDirectory() as d:
            r=gate(*self.fixture(d,30,1),min_days=25)
            self.assertTrue(r['passed'])
            self.assertEqual(r['admission'],'PILOT_ACCEPTED_PARTIAL')
            self.assertFalse(r['full_month_research_ready'])
    def test_false_complete_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths=self.fixture(d,31)
            paths[0].write_text(paths[0].read_text().replace(',24\n',',23\n',1))
            r=gate(*paths)
            self.assertFalse(r['passed']);self.assertTrue(any('false-complete' in x for x in r['errors']))
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths=self.fixture(d,31)
            with paths[0].open('a') as f:f.write('SRP,2025-07-01,24\n')
            r=gate(*paths)
            self.assertFalse(r['passed']);self.assertTrue(any('duplicate' in x for x in r['errors']))
    def test_missing_manifest_month_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths=self.fixture(d,31)
            paths[2].write_text(json.dumps({'origin':'bulk','month_ba_manifest':[]}))
            self.assertFalse(gate(*paths)['passed'])
if __name__=='__main__':unittest.main()
