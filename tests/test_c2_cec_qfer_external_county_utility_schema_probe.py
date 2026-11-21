"""Synthetic XLSX source-inventory contract; not invented CEC measurements."""
import tempfile,unittest,zipfile
from pathlib import Path
from scripts.c2_cec_qfer_external_county_utility_schema_probe import inspect_xlsx

BOOK=b'''<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="SyntheticAnnual" sheetId="1" r:id="rId1"/></sheets></workbook>'''
RELS=b'''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'''
SHEET=b'''<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:B2"/><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>County</t></is></c><c r="B1" t="inlineStr"><is><t>Annual MWh</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>TestCounty</t></is></c><c r="B2"><v>123</v></c></row></sheetData></worksheet>'''

class CECSourceInventoryTests(unittest.TestCase):
    def test_official_like_xlsx_has_no_claimed_joint_allocation(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"synthetic.xlsx"
            with zipfile.ZipFile(f,"w") as z:
                z.writestr("xl/workbook.xml",BOOK)
                z.writestr("xl/_rels/workbook.xml.rels",RELS)
                z.writestr("xl/worksheets/sheet1.xml",SHEET)
            record=inspect_xlsx(f,source_url="https://example.org/only-synthetic")
            self.assertEqual(record["sheets"][0]["name"],"SyntheticAnnual")
            self.assertEqual(record["sheets"][0]["sheet_dimension_claim"],"A1:B2")
            self.assertFalse(record["historical_CISO_operational_BA_scope_verified"])
            self.assertFalse(record["sheets"][0]["joint_county_utility_measurement_verified"])
            self.assertFalse(record["model_training_permitted"])
    def test_rejects_non_workbook(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"not.xlsx";f.write_bytes(b"NOT A ZIP"*100)
            with self.assertRaises(ValueError):inspect_xlsx(f,source_url="https://example.org/fake")

if __name__=="__main__":unittest.main()
