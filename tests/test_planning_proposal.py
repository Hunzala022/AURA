import unittest
from core.planning_proposal import compile_proposal

class ProposalCompilation(unittest.TestCase):
    def test_only_derived_metadata_changes(self):
        raw={'decision':'EXECUTE','steps':[{'action':'copy_file','arguments':{'source':'a','destination':'b'}}]}
        plan=compile_proposal(raw)
        self.assertEqual('copy_file',plan['plan'][0]['tool'])
        self.assertEqual({'source':'a','destination':'b'},plan['plan'][0]['parameters'])
        self.assertEqual('os_agent',plan['plan'][0]['agent'])
    def test_invalid_parameters_decisions_and_forward_bindings_still_reject(self):
        for raw in [
            {'decision':'EXECUTE','steps':[{'action':'browser_click','arguments':{'url':'https://sample.test'}}]},
            {'decision':'CLARIFY','steps':[{'action':'read_file','arguments':{'path':'a'}}]},
            {'decision':'EXECUTE','steps':[{'action':'write_file','arguments':{'path':'a','content':{'from_step':1}}}]},
        ]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):compile_proposal(raw)
