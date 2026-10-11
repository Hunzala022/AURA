import unittest
from pathlib import Path
import tempfile
from core.policy import evaluate_risk
class Policy(unittest.TestCase):
    def test_execution_code_requires_approval(self):
        from core.policy import WORKSPACE
        self.assertEqual('HIGH',evaluate_risk('write_file',{'path':str(WORKSPACE/'core/policy.py'),'content':'replacement'}))
        self.assertEqual('HIGH',evaluate_risk('write_file',{'path':str(WORKSPACE/'core/policy.py')+'::$DATA','content':'replacement'}))
    def test_both_endpoints_and_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            benign=str(Path(tmp)/'ordinary.txt')
            destinations=['C:/Windows/System32/x','c:/WINDOWS/system32/x','C:/Windows/a/../System32/x',str(Path(tmp)/'.keys/x'),str(Path(tmp)/'../outside.txt')]
            for tool in ('copy_file','move_file'):
                for danger in destinations:
                    for source,dest in ((benign,danger),(danger,benign),(danger,danger)):
                        with self.subTest(tool=tool,source=source,dest=dest):
                            self.assertEqual('HIGH',evaluate_risk(tool,{'source':source,'destination':dest},workspace=tmp))
            self.assertEqual('MEDIUM',evaluate_risk('copy_file',{'source':benign,'destination':str(Path(tmp)/'other')},workspace=tmp))
    def test_unknown_fails_closed(self):
        with self.assertRaises(PermissionError):evaluate_risk('invented',{})
    def test_exfiltration_and_ui_require_approval(self):
        for name in ('send_message','browser_fill','browser_click','navigate_and_read','type_in_window','open_application'):
            self.assertEqual('HIGH',evaluate_risk(name,{}))
