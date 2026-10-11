import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock
from core.control_plane import execute_pipeline
from tests.helpers import plan,AuditMemory
class Pipeline(unittest.TestCase):
    def run_plan(self,p,memory=None,**kwargs):
        memory=memory or AuditMemory()
        with patch('core.control_plane.generate_plan',return_value=p):
            return execute_pipeline('test',memory_factory=lambda:memory,**kwargs),memory
    def test_real_write_and_readback(self):
        with tempfile.TemporaryDirectory() as tmp,patch('core.control_plane.authorize_high_risk_action',return_value=True):
            path=Path(tmp)/'written.txt'
            result,memory=self.run_plan(plan(('write_file',{'path':str(path),'content':'verified'})))
            self.assertEqual('verified',path.read_text())
            self.assertTrue(result['success']);self.assertTrue(result['steps'][0]['verified'])
            self.assertEqual('VERIFIED',memory.audits[-1][-1]);self.assertEqual(1,len(memory.sessions))
    def test_denied_destructive_action(self):
        with tempfile.TemporaryDirectory() as tmp,patch('core.control_plane.authorize_high_risk_action',return_value=False) as approval:
            path=Path(tmp)/'keep.txt';path.write_text('keep')
            result,memory=self.run_plan(plan(('delete_file',{'path':str(path)})))
            self.assertEqual('BLOCKED',result['status']);self.assertEqual('keep',path.read_text())
            approval.assert_called_once();self.assertIn('DENIED_BY_HITL',[a[-1] for a in memory.audits])
    def test_invalid_later_step_prevents_earlier_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'must-not-exist'
            result,_=self.run_plan(plan(('write_file',{'path':str(path),'content':'x'}),('invented',{})))
            self.assertEqual('INVALID_PLAN',result['status']);self.assertFalse(path.exists())
    def test_agent_scope(self):
        result,_=self.run_plan(plan(('read_file',{'path':'x'})),allowed_agents={'comm_agent'})
        self.assertEqual('INVALID_PLAN',result['status'])
    def test_exception_stops_remaining_steps(self):
        with patch('core.control_plane.authorize_high_risk_action',return_value=True),patch.dict('core.control_plane.AGENT_REGISTRY',{'os_agent':{'read_file':Mock(side_effect=RuntimeError('boom')),'create_folder':Mock()}}):
            result,memory=self.run_plan(plan(('read_file',{'path':'x'}),('create_folder',{'path':'y'})))
            self.assertEqual('ERROR',result['status']);self.assertEqual(1,len(result['steps']));self.assertEqual(1,len(memory.sessions))
    def test_tool_lie_fails_readback(self):
        with tempfile.TemporaryDirectory() as tmp,patch('core.control_plane.authorize_high_risk_action',return_value=True),patch.dict('core.control_plane.AGENT_REGISTRY',{'os_agent':{'write_file':lambda p:(True,'claimed')}}):
            result,_=self.run_plan(plan(('write_file',{'path':str(Path(tmp)/'absent'),'content':'x'})))
            self.assertFalse(result['success'])
    def test_clarify_not_completion(self):
        result,_=self.run_plan(plan(decision='CLARIFY'))
        self.assertEqual('CLARIFY',result['status']);self.assertFalse(result['success'])
    def test_audit_failure_blocks_execution(self):
        memory=AuditMemory();memory.log_audit_trail=Mock(side_effect=OSError())
        with patch.dict('core.control_plane.AGENT_REGISTRY',{'os_agent':{'read_file':Mock()}}) as registry:
            result,_=self.run_plan(plan(('read_file',{'path':'x'})),memory)
            self.assertFalse(result['success']);registry['os_agent']['read_file'].assert_not_called()
    def test_sensitive_destination_denied_at_executor(self):
        with patch('core.control_plane.authorize_high_risk_action',return_value=False),patch.dict('core.control_plane.AGENT_REGISTRY',{'os_agent':{'copy_file':Mock()}}) as registry:
            result,_=self.run_plan(plan(('copy_file',{'source':'D:/safe.txt','destination':'C:/Windows/System32/probe'})))
            self.assertEqual('BLOCKED',result['status']);registry['os_agent']['copy_file'].assert_not_called()
