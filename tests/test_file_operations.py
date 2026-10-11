import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from core.control_plane import execute_pipeline
from tests.helpers import plan,AuditMemory
class Files(unittest.TestCase):
    def test_directory_cannot_satisfy_expected_file_contents(self):
        from agents.os_agent import verify_file
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(verify_file({'path':folder,'expected_content':'alpha'})[0])
    def test_actual_copy_move_directory_and_empty_content(self):
        with tempfile.TemporaryDirectory() as folder,patch('core.control_plane.authorize_high_risk_action',return_value=True):
            root=Path(folder);source=root/'source';source.mkdir();(source/'empty.txt').write_text('')
            steps=plan(('copy_file',{'source':str(source),'destination':str(root/'copy')}),('move_file',{'source':str(root/'copy'),'destination':str(root/'moved')}),('verify_file',{'path':str(root/'moved/empty.txt'),'expected_content':''}))
            with patch('core.control_plane.generate_plan',return_value=steps):
                result=execute_pipeline('fixture workflow',memory_factory=AuditMemory)
            self.assertTrue(result['success'],result);self.assertFalse((root/'copy').exists())
            self.assertEqual('',(root/'moved/empty.txt').read_text())
    def test_mismatch_preserves_partial_effects_in_report(self):
        with tempfile.TemporaryDirectory() as folder,patch('core.control_plane.authorize_high_risk_action',return_value=True):
            file=Path(folder)/'written';p=plan(('write_file',{'path':str(file),'content':'actual'}),('verify_file',{'path':str(file),'expected_content':'different'}))
            with patch('core.control_plane.generate_plan',return_value=p):result=execute_pipeline('fixture',memory_factory=AuditMemory)
            self.assertEqual('FAILED',result['status']);self.assertTrue(result['steps'][0]['verified'])
            self.assertEqual('actual',file.read_text())
