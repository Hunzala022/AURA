"""Opt-in native self-chat acceptance; explicit observed labels required.

Only a synthetic message is permitted. Does not retry uncertain sends. Uses
production durable quota and a temporary real encrypted audit store. Recipient
labels are deliberately omitted from the public report.
"""
import argparse
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.human_layer import COMM_RATE_LIMITER
from agents.comm_agent import composer_value


def run(args):
    import uiautomation as auto
    if not args.recipient.endswith(' (You) Message yourself'):
        raise ValueError('Explicit self-chat header required')
    matches = [w for w in auto.GetRootControl().GetChildren()
               if w.Name == args.window_title and w.NativeWindowHandle == args.window_handle]
    if len(matches) != 1 or 'WhatsApp Business' not in args.window_title:
        raise RuntimeError('Exact authorized Business WhatsApp window is absent')
    win = matches[0]
    recipient = win.Control(searchDepth=30, Name=args.recipient)
    composer = win.EditControl(searchDepth=30, Name=args.composer)
    if not recipient.Exists(2, 1) or not composer.Exists(2, 1):
        raise RuntimeError('Exact observed self-chat controls absent')
    values = [composer_value(composer, {'app_name':args.window_title, 'message_box_name':args.composer})]
    if any(values):
        diagnostics = [dict(length=len(v), whitespace_only=bool(v) and v.isspace(),
                            whitespace_codes=[ord(c) for c in v] if v and v.isspace() else [],
                            matches_placeholder=v in ('Type a message', args.composer, args.search)) for v in values]
        print('Precondition value metadata (composer):', diagnostics)
        raise RuntimeError('Existing draft/search preserved; no action attempted')
    params = dict(app_name=args.window_title, contact=args.recipient.removesuffix(' (You) Message yourself'),
                  recipient_control_name=args.recipient, search_bar_name=args.search,
                  message_box_name=args.composer, text='AURA acceptance test')
    plan = dict(decision='EXECUTE', plan=[dict(step=1, tool='send_message', parameters=params,
                reasoning='User-authorized synthetic self-chat acceptance')], overall_reasoning='Controlled acceptance',
                risk='high', risk_justification='Python policy authoritative', confidence=1.0)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        root = Path(folder)
        memory = MemoryManager(db_path=root/'memory.db', chroma_path=root/'chroma', key_file=root/'key',
                               embedding_function=lambda _: [1., 0., 0.])
        with patch.object(cp, 'generate_plan', return_value=plan), patch.object(cp, 'authorize_high_risk_action', return_value=False):
            denied = cp.execute_pipeline('Deny synthetic self-message', memory_factory=lambda: memory, allowed_agents={'comm_agent'})
        denied_empty = composer_value(composer,params) == ''
        with patch.object(cp, 'generate_plan', return_value=plan), patch.object(cp, 'authorize_high_risk_action', return_value=True):
            result = cp.execute_pipeline('Approved synthetic self-message', memory_factory=lambda: memory, allowed_agents={'comm_agent'})
        with sqlite3.connect(memory.db_path) as db:
            statuses = [r[0] for r in db.execute('select action_status from audit_logs order by id')]
        with sqlite3.connect(COMM_RATE_LIMITER.path) as db:
            reservations = db.execute('select count(*) from attempts').fetchone()[0]
        passed = denied['status'] == 'BLOCKED' and denied_empty and result['success'] and reservations >= 1
        report = dict(mode='Real native adapter, persistent quota and encrypted audit; planner/approval fixtures',
                      self_chat_precondition=True, denied_result=denied, denied_composer_empty=denied_empty,
                      result=result, audit_statuses=statuses, persistent_reservations=reservations, passed=passed)
        Path('reports/messaging_acceptance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Native messaging acceptance:', passed, result['status'], result['error'])
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for flag in ('window-title', 'recipient', 'composer', 'search'):
        parser.add_argument('--'+flag, required=True)
    parser.add_argument('--window-handle', type=int, required=True)
    raise SystemExit(0 if run(parser.parse_args()) else 1)
