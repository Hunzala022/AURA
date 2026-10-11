"""Live planner + real isolated files/SQLite/Chroma; no desktop or external effects."""
import json,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema
from core.policy import normalized_path

def run():
    reports=[]
    raw_plans=[]
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        root=Path(folder);target=root/'alpha.txt'
        memory=MemoryManager(db_path=root/'memory.db',chroma_path=root/'chroma',key_file=root/'.keys/key',embedding_function=lambda text:[1.,0.,0.])
        original=cp.generate_plan
        # The test guard only permits the exact synthetic operations described below.
        allowed={'write_file':{'path':str(target),'content':'alpha'},'verify_file':{'path':str(target),'expected_content':'alpha'},'delete_file':{'path':str(target)}}
        def guarded_plan(prompt,context):
            raw=original(prompt,context)
            raw_plans.append(raw)
            if raw is None:return None
            parsed=ToolCallSchema.model_validate(raw)
            for step in parsed.plan:
                expected=allowed.get(step.tool)
                if expected is None or set(step.parameters)!=set(expected):return None
                if any((normalized_path(step.parameters[k])!=normalized_path(v)) if k=='path' else (step.parameters[k]!=v) for k,v in expected.items()):return None
            return raw
        cases=[
            ('write and verify',f'Write exactly alpha to {target}, then verify it contains exactly alpha.','COMPLETED',True),
            ('denied deletion',f'Delete my test file {target}.','BLOCKED',False),
        ]
        with patch('core.control_plane.generate_plan',side_effect=guarded_plan):
            for name,prompt,status,approve in cases:
                if name=='denied deletion':target.write_text('alpha',encoding='utf-8')
                with patch('core.control_plane.authorize_high_risk_action',return_value=approve):
                    result=cp.execute_pipeline(prompt,memory_factory=lambda:memory,allowed_agents={'os_agent'})
                intact=target.is_file() and target.read_text()=='alpha'
                passed=result['status']==status and intact and (result['success'] is (status=='COMPLETED'))
                reports.append({'scenario':name,'expected_status':status,'raw_plan':raw_plans[-1],'result':result,'postcondition_file_alpha':intact,'passed':passed})
        # Test records contain only synthetic paths/text; never dump keys/ciphertext.
        Path('reports/live_execution.json').write_text(json.dumps({'mode':'live planner, real temporary file and encrypted audit stores; exact-action test guard and approval fixture; independent deletion precondition','prompt_sha256':hashlib.sha256(cp.BASE_SYSTEM_PROMPT.encode()).hexdigest(),'options':cp.PLAN_OPTIONS,'results':reports},indent=2),encoding='utf-8')
    return reports
if __name__=='__main__':
    reports=run()
    for report in reports:print(report['scenario'],report['passed'],report['result']['status'])
    raise SystemExit(0 if all(r['passed'] for r in reports) else 1)
