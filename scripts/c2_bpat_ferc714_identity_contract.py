"""Strict source-only FERC-714 respondent to EIA BA mapping review.

A name and utility EIA numeric ID alone cannot validate a respondent as BPAT.
An externally cited, independently checked BAA link is required.
"""
import json
import re
from pathlib import Path


def assess(candidate, reviewed_link):
    required = ('respondent_id_ferc714', 'respondent_name_ferc714', 'eia_code')
    if any(key not in candidate for key in required):
        raise ValueError('Missing PUDL FERC respondent field')
    rid = candidate['respondent_id_ferc714']
    if not isinstance(rid, int) or isinstance(rid, bool) or rid <= 0:
        raise ValueError('Respondent ID must be a positive integer')
    name = str(candidate['respondent_name_ferc714'] or '').strip()
    if not re.search(r'BONNEVILLE|\bBPA\b', name, re.I):
        raise ValueError('Respondent name is not a BPA candidate')
    eid = candidate['eia_code']
    if eid is None or isinstance(eid, bool) or not str(eid).isdigit() or int(eid) <= 0:
        raise ValueError('EIA code must be a positive numeric ID, not BPAT text')
    if not isinstance(reviewed_link, dict):
        raise ValueError('Missing independent BA linkage review')
    if reviewed_link.get('respondent_id_ferc714') != rid:
        raise ValueError('Reviewed FERC respondent does not match source candidate')
    if reviewed_link.get('eia_numeric_id') != int(eid):
        raise ValueError('Reviewed EIA numeric ID does not match PUDL candidate')
    if reviewed_link.get('balancing_authority_code_eia') != 'BPAT':
        raise ValueError('Independent BA code does not match BPAT')
    if reviewed_link.get('independently_reviewed') is not True:
        raise ValueError('BA linkage not independently reviewed')
    if not isinstance(reviewed_link.get('evidence_url'), str) or not reviewed_link['evidence_url'].startswith(('https://', 'http://')):
        raise ValueError('BA linkage lacks source evidence URL')
    if not isinstance(reviewed_link.get('evidence_date'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', reviewed_link['evidence_date']):
        raise ValueError('BA linkage lacks reviewed evidence date')
    return {
        'respondent_id_ferc714': rid,
        'respondent_name_ferc714': name,
        'eia_numeric_id': int(eid),
        'balancing_authority_code_eia': 'BPAT',
        'source_linkage_review_declaration_verified': True,
        'underlying_evidence_independently_authenticated_by_code': False,
        'BPA_original_xlsx_verified': False,
        'model_training_permitted': False,
        'full_FERC_EIA_comparison_completed': False,
    }


def evaluate_files(candidate_json, review_json, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Do not overwrite identity review')
    result = assess(json.loads(Path(candidate_json).read_text()), json.loads(Path(review_json).read_text()))
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result
