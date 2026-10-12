"""Opt-in production adapter acceptance against a pre-created synthetic Notepad.

No live planner: this isolates policy, native UIA, verification and real audit.
Never targets an arbitrary document or overwrites non-fixture content.
"""
import argparse
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from core import control_plane as cp
from core.memory import MemoryManager

FIXTURE = 'AURA acceptance fixture alpha {Enter}'
OUTPUT = 'AURA native adapter verified {Enter}'


def run(title, handle):
    import uiautomation as auto
    matches = [w for w in auto.GetRootControl().GetChildren()
               if w.Name == title and w.NativeWindowHandle == handle]
    if len(matches) != 1:
        raise RuntimeError('Exact observed fixture window is absent')
    window = matches[0]
    document = window.DocumentControl()
    if not document.Exists(1) or document.GetValuePattern().Value != FIXTURE:
        raise RuntimeError('Synthetic fixture precondition failed; no action attempted')
    plan = dict(decision='EXECUTE', plan=[dict(step=1, tool='type_in_window',
                parameters=dict(window_title=title, text=OUTPUT), reasoning='Synthetic acceptance fixture')],
                overall_reasoning='Controlled adapter acceptance', risk='low',
                risk_justification='Python policy is authoritative', confidence=1.0)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        root = Path(folder)
        memory = MemoryManager(db_path=root/'memory.db', chroma_path=root/'chroma',
                               key_file=root/'key', embedding_function=lambda _: [1., 0., 0.])
        with patch.object(cp, 'generate_plan', return_value=plan), patch.object(cp, 'authorize_high_risk_action', return_value=False):
            denied = cp.execute_pipeline('Denied synthetic desktop acceptance',
                                         memory_factory=lambda: memory, allowed_agents={'os_agent'})
        denied_intact = document.GetValuePattern().Value == FIXTURE
        # The user authorized this exact synthetic acceptance operation. Keep
        # the approval fixture explicit: this does not test interactive HITL.
        with patch.object(cp, 'generate_plan', return_value=plan), patch.object(cp, 'authorize_high_risk_action', return_value=True):
            result = cp.execute_pipeline('Type the exact synthetic acceptance text into the fixture',
                                         memory_factory=lambda: memory, allowed_agents={'os_agent'})
        exact = document.GetValuePattern().Value == OUTPUT
        with sqlite3.connect(memory.db_path) as db:
            statuses = [r[0] for r in db.execute('select action_status from audit_logs order by id')]
        passed = result['success'] and exact and denied['status'] == 'BLOCKED' and denied_intact and statuses == ['ATTEMPTED', 'DENIED_BY_HITL', 'ATTEMPTED', 'APPROVED_BY_HITL', 'VERIFIED']
        report = dict(mode='Real native UIA adapter and audit; deterministic planner and approval fixtures',
                      denied_result=denied, denied_preserved_fixture=denied_intact,
                      result=result, exact_readback=exact, audit_statuses=statuses,
                      title_changed=window.Name != title, passed=passed)
        Path('reports/desktop_acceptance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Native desktop adapter acceptance:', passed)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--window-title', required=True)
    parser.add_argument('--window-handle', required=True, type=int)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.window_title, args.window_handle) else 1)
