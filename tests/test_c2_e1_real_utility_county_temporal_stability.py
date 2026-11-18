import unittest
from src.c2_e1_real_utility_county_temporal_stability import audit

def r(y,ba,util,st,count,cross=0):
    return dict(year=str(y),BA=ba,utility_id_eia=str(util),state=st,
        utility_counties_reported=str(count),other_state_counties_excluded=str(cross))
class UtilityCountyTemporalTests(unittest.TestCase):
    def test_persistent_and_changing_and_overlap(self):
        rows=[r(y,"AZPS",101,"AZ",0 if y==2020 else 2) for y in range(2020,2024)]
        rows += [r(y,"SRP",101,"AZ",1) for y in range(2020,2024)]
        rows += [r(y,"CISO",301,"CA",0) for y in range(2020,2024)]
        rows += [r(y,"BPAT",401,"WA",3,2) for y in range(2020,2024)]
        d,s=audit(rows)
        a=next(x for x in d if x["BA"]=="AZPS")
        self.assertTrue(a["county_presence_switch"])
        self.assertEqual(a["year_associations_nonexclusive"],4)
        self.assertEqual(next(x for x in s if x["BA"]=="CISO")["zero_county_all_year_entities"],1)
        self.assertEqual(next(x for x in s if x["BA"]=="BPAT")["any_cross_state_county_exclusion_entities"],1)
        self.assertFalse(all(x["E2_training_permitted"] for x in s))
    def test_duplicate_source_fails(self):
        x=r(2020,"AZPS",10,"AZ",2)
        with self.assertRaisesRegex(ValueError,"Duplicated"):
            audit([x,x])
    def test_negative_count_fails(self):
        with self.assertRaisesRegex(ValueError,"Negative"):
            audit([r(2020,"AZPS",10,"AZ",-1)])
if __name__=="__main__":unittest.main()
