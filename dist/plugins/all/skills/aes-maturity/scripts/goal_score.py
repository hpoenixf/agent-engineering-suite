#!/usr/bin/env python3
"""Offline three-goal scoring, v2: scoped evidence, honest denominators and versioned baselines."""
from __future__ import annotations
import argparse
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / 'references/three-goal-rubric.json'
SHA = re.compile(r'^[a-f0-9]{40}$')
HASH = re.compile(r'^[a-f0-9]{64}$')
FORBIDDEN = re.compile(r'(?:^|/)\.github/workflows(?:/|$)|/actions(?:/|$)|/check-runs(?:/|$)|/check-suites(?:/|$)|/commits/[^/]+/(?:status|statuses)(?:[/?]|$)|(?:^|/)ci[-_]?logs?/', re.I)
STATES = {'pass','partial','failed','blocked','not_run','unknown'}
PRODUCT_STAGES = ('implemented','generated','saved','accessible','opened','output_quality','user_accepted','repeatability')
CONFIDENCE = {'low','medium','high','unverified'}
OUTCOMES = ('unassisted','assisted_completed','partial','failed','unknown','user_cancelled')
EVIDENCE_LEVELS = {'design','source','offline','system_integration','real_model','actual_artifact','human_review','longitudinal','regulatory_review','independent_review'}
STRONG = {'system_integration','real_model','actual_artifact','human_review','longitudinal','independent_review'}
APPLICABILITY = {'current_source','unchanged_relevant_code','historical_scope','changed_not_retested','unknown'}

class ScoreError(ValueError):
    """Malformed assessment, never a judgment about the assessed product."""


def require(condition, message):
    if not condition:
        raise ScoreError(message)


def text(value, field, minimum=1):
    require(isinstance(value,str) and len(value.strip()) >= minimum, field + ': nonempty text required')
    return value


def valid_date(value, field):
    text(value,field)
    try:
        parsed=date.fromisoformat(value)
    except ValueError as exc:
        raise ScoreError(field + ': valid YYYY-MM-DD required') from exc
    require(parsed.isoformat()==value,field + ': ISO calendar date required')
    return parsed


def score_number(value):
    require(type(value) in (int,float), 'score: numeric value required (not bool)')
    try:
        number=Decimal(str(value))
        require(number.is_finite() and Decimal(0)<=number<=Decimal(10), 'score: finite 0..10 required')
        require(number==number.quantize(Decimal('0.1')), 'score: at most one decimal')
    except InvalidOperation as exc:
        raise ScoreError('score: invalid decimal') from exc
    return number


def rounded(value):
    return str(value.quantize(Decimal('0.1'),rounding=ROUND_HALF_UP))


def rubric_load(path=RUBRIC):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    require(data.get('schema_version')==2, 'rubric: schema 2 required')
    expected={'production_agent','data_controls','user_value'}
    goals=data.get('goals',[])
    require(len(goals)==3 and {g.get('id') for g in goals}==expected,'rubric: exact three goals required')
    seen=set()
    for goal in goals:
        criteria=goal.get('criteria',[])
        require(len(criteria)==8,'rubric: eight criteria per goal required')
        require(all(type(c.get('weight')) is int and 0<c['weight']<=100 for c in criteria),'rubric: positive integer weights required')
        require(sum(c['weight'] for c in criteria)==100,'rubric: weights must total 100')
        for c in criteria:
            require(c['id'].startswith(goal['id']+'.') and c['id'] not in seen,'rubric: invalid/duplicate criterion')
            seen.add(c['id']);text(c.get('proof'),'rubric proof')
    return data


