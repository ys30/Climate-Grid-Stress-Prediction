"""No-network regression tests for EIA-930 monthly official source collector."""
import csv
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from scripts.c2_fetch_eia930_df import month_window, request_page, collect

class TestEiaFetcher(unittest.TestCase):
    def fake(self,url):
        query=parse_qs(urlsplit(url).query)
        ba=query["facets[respondent][]"][0]
        start=query["start"][0]
        return {"response":{"total":"2","data":[
            {"period":start,"respondent":ba,"type":"D","value":"120"},
            {"period":start,"respondent":ba,"type":"DF","value":"115"}]}}
    def test_leap_year(self):
        self.assertEqual(month_window(2024,2)[1],"2024-02-29T23")
    def test_month_fetch(self):
        rows,meta=request_page("SRP",2023,1,None,self.fake)
        self.assertEqual(len(rows),2)
        self.assertEqual(meta["api_total"],2)
    def test_duplicate_fails(self):
        def bad(url):
            result=self.fake(url)
            result["response"]["data"][1]["type"]="D"
            return result
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            request_page("SRP",2023,1,None,bad)
    def test_incomplete_page_fails(self):
        with self.assertRaisesRegex(ValueError,"ended"):
            request_page("SRP",2023,1,None,
                         lambda url: {"response":{"total":"2","data":[]}})
    def test_manifest_export_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            output=Path(root)/"run"
            meta=collect(output,2023,2023,("SRP",),fetch=self.fake)
            self.assertEqual(meta["row_count"],24)
            with (output/"eia930_D_DF_hourly.csv").open() as f:
                self.assertEqual(len(list(csv.DictReader(f))),24)
            self.assertTrue((output/"source_manifest.json").exists())
            with self.assertRaisesRegex(ValueError,"exists"):
                collect(output,2023,2023,("SRP",),fetch=self.fake)

if __name__=="__main__":
    unittest.main()
