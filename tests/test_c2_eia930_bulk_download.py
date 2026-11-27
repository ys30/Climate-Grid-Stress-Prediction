"""Offline tests for official EIA-930 six-month source retry/cleanup."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
from scripts.c2_fetch_eia930_bulk import download_bulk

class _Response(io.BytesIO):
    def __init__(self,payload,ctype="text/csv"):
        super().__init__(payload)
        self.headers={"Content-Type":ctype}

class TestEiaBulkDownload(unittest.TestCase):
    def test_transient_failure_then_valid_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"source.csv"
            events=[URLError("temporary error"), _Response(b"a,b\n1,2\n")]
            def respond(*args,**kwargs):
                entry=events.pop(0)
                if isinstance(entry,Exception):
                    raise entry
                return entry
            with patch("scripts.c2_fetch_eia930_bulk.urllib.request.urlopen",side_effect=respond),patch("time.sleep"):
                url=download_bulk(dest,2025,7)
            self.assertIn("EIA930_BALANCE_2025_Jul_Dec.csv",url)
            self.assertEqual(dest.read_bytes(),b"a,b\n1,2\n")
    def test_html_rejected_and_partial_file_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"source.csv"
            with patch("scripts.c2_fetch_eia930_bulk.urllib.request.urlopen",
                       side_effect=lambda *a,**kw:_Response(b"<html>error</html>","text/html")),patch("time.sleep"):
                with self.assertRaisesRegex(RuntimeError,"after 3 attempts"):
                    download_bulk(dest,2025,7)
            self.assertFalse(dest.exists())
    def test_empty_response_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"source.csv"
            with patch("scripts.c2_fetch_eia930_bulk.urllib.request.urlopen",
                       side_effect=lambda *a,**kw:_Response(b"")),patch("time.sleep"):
                with self.assertRaisesRegex(RuntimeError,"after 3 attempts"):
                    download_bulk(dest,2025,7)
            self.assertFalse(dest.exists())
    def test_existing_raw_file_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"source.csv"
            dest.write_text("previous archive")
            with self.assertRaisesRegex(ValueError,"exists"):
                download_bulk(dest,2025,7)
            self.assertEqual(dest.read_text(),"previous archive")

if __name__=="__main__":
    unittest.main()
