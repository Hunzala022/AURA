import unittest
from importlib import import_module
from pydantic import ValidationError
from core.tools import TOOLS,AGENT_REGISTRY
from core.prompt import BASE_SYSTEM_PROMPT
from core.schema import ToolCallSchema
from tests.helpers import plan
class Contracts(unittest.TestCase):
    def test_generation_schema_has_exact_tool_identifiers(self):
        step=ToolCallSchema.model_json_schema()['$defs']['PlanStep']
        self.assertEqual(set(TOOLS),set(step['properties']['tool']['enum']))
        self.assertFalse(step['additionalProperties'])
    def test_every_canonical_identifier_and_parameter_contract(self):
        for name,tool in TOOLS.items():
            with self.subTest(tool=name):
                self.assertIn(name,import_module('agents.'+tool.agent).TOOL_REGISTRY)
                self.assertIn(name+'(',BASE_SYSTEM_PROMPT)
                fields=tool.parameters.model_fields
                params={k:'test' for k,v in fields.items() if v.is_required()}
                parsed=ToolCallSchema.model_validate(plan((name,params)))
                self.assertEqual(parsed.plan[0].agent,tool.agent)
                params['invented']='bad'
                with self.assertRaises(ValidationError):ToolCallSchema.model_validate(plan((name,params)))
    def test_registry_has_no_extra_implementations(self):
        actual={k for a in AGENT_REGISTRY if a!='security_agent' for k in import_module('agents.'+a).TOOL_REGISTRY}
        self.assertEqual(set(TOOLS),actual)
    def test_unknown_tool(self):
        with self.assertRaises(ValidationError):ToolCallSchema.model_validate(plan(('run_command',{})))
    def test_all_fourteen_ghost_names_rejected(self):
        for name in ('click_element','describe_image','extract_text_from_page','extract_text_from_vision','get_system_info','list_processes','modify_content','open_url','read_page','retrieve_memory','retrieve_url','store_memory','type_text','web_search'):
            with self.subTest(tool=name),self.assertRaises(ValidationError):
                ToolCallSchema.model_validate(plan((name,{})))
    def test_agent_mismatch(self):
        p=plan(('read_file',{'path':'x'}));p['plan'][0]['agent']='comm_agent'
        with self.assertRaises(ValidationError):ToolCallSchema.model_validate(p)
    def test_missing_parameter(self):
        with self.assertRaises(ValidationError):ToolCallSchema.model_validate(plan(('write_file',{'path':'x'})))
    def test_wrong_parameter_type(self):
        with self.assertRaises(ValidationError):ToolCallSchema.model_validate(plan(('read_file',{'path':42})))
    def test_decision_and_order(self):
        cases=[plan(decision='EXECUTE'),plan(('read_file',{'path':'x'}),decision='CLARIFY')]
        p=plan(('read_file',{'path':'x'}));p['plan'][0]['step']=2;cases.append(p)
        for p in cases:
            with self.assertRaises(ValidationError):ToolCallSchema.model_validate(p)
