"""Real-model native recipient navigation; exactly one bounded self-send attempt."""
import argparse
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema
from core.human_layer import COMM_RATE_LIMITER
from agents import comm_agent


def run(args):
    import sqlite3
    import uiautomation as auto
    if not args.recipient.endswith(' (You) Message yourself'):raise ValueError('Explicit self-chat required')
    matches=[w for w in auto.GetRootControl().GetChildren() if w.Name==args.window_title]
    if len(matches)!=1 or matches[0].NativeWindowHandle!=args.window_handle or 'WhatsApp Business' not in args.window_title:raise RuntimeError('Authorized window absent')
    window=matches[0]
    params={'app_name':args.window_title,'contact':args.recipient.removesuffix(' (You) Message yourself'),
            'recipient_control_name':args.recipient,'search_bar_name':args.search,'message_box_name':args.composer,'text':'AURA acceptance test'}
    if args.inspect_only:
        label=params['contact']+' (You)'
        roles=[{'type':c.ControlTypeName,'depth':d,'exact_label':c.Name==label}
               for c,d in auto.WalkControl(window,maxDepth=30) if c.Name==label or c.Name.startswith(label+' ')]
        print(json.dumps({'matching_self_control_roles':roles,'input_performed':False},indent=2))
        return True
    def unselected():
        header=window.Control(searchDepth=30,Name=args.recipient)
        search=window.EditControl(searchDepth=30,Name=args.search)
        return window.Name==args.window_title and not header.Exists(0,0) and search.Exists(1,1) and search.GetValuePattern().Value in ('','\n')
    if not unselected():raise RuntimeError('Navigation requires unselected self-chat and an empty search control')
    def quota_count():
        if hasattr(COMM_RATE_LIMITER,'export_attempts'):
            return sum(t>time.time()-86400 for _,t in COMM_RATE_LIMITER.export_attempts())
        with sqlite3.connect(COMM_RATE_LIMITER.path) as db:
            return db.execute('SELECT COUNT(*) FROM attempts WHERE timestamp>?',(time.time()-86400,)).fetchone()[0]
    before_quota=quota_count();observations=[];pointer=[];pauses=[]
    original_walk=auto.WalkControl;original_move=comm_agent.move_pointer_to;original_pause=comm_agent.typing_pause
    def observe_walk(*a,**kw):
        rows=list(original_walk(*a,**kw))
        if window.Control(searchDepth=30,Name=args.recipient).Exists(0,0):
            observations.append(sum(c.ControlTypeName=='TextControl' and c.Name==params['text'] for c,d in rows))
        return iter(rows)
    def observe_move(*a,**kw):
        value=original_move(*a,**kw);pointer.append(value);return value
    def observe_pause():
        start=time.perf_counter();original_pause();pauses.append(time.perf_counter()-start)
    original_plan=cp.generate_plan;plans=[];guard_checks=[]
    def guarded(user,context=''):
        raw=original_plan(user,context);plans.append(raw)
        try:
            p=ToolCallSchema.model_validate(raw)
            checks={'decision':p.decision=='EXECUTE','one_step':len(p.plan)==1,
                    'tool':len(p.plan)==1 and p.plan[0].tool=='send_message',
                    'parameters':len(p.plan)==1 and p.plan[0].parameters==params,'ui_precondition':unselected()}
            guard_checks.append(checks)
            if not all(checks.values()):return None
            return raw
        except (ValueError,TypeError):guard_checks.append({'valid_contract':False});return None
    prompt=('Send exactly '+json.dumps(params['text'])+' to contact '+json.dumps(params['contact'])+' using exact application window '+json.dumps(params['app_name'])+
            '. The exact recipient header is '+json.dumps(params['recipient_control_name'])+', search box is '+json.dumps(params['search_bar_name'])+', and message input is '+json.dumps(params['message_box_name'])+'.')
    with tempfile.TemporaryDirectory(prefix='aura_navigation_',ignore_cleanup_errors=True) as folder:
        root=Path(folder);memory=MemoryManager(root/'memory.db',root/'chroma',root/'key')
        with patch.object(cp,'generate_plan',side_effect=guarded),patch.object(cp,'authorize_high_risk_action',return_value=True),patch.object(auto,'WalkControl',side_effect=observe_walk),patch.object(comm_agent,'move_pointer_to',side_effect=observe_move),patch.object(comm_agent,'typing_pause',side_effect=observe_pause):
            result=cp.execute_pipeline(prompt,memory_factory=lambda:memory,allowed_agents={'comm_agent'})
        header=window.Control(searchDepth=30,Name=args.recipient);box=window.EditControl(searchDepth=30,Name=args.composer)
        after_quota=quota_count()
        verified=header.Exists(1,1) and box.Exists(1,1) and comm_agent.composer_value(box,params)==''
        observed_new=len(observations)>=2 and observations[-1]==observations[0]+1
        passed=result['success'] and verified and observed_new and after_quota==before_quota+1
        report={'mode':'Real model and real native search/send; observation wrappers preserve adapter behavior; no retry',
                'navigation_required_before':True,'status':result['status'],'error':result['error'],'guard_checks':guard_checks,
                'verified_self_chat_and_empty_composer_after':verified,'new_message_observed':observed_new,
                'message_counts_during_adapter':observations,'quota_before':before_quota,'quota_after':after_quota,
                'successful_curved_pointer_moves':sum(pointer),'typing_pause_count':len(pauses),
                'typing_pause_seconds':pauses,'passed':passed}
        Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8')
        private=Path('.aura-private/acceptance/navigation-plans.json');private.parent.mkdir(parents=True,exist_ok=True)
        private.write_text(json.dumps(plans,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2));return passed


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('window-title','recipient','search','composer'):p.add_argument('--'+name,required=True)
    p.add_argument('--window-handle',required=True,type=int);p.add_argument('--output',default='reports/live_message_navigation.json')
    p.add_argument('--inspect-only',action='store_true')
    raise SystemExit(0 if run(p.parse_args()) else 1)
