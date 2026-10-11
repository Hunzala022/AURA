"""Safe deterministic system scenarios. Real files/research; mocked planner/UI/network.
This measures execution enforcement, NOT live model accuracy or desktop reliability.
"""
import json,tempfile,time
from pathlib import Path
from unittest.mock import patch,Mock
from contextlib import ExitStack
from core.control_plane import execute_pipeline
from core.evaluation import score_execution
from core.sanitization import sanitize_content
from tests.helpers import plan,AuditMemory
def run_system_benchmark():
    results=[]
    with tempfile.TemporaryDirectory() as folder:
        base=Path(folder)
        for case in range(1,21):
            root=base/str(case);root.mkdir()
            source=root/'source.txt';source.write_text('fixture data',encoding='utf-8')
            destination=root/'destination.txt'
            read=('read_file',{'path':str(source)})
            write=('write_file',{'path':str(destination),'content':'fixture data'})
            search=('search_files_by_name',{'directory':str(root),'pattern':'*.txt'})
            verify=('verify_file',{'path':str(destination),'expected_content':'fixture data'})
            expected='COMPLETED'; post=lambda d=destination:d.read_text()=='fixture data'
            memory=AuditMemory();approve=True;registry=None;scope=None
            if case==1: label='Write and verify';p=plan(write,verify)
            elif case==2: label='Research name then copy';p=plan(search,('copy_file',{'source':str(source),'destination':str(destination)}),verify)
            elif case==3: label='Research content then read';p=plan(('search_files_by_content',{'directory':str(root),'query':'fixture data'}),read);post=lambda s=source:s.read_text()=='fixture data'
            elif case==4: label='Move and verify';p=plan(('move_file',{'source':str(source),'destination':str(destination)}),verify);post=lambda s=source,d=destination:not s.exists() and d.read_text()=='fixture data'
            elif case==5: label='Create folder and file';p=plan(('create_folder',{'path':str(root/'nested')}),write,verify)
            elif case==6: label='Approved isolated deletion';p=plan(('delete_file',{'path':str(source)}));post=lambda s=source:not s.exists()
            elif case==7: label='Denied deletion';p=plan(('delete_file',{'path':str(source)}));approve=False;expected='BLOCKED';post=lambda s=source:s.exists()
            elif case==8: label='Missing file';p=plan(('read_file',{'path':str(root/'missing')}));expected='FAILED';post=lambda d=destination:not d.exists()
            elif case==9: label='Ambiguous request';p=plan(decision='CLARIFY');expected='CLARIFY';post=lambda d=destination:not d.exists()
            elif case==10: label='Refused request';p=plan(decision='REFUSE');expected='REFUSE';post=lambda d=destination:not d.exists()
            elif case==11: label='Late unknown tool rejects whole plan';p=plan(write,('run_command',{}));expected='INVALID_PLAN';post=lambda d=destination:not d.exists()
            elif case==12: label='Caller agent boundary';p=plan(write);scope={'comm_agent'};expected='INVALID_PLAN';post=lambda d=destination:not d.exists()
            elif case==13: label='Read then denied message';p=plan(read,('send_message',{'app_name':'Fixture','contact':'Recipient','recipient_control_name':'Recipient','text':'fixture data'}));approve=False;expected='BLOCKED';post=lambda s=source:s.exists()
            elif case==14:
                label='Sanitized browser fixture and write';p=plan(('navigate_and_read',{'url':'https://example.invalid'}),write,verify)
                registry={'browser_agent':{'navigate_and_read':lambda params:(True,sanitize_content('<script>bad()</script><p>fixture data</p>'))}}
            elif case==15:
                label='Read communication fixture then write';p=plan(('read_latest_message',{'app_name':'Fixture'}),write,verify)
                registry={'comm_agent':{'read_latest_message':lambda params:(True,'fixture data')}}
            elif case==16:
                label='Vision fixture failure stops write';p=plan(('vision_locate_element',{'window_title':'Fixture','element_description':'absent'}),write)
                registry={'vision_agent':{'vision_locate_element':lambda params:(False,'not found')}};expected='FAILED';post=lambda d=destination:not d.exists()
            elif case==17:
                label='Exception stops remaining workflow';p=plan(read,write)
                registry={'os_agent':{'read_file':Mock(side_effect=RuntimeError()),'write_file':Mock()}};expected='ERROR';post=lambda d=destination:not d.exists()
            elif case==18:
                label='False tool success rejected';p=plan(write)
                registry={'os_agent':{'write_file':lambda params:(True,'claimed')}};expected='ERROR';post=lambda d=destination:not d.exists()
            elif case==19:
                label='Audit failure prevents side effects';p=plan(write);memory.log_audit_trail=Mock(side_effect=OSError());expected='ERROR';post=lambda d=destination:not d.exists()
            else:
                label='Research then rejected forged agent';p=plan(search,write);p['plan'][1]['agent']='comm_agent';expected='INVALID_PLAN';post=lambda d=destination:not d.exists()
            started=time.perf_counter()
            with ExitStack() as stack:
                stack.enter_context(patch('core.control_plane.generate_plan',return_value=p))
                stack.enter_context(patch('core.control_plane.authorize_high_risk_action',return_value=approve))
                if registry:stack.enter_context(patch.dict('core.control_plane.AGENT_REGISTRY',registry))
                outcome=execute_pipeline(label,memory_factory=lambda:memory,allowed_agents=scope)
            score=score_execution(outcome,expected,post)
            results.append({'id':case,'scenario':label,'expected_status':expected,'actual':outcome,'score':score,'elapsed_seconds':time.perf_counter()-started,
                'planner':'mocked','external_agents':'fixture mocks where used','filesystem':'real temporary directory',
                'ttft':None,'tokens_per_second':None,'vram_mb':None})
    Path('reports').mkdir(exist_ok=True)
    Path('reports/stage4_system.json').write_text(json.dumps({'mode':'deterministic integration, not live LLM benchmark','results':results},indent=2),encoding='utf-8')
    print(f"Observable expectations met: {sum(r['score']['passed'] for r in results)}/{len(results)}")
    return results
if __name__=='__main__':
    raise SystemExit(0 if all(r['score']['passed'] for r in run_system_benchmark()) else 1)
