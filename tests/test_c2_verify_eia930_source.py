"""Offline regression tests for archived EIA D/DF source provenance gate."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_verify_eia930_source import verify

class TestSourceProvenance(unittest.TestCase):
    def fixture(self,root,change=None):
        path=Path(root)/'hourly.csv'
        entries=[
            {"period":"2025-07-01T01","respondent":"SRP","type":"D","value":"100"},
            {"period":"2025-07-01T01","respondent":"SRP","type":"DF","value":"95"},
            {"period":"2025-08-01T00","respondent":"SRP","type":"D","value":"120"},
            {"period":"2025-08-01T00","respondent":"SRP","type":"DF","value":"110"},
        ]
        if change:change(entries)
        with path.open('w',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=['period','respondent','type','value'])
            wr.writeheader()
            wr.writerows(entries)
        manifest=Path(root)/'manifest.json'
        meta={"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"row_count":len(entries),
              "month_ba_manifest":[{"ba":"SRP","year":2025,"month":7,"rows":len(entries),"api_total":len(entries)}]}
        manifest.write_text(json.dumps(meta))
        return path,manifest
    def test_valid_inclusive_month_end_hour(self):
        with tempfile.TemporaryDirectory() as root:
            result=verify(*self.fixture(root))
            self.assertTrue(result['passed'],result['issues'])
            self.assertEqual(result['rows'],4)
    def test_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            file,manifest=self.fixture(root)
            file.write_text(file.read_text().replace('100','999'))
            result=verify(file,manifest)
            self.assertFalse(result['passed'])
            self.assertTrue(any('SHA-256' in x for x in result['issues']))
    def test_duplicate_hour_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            result=verify(*self.fixture(root,lambda x:x.append(dict(x[0]))))
            self.assertFalse(result['passed'])
            self.assertTrue(any('duplicate' in x for x in result['issues']))
    def test_wrong_month_row_count_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            file,manifest=self.fixture(root)
            meta=json.loads(manifest.read_text())
            meta['month_ba_manifest'][0]['rows']=3
            manifest.write_text(json.dumps(meta))
            result=verify(file,manifest)
            self.assertFalse(result['passed'])
    def test_unexpected_ba_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            def mutate(rows):rows[0]['respondent']='AZPS'
            result=verify(*self.fixture(root,mutate))
            self.assertFalse(result['passed'])
            self.assertTrue(any('outside manifest' in x for x in result['issues']))

if __name__=='__main__':
    unittest.main()
