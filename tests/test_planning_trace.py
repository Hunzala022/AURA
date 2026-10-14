import json
import unittest
from unittest.mock import Mock, patch
from core.control_plane import generate_plan
from core.planning_trace import collect_planning_trace
from tests.helpers import proposal as plan


class PlanningTrace(unittest.TestCase):
    def test_stream_timing_and_scope_are_real_and_opt_in(self):
        raw=json.dumps(plan(('read_file',{'path':'fixture'})))
        response=Mock()
        response.iter_lines.return_value=[json.dumps({'message':{'content':raw[:15]}}).encode(),
                                         json.dumps({'message':{'content':raw[15:]},'done':True,'eval_count':10,'eval_duration':2_000_000_000}).encode()]
        with collect_planning_trace() as trace,patch('core.control_plane.requests.post',return_value=response):
            self.assertIsNotNone(generate_plan('read fixture'))
        self.assertEqual(1,len(trace));self.assertGreaterEqual(trace[0]['ttft_seconds'],0)
        self.assertEqual(5,trace[0]['tokens_per_second']);response.close.assert_called_once()
        with collect_planning_trace() as other:
            self.assertEqual([],other)
    def test_incomplete_stream_cannot_become_a_plan(self):
        response=Mock();response.iter_lines.return_value=[json.dumps({'message':{'content':json.dumps(plan(decision='NO_ACTION'))}}).encode()]
        with collect_planning_trace() as trace,patch('core.control_plane.requests.post',return_value=response):
            self.assertIsNone(generate_plan('hello'))
        self.assertEqual('ValueError',trace[0]['error']);response.close.assert_called_once()
