"""Real-model native self-message, with exact fixture scope and no send retry."""
import argparse,hashlib,json,sqlite3,tempfile,time
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema
from core.planning_trace import collect_planning_trace
from core.human_layer import COMM_RATE_LIMITER
from agents.comm_agent import composer_value

def run(args):
    import uiautomation as auto
    if not args.recipient.endswith(' (You) Message yourself'):raise ValueError('Only the authorized self-chat is supported by this test')
    windows=[w for w in auto.GetRootControl().GetChildren() if w.Name==args.window_title]
    if len(windows)!=1 or windows[0].NativeWindowHandle!=args.window_handle or 'WhatsApp Business' not in args.window_title:
        raise RuntimeError('Unique authorized Business WhatsApp window absent')
    window=windows[0]
    params={'app_name':args.window_title,'contact':args.recipient.removesuffix(' (You) Message yourself'),
            'recipient_control_name':args.recipient,'search_bar_name':args.search,'message_box_name':args.composer,'text':'AURA acceptance test'}
    def ready():
        recipient=window.Control(searchDepth=30,Name=args.recipient);box=window.EditControl(searchDepth=30,Name=args.composer)
        return window.Name==args.window_title and recipient.Exists(1,1) and box.Exists(1,1) and composer_value(box,params)==''
    def count_messages():
        return sum(c.Name==params['text'] and c.ControlTypeName=='TextControl' for c,d in auto.WalkControl(window,maxDepth=30))
    def quota_count():
        if not COMM_RATE_LIMITER.path.exists():return 0
        with sqlite3.connect(COMM_RATE_LIMITER.path) as db:return db.execute('select count(*) from attempts where timestamp>?',(time.time()-86400,)).fetchone()[0]
    if not ready():raise RuntimeError('Observed self-chat and empty composer required; existing draft preserved')
    prompt=('Send exactly '+json.dumps(params['text'])+' to contact '+json.dumps(params['contact'])+' using the exact application window '+json.dumps(params['app_name'])+
            '. The exact recipient header is '+json.dumps(params['recipient_control_name'])+', search box is '+json.dumps(params['search_bar_name'])+', and message input is '+json.dumps(params['message_box_name'])+'.')
    original=cp.generate_plan;private_rows=[];rows=[];before=count_messages();quota_before=quota_count()
    with tempfile.TemporaryDirectory(prefix='aura_message_',ignore_cleanup_errors=True) as folder:
        root=Path(folder);memory=MemoryManager(db_path=root/'memory.db',chroma_path=root/'chroma',key_file=root/'key')
        for approved in (False,True):
            plans=[];rejections=[]
            def guarded(user,context=''):
                raw=original(user,context);plans.append(raw)
                try:
                    p=ToolCallSchema.model_validate(raw)
                    if p.decision!='EXECUTE' or len(p.plan)!=1 or p.plan[0].tool!='send_message' or p.plan[0].parameters!=params or not ready():
                        raise ValueError('Outside authorized synthetic self-chat scope')
                    return raw
                except (ValueError,TypeError):rejections.append('Exact fixture scope not met');return None
            with patch.object(cp,'generate_plan',side_effect=guarded),patch.object(cp,'authorize_high_risk_action',return_value=approved),collect_planning_trace() as trace:
                result=cp.execute_pipeline(prompt,memory_factory=lambda:memory,allowed_agents={'comm_agent'})
            after=count_messages();quota_after=quota_count()
            passed=not rejections and ready() and (result['success'] and after>before and quota_after==quota_before+1 if approved else result['status']=='BLOCKED' and after==before and quota_after==quota_before)
            private_rows.append({'approved':approved,'raw_plans':plans,'inference':trace,'result':result})
            rows.append({'approved':approved,'status':result['status'],'success':result['success'],'error':result['error'],
                         'exact_scope_accepted':not rejections,'self_chat_verified_and_composer_empty':ready(),
                         'synthetic_message_count_before':before,'synthetic_message_count_after':after,
                         'quota_before':quota_before,'quota_after':quota_after,
                         'raw_plan_sha256':hashlib.sha256(json.dumps(plans,sort_keys=True).encode()).hexdigest(),'passed':passed})
            private=Path('.aura-private/acceptance/live_messaging_raw.json');private.parent.mkdir(parents=True,exist_ok=True)
            private.write_text(json.dumps(private_rows,indent=2),encoding='utf-8')
            Path('reports/live_messaging.json').write_text(json.dumps({'mode':'Real production model, native adapter, persistent quota, real audit; explicit bounded operator approval; recipient labels remain private','results':rows},indent=2),encoding='utf-8')
            print('Approved' if approved else 'Denied',passed,result['status'],flush=True)
            if not passed:break
    return len(rows)==2 and all(r['passed'] for r in rows)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for flag in ('window-title','recipient','composer','search'):p.add_argument('--'+flag,required=True)
    p.add_argument('--window-handle',type=int,required=True)
    raise SystemExit(0 if run(p.parse_args()) else 1)
