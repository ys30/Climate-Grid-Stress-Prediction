import unittest
from src.c2_e1_real_BA_county_proxy_vs_utility_links import analyze

BAS=("AZPS","BPAT","CISO","SRP")
def county(y,ba,f):
    return {"year":str(y),"eia930_BA_code":ba,"county_id_fips":f,
      "model_ready":"False","historically_approved_BA_polygon":"False"}
def utility(y,ba,u,st,n=1,c=0):
    return {"year":str(y),"BA":ba,"utility_id_eia":str(u),"state":st,
      "utility_counties_reported":str(n),"other_state_counties_excluded":str(c)}

class GeographySourceGateTests(unittest.TestCase):
    def fixtures(self):
        c=[];u=[]
        for y in range(2020,2026):
            for ba in BAS:
                for i in range({"AZPS":15,"BPAT":109,"CISO":58,"SRP":3}[ba]):
                    f=f"{i+1:05d}" if ba not in ("AZPS","SRP") else f"{i+100:05d}"
                    # Distinct BPAT/CISO keys for all non-AZ BA
                    if ba=="BPAT":f=f"{i+200:05d}"
                    if ba=="CISO":f=f"{i+400:05d}"
                    c.append(county(y,ba,f))
                u.append(utility(y,ba,1000+len(u),ba,1))
        # 1110 source FIPS rows, 1418 utility rows expected fail closed
        return c,u
    def test_reject_incomplete_utility_bridge(self):
        c,u=self.fixtures()
        with self.assertRaisesRegex(ValueError,"utility bridge count"):
            analyze(c,u)
    def test_reject_claimed_BA_approval(self):
        c,u=self.fixtures()
        c[0]["model_ready"]="True"
        with self.assertRaisesRegex(ValueError,"claims approval"):
            analyze(c,u)
    def test_reject_bad_fips(self):
        c,u=self.fixtures()
        c[0]["county_id_fips"]="invalid"
        with self.assertRaisesRegex(ValueError,"Invalid source"):
            analyze(c,u)
if __name__=="__main__":unittest.main()
