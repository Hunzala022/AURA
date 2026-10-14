"""Diagnostic only until explicitly promoted; unchanged benchmark gold."""
import argparse,hashlib,json,time
from pathlib import Path
from core.planning_proposal import propose,PROPOSAL_PROMPT
from core.planning_trace import collect_planning_trace
from core.evaluation import score_plan
from validate_model import cases,Monitor

def run(output,names):
    rows=[]
    for i,case in enumerate(cases(),1):
        if names and case['name'] not in names:continue
        started=time.perf_counter()
        with collect_planning_trace() as trace,Monitor() as monitor:
            raw=propose(case['prompt'])
        score=score_plan(raw,case)
        rows.append({'id':i,'scenario':case['name'],'expected':case,'raw_plan':raw,'score':score,
                     'inference':trace,'elapsed_seconds':time.perf_counter()-started,**monitor.values()})
        Path(output).write_text(json.dumps({'mode':'Diagnostic compact proposal; canonical plan validation; unchanged gold; no effects',
                                          'prompt_sha256':hashlib.sha256(PROPOSAL_PROMPT.encode()).hexdigest(),'results':rows},indent=2),encoding='utf-8')
        print(case['name'],score['passed'],score['reasons'],flush=True)
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--case',action='append');a=p.parse_args()
    rows=run(a.output,a.case);raise SystemExit(0 if rows and all(r['score']['passed'] for r in rows) else 1)
