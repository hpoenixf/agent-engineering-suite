#!/usr/bin/env python3
"""Deterministic, offline 16-item strategic focus scorecard. No network or live-model access.

This generic adaptation uses new scale identities. It validates a separate
45/30/25 engineering focus score and independent self-use business capability score.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
RUBRIC=ROOT/'references/strategic-focus-rubric.json'
ONE=Decimal('0.1')
SHA=re.compile(r'^[0-9a-f]{40}$')
REVIEW_STATUSES={'strategic_candidate_unlocked','strategic_partial_candidate','strategic_locked'}
EVIDENCE_STATUSES={'advanced','retained','changed_unknown','regressed'}
CONFIDENCES={'high','medium','low'}

class ScoreError(ValueError):
    pass

def require(check,message):
    if not check: raise ScoreError(message)

def unique_pairs(pairs):
    result={}
    for k,v in pairs:
        require(k not in result,f'duplicate JSON key: {k}')
        result[k]=v
    return result

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=unique_pairs)

def number(value, field):
    require(isinstance(value,(str,int,float)) and not isinstance(value,bool),f'{field} must be numeric')
    try: n=Decimal(str(value))
    except (InvalidOperation,ValueError): raise ScoreError(f'{field} invalid number')
    require(n.is_finite() and 0<=n<=10,f'{field} outside 0..10')
    require(n==n.quantize(ONE),f'{field} must have one decimal precision')
    return n

def rounded(value):return value.quantize(ONE,rounding=ROUND_HALF_UP)

def exact_keys(d,ids,label):
    require(isinstance(d,dict),f'{label} must be object')
    require(set(d)==set(ids),f'{label} missing={sorted(set(ids)-set(d))} extra={sorted(set(d)-set(ids))}')

def axes_for(rubric):
    require(rubric.get('scale_id')=='aes-generic-strategic-v1','wrong rubric scale')
    axes=rubric['technology_pillars']
    require([a['id'] for a in axes]==['deep_async','subagent','data_trust'],'technology pillar order changed')
    require([a['weight'] for a in axes]==[45,30,25],'strategic weight contract changed')
    business=rubric['business_value_companion']
    require(business['id']=='user_value' and business['included_in_technical_total'] is False,'business must remain independent')
    all_axes=axes+[business]
    ids=[]
    for a in all_axes:
        c=a['criteria']
        require(len(c)==4 and sum(x['weight'] for x in c)==100,f"{a['id']} criteria weights invalid")
        require(all(type(x['weight']) is int and x['weight']>0 for x in c),f"{a['id']} invalid integer weights")
        require(all(x['id'].startswith(a['id']+'.') for x in c),f"{a['id']} foreign criterion id")
        ids.extend(x['id'] for x in c)
    require(len(ids)==16 and len(set(ids))==16,'require exactly 16 unique criteria')
    return axes,business

def compute(rubric, assessment,strict_evidence=False):
    axes,business=axes_for(rubric)
    require(assessment.get('scale_id')==rubric['scale_id'],'assessment/rubric scale mismatch')
    require(isinstance(assessment.get('source_ref'),str) and bool(assessment['source_ref'].strip()),'must identify assessed repository')
    require(bool(SHA.fullmatch(assessment.get('source_commit',''))),'source_commit not 40 hex')
    require(assessment.get('review_status') in REVIEW_STATUSES,'invalid review status')
    declared=assessment.get('scores')
    exact_keys(declared,[a['id'] for a in axes]+[business['id']],'scores')
    raw,display,weights={}, {},{}
    all_criteria={}
    for a in axes+[business]:
        key=a['id']; val=declared[key]
        ids=[c['id'] for c in a['criteria']]
        exact_keys(val['criteria'],ids,f'{key} criteria')
        for c in a['criteria']:
            all_criteria[c['id']]=(key,c['weight'])
        num=sum(number(val['criteria'][c['id']],c['id'])*Decimal(c['weight']) for c in a['criteria'])/Decimal(100)
        raw[key]=num;display[key]=rounded(num)
        require('score' not in val or Decimal(str(val['score']))==display[key],f'{key} cached score mismatch')
        require('raw' not in val or Decimal(str(val['raw']))==num,f'{key} cached raw mismatch')
        weights[key]=a.get('weight')
    tech=sum(raw[a['id']]*Decimal(a['weight']) for a in axes)/Decimal(100)
    require(Decimal(str(assessment['technology']['score']))==rounded(tech),'cached technical total score mismatch')
    require(Decimal(str(assessment['technology']['raw']))==tech,'cached technical raw mismatch')
    exact_keys(assessment['technology']['weights'],[a['id'] for a in axes],'technology weights')
    require(all(assessment['technology']['weights'][a['id']]==a['weight'] for a in axes),'technology stored weights mismatch')
    require(assessment['business_value']['included_in_technology_total'] is False,'business value has been mixed into technical total')
    require(Decimal(str(assessment['business_value']['independent_score']))==display[business['id']],'business stored score mismatch')
    if strict_evidence:
        details=assessment.get('criteria_evidence')
        exact_keys(details,list(all_criteria),'criteria_evidence')
        for criterion,(pillar,weight) in all_criteria.items():
            row=details[criterion]
            require(row.get('criterion_id')==criterion,criterion+' id mismatch')
            require(row.get('weight')==weight,criterion+' weight mismatch')
            require(row.get('score')==declared[pillar]['criteria'][criterion],criterion+' score mismatch')
            require(row.get('evidence_status') in EVIDENCE_STATUSES,criterion+' evidence_status missing')
            require(row.get('confidence') in CONFIDENCES,criterion+' confidence missing')
            require(row.get('source_sha')==assessment['source_commit'],criterion+' wrong reviewed source')
            require(isinstance(row.get('owner_link'),str) and (row['owner_link'].startswith('https://') or (not row['owner_link'].startswith('/') and '..' not in Path(row['owner_link']).parts)),criterion+' owner link missing')
            require(isinstance(row.get('rationale'),str) and len(row['rationale'])>=30,criterion+' rationale too short')
            require(isinstance(row.get('limitation'),str) and len(row['limitation'])>=12,criterion+' limitation too short')
            require(row.get('actual_execution_sha')=='unknown' or bool(SHA.fullmatch(str(row.get('actual_execution_sha','')))),criterion+' invalid actual execution SHA')
        require(assessment.get('task_success_rate')=='unknown' or isinstance(assessment['task_success_rate'],dict),'task success rate must be unknown or full cohort')
        require(assessment.get('domain_regulatory_review') in ('not_reviewed','reviewed_with_scope'),'regulatory review must be separate')
    return {
        'scale_id':rubric['scale_id'],
        'source_commit':assessment['source_commit'],
        'review_status':assessment['review_status'],
        'technology':{'scores':{k:str(display[k]) for k in (a['id'] for a in axes)},'total':str(rounded(tech)),'raw':str(tech),'weights':{a['id']:a['weight'] for a in axes}},
        'business_value':{'score':str(display[business['id']]),'included_in_technology_total':False},
        'criteria_count':len(all_criteria),
        'strict_evidence_validated':strict_evidence,
        'task_success_rate':assessment.get('task_success_rate','unknown'),
        'domain_regulatory_review':assessment.get('domain_regulatory_review','not_reviewed'),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assessment',type=Path,required=True)
    p.add_argument('--rubric',type=Path,default=RUBRIC)
    p.add_argument('--strict-evidence',action='store_true')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    try: result=compute(load(args.rubric),load(args.assessment),args.strict_evidence)
    except (ScoreError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(f'STRATEGIC_SCORE_INVALID: {exc}',file=sys.stderr);return 2
    body=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(body,encoding='utf-8')
    print(body,end='')
    return 0

if __name__=='__main__':sys.exit(main())

