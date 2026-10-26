"""Recommendation component evaluation using retained live evidence.

Uses an explicit controlled profile, now also adopted by the application.
Every fixed case is evaluated, not only failed or promising baseline cases.
"""
from pathlib import Path
import argparse,json,time,random,hashlib,copy
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
from dotenv import dotenv_values
from growth.providers import LiveAnalyst,bounded_call
from growth.usage import summarize
from .run_live import RUBRIC,Judgments,structural,discovery
from .scoring import DIMENSIONS,outcome,aggregate

def wait_for_baseline(evidence,result,seconds=1800):
    deadline=time.monotonic()+seconds
    while not (evidence.exists() and result.exists()):
        if time.monotonic()>=deadline:raise TimeoutError('Baseline pair not ready')
        time.sleep(.5)

def evaluate(case,settings,baseline,output):
    start=time.perf_counter()
    path=baseline/(case['id']+'-evidence.json')
    state={}
    analyst=LiveAnalyst(settings['OPENAI_API_KEY'],settings.get('OPENAI_MODEL') or 'gpt-6-luna')
    judge=LiveAnalyst(settings['OPENAI_API_KEY'],settings.get('OPENAI_MODEL') or 'gpt-6-luna')
    class ObservedModel:
        def __init__(self,owner):
            self.owner=owner
            self.bound=owner.model.bind(timeout=120,max_tokens=8000,reasoning_effort='low')
        def invoke(self,*args,**kwargs):
            response=self.bound.invoke(*args,**kwargs)
            self.owner.events[-1]['finish_reason']=(response.response_metadata or {}).get('finish_reason')
            return response
    analyst.model=ObservedModel(analyst)
    judge.model=ObservedModel(judge)
    result={'case':case,'draft':None,'final':None,'error_type':None,'baseline_error_type':None}
    trace=[]
    try:
        wait_for_baseline(path,baseline/(case['id']+'-result.json'))
        state=json.loads(path.read_text(encoding='utf-8'))
        base_result=json.loads((baseline/(case['id']+'-result.json')).read_text(encoding='utf-8'))
        result['baseline_error_type']=base_result.get('error_type')
        if len(state.get('profiles',[]))!=4:raise ValueError('Baseline did not produce four profiles')
        state=copy.deepcopy(state)
        state['request']['client_discovery']=discovery(case)
        supported={f['source_id'] for p in state['profiles'] for f in p['facts'].values() if f['status']=='Source-supported'}
        if not supported:raise ValueError('No grounded context')
        def accepted(analysis):
            return [h.model_dump() for h in analysis.hypotheses if h.source_ids and set(h.source_ids)<=supported]
        def accepted_takeaway(analysis):
            return analysis.takeaway.model_dump() if analysis.takeaway and set(analysis.takeaway.source_ids)<=supported else None
        draft=bounded_call(lambda:analyst.analyze(state['request'],state['profiles']),'analysis:agent',trace)
        state['draft_hypotheses']=accepted(draft)
        state['draft_takeaway']=accepted_takeaway(draft)
        state['hypotheses']=state['draft_hypotheses']
        state['strategist_takeaway']=state['draft_takeaway']
        state['review_findings']=[];state['revision_instructions']='';state['revision_count']=0
        def context():return {k:state.get(k) for k in ('request','profiles','hypotheses','strategist_takeaway','benchmarks','review_findings','revision_instructions')}
        review=bounded_call(lambda:analyst.critique(context()),'strategy:review',trace)
        state['review_findings']=review.findings;state['revision_instructions']=review.revision_instructions
        if review.revision_instructions:
            try:
                revised=bounded_call(lambda:analyst.revise(context()),'strategy:revision',trace)
                ids=[h.source_ids for h in revised.hypotheses]+([revised.takeaway.source_ids] if revised.takeaway else [])
                if not all(i and set(i)<=supported for i in ids):raise ValueError('Unsupported revision references')
                state['hypotheses']=accepted(revised);state['strategist_takeaway']=accepted_takeaway(revised);state['revision_count']=1
            except Exception as exc:
                state['evaluation_revision_warning']=type(exc).__name__
        versions=[('draft',state['draft_hypotheses'],state['draft_takeaway']),('final',state['hypotheses'],state['strategist_takeaway'])]
        random.Random(case['id']).shuffle(versions)
        ctx={'request':state['request'],'profiles':state['profiles'],'versions':{label:{'hypotheses':v[1],'takeaway':v[2]} for label,v in zip(('A','B'),versions)}}
        def strings(value):
            if isinstance(value,str):return [value]
            if isinstance(value,list):return [s for v in value for s in strings(v)]
            if isinstance(value,dict):return [s for v in value.values() for s in strings(v)]
            return []
        def judging():
            pair=judge._json(Judgments,RUBRIC,ctx)
            if {v.label for v in pair.versions}!={'A','B'}:raise ValueError('Missing version')
            for v in pair.versions:
                text='\n'.join(strings(ctx['versions'][v.label]))
                if any(f.recommendation_quote not in text for f in v.critical_flags):raise ValueError('Unsupported judge quote')
            return pair
        pair=bounded_call(judging,'evaluation:judge',trace)
        for v in pair.versions:
            name,hypotheses,_=versions[0 if v.label=='A' else 1]
            result[name]={**outcome([getattr(v,k).score for k in DIMENSIONS],[f.model_dump() for f in v.critical_flags],structural(state,hypotheses)),
                          'rubric_notes':{k:getattr(v,k).reason for k in DIMENSIONS},'strength':v.strength,'gap':v.gap}
        result['revision_count']=state['revision_count']
        result['supported_fields']=sum(f['status']=='Source-supported' for p in state['profiles'] for f in p['facts'].values())
        result['evidence_sha256']=hashlib.sha256(json.dumps(state['profiles'],sort_keys=True).encode()).hexdigest()
        result['warnings']=[state['evaluation_revision_warning']] if state.get('evaluation_revision_warning') else []
    except Exception as exc:result['error_type']=type(exc).__name__
    finally:
        result['production_usage']=summarize(analyst.events)
        result['judge_usage']=summarize(judge.events)
        result['evaluation_trace']=trace
        result['provider_attempts']=analyst.events+judge.events
        result['elapsed_seconds']=round(time.perf_counter()-start,2)
        (output/(case['id']+'-evidence.json')).write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/(case['id']+'-result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=True);baseline=Path(a.baseline).resolve()
    settings=dotenv_values(Path(__file__).resolve().parents[1]/'.env')
    cases=json.loads(Path(__file__).with_name('cases.json').read_text(encoding='utf-8'))
    metadata={'started_at':datetime.now(timezone.utc).isoformat(),'model':settings.get('OPENAI_MODEL') or 'gpt-6-luna',
              'rubric':RUBRIC,'rubric_sha256':hashlib.sha256(RUBRIC.encode()).hexdigest(),
              'cases_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),
              'threshold':'75/100, every dimension >=2/4, no critical flags, structural gates pass',
              'evaluation_settings':{'timeout_seconds':120,'max_completion_tokens':8000,'reasoning_effort':'low'},
              'baseline_model_settings':json.loads((baseline/'manifest.json').read_text(encoding='utf-8')).get('model_settings',{'timeout_seconds':35,'max_completion_tokens':3800,'reasoning_effort':'provider default'}),
              'method':'Recommendation component evaluation of all 10 fixed FI cases, reusing baseline live research and production analyze/critique/revise prompts and citation gates under an explicit 120s, 8000-token, low-reasoning profile; chronology-blinded paired same-model judge. Baseline settings are recorded separately; no actual client approvals.',
              'limitations':'This is a controlled component evaluation, not a production reliability pass. Same-model bias; one run per case; synthetic goals and fixed comparison sets. It does not establish human acceptance, campaign outcomes or the 60-minute productivity target.'}
    (output/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[pool.submit(evaluate,c,settings,baseline,output) for c in cases]
        for future in as_completed(tasks):
            r=future.result();results.append(r)
            print(json.dumps({'case':r['case']['id'],'draft':(r.get('draft') or {}).get('score'),'final':(r.get('final') or {}).get('score'),'passed':(r.get('final') or {}).get('passed'),'error_type':r['error_type']}),flush=True)
    results.sort(key=lambda r:r['case']['id'])
    summary={**metadata,'completed_at':datetime.now(timezone.utc).isoformat(),'aggregate':aggregate(results),'results':results,
             'paired_deltas':[{'case':r['case']['id'],'draft':r['draft']['score'],'final':r['final']['score'],'delta':round(r['final']['score']-r['draft']['score'],2)} for r in results if r.get('draft') and r.get('final')]}
    for name in ('production_usage','judge_usage'):
        keys=('model_calls','search_calls','input_tokens','output_tokens','cached_input_tokens','cache_write_tokens','total_cost_usd','unknown_usage','unpriced_calls')
        summary[name]={k:sum(r[name][k] for r in results) for k in keys}
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary['aggregate']),flush=True)

if __name__=='__main__':main()
