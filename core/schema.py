from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal

class PlanStep(BaseModel):
    step: int = Field(..., description="The step number in the plan (1-indexed).")
    tool: str = Field(..., description="The exact name of the tool to execute.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters required by the tool.")
    reasoning: str = Field(..., description="Why this step is necessary.")

class ToolCallSchema(BaseModel):
    decision: Literal["EXECUTE", "CLARIFY", "REFUSE", "NO_ACTION"] = Field(
        ..., 
        description="Your decision on how to handle the prompt."
    )
    plan: List[PlanStep] = Field(
        default_factory=list, 
        description="A list of steps to execute. Must be empty if decision is CLARIFY, REFUSE, or NO_ACTION."
    )
    overall_reasoning: str = Field(
        ..., 
        description="Explanation of why this plan was chosen, or why clarification/refusal is needed."
    )
    risk: Literal["low", "medium", "high"] = Field(
        ..., 
        description="Risk level of the requested action."
    )
    risk_justification: str = Field(
        ..., 
        description="Why this risk level was assigned."
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score between 0.0 and 1.0."
    )
