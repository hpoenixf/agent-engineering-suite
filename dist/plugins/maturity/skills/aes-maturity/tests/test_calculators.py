"""Synthetic portability and arithmetic checks; no real project assessment."""
import copy
import importlib.util
from pathlib import Path
import unittest
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
S=module('strategic_score'); B=module('benchmark_score'); G=module('goal_score')
R=S.load(S.RUBRIC)
def fixture():
 axes=R['technology_pillars']+[R['business_value_companion']]
 return {'scale_id':R['scale_id'],'source_ref':'example/project@test','source_commit':'a'*40,'review_status':'strategic_candidate_unlocked','scores':{a['id']:{'criteria':{c['id']:'2.0' for c in a['criteria']}} for a in axes},'technology':{'score':'2.0','raw':'2','weights':{'deep_async':45,'subagent':30,'data_trust':25}},'business_value':{'included_in_technology_total':False,'independent_score':'2.0'}}
class Calculators(unittest.TestCase):
 def test_preserved_dimensions(self):
  self.assertEqual(sum(len(x['criteria']) for x in B.load_rubric()['axes']),28)
  self.assertEqual(S.compute(R,fixture())['criteria_count'],16)
  self.assertIsInstance(G.rubric_load(),dict)
 def test_independent_business(self):
  a=fixture();a['scores']['user_value']['criteria']={k:'8.0' for k in a['scores']['user_value']['criteria']};a['business_value']['independent_score']='8.0'
  r=S.compute(R,a);self.assertEqual(r['technology']['total'],'2.0');self.assertEqual(r['business_value']['score'],'8.0')
 def test_half_up(self):self.assertEqual(S.rounded(Decimal('5.65')),Decimal('5.7'))
 def test_weight_changes_rejected(self):
  r=copy.deepcopy(R);r['technology_pillars'][0]['weight']=44
  with self.assertRaises(S.ScoreError):S.compute(r,fixture())
 def test_missing_evidence_not_qualified(self):
  with self.assertRaises(S.ScoreError):S.compute(R,fixture(),True)
 def test_missing_criterion_rejected(self):
  a=fixture();a['scores']['deep_async']['criteria'].pop(next(iter(a['scores']['deep_async']['criteria'])))
  with self.assertRaises(S.ScoreError):S.compute(R,a)
 def test_wrong_total_and_nonfinite_rejected(self):
  a=fixture();a['technology']['score']='3'
  with self.assertRaises(S.ScoreError):S.compute(R,a)
  with self.assertRaises(S.ScoreError):S.number('NaN','score')
 def test_duplicate_json_and_foreign_scope(self):
  with self.assertRaises(S.ScoreError):S.unique_pairs([('x',1),('x',2)])
  a=fixture();a['source_ref']=''
  with self.assertRaises(S.ScoreError):S.compute(R,a)

L=module('review_lock')
class ReviewGuards(unittest.TestCase):
 def pair(self):
  old={'scale_id':'synthetic','scale_fingerprint':'fixed','reviewed_at':'2026-01-01','source_commit':'a'*40,'goals':[{'criteria':[{'id':f'g.c{i}','score':'2.0','stage':'code','weight':1,'evidence':[]} for i in range(24)]}]}
  return old,copy.deepcopy(old)
 def test_unchanged_has_no_product_credit(self):
  a,b=self.pair();raw={'calibration_policy':L.POLICY};r=L.validate_changes(a,b,raw,raw,[],'goals');self.assertEqual(r['status'],'unchanged');self.assertEqual(r['product_delta'],{})
 def test_item_change_requires_exact_ledger(self):
  a,b=self.pair();b['goals'][0]['criteria'][0]['score']='3.0'
  with self.assertRaises(L.ReviewLockError):L.validate_changes(a,b,{}, {},[],'goals')
 def test_scale_change_not_comparable(self):
  a,b=self.pair();b['scale_fingerprint']='different'
  with self.assertRaises(L.ReviewLockError):L.validate_changes(a,b,{}, {},[],'goals')
 def test_same_source_cannot_be_product_change(self):
  a,b=self.pair();b['goals'][0]['criteria'][0]['score']='3.0';change={'criterion_id':'g.c0','kind':'product_change','reason':'Synthetic rationale with sufficient detail for this test case.','scope':'Synthetic scope only','limitations':'No real observations'}
  with self.assertRaisesRegex(L.ReviewLockError,'same SHA'):L.validate_changes(a,b,{}, {},[change],'goals')
 def test_private_prior_baseline_not_implicit(self):
  with self.assertRaisesRegex(L.ReviewLockError,'previous benchmark assessment required'):L.review(None,{'ratings':{}},None,None,None)


class GenericPublicProfiles(unittest.TestCase):
 def test_no_embedded_private_mappings(self):
  import json
  for name in ['three-goal-rubric.json','comparator-rubric.json','strategic-focus-rubric.json']:
   raw=(ROOT/'references'/name).read_text();r=json.loads(raw)
   self.assertTrue(r['scale_id'].startswith('aes-generic-'))
   for marker in ['default_gap_owner','example_evidence','roadmap_targets','agent-app/','openspec/changes/','doc/','/Users/','etf-agent','I01/','A03/']:
    self.assertNotIn(marker,raw)
 def test_generic_reference_and_evidence_locators(self):
  B.checked_sources(['evidence/synthetic-case.json'],'synthetic')
  for locator in ['../private','/absolute','C:\\private']:
   with self.assertRaises(B.BenchmarkError):B.checked_sources([locator],'synthetic')
 def test_synthetic_benchmark_not_a_real_rating(self):
  r=B.load_rubric();ratings={c['id']:{'score':2.0,'proof_level':'design','rationale':'Synthetic fixture only, not a real assessment','limitation':'No system execution occurred in this fixture','action':'Replace fixture with independently observed evidence','cost':'S','evidence':['examples/synthetic.json']} for a in r['axes'] for c in a['criteria']}
  a={'schema_version':1,'scale_id':r['scale_id'],'source_commit':'a'*40,'reviewed_at':'2026-01-01','ratings':ratings}
  result=B.evaluate(a,r);self.assertEqual([x['capability'] for x in result['axes']],['2.0']*3)
  ratings[next(iter(ratings))]['evidence']=[]
  with self.assertRaises(B.BenchmarkError):B.evaluate(a,r)

if __name__=='__main__':unittest.main()
