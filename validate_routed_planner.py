"""Experimental planning only: same 25 cases, no tools or private memory."""
import argparse,json,time,hashlib
from pathlib import Path
from core.routed_planner import routed_plan,ROUTING_PROMPT,PARAMETER_PROMPT
from core.evaluation import score_plan
from validate_model import cases,Monitor

def run(names,output):
    results=[]
    for index,case in enumerate(cases(),1):
        if names and case['name'] not in names:continue
        trace={};start=time.perf_counter()
        with Monitor() as monitor:raw=routed_plan(case['prompt'],trace=trace)
        score=score_plan(raw,case)
        results.append({'id':index,'scenario':case['name'],'expected':case,'raw_plan':raw,'score':score,'trace':trace,'elapsed_seconds':time.perf_counter()-start,**monitor.values()})
        metadata={'mode':'experimental route then parameters; no tools executed; no advisory risk estimate','routing_prompt_sha256':hashlib.sha256(ROUTING_PROMPT.encode()).hexdigest(),'parameter_prompt_sha256':hashlib.sha256(PARAMETER_PROMPT.encode()).hexdigest(),'source_sha256':hashlib.sha256(Path('core/routed_planner.py').read_bytes()).hexdigest()}
        Path(output).write_text(json.dumps({'metadata':metadata,'results':results},indent=2),encoding='utf-8')
        print(case['name'],score['passed'],score['reasons'],round(results[-1]['elapsed_seconds'],1),flush=True)
    return all(r['score']['passed'] for r in results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',action='append');p.add_argument('--output',default='reports/model_routed_validation.json');a=p.parse_args()
    raise SystemExit(0 if run(a.case,a.output) else 1)
