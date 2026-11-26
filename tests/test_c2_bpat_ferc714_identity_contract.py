import unittest
from scripts.c2_bpat_ferc714_identity_contract import assess

class TestIdentity(unittest.TestCase):
    def setUp(self):
        self.c={'respondent_id_ferc714':123,'respondent_name_ferc714':'Bonneville Power Administration','eia_code':542}
        self.r={'respondent_id_ferc714':123,'eia_numeric_id':542,'balancing_authority_code_eia':'BPAT',
                'independently_reviewed':True,'evidence_url':'https://example.org/actual-source','evidence_date':'2026-11-25'}
    def test_reviewed_link_keeps_scientific_gate_closed(self):
        x=assess(self.c,self.r);self.assertFalse(x['model_training_permitted']);self.assertFalse(x['underlying_evidence_independently_authenticated_by_code'])
    def test_textual_eia_code_rejected(self):
        self.c['eia_code']='BPAT'
        with self.assertRaisesRegex(ValueError,'numeric'):assess(self.c,self.r)
    def test_wrong_eia_id_rejected(self):
        self.r['eia_numeric_id']=543
        with self.assertRaisesRegex(ValueError,'numeric ID'):assess(self.c,self.r)
    def test_wrong_ba_rejected(self):
        self.r['balancing_authority_code_eia']='CISO'
        with self.assertRaisesRegex(ValueError,'BPAT'):assess(self.c,self.r)
    def test_unreviewed_rejected(self):
        self.r['independently_reviewed']=False
        with self.assertRaisesRegex(ValueError,'independently'):assess(self.c,self.r)
    def test_missing_evidence_rejected(self):
        self.r['evidence_url']=''
        with self.assertRaisesRegex(ValueError,'URL'):assess(self.c,self.r)
    def test_wrong_respondent_rejected(self):
        self.r['respondent_id_ferc714']=999
        with self.assertRaisesRegex(ValueError,'respondent'):assess(self.c,self.r)
    def test_alias_name_required(self):
        self.c['respondent_name_ferc714']='Another Utility'
        with self.assertRaisesRegex(ValueError,'name'):assess(self.c,self.r)

if __name__=='__main__':unittest.main()
