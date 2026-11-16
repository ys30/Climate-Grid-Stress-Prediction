"""Synthetic fixtures only: verify raw EIA-930 vintage comparison contracts."""
import csv,io,unittest,zipfile
from datetime import timedelta
from src.c2_srp_eia930_raw_vintage_compare import FIRST,read_srp,compare,archived_balance_digest

def source_zip(vals,extra=None):
    s=io.StringIO()
    w=csv.writer(s)
    w.writerow(["Balancing Authority","UTC Time at End of Hour","Demand (MW)"])
    for h,v in vals:
        end=FIRST+timedelta(hours=h+1)
        w.writerow(["SRP",end.strftime("%m/%d/%Y %I:%M:%S %p"),v])
    dest=io.BytesIO()
    with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("eia930-2023half1-balance.csv",s.getvalue())
        if extra is not None:
            z.writestr("archive-description.txt",extra)
    return dest.getvalue()

class TestVintage(unittest.TestCase):
    def test_hour_ending_utc_conversion(self):
        rows=read_srp(source_zip([(3,68520),(4,45097),(5,27030)]))
        self.assertEqual(rows["2023-02-26T23:00:00Z"],68520)
        self.assertEqual(rows["2023-02-27T00:00:00Z"],45097)
        self.assertEqual(rows["2023-02-27T01:00:00Z"],27030)
    def test_changed_hour_value(self):
        a=source_zip([(h,3000) for h in range(11)])
        b=source_zip([(h,45097 if h==4 else 3000) for h in range(11)])
        rows,qa=compare({"2025-11-v53":a,"2026-09-v92":b})
        self.assertEqual(qa["n_changed_original_demand_hours"],1)
        self.assertTrue(qa["all_hours_present_in_both_sources"])
        self.assertFalse(qa["E2_training_permitted"])
    def test_identical_hourly_values_do_not_imply_revision(self):
        a=source_zip([(h,3000) for h in range(11)])
        _,qa=compare({"2025-11-v53":a,"2026-09-v92":a})
        self.assertEqual(qa["n_changed_original_demand_hours"],0)
    def test_zip_bytes_can_differ_while_balance_csv_is_identical(self):
        values=[(h,3000+h) for h in range(11)]
        first=source_zip(values)
        second=source_zip(values,extra="different ZIP contents, same balance CSV")
        self.assertNotEqual(first,second)
        self.assertEqual(archived_balance_digest(first)["balance_csv_sha256"],
                         archived_balance_digest(second)["balance_csv_sha256"])
        _,qa=compare({"2025-11-v53":first,"2026-09-v92":second})
        self.assertTrue(qa["original_balance_files_identical"])
        self.assertEqual(qa["n_changed_original_demand_hours"],0)

    def test_missing_source_hour_blocks_complete_vintage_admission(self):
        first=source_zip([(h,3000) for h in range(11)])
        second=source_zip([(h,3000) for h in range(11) if h!=4])
        _,qa=compare({"2025-11-v53":first,"2026-09-v92":second})
        self.assertFalse(qa["all_hours_present_in_both_sources"])
        self.assertEqual(qa["n_paired"],10)

    def test_three_independent_archives_detect_two_change_intervals(self):
        early=source_zip([(h,2900 if h==4 else 3000) for h in range(11)])
        mid=source_zip([(h,45097 if h==4 else 3000) for h in range(11)])
        late=source_zip([(h,45097 if h==4 else 3000) for h in range(11)])
        rows,qa=compare({"2025-06-archive":early,
                         "2025-11-v53":mid,"2026-09-v92":late})
        self.assertTrue(qa["all_hours_present_in_three_sources"])
        self.assertEqual(qa["n_changed_demand_hours_june_to_nov"],1)
        self.assertEqual(qa["n_changed_original_demand_hours"],0)
        self.assertTrue(rows[4]["june_to_nov_demand_changed"])
        self.assertTrue(rows[4]["june_to_september_demand_changed"])
        self.assertEqual(qa["n_november_revisions_reverted_by_september"],0)

    def test_three_archive_intermediate_change_can_revert(self):
        early=source_zip([(h,3000) for h in range(11)])
        changed=source_zip([(h,12345 if h==4 else 3000) for h in range(11)])
        rows,qa=compare({"2025-06-archive":early,
                         "2025-11-v53":changed,"2026-09-v92":early})
        self.assertEqual(qa["n_changed_demand_hours_june_to_nov"],1)
        self.assertEqual(qa["n_changed_original_demand_hours"],1)
        self.assertEqual(qa["n_changed_demand_hours_june_to_september"],0)
        self.assertEqual(qa["n_november_revisions_reverted_by_september"],1)
        self.assertTrue(rows[4]["november_revision_reverted_by_september"])

    def test_three_archive_incomplete_hour_fails_qa(self):
        complete=source_zip([(h,3000) for h in range(11)])
        early=source_zip([(h,3000) for h in range(11) if h!=5])
        _,qa=compare({"2025-06-archive":early,
                      "2025-11-v53":complete,"2026-09-v92":complete})
        self.assertFalse(qa["all_hours_present_in_three_sources"])

    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            read_srp(source_zip([(3,3000),(3,3000)]))
if __name__=="__main__":unittest.main()
