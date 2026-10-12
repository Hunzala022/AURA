from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from core.tools import TOOLS, validate_parameters
ToolName = Literal[tuple(TOOLS)]
class PlanStep(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    step: int = Field(ge=1)
    tool: ToolName
    parameters: dict[str, Any]
    reasoning: str
    agent: str | None = None
    @model_validator(mode='after')
    def check_contract(self):
        owner = TOOLS[self.tool].agent
        if self.agent is not None and self.agent != owner:
            raise ValueError('Tool is outside requested agent permissions')
        self.agent = owner
        references = {k:v for k,v in self.parameters.items() if isinstance(v,dict)}
        for key, value in references.items():
            if key not in ('content','text','expected_content','query') or set(value) != {'from_step'} or type(value['from_step']) is not int or value['from_step'] < 1:
                raise ValueError('Only explicit earlier text-result bindings are supported')
        checked = {k:('binding placeholder' if k in references else v) for k,v in self.parameters.items()}
        self.parameters = validate_parameters(self.tool, checked)
        self.parameters.update(references)
        return self
class ToolCallSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    decision: Literal['EXECUTE','CLARIFY','REFUSE','NO_ACTION']
    plan: list[PlanStep] = Field(default_factory=list,max_length=30)
    overall_reasoning: str
    risk: Literal['low','medium','high']
    risk_justification: str
    confidence: float = Field(ge=0,le=1)
    @model_validator(mode='after')
    def check_decision(self):
        if (self.decision=='EXECUTE') != bool(self.plan):
            raise ValueError('Decision and plan disagree')
        if [s.step for s in self.plan] != list(range(1,len(self.plan)+1)):
            raise ValueError('Steps must be consecutive and ordered')
        for step in self.plan:
            for value in step.parameters.values():
                if isinstance(value,dict) and value['from_step'] >= step.step:
                    raise ValueError('Bindings must reference an earlier step')
        return self
