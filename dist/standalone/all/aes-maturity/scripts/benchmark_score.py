#!/usr/bin/env python3
"""Offline, auditable generic capability-reference assessment. No network or CI access."""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import sys

BASE=Path(__file__).resolve().parents[1]
RUBRIC=BASE/'references/comparator-rubric.json'
SHA=re.compile(r'^[a-f0-9]{40}$')
CI=re.compile(r'(?:^|/)\.github/workflows(?:/|$)|(?:^|/)actions/runs(?:/|$)|(?:^|/)check-runs(?:/|$)',re.I)
EXPECTED={'research_workflow':9,'agent_runtime':10,'extension_design':9}

class BenchmarkError(ValueError):
    pass

def require(c,msg):
    if not c: raise BenchmarkError(msg)

def dec(n):
    require(type(n) in (int,float), 'score must be a number')
    x=Decimal(str(n))
    require(x.is_finite() and 0<=x<=10 and x==x.quantize(Decimal('0.1')),'score 0..10 with one decimal')
    return x

def r1(n):return str(n.quantize(Decimal('0.1'),rounding=ROUND_HALF_UP))

def fingerprint(rubric):
    core={'scale_id':rubric['scale_id'],'axes':[(a['id'], [(c['id'],c['weight']) for c in a['criteria']]) for a in rubric['axes']]}
    return hashlib.sha256(json.dumps(core,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def load_rubric(path=RUBRIC):
    r=json.loads(Path(path).read_text(encoding='utf8'))
    require(r.get('schema_version')==1 and r.get('scale_id')=='aes-generic-capability-reference-v1','unsupported comparator rubric')
    require({a['id'] for a in r['axes']}==set(EXPECTED) and len(r['axes'])==3,'exactly three independent reference axes required')
    ids=set()
    for a in r['axes']:
        cs=a['criteria']
        require(len(cs)==EXPECTED[a['id']] and sum(x['weight'] for x in cs)==100,a['id']+' weights or criteria invalid')
        ref=a['reference']
        require(ref.get('kind')=='generic_design_rubric' and ref.get('scope'),'generic reference scope required')
        for c in cs:
            k=c['id']
            require(k not in ids and k.startswith({'research_workflow':'research.','agent_runtime':'runtime.','extension_design':'extension.'}[a['id']]),'invalid/duplicate criterion id')
            ids.add(k)
            require(type(c['weight']) is int and c['weight']>0,'weight invalid')
            require(c['task_relevance'] in r['gap_relevance'] and c['cost'] in r['effort_order'],'impact or effort invalid')
    require(len(ids)==28,'28 benchmark criteria expected')
    return r

def checked_sources(sources,name):
    require(isinstance(sources,list) and sources, name+': evidence references required')
    for s in sources:
        require(isinstance(s,str) and s.strip() and not CI.search(s),name+': missing or CI evidence forbidden')
        require(s.startswith('https://') or (not Path(s).is_absolute() and '..' not in Path(s).parts and not re.match(r'^[A-Za-z]:',s) and '\\' not in s), name+': invalid evidence locator')

def evaluate(assessment,rubric=None):
    rubric=rubric or load_rubric()
    require(assessment.get('schema_version')==1 and assessment.get('scale_id')==rubric['scale_id'],'assessment scale mismatch')
    require(bool(SHA.fullmatch(assessment.get('source_commit',''))),'full source SHA required')
    require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}',assessment.get('reviewed_at',''))),'reviewed_at required')
    metrics={c['id']:c for a in rubric['axes'] for c in a['criteria']}
    ratings=assessment.get('ratings')
    require(isinstance(ratings,dict) and set(ratings)==set(metrics),'assessment must explicitly cover all 28 criteria')
    rows={}; stages=rubric['proof_maturity_points']
    for key,metric in metrics.items():
        a=ratings[key]
        require(isinstance(a,dict),'invalid rating')
        score=dec(a.get('score'))
        level=a.get('proof_level')
        require(level in stages,'unknown proof level: '+key)
        for fld in ('rationale','limitation','action'):
            require(isinstance(a.get(fld),str) and len(a[fld].strip())>=12,key+': '+fld+' required')
        require(a.get('cost') in rubric['effort_order'],key+': invalid cost')
        checked_sources(a.get('evidence'),key)
        require(not (level=='design' and score>Decimal('3.9')),key+': design-only capability ceiling')
        require(not (level=='implemented' and score>Decimal('8.0')),key+': code-only capability needs more proof')
        rows[key]={**metric, 'score':score,'proof_level':level,'proof_maturity':dec(stages[level]),'rationale':a['rationale'],'limitation':a['limitation'],'action':a['action'],'cost':a['cost'],'evidence':a['evidence']}
    result=[]
    for axis in rubric['axes']:
        cs=[rows[c['id']] for c in axis['criteria']]
        cap=sum((c['score']*c['weight'] for c in cs),Decimal(0))/100
        proof=sum((c['proof_maturity']*c['weight'] for c in cs),Decimal(0))/100
        result.append(dict(id=axis['id'],title=axis['title'],reference=axis['reference'],scope=axis['description'],capability=r1(cap),evidence_maturity=r1(proof),criteria=cs))
    priority=[]
    for a in result:
        for c in a['criteria']:
            # Gap severity only for prioritization, not used to change scores or benchmark weights
            impact={'high':3,'medium':2,'low':1}[c['task_relevance']]
            effort={'S':3,'M':2,'L':1}[c['cost']]
            order=(Decimal(10)-c['score'])*impact*effort
            priority.append(dict(id=c['id'],axis=a['id'],title=c['title'],score=str(c['score']),potential=r1(order),impact=c['task_relevance'],effort=c['cost'],gap=c['limitation'],action=c['action']))
    priority.sort(key=lambda k:(-Decimal(k['potential']),k['id']))
    return dict(source_commit=assessment['source_commit'],reviewed_at=assessment['reviewed_at'],assessment_id=assessment.get('assessment_id'),scale_id=rubric['scale_id'],scale_fingerprint=fingerprint(rubric),kind=assessment.get('kind','evaluation'),axes=result,task_gap_ranking=[p for p in priority if p['impact']=='high'],reference_policy='Generic reference scale, not a competitor score or measured task success rate.',maturity_policy='Evidence maturity is a separate rubric-stage weighted score; not deployment qualification. Low maturity does not automatically create a development P0.',not_now=assessment.get('not_now',[]))

def compare(now,prev):
    require(now['scale_id']==prev['scale_id'] and now['scale_fingerprint']==prev['scale_fingerprint'],'cannot compare different benchmark scale/weights')
    require(now['source_commit']!=prev['source_commit'],'comparison must use a new source revision')
    return {a['id']:{'prior':b['capability'],'current':a['capability'],'delta':r1(Decimal(a['capability'])-Decimal(b['capability']))} for a,b in zip(now['axes'],prev['axes'])}

def md(res):
    lines=[f"# Generic capability assessment ({res['reviewed_at']})",'',f"Revision: `{res['source_commit']}`; scale: `{res['scale_id']}`",'', 'Independent axes; no competitor measurement, overall average or deployment approval.', '', '| Axis | Capability | Evidence maturity |', '|---|---:|---:|']
    for axis in res['axes']:
        lines.append(f"| {axis['title']} | {axis['capability']} | {axis['evidence_maturity']} |")
        for c in axis['criteria']:
            lines.append(f"- {c['title']}: {c['score']} ({c['proof_level']}); limits: {c['limitation']}; next: {c['action']}")
    return '\n'.join(lines)+'\n'

def clean(o):
    if isinstance(o,Decimal):return str(o)
    if isinstance(o,dict):return {k:clean(v) for k,v in o.items()}
    if isinstance(o,list):return [clean(v) for v in o]
    return o

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--assessment',required=True,type=Path);ap.add_argument('--previous',type=Path);ap.add_argument('--format',choices=['json','markdown'],default='markdown');ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    try:
        rub=load_rubric();cur=evaluate(json.loads(args.assessment.read_text(encoding='utf8')),rub)
        if args.previous:
            prev=evaluate(json.loads(args.previous.read_text(encoding='utf8')),rub)
            cur['comparison']=compare(cur,prev)
        result=json.dumps(clean(cur),ensure_ascii=False,indent=2)+'\n' if args.format=='json' else md(cur)
        if args.output:args.output.write_text(result,encoding='utf8')
        else:print(result)
    except (OSError,ValueError,KeyError,TypeError) as e:
        print('benchmark-score: '+str(e),file=sys.stderr);return 2
    return 0

if __name__=='__main__':sys.exit(main())

