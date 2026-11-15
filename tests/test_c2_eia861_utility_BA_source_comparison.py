import unittest
from src.c2_eia861_utility_BA_source_comparison import compare,BAS,YEARS
class Tests(unittest.TestCase):
    def test_overlap_and_unrestricted_territory_not_load(self):
        old=[{"year":y,"eia930_BA_code":ba,"county_id_fips":"04013"}
             for y in YEARS for ba in BAS]
        bridge=[{"year":y,"BA":ba,
          "candidate_union_FIPS_semicolon":"04013;04015",
          "unrestricted_utility_union_FIPS_semicolon":"04013;04015;32001",
          "candidate_union_counties":"2","unrestricted_utility_union_counties":"3",
          "source_utility_state_associations":"1","associations_with_county_source":"1",
          "unmatched_associations":"0"} for y in YEARS for ba in BAS]
        rows=compare(bridge,old)
        self.assertEqual(len(rows),24)
        self.assertTrue(all(x["county_FIPS_only_in_utility_source"]==1 for x in rows))
        self.assertTrue(all(x["operating_geography_approved"] is False for x in rows))
        self.assertTrue(all(x["model_training_permitted"] is False for x in rows))
        self.assertTrue(all(x["county_jaccard_is_descriptive_only"] is True for x in rows))
        self.assertTrue(all(x["incomplete_utility_territory_join"] is False for x in rows))
        with self.assertRaises(ValueError):compare(bridge[:-1],old)
    def test_reject_bad_unrestricted_fips_duplicate_and_negative(self):
        original=[{"year":y,"eia930_BA_code":ba,"county_id_fips":"04013"} for y in YEARS for ba in BAS]
        bridge=[{"year":y,"BA":ba,
          "candidate_union_FIPS_semicolon":"04013",
          "unrestricted_utility_union_FIPS_semicolon":"04013;32001",
          "candidate_union_counties":"1","unrestricted_utility_union_counties":"2",
          "source_utility_state_associations":"1","associations_with_county_source":"1",
          "unmatched_associations":"0"} for y in YEARS for ba in BAS]
        good=compare(bridge,original)
        self.assertTrue(all(x["additional_cross_state_unique_counties"]==1 for x in good))
        bad=[dict(x) for x in bridge]
        bad[0]["unrestricted_utility_union_FIPS_semicolon"]="04013;bad"
        with self.assertRaises(ValueError): compare(bad,original)
        bad=[dict(x) for x in bridge]
        bad[0]["unmatched_associations"]="-1"
        with self.assertRaises(ValueError): compare(bad,original)
        bad=[dict(x) for x in bridge]
        bad[0]["associations_with_county_source"]="0"
        with self.assertRaises(ValueError): compare(bad,original)
        partially_unmatched=[dict(x) for x in bridge]
        partially_unmatched[0].update({
            "source_utility_state_associations":"2",
            "associations_with_county_source":"1",
            "unmatched_associations":"1",
        })
        result=compare(partially_unmatched,original)
        self.assertTrue(result[0]["incomplete_utility_territory_join"])
        self.assertEqual(result[0]["utility_state_association_match_fraction"],0.5)
        self.assertFalse(result[0]["operating_geography_approved"])
        with self.assertRaises(ValueError): compare(bridge,original+[dict(original[0])])
if __name__=="__main__":unittest.main()