def scale_fingerprint(rubric):
    """Meaning/version + weights, not the evaluated application's version."""
    shape={'scale_id':rubric['scale_id'],'criteria':[(c['id'],c['weight']) for g in rubric['goals'] for c in g['criteria']]}
    return hashlib.sha256(json.dumps(shape,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def evidence_index(data, reviewed_at):
    items=data.get('evidence',[])
    require(isinstance(items,list),'evidence: array required')
    index={}
    for item in items:
        require(isinstance(item,dict),'evidence: object required')
        eid=text(item.get('id'),'evidence id')
        require(eid not in index,'evidence: duplicate ID')
        path=text(item.get('path'),eid+' path')
        require(not FORBIDDEN.search(unquote(path)),eid+': CI/Actions evidence forbidden')
        require(not path.startswith(('/mnt/','/home/','.work/')) and '..' not in Path(path).parts,eid+': safe repository/public evidence path required')
        observed=valid_date(item.get('observed_at'),eid+' observed_at')
        require(observed<=reviewed_at,eid+': future observation forbidden')
        origin=item.get('origin','repository')
        require(origin in ('repository','external'),eid+': origin invalid')
        if origin=='repository':
            require(SHA.fullmatch(str(item.get('record_revision',''))) is not None,eid+': full record_revision required')
        else:
            require(path.startswith('https://'),eid+': external HTTPS reference required')
        # The version containing the ledger is NOT the version that executed the test.
        version=item.get('observed_version')
        require(isinstance(version,dict),eid+': observed_version required separately from record_revision')
        for field in ('commit','source_tree'):
            val=version.get(field)
            require(val is None or SHA.fullmatch(str(val)) is not None,eid+': invalid observed '+field)
        text(version.get('note'),eid+' observed-version note')
        app=item.get('applicability',{})
        require(app.get('status') in APPLICABILITY,eid+': applicability required')
        text(app.get('basis'),eid+' applicability basis')
        require(item.get('level') in EVIDENCE_LEVELS,eid+': invalid level')
        require(item.get('outcome') in STATES,eid+': invalid outcome')
        text(item.get('scope'),eid+' scope');text(item.get('limitations'),eid+' limitations')
        require(isinstance(item.get('supports'),list) and item['supports'],eid+': explicit supports required')
        require(isinstance(item.get('methods'),list),eid+': methods array required')
        if item.get('artifact_hash') is not None:
            require(HASH.fullmatch(item['artifact_hash']) is not None,eid+': invalid artifact hash')
        index[eid]=item
    return index


def references(ids,index,target,required=True):
    require(isinstance(ids,list),target+': evidence IDs array required')
    if required: require(bool(ids),target+': evidence required')
    require(len(ids)==len(set(ids)),target+': duplicate evidence reference')
    result=[]
    for eid in ids:
        require(eid in index,target+': unknown evidence '+str(eid))
        item=index[eid]
        require(target in item['supports'],target+': evidence does not support this target')
        result.append(item)
    return result


def validate_cohort(cohort,index):
    if cohort is None:return None
    require(isinstance(cohort,dict),'cohort: object or null required')
    require(cohort.get('kind') in ('personal_live','model_diagnostic','synthetic'),'cohort: kind required')
    for key in ('scope','window','sampling','case_id_policy'):
        text(cohort.get(key),'cohort '+key)
    require(type(cohort.get('total')) is int and cohort['total']>=0,'cohort: nonnegative total required')
    for key in OUTCOMES:
        require(type(cohort.get(key)) is int and cohort[key]>=0,'cohort: nonnegative '+key+' required')
    require(sum(cohort[k] for k in OUTCOMES)==cohort['total'],'cohort: every outcome including assisted/cancelled must equal total')
    refs=references(cohort.get('evidence',[]),index,'user_task_cohort',cohort['total']>0)
    if cohort['kind']=='personal_live':
        require(any('personal_live' in e['methods'] for e in refs) or cohort['total']==0,'cohort: personal-live evidence required')
    result={**cohort,'raw':f"{cohort['unassisted']}/{cohort['total']}",'generalizable':False,'rate':None}
    # n>=20 permits only a DESCRIPTIVE personal-live sample rate, never extrapolation.
    if cohort['kind']=='personal_live' and cohort['total']>=20:
        result['rate']=rounded(Decimal(100)*cohort['unassisted']/cohort['total'])+'%'
    result['rate_scope']='observed cohort only; sample size alone never establishes SLO, representativeness or long-term reliability'
    return result


def validate_products(products,index):
    require(isinstance(products,list),'products: array required')
    seen=set()
    for p in products:
        require(isinstance(p,dict),'product: object required')
        pid=text(p.get('id'),'product id');require(pid not in seen,'product: duplicate ID');seen.add(pid)
        text(p.get('title'),pid+' title');text(p.get('limitations'),pid+' limitations')
        require(set(p.get('stages',{}))==set(PRODUCT_STAGES),'product: eight stages required')
        stage_evidence=p.get('stage_evidence',{})
        require(isinstance(stage_evidence,dict),'product stage_evidence required')
        for stage,state in p['stages'].items():
            require(state in STATES,'product: invalid outcome')
            refs=references(stage_evidence.get(stage,[]),index,f'product:{pid}:{stage}',state not in ('not_run','unknown'))
            if state!='pass':continue
            passing=[e for e in refs if e['outcome']=='pass']
            require(bool(passing),pid+': pass needs positive stage evidence')
            if stage=='implemented':
                require(any(e['level']!='design' for e in passing),pid+': design alone cannot prove implemented')
            elif stage in ('generated','saved','accessible'):
                require(any(e['level'] not in ('design','source') for e in passing),pid+': code alone cannot prove artifact effect')
            elif stage=='opened':
                require(any('real_browser' in e['methods'] or 'user_opened' in e['methods'] for e in passing),pid+': opened requires actual browser/user observation')
            elif stage=='output_quality':
                require(any('independent_output_review' in e['methods'] for e in passing),pid+': output quality requires independent review')
            elif stage=='user_accepted':
                require(any('user_acceptance' in e['methods'] for e in passing),pid+': user acceptance cannot be inferred from file creation')
            elif stage=='repeatability':
                require(any(e['level']=='longitudinal' and 'independent_tasks' in e['methods'] for e in passing),pid+': same-Run replay cannot prove repeatability')
    return products


def evaluate(data,rubric=None):
    rubric=rubric or rubric_load()
    require(data.get('schema_version')==2,'assessment: schema 2 required; migrate v1 provenance and task denominator explicitly')
    require(data.get('scale_id')==rubric['scale_id'],'assessment: scale_id mismatch')
    text(data.get('assessment_id'),'assessment_id')
    require(SHA.fullmatch(str(data.get('source_commit',''))) is not None,'assessment: full source_commit required')
    reviewed=valid_date(data.get('reviewed_at'),'reviewed_at')
    scope=data.get('scope',{})
    for f in ('environment','activity','not_claimed'):text(scope.get(f),'scope '+f)
    index=evidence_index(data,reviewed)
    fields=data.get('goal_scores',{})
    require(isinstance(fields,dict),'goal_scores: object required')
    all_ids={c['id'] for g in rubric['goals'] for c in g['criteria']}
    require(not set(fields)-all_ids,'unknown goal criteria')
    goals=[]
    for g in rubric['goals']:
        total=Decimal(0);unknown_weight=0;rows=[]
        for c in g['criteria']:
            item=fields.get(c['id'])
            require(item is None or isinstance(item,dict),c['id']+': invalid metric record')
            if item is None or item.get('status')=='unrated':
                if item is not None: require(item.get('score') is None,c['id']+': unrated cannot carry score')
                unknown_weight+=c['weight'];rows.append({**c,'score':None,'stage':'unrated','confidence':'unverified','rationale':item.get('rationale','证据未充分收集') if item else '证据未充分收集','evidence':[]});continue
            require(isinstance(item,dict) and item.get('status','assessed')=='assessed',c['id']+': invalid status')
            value=score_number(item.get('score'))
            require(item.get('stage') in rubric['stages'],c['id']+': stage required')
            require(item.get('confidence') in CONFIDENCE,c['id']+': confidence required')
            text(item.get('rationale'),c['id']+' rationale',15)
            text(item.get('remaining'),c['id']+' remaining')
            proof=references(item.get('evidence',[]),index,c['id'])
            if item['stage']=='spec':require(value<=3.9,c['id']+': spec-only score cannot exceed 3.9')
            if item['stage']=='code':require(value<=6.9,c['id']+': code-only score cannot exceed 6.9')
            if value>=8:
                require(any(e['outcome']=='pass' and e['level'] in STRONG for e in proof),c['id']+': >=8 requires relevant integrated/real passing evidence')
            if value>=9:
                require(any(e['outcome']=='pass' and e['level'] in ('longitudinal','independent_review','human_review','system_integration') for e in proof),c['id']+': >=9 requires independent/durable evidence')
                text(item.get('high_score_scope'),c['id']+' high_score_scope',15)
            if c['id']=='data_controls.regulatory_review' and value>=7:
                require(any(e['outcome']=='pass' and e['level']=='regulatory_review' for e in proof),'regulatory_review: applicable independent review required for >=7')
            if item['stage']=='repeated':
                require(any(e['outcome']=='pass' and e['level']=='longitudinal' and 'independent_tasks' in e['methods'] for e in proof),c['id']+': repeated requires independent tasks not replay')
            total+=value*Decimal(c['weight'])/100
            rows.append({**c,**item,'score':str(value)})
        goals.append({'id':g['id'],'title':g['title'],'score':rounded(total) if not unknown_weight else None,'covered':sum(r['score'] is not None for r in rows),'total':len(rows),'unrated_weight':unknown_weight,'possible_range_if_unrated':[rounded(total),rounded(total+Decimal(unknown_weight)/10)] if unknown_weight else None,'criteria':rows})
    products=validate_products(data.get('product_capabilities',[]),index)
    cohort=validate_cohort(data.get('user_task_cohort'),index)
    reg=data.get('regulatory_context')
    require(isinstance(reg,dict) and reg.get('status') in ('not_reviewed','scoped_review','independent_review'),'regulatory_context status required')
    require(isinstance(reg.get('jurisdictions'),list),'regulatory_context jurisdictions required')
    text(reg.get('activity'),'regulatory activity');text(reg.get('limitations'),'regulatory limitations')
    if reg['status']!='not_reviewed':
        require(bool(reg['jurisdictions']),'regulatory: reviewed jurisdiction required')
        refs=references(reg.get('evidence',[]),index,'regulatory_context')
        require(any(e['level']=='regulatory_review' and e['outcome']=='pass' for e in refs),'regulatory: review evidence required')
    findings=data.get('critical_findings',[])
    require(isinstance(findings,list),'critical_findings array required')
    for f in findings:
        text(f.get('id'),'finding id');text(f.get('description'),'finding description')
        require(f.get('status') in ('open','repaired_not_retested','verified_closed'),'finding status required')
        require(f.get('severity') in ('critical','high','medium'),'finding severity required')
        require(isinstance(f.get('goals'),list) and set(f['goals'])<= {g['id'] for g in goals},'finding goals invalid')
        references(f.get('evidence',[]),index,'finding:'+f['id'])
    claims=data.get('goal_claims',{})
    require(set(claims)=={g['id'] for g in goals},'goal_claims: three independent proof statuses required')
    for g in goals:
        claim=claims[g['id']]
        require(claim.get('status') in ('partially_demonstrated','demonstrated_in_scope','not_demonstrated'),'claim: invalid status')
        text(claim.get('scope'),'claim scope');require(isinstance(claim.get('missing'),list),'claim missing list required')
        blocking=[f['id'] for f in findings if f['status']!='verified_closed' and f['severity']=='critical' and g['id'] in f['goals']]
        if blocking:require(claim['status']!='demonstrated_in_scope','critical unresolved finding cannot be averaged into a proven claim')
        if claim['status']=='demonstrated_in_scope':
            require(g['score'] is not None,'unrated goal cannot be fully demonstrated')
            references(claim.get('evidence',[]),index,'claim:'+g['id'])
        g['proof_status']=claim;g['critical_blockers']=blocking
    priorities=data.get('priorities',[])
    require(isinstance(priorities,list),'priorities: array required')
    orders=set()
    for p in priorities:
        require(p.get('priority') in ('P0','P1','P2'),'priority level required')
        require(type(p.get('order')) is int and p['order']>0 and p['order'] not in orders,'priority: unique positive order required');orders.add(p['order'])
        require(p.get('goal') in claims,'priority: goal required')
        for f in ('owner','title','next_action','done_when','roadmap','dependencies','why_now'):text(p.get(f),'priority '+f)
        require(p.get('change') in ('new','retained','updated'),'priority change required')
        references(p.get('evidence',[]),index,'priority:'+str(p['order']))
    measurement=data.get('personal_value_measurements',{})
    require(isinstance(measurement,dict),'personal_value_measurements object required')
    return {'schema_version':2,'scale_id':rubric['scale_id'],'scale_fingerprint':scale_fingerprint(rubric),'assessment_id':data['assessment_id'],'source_commit':data['source_commit'],'reviewed_at':data['reviewed_at'],'scope':scope,'goals':goals,'products':products,'evidence':list(index.values()),'user_task_cohort':cohort,'personal_value_measurements':measurement,'regulatory_context':reg,'critical_findings':findings,'priorities':sorted(priorities,key=lambda p:(int(p['priority'][1]),p['order'])),'not_now':data.get('not_now',''), 'ci':'not_checked_by_default','comparison':{'status':'first_baseline','deltas':{}},'review_notes':data.get('review_notes',[]),'score_meaning':'Evidence-grounded capability judgment; not legal approval or measured success rate.'}


def compare(current,previous):
    if current['scale_fingerprint']!=previous['scale_fingerprint']:
        return {'status':'not_comparable_scale_change','deltas':{}}
    require(previous['reviewed_at']<=current['reviewed_at'],'previous baseline cannot be later than current')
    old={g['id']:g for g in previous['goals']}
    deltas={g['id']:(rounded(Decimal(g['score'])-Decimal(old[g['id']]['score'])) if g['score'] is not None and old[g['id']]['score'] is not None else None) for g in current['goals']}
    return {'status':'comparable','previous_assessment':previous['assessment_id'],'deltas':deltas,'note':'Separate product changes, newly collected proof, and scoring recalibration in prose.'}


def escape(value):return str(value).replace('|','\\|').replace('\n',' ')


def markdown(r):
    out=[f"# Generic three-goal assessment｜{r['reviewed_at']}",'',f"评审版本 `{r['source_commit']}`；量表 `{r['scale_id']}`；评审 ID `{r['assessment_id']}`。",'',f"范围：{r['scope']['environment']}；{r['scope']['activity']}。",f"不主张：{r['scope']['not_claimed']}。",'分数是能力成熟度判断，不是实测成功率；三目标不平均为总分。','', '| 目标 | 分数 /10 | 证据覆盖 | 目标证明状态 |','|---|---:|---:|---|']
    for g in r['goals']:
        out.append(f"| {g['title']} | {g['score'] or '未定'} | {g['covered']}/{g['total']} | {g['proof_status']['status']} |")
    for note in r.get('review_notes',[]):out+=['',note]
    out+=['',f"比较状态：`{r['comparison']['status']}`。首次三目标基线不得与旧五维7.4/9.1直接作涨跌比较。",'','## 24项评分依据']
    ev={e['id']:e for e in r['evidence']}
    for g in r['goals']:
        out+=['',f"### {g['title']}",'','| 指标 | 权重 | 分数 | 阶段/置信度 |','|---|---:|---:|---|']
        for c in g['criteria']:
            out.append(f"| {c['title']} | {c['weight']}% | {c['score'] or '未定'} | {c['stage']} / {c['confidence']} |")
        for c in g['criteria']:
            out+=['',f"**{c['title']}**：{c['rationale']} 未完成：{c.get('remaining','未采集')} 证据：{', '.join(c['evidence']) or '无'}。"]
        out+=['',f"已证明范围：{g['proof_status']['scope']}", '剩余证明：'+'；'.join(g['proof_status']['missing'])+'。']
    out+=['','## 产品里程碑（分别计证）','','| 产品 | 实现 | 生成 | 保存 | 访问/下载 | 实际打开 | 金融质量 | 用户接受 | 重复成功 |','|---|---|---|---|---|---|---|---|---|']
    for p in r['products']:
        out.append('| '+p['title']+' | '+' | '.join(p['stages'][s] for s in PRODUCT_STAGES)+' |')
    for p in r['products']:out+=['',f"**{p['title']}边界**：{p['limitations']}"]
    out+=['','## 无补位与实际省事证据']
    co=r['user_task_cohort']
    if co:
        out.append(f"{co['kind']}；{co['window']}；{co['scope']}。总计{co['total']}，无需补位{co['unassisted']}，补位后完成{co['assisted_completed']}，partial{co['partial']}，failed{co['failed']}，unknown{co['unknown']}，用户取消{co['user_cancelled']}。")
        out.append(('仅该个人样本比例：'+co['rate']) if co['rate'] else '不输出小样本或合成样本的个人稳定完成率。')
        out.append('样本数量不能自动证明可外推性或SLO。')
    else:out.append('当前未建立统一真实自用任务窗口：成功率、节省时间及每月净收益均 unknown，不按0处理，不把工程测试当用户样本。')
    for k,v in r['personal_value_measurements'].items():out.append(f"{k}：{v}")
    out+=['','## 合规与风险证明边界',f"监管核验：{r['regulatory_context']['status']}；活动：{r['regulatory_context']['activity']}；司法辖区：{', '.join(r['regulatory_context']['jurisdictions']) or '尚未界定'}。",r['regulatory_context']['limitations'],'金融控制分数不是许可、法律意见或监管认证。']
    for f in r['critical_findings']:out.append(f"- {f['id']} [{f['severity']}/{f['status']}] {f['description']}")
    out+=['','## 下一步（不执行额外测评）']
    for p in r['priorities']:
        out+=['',f"### {p['priority']}-{p['order']} {p['title']} [{p['change']}]",f"Owner `{p['owner']}`；Roadmap {p['roadmap']}。",f"原因：{p['why_now']} 前置：{p['dependencies']}",f"下一步：{p['next_action']} 验收：{p['done_when']}"]
    out+=['',f"暂不优先：{r['not_now']}",'','## 证据索引（记录版本与实际运行版本分开）']
    for e in r['evidence']:
        observed=e['observed_version'];pin=observed.get('commit') or observed.get('source_tree') or '精确运行版本unknown'
        link=f"{e['path']}?revision={e['record_revision']}" if e.get('origin','repository')=='repository' else e['path']
        out+=['',f"**{e['id']}** [{e['path']}]({link})；观察 {e['observed_at']}；{e['level']}/{e['outcome']}；运行 `{pin}`。",f"范围：{e['scope']} 限制：{e['limitations']} 对当前代码：{e['applicability']['status']}；{e['applicability']['basis']}。"]
    out+=['','本次不查CI、不运行付费模型、不改the assessed project源码；只运行插件本地计算和测试。','']
    return '\n'.join(out)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessment',type=Path,required=True)
    parser.add_argument('--previous',type=Path)
    parser.add_argument('--format',choices=('markdown','json'),default='markdown')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        result=evaluate(json.loads(args.assessment.read_text(encoding='utf-8')))
        if args.previous:result['comparison']=compare(result,evaluate(json.loads(args.previous.read_text(encoding='utf-8'))))
        output=markdown(result) if args.format=='markdown' else json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:args.output.write_text(output,encoding='utf-8')
        else:print(output,end='')
    except (ScoreError,OSError,json.JSONDecodeError,KeyError,TypeError) as exc:
        print('goal-scorecard: '+str(exc),file=sys.stderr);return 2
    return 0

if __name__=='__main__':sys.exit(main())

