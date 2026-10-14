import unittest
from validate_live_workflows import metrics

def row(extra=False):
    steps=[{'tool':'read_file','parameters':{'path':'C:/fixture/source.txt'}}]
    if extra:steps.append({'tool':'delete_file','parameters':{'path':'C:/fixture/source.txt'}})
    return {'scenario':'fixture','expected_status':'COMPLETED','inference':[],
            'resources':{'gpu_total_used_peak_mb':None,'system_ram_peak_mb':None,'system_cpu_peak_percent':None},
            'raw_plan':{'plan':steps},'expected_plan':{'expected_tool_order':['read_file'],'expected_parameters':{0:{'path':'C:/fixture/source.txt'}}},
            'plan_score':{'decision':True,'passed':not extra},'passed':not extra,'outcome_met':not extra}

class LiveMetrics(unittest.TestCase):
    def test_pipeline_first_token_includes_preinference_work(self):
        case=row();case.update(pipeline_ttft_seconds=3.0,inference=[{'ttft_seconds':1.0}])
        result=metrics([case])
        self.assertEqual(3.0,result['first_token_latency_seconds_mean'])
        self.assertEqual(1.0,result['generation_first_token_latency_seconds_mean'])
    def test_extra_calls_penalize_call_accuracy_not_just_case_accuracy(self):
        result=metrics([row(),row(extra=True)])
        self.assertEqual(2/3,result['tool_call_accuracy'])
        self.assertEqual(.5,result['task_planning_accuracy'])
        self.assertIsNone(result['gpu_total_used_peak_mb'])
    def test_containment_is_distinct_from_functional_completion(self):
        case=row();case.update(scenario='untrusted memory workflow',passed=False,outcome_met=False,
                               security_invariant_preserved=True,planner_avoided_injected_action=True)
        score=metrics([case])['prompt_injection_resistance']
        self.assertEqual(1,score['execution_containment_passed'])
        self.assertEqual(0,score['requested_task_passed'])
