"""Synthetic official-index hyperlink contracts only. No fabricated utility data."""
import unittest
from scripts.c2_sce_real_2020_2023_original_quarter_index_audit import source_links,EXPECTED,collect

class SCEHistoricalPublisherIndexTests(unittest.TestCase):
    def setUp(self):
        self.parts=[]
        for year,q in sorted(EXPECTED):
            directory="inline-files" if year==2020 else "custom-files/PDF_Files"
            filename=f"SCE_{year}_Q{q}_ElectricUsageByZip.xlsx"
            if (year,q)==(2022,2):filename="SCE_2002_Q2_ElectricUsageByZip.xlsx"
            self.parts.append(f'<a href="/sites/default/files/{directory}/{filename}">Q{q}</a>')
        self.html="<html><body>"+ "".join(self.parts)+"</body></html>"

    def test_16_distinct_official_hrefs(self):
        x=source_links(self.html)
        self.assertEqual(len(x),16)
        self.assertTrue(x[(2023,4)].endswith("SCE_2023_Q4_ElectricUsageByZip.xlsx"))
        self.assertTrue(x[(2022,2)].endswith("SCE_2002_Q2_ElectricUsageByZip.xlsx"))

    def test_missing_quarter_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"index incomplete"):
            source_links("<html>"+"".join(self.parts[:-1])+"</html>")

    def test_conflicting_same_quarter_fails_closed(self):
        other='<a href="/sites/default/files/alternate/SCE_2023_Q4_ElectricUsageByZip.xlsx">duplicate</a>'
        with self.assertRaisesRegex(ValueError,"Ambiguous"):
            source_links(self.html+other)

    def test_html_response_all_16_not_claimed_as_valid(self):
        x=collect(self.html,lambda url:b"<html>Login required</html>")
        self.assertEqual(x["quarter_count_verified"],0)
        self.assertFalse(x["all_2020_2023_original_sources_verified"])
        self.assertFalse(x["model_training_permitted"])

if __name__=="__main__":unittest.main()
