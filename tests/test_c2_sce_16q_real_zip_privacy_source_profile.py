"""Synthetic correctness of real-source SCE strict row-grain parser."""
import io,unittest
from openpyxl import Workbook
from scripts.c2_sce_16q_real_zip_privacy_source_profile import parse,numeric_state

class QuarterlySCEContracts(unittest.TestCase):
    def fixture(self,rows):
        wb=Workbook()
        sh=wb.active
        sh.append(["Report"])
        sh.append(["SCE Monthly"])
        sh.append(["Zip\nCode","Month","Year","Customer\nClass","Combined","TotalAccounts","TotalkWh","AveragekWh"])
        for row in rows:sh.append(row)
        buf=io.BytesIO();wb.save(buf);return buf.getvalue()
    def test_month_class_duplicate_and_blank_preserved(self):
        rows=[
          [93691,1,2020,"Residential","Y",None,None,None],
          [93691,1,2020,"Residential","Y",10,1230,123],
          [93691,2,2020,"Residential","N",10,-50,-5],
          [93691,3,2020,"Residential","N",10,120,12]]
        d=parse(self.fixture(rows),2020,1)
        self.assertEqual(d["data_rows"],4)
        self.assertEqual(d["duplicate_ZIP_month_class_extra_rows"],1)
        self.assertEqual(d["kwh_original_value_states"],{"blank":1,"positive":2,"negative":1})
        self.assertFalse(d["source_ZIP_recipient_physical_location_verified"])
    def test_source_year_guard(self):
        rows=[[93691,1,2002,"Residential","N",10,1230,123]]
        with self.assertRaisesRegex(ValueError,"year/month"):
            parse(self.fixture(rows),2022,1)
    def test_blank_not_physical_zero(self):
        self.assertEqual(numeric_state(None),"blank")
        self.assertEqual(numeric_state(0),"zero")
        self.assertEqual(numeric_state(-3),"negative")
if __name__=="__main__":unittest.main()
