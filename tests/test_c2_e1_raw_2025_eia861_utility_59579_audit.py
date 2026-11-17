import hashlib,io,zipfile,tempfile,unittest,json
from pathlib import Path
from openpyxl import Workbook
from unittest.mock import patch
from src import c2_e1_raw_2025_eia861_utility_59579_audit as m

class RawArchiveSafetyTests(unittest.TestCase):
    def test_pinned_archive_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"archive.zip";p.write_bytes(b"unverified")
            with self.assertRaisesRegex(ValueError,"MD5 mismatch"):
                m.inspect(p,Path(d)/"out")
    def test_utility_59579_scan_preserves_actual_excel_rows(self):
        book=Workbook();sheet=book.active;sheet.title="Sales"
        sheet.append(["utility_id_eia","residential","other"])
        sheet.append([59579,None,None])
        sheet.append([12345,100,None])
        buf=io.BytesIO();book.save(buf)
        zbuf=io.BytesIO()
        with zipfile.ZipFile(zbuf,"w") as z:z.writestr("Sales_2025.xlsx",buf.getvalue())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"archive.zip";p.write_bytes(zbuf.getvalue())
            with patch.object(m,"RAW_MD5",hashlib.md5(zbuf.getvalue()).hexdigest()):
                m.inspect(p,Path(d)/"out")
            source=json.loads((Path(d)/"out"/"C2_E1_RAW_2025_ARCHIVE_PROVENANCE.json").read_text())
            self.assertEqual(source["candidate_rows_with_59579"],1)
            self.assertEqual(source["candidate_rows_in_sales_named_sources"],1)
            self.assertFalse(source["raw_cell_to_derived_class_lineage_verified"])
if __name__=="__main__":unittest.main()
