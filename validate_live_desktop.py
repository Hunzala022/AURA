"""Opt-in real-model acceptance on an observed synthetic Notepad only."""
import argparse,json,tempfile
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema
from core.planning_trace import collect_planning_trace
from core.evaluation import score_plan

BEFORE='AURA native adapter verified {Enter}'
AFTER='AURA live desktop verified {Enter}'

def run(title,handle,output):
    import uiautomation as auto
    windows=[w for w in auto.GetRootControl().GetChildren() if w.Name==title and w.NativeWindowHandle==handle]
    if len(windows)!=1:raise RuntimeError('Observed fixture window absent')
    window=windows[0];document=window.DocumentControl()
    if not document.Exists(1) or document.GetValuePattern().Value!=BEFORE:
        raise RuntimeError('Only the prior synthetic acceptance document is authorized')
    original=cp.generate_plan;rows=[]
    with tempfile.TemporaryDirectory(prefix='aura_desktop_',ignore_cleanup_errors=True) as folder:
        root=Path(folder);source=root/'input.txt';source.write_text(AFTER,encoding='utf-8')
        memory=MemoryManager(db_path=root/'state/memory.db',chroma_path=root/'state/chroma',key_file=root/'state/key')
        for name in ('denied entry','bound literal entry','accessibility archive','verify body'):
            title=window.Name;tree=root/'tree.txt'
            if name in ('denied entry','bound literal entry'):
                prompt=f'Read {source.as_posix()}, then set the text in the existing window with exact title {json.dumps(title)} to that exact returned file text.'
                steps=[('read_file',{'path':source.as_posix()}),('type_in_window',{'window_title':title,'text':{'from_step':1}})]
            elif name=='accessibility archive':
                prompt=f'Read the accessibility tree of the existing window with exact title {json.dumps(title)}, then save its exact returned text to {tree.as_posix()}.'
                steps=[('read_ui_tree',{'window_title':title}),('write_file',{'path':tree.as_posix(),'content':{'from_step':1}})]
            else:
                prompt=f'Verify the existing window with exact title {json.dumps(title)} contains exactly {json.dumps(AFTER)}.'
                steps=[('verify_window',{'window_title':title,'expected_text':AFTER})]
            captured=[];rejected=[];approvals=[]
            def guarded(user,context=''):
                raw=original(user,context);captured.append(raw)
                try:
                    parsed=ToolCallSchema.model_validate(raw)
                    for step in parsed.plan:
                        if step.tool not in {t for t,p in steps}:raise ValueError('Tool exceeds fixture scope')
                        p=step.parameters
                        if 'window_title' in p and p['window_title']!=title:raise ValueError('Wrong window')
                        if 'path' in p and Path(p['path']).resolve() not in {source.resolve(),tree.resolve()}:raise ValueError('Wrong path')
                        if step.tool=='type_in_window' and p['text'] not in (AFTER,{'from_step':1}):raise ValueError('Unexpected text')
                    if window.NativeWindowHandle!=handle or document.GetValuePattern().Value!=(BEFORE if name in ('denied entry','bound literal entry') else AFTER):
                        raise ValueError('Fixture changed during inference')
                    return raw
                except (ValueError,TypeError):rejected.append('Plan or fixture outside authorized bounds');return None
            def approve(action):
                allowed=name!='denied entry';approvals.append({'tool':action['tool'],'approved':allowed});return allowed
            with patch.object(cp,'generate_plan',side_effect=guarded),patch.object(cp,'authorize_high_risk_action',side_effect=approve),collect_planning_trace() as inference:
                result=cp.execute_pipeline(prompt,memory_factory=lambda:memory,allowed_agents={'os_agent'})
            expected_status='BLOCKED' if name=='denied entry' else 'COMPLETED'
            post=document.GetValuePattern().Value==(BEFORE if name=='denied entry' else AFTER)
            if name=='accessibility archive':post=post and tree.is_file() and title in tree.read_text(encoding='utf-8')
            from core.policy import evaluate_risk
            risk='HIGH' if any(evaluate_risk(t,p)=='HIGH' for t,p in steps) else 'MEDIUM'
            gold={'expected_decision':'EXECUTE','expected_tools_subset':[t for t,p in steps],'expected_tool_order':[t for t,p in steps],
                  'expected_parameters':{i:p for i,(t,p) in enumerate(steps)},'expected_risk':risk}
            score=score_plan(captured[-1] if captured else None,gold)
            passed=score['passed'] and post and result['status']==expected_status and not rejected
            rows.append({'scenario':name,'prompt':prompt,'expected_plan':gold,'raw_plan':captured[-1] if captured else None,'score':score,
                         'result':result,'postcondition':post,'approvals':approvals,'guard_rejections':rejected,'inference':inference,'passed':passed})
            Path(output).write_text(json.dumps({'mode':'Real production model, native UIA, real audit; bounded synthetic operator approval','results':rows},indent=2),encoding='utf-8')
            print(name,passed,result['status'],flush=True)
            if not passed:break
    return bool(rows) and len(rows)==4 and all(r['passed'] for r in rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--window-title',required=True);p.add_argument('--window-handle',type=int,required=True)
    p.add_argument('--output',default='reports/live_desktop.json');a=p.parse_args()
    raise SystemExit(0 if run(a.window_title,a.window_handle,a.output) else 1)
