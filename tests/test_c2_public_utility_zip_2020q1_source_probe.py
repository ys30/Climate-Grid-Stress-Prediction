"""Synthetic format guards; no invented original utility observations."""
import csv,io,unittest,zipfile
from scripts.c2_public_utility_zip_2020q1_source_probe import inspect_csv,inspect_excel,inspect_pge

class UtilityZipSourceProbeTests(unittest.TestCase):
    def test_csv_real_source_format_and_html_rejected(self):
        d=inspect_csv(b"zip,month,kwh\n92101,2020-01,123\n")
        self.assertEqual(d["format"],"CSV")
        self.assertFalse(d["joint_ZIP_county_observed"])
        with self.assertRaisesRegex(ValueError,"HTML"):
            inspect_csv(b"<!DOCTYPE html><html>error</html>")
    def test_pge_zip_must_not_be_fabricated(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,"w") as z:z.writestr("synthetic.csv","x,y\n1,2\n")
        self.assertIn("synthetic.csv",inspect_pge(stream.getvalue())["archive_members"])
        with self.assertRaisesRegex(ValueError,"not ZIP"):
            inspect_pge(b"not a source zip")
    def test_excel_workbook_must_exist(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,"w") as z:z.writestr("xl/workbook.xml","<workbook/>")
        self.assertEqual(inspect_excel(stream.getvalue())["format"],"XLSX")
        with self.assertRaisesRegex(ValueError,"workbook"):
            other=io.BytesIO()
            with zipfile.ZipFile(other,"w") as z:z.writestr("other.xml","bad")
            inspect_excel(other.getvalue())

if __name__=="__main__":unittest.main()
