import json,unittest
from unittest.mock import Mock,patch
from core.control_plane import generate_plan
from tests.helpers import proposal as plan

class PlanRepair(unittest.TestCase):
    def response(self,raw):
        r=Mock();r.iter_lines.return_value=[json.dumps({'message':{'content':json.dumps(raw)},'done':True}).encode()];return r
    def test_one_contract_repair_with_no_effects(self):
        invalid=plan(('read_file',{}));valid=plan(('read_file',{'path':'fixture'}))
        with patch('core.control_plane.requests.post',side_effect=[self.response(invalid),self.response(valid)]) as call:
            result=generate_plan('read fixture')
            self.assertEqual('read_file',result['plan'][0]['tool']);self.assertEqual(2,call.call_count)
            self.assertIn('Contract errors',call.call_args.kwargs['json']['messages'][-1]['content'])
    def test_repair_failure_stops_without_unbounded_retry(self):
        invalid=plan(('read_file',{}))
        with patch('core.control_plane.requests.post',return_value=self.response(invalid)) as call:
            self.assertIsNone(generate_plan('read fixture'));self.assertEqual(2,call.call_count)
    def test_valid_but_wrong_plan_is_not_silently_gold_corrected(self):
        with patch('core.control_plane.requests.post',return_value=self.response(plan(('copy_file',{'source':'a','destination':'b'})))) as call:
            result=generate_plan('move a to b')
            self.assertEqual('copy_file',result['plan'][0]['tool']);self.assertEqual(1,call.call_count)
