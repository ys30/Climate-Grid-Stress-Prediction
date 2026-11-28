"""No-network tests for the pinned PUDL/Zenodo original EIA-930 ZIP backup."""
import csv
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.c2_fetch_eia930_zenodo import acquire_archive, extract_balance, fetch_zenodo
from scripts.c2_verify_eia930_source import verify

class TestZenodoFallback(unittest.TestCase):
    @staticmethod
    def archive_bytes():
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
            payload=io.StringIO()
            writer=csv.writer(payload)
            writer.writerow(["Balancing Authority","UTC Time at End of Hour",
                             "Demand (MW)","Demand Forecast (MW)"])
            writer.writerow(["SRP","2025-07-01 01:00:00","1200","1150"])
            writer.writerow(["SRP","2025-08-01 00:00:00","1210","1160"])
            z.writestr("eia930-2025half2-balance.csv",payload.getvalue())
            z.writestr("eia930-2025half2-interchange.csv","a,b\n1,2\n")
        return buf.getvalue()

    def test_pinned_archive_to_audited_source(self):
        blob=self.archive_bytes()
        with tempfile.TemporaryDirectory() as td:
            with patch("scripts.c2_fetch_eia930_zenodo.PUBLISHED_MD5",hashlib.md5(blob).hexdigest()):
                data=fetch_zenodo(Path(td)/"source",opener=lambda *args,**kw:io.BytesIO(blob))
            output=Path(td)/"source"
            self.assertEqual(data["origin"],"pudl_zenodo_raw")
            self.assertEqual(data["row_count"],4)
            self.assertTrue((output/"eia930-2025half2.zip").exists())
            integrity=verify(output/"eia930_D_DF_hourly.csv",output/"source_manifest.json")
            self.assertTrue(integrity["passed"],integrity["issues"])

    def test_wrong_published_md5_rejected_without_destination(self):
        blob=self.archive_bytes()
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/"source"
            with patch("scripts.c2_fetch_eia930_zenodo.PUBLISHED_MD5","0"*32):
                with self.assertRaisesRegex(ValueError,"MD5"):
                    fetch_zenodo(dest,opener=lambda *args,**kw:io.BytesIO(blob))
            self.assertFalse(dest.exists())

    def test_tampered_retained_zip_rejected(self):
        blob=self.archive_bytes()
        with tempfile.TemporaryDirectory() as td:
            with patch("scripts.c2_fetch_eia930_zenodo.PUBLISHED_MD5",hashlib.md5(blob).hexdigest()):
                fetch_zenodo(Path(td)/"source",opener=lambda *args,**kw:io.BytesIO(blob))
            out=Path(td)/"source"
            archive=out/"eia930-2025half2.zip"
            archive.write_bytes(archive.read_bytes()+b"tampering")
            result=verify(out/"eia930_D_DF_hourly.csv",out/"source_manifest.json")
            self.assertFalse(result["passed"])
            self.assertTrue(any("Zenodo archive" in s for s in result["issues"]))

    def test_missing_archive_member_rejected(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,"w") as z:
            z.writestr("wrong-file.csv","a,b\n")
        with tempfile.TemporaryDirectory() as td:
            archive=Path(td)/"bad.zip"
            archive.write_bytes(data.getvalue())
            with self.assertRaisesRegex(ValueError,"archive members"):
                extract_balance(archive,Path(td)/"balance.csv")

    def test_wrong_year_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"half2"):
                fetch_zenodo(Path(td)/"dest",year=2024,month=7)

if __name__=="__main__":
    unittest.main()
