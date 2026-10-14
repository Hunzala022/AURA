"""Read-only native self-chat acceptance; private message text never enters reports."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema


def run(args):
    import uiautomation as auto
    def ready():
        windows=[w for w in auto.GetRootControl().GetChildren() if w.Name==args.window_title]
        return (len(windows)==1 and windows[0].NativeWindowHandle==args.window_handle
                and 'WhatsApp Business' in args.window_title
                and args.recipient.endswith(' (You) Message yourself')
                and windows[0].Control(searchDepth=30,Name=args.recipient).Exists(1,1))
    if not ready():raise RuntimeError('Authorized Business WhatsApp self-chat is not selected')
    original=cp.generate_plan;plans=[]
    def guarded(user,context=''):
        raw=original(user,context);plans.append(raw)
        try:
            p=ToolCallSchema.model_validate(raw)
            if p.decision!='EXECUTE' or len(p.plan)!=1 or p.plan[0].tool!='read_latest_message' or p.plan[0].parameters!={'app_name':args.window_title} or not ready():return None
            return raw
        except (ValueError,TypeError):return None
    with tempfile.TemporaryDirectory(prefix='aura_message_read_',ignore_cleanup_errors=True) as folder:
        root=Path(folder);memory=MemoryManager(root/'memory.db',root/'chroma',root/'key')
        with patch.object(cp,'generate_plan',side_effect=guarded),patch.object(cp,'authorize_high_risk_action',return_value=True):
            result=cp.execute_pipeline('Read recent visible messages from the exact window '+json.dumps(args.window_title)+'.',memory_factory=lambda:memory,allowed_agents={'comm_agent'})
        observed=result['steps'][-1].get('result','') if result['steps'] else ''
        passed=result['success'] and ready() and 'AURA acceptance test' in observed
        report={'mode':'Real model and native read-only adapter; exact authorized self-chat guard; bounded approval',
                'status':result['status'],'synthetic_message_observed':'AURA acceptance test' in observed,
                'private_text_sha256':hashlib.sha256(observed.encode()).hexdigest(),
                'input_or_send_performed':False,'passed':passed}
        Path('reports/live_message_read.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2));return passed


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--window-title',required=True);p.add_argument('--window-handle',type=int,required=True);p.add_argument('--recipient',required=True)
    raise SystemExit(0 if run(p.parse_args()) else 1)
