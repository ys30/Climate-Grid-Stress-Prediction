"""Only synthetic XLSX fixtures; not actual BPA load evidence."""
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.c2_bpa_ferc714_original_acquisition import acquire, extract_inventory

def fake_xlsx():
    wb = """<?xml version="1.0"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <sheets><sheet name="PT III Sch1" sheetId="1" r:id="rId1"/></sheets></workbook>"""
    rels = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
      Target="worksheets/sheet1.xml"/></Relationships>"""
    data = """<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Balancing Authority Load</t></is></c>
    <c r="B1"><v>2025</v></c></row></sheetData></worksheet>"""
    with io.BytesIO() as buff:
        with zipfile.ZipFile(buff, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("xl/workbook.xml", wb)
            z.writestr("xl/_rels/workbook.xml.rels", rels)
            z.writestr("xl/worksheets/sheet1.xml", data)
        return buff.getvalue()

class TestBPASourceGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_real_xlsx_structure_parser_on_synthetic_sample(self):
        sheets = extract_inventory(fake_xlsx())
        self.assertEqual(len(sheets), 1)
        self.assertEqual(sheets[0]["sheet_name"], "PT III Sch1")
        self.assertEqual(sheets[0]["sample_first_35_rows"][0]["cells"][0]["value"],
                         "Balancing Authority Load")

    def test_six_year_manifest_is_comprehensive_without_claiming_metrics(self):
        rows = acquire(self.root, opener=lambda url: fake_xlsx() + b" " * 1300)
        self.assertEqual(len(rows), 6)
        self.assertEqual([r["year"] for r in rows], list(range(2020,2026)))
        # Adding tail bytes to a valid ZIP is allowed; workbook inventory still checked.
        self.assertTrue(all(r["status"].startswith("original_downloaded") for r in rows))
        manifest = json.loads((self.root / "BPA_FERC714_2020_2025_ORIGINAL_SOURCE_MANIFEST.json").read_text())
        self.assertFalse(manifest["model_training_permitted"])
        self.assertFalse(manifest["actual_EIA930_source_comparison_completed"])

    def test_existing_original_is_reverified_without_new_download(self):
        sample = fake_xlsx() + b" " * 1300
        acquire(self.root, years=(2025,), opener=lambda url: sample)
        def forbidden_network(url):
            raise AssertionError("Should not redownload a previously archived original")
        rows = acquire(self.root, years=(2025,), opener=forbidden_network)
        self.assertEqual(rows[0]["status"], "existing_original_reverified")
        self.assertEqual(rows[0]["sha256"], hashlib.sha256(sample).hexdigest())

    def test_invalid_preexisting_source_is_not_overwritten(self):
        target = self.root / "BPA_FERC714_2025_ORIGINAL.xlsx"
        target.write_bytes(b"corrupted archived source")
        rows = acquire(self.root, years=(2025,), opener=lambda url: fake_xlsx() + b" " * 1300)
        self.assertEqual(rows[0]["status"], "existing_original_invalid")
        self.assertEqual(target.read_bytes(), b"corrupted archived source")

    def test_invalid_bytes_fail_closed_with_written_diagnostics(self):
        rows = acquire(self.root, years=(2025,), opener=lambda url: b"not xlsx")
        self.assertEqual(rows[0]["status"], "source_not_verified")
        self.assertFalse((self.root / "BPA_FERC714_2025_ORIGINAL.xlsx").exists())

    def test_no_year_outside_contract(self):
        with self.assertRaises(ValueError):
            acquire(self.root, years=(2019,), opener=lambda url: fake_xlsx())

if __name__ == "__main__":
    unittest.main()
