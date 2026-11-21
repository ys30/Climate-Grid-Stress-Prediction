"""No fabricated source evidence; test exact original SDGE hash and header guards."""
import hashlib,tempfile,unittest
from pathlib import Path
from scripts.c2_sdge_real_2020_2023_sixteen_quarter_source_audit import inspect_one

class SixteenQuarterSourceContracts(unittest.TestCase):
    def make(self,data,valid_hash=True):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        d=Path(t.name);csv=d/"SDGE-ELEC-2020-Q1.csv";s=d/"SDGE-ELEC-2020-Q1-HASH.txt"
        csv.write_bytes(data);s.write_text(hashlib.sha512(data).hexdigest() if valid_hash else "0"*128)
        return csv,s
    def test_real_format_source_hash_and_privacy(self):
        data=(b"ZipCode,Month,Year,CustomerClass,Combined,TotalCustomers,TotalkWh,AveragekWh\n"
              b"92101,1,2020,R,Y,0,0,0\n"
              b"92102,2,2020,R,N,100,100000,1000\n"
              b"92103,3,2020,C,Y,4,220,55\n")
        csv,sidecar=self.make(data)
        r=inspect_one(csv,sidecar,2020,1)
        self.assertEqual(r["source_rows"],3)
        self.assertEqual(r["privacy_Combined_counts"],{"Y":2,"N":1})
        self.assertEqual(r["kwh_value_states"],{"literal_zero":1,"positive":2})
        self.assertFalse(r["reporting_ZIP_aggregate_is_observed_county_load"])
    def test_bad_publisher_digest_rejected(self):
        data=(b"ZipCode,Month,Year,CustomerClass,Combined,TotalCustomers,TotalkWh,AveragekWh\n"
              b"92101,1,2020,R,N,100,100000,1000\n"
              b"92102,2,2020,R,Y,0,0,0\n"
              b"92103,3,2020,C,Y,4,220,55\n")
        csv,s=self.make(data,valid_hash=False)
        with self.assertRaisesRegex(ValueError,"SHA512"):
            inspect_one(csv,s,2020,1)
    def test_wrong_period_rejected(self):
        data=(b"ZipCode,Month,Year,CustomerClass,Combined,TotalCustomers,TotalkWh,AveragekWh\n"
              b"92101,5,2020,R,Y,0,0,0\n")
        csv,s=self.make(data)
        with self.assertRaisesRegex(ValueError,"calendar period"):
            inspect_one(csv,s,2020,1)

if __name__=="__main__":unittest.main()
