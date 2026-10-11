"""Canonical contracts; importing this catalog never opens desktop apps."""
from dataclasses import dataclass
from importlib import import_module
from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints, create_model
Text = Annotated[str, StringConstraints(min_length=1)]
class Parameters(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
@dataclass(frozen=True)
class Tool:
    agent: str
    parameters: type[BaseModel]
    def execute(self, name, parameters):
        return import_module('agents.' + self.agent).TOOL_REGISTRY[name](parameters)
TOOLS = {}
def add(agent, name, required, **optional):
    fields = {k: (Text, ...) for k in required.split()}
    fields.update(optional)
    TOOLS[name] = Tool(agent, create_model(name + 'Parameters', __base__=Parameters, **fields))
for name in ('list_directory','read_file','delete_file','create_folder'):
    add('os_agent', name, 'path')
add('os_agent','write_file','path',content=(str,...))
for name in ('copy_file','move_file'): add('os_agent',name,'source destination')
add('os_agent','verify_file','path',expected_content=(str | None,None))
add('os_agent','open_application','app_name window_title')
add('os_agent','type_in_window','window_title text')
add('os_agent','read_ui_tree','window_title')
add('os_agent','click_ui_element','window_title element_name expected_element')
add('os_agent','verify_window','window_title',expected_text=(str,''))
add('browser_agent','navigate_and_read','url')
add('browser_agent','browser_click','url selector expected_selector')
add('browser_agent','browser_fill','url selector',text=(str,...))
add('comm_agent','send_message','app_name contact text recipient_control_name',search_bar_name=(Text,'Search'),message_box_name=(Text,'Type a message'))
add('comm_agent','read_latest_message','app_name')
add('research_agent','search_files_by_name','directory pattern')
add('research_agent','search_files_by_content','directory query',extension=(str,'.txt'))
add('vision_agent','vision_locate_element','window_title element_description')
add('vision_agent','capture_screenshot','output_path')
AGENT_REGISTRY = {}
for name, tool in TOOLS.items():
    def dispatch(parameters, name=name, tool=tool):
        return tool.execute(name, parameters)
    AGENT_REGISTRY.setdefault(tool.agent,{})[name] = dispatch
AGENT_REGISTRY['security_agent'] = {}
def validate_parameters(name, values):
    if name not in TOOLS: raise ValueError('Unknown tool')
    return TOOLS[name].parameters.model_validate(values).model_dump(exclude_none=True)
def tool_catalog():
    rows=[]
    for name,tool in TOOLS.items():
        signature=', '.join(k+('' if v.is_required() else '?') for k,v in tool.parameters.model_fields.items())
        rows.append(f'- {tool.agent}: {name}({signature})')
    return '\n'.join(rows)
