import json
import requests
from typing import Dict, Any, List

from core.schema import ToolCallSchema
from core.prompt import BASE_SYSTEM_PROMPT
from core.policy import evaluate_risk, authorize_high_risk_action
from agents.os_agent import TOOL_REGISTRY as OS_TOOLS
from agents.browser_agent import TOOL_REGISTRY as BROWSER_TOOLS
from agents.comm_agent import TOOL_REGISTRY as COMM_TOOLS
from agents.research_agent import TOOL_REGISTRY as RESEARCH_TOOLS
from agents.vision_agent import TOOL_REGISTRY as VISION_TOOLS

# Milestone 3.1 - All 5 Agents Registered
SECURITY_TOOLS = {}  # Security agent is the regression checker, no runtime tools

AGENT_REGISTRY = {
    "os_agent": OS_TOOLS,
    "browser_agent": BROWSER_TOOLS,
    "comm_agent": COMM_TOOLS,
    "research_agent": RESEARCH_TOOLS,
    "vision_agent": VISION_TOOLS,
    "security_agent": SECURITY_TOOLS
}

OLLAMA_API = "http://localhost:11434"
MODEL_NAME = "aura-qwen:latest"

class TaskStateManager:
    """Milestone 2.1 - Task state manager."""
    def __init__(self):
        self.current_task = None
        self.plan = []
        self.current_step = 0
        self.history = []

    def load_plan(self, task: str, plan: List[Dict[str, Any]]):
        self.current_task = task
        self.plan = plan
        self.current_step = 0
        self.history.clear()

    def get_next_step(self) -> Dict[str, Any]:
        if self.current_step < len(self.plan):
            return self.plan[self.current_step]
        return None

    def mark_step_complete(self, result: str):
        self.history.append({"step": self.current_step + 1, "result": result})
        self.current_step += 1

def generate_plan(prompt_text: str, memory_context: str = "") -> Dict[str, Any]:
    """Calls the model to generate a plan based on the prompt and retrieved memory."""
    print("[*] Thinking...")
    
    # Inject memory context into prompt
    full_prompt = prompt_text
    if memory_context:
        full_prompt = f"RELEVANT MEMORY:\n{memory_context}\n\nUSER REQUEST:\n{prompt_text}"
        
    try:
        resp = requests.post(
            f"{OLLAMA_API}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": BASE_SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False,
                "format": ToolCallSchema.model_json_schema(),
                "options": {"temperature": 0.1, "num_ctx": 4096}
            },
            timeout=600
        )
        resp.raise_for_status()
        output = resp.json()["message"]["content"]
        parsed = json.loads(output)
        return ToolCallSchema(**parsed).model_dump()
    except Exception as e:
        print(f"[X] Failed to generate plan: {e}")
        return None

def execute_pipeline(user_prompt: str):
    """
    Milestone 2.5 - Full Wire-up (Text -> Plan -> Risk -> Approval -> Execute -> Verify)
    Milestone 3.5 - Memory Retrieval & Injection
    """
    print(f"\nUser Request: {user_prompt}")
    
    # Milestone 3.5 - Setup Memory
    try:
        from core.memory import MemoryManager
        memory = MemoryManager()
        retrieved_memories = memory.retrieve_memory(user_prompt, n_results=2)
        memory_context = "\n".join(retrieved_memories) if retrieved_memories else ""
        if memory_context:
            print("[*] Retrieved relevant memories for context.")
    except Exception as e:
        print(f"[!] Warning: Memory system not available ({e})")
        memory = None
        memory_context = ""
    
    # 1. Generate Plan (Stage 1)
    plan_data = generate_plan(user_prompt, memory_context)
    if not plan_data:
        return

    decision = plan_data.get("decision")
    print(f"\n[Decision] {decision}")
    print(f"[Overall Reasoning] {plan_data.get('overall_reasoning')}")
    
    if decision != "EXECUTE":
        print("[!] Pipeline stopped by model decision.")
        return

    plan_steps = plan_data.get("plan", [])
    if not plan_steps:
        print("[X] Error: Decision was EXECUTE but plan is empty.")
        return

    # 2. Task State Manager
    state_manager = TaskStateManager()
    state_manager.load_plan(user_prompt, plan_steps)

    print(f"\n[*] Executing Plan ({len(plan_steps)} steps):")
    
    # 3. Execution Loop
    final_result = "Success"
    while step_data := state_manager.get_next_step():
        step_num = step_data["step"]
        tool_name = step_data["tool"]
        params = step_data.get("parameters", {})
        
        print(f"\n--- Step {step_num}: {tool_name} ---")
        print(f"Params: {params}")
        
        # Locate tool in registry
        tool_func = None
        active_agent = "unknown"
        for agent_name, tools in AGENT_REGISTRY.items():
            if tool_name in tools:
                tool_func = tools[tool_name]
                active_agent = agent_name
                break
                
        if not tool_func:
            print(f"[X] Tool '{tool_name}' not found in registry. Aborting plan.")
            final_result = "Failed: Tool not found"
            break

        # 4. Risk / Policy Engine Check (Milestone 2.2 & 2.3)
        risk_level = evaluate_risk(tool_name, params)
        print(f"[*] Policy Engine Risk Assessment: {risk_level}")
        
        action_status = "APPROVED_BY_POLICY"
        
        if risk_level == "HIGH":
            # Mandatory HITL
            authorized = authorize_high_risk_action({
                "tool": tool_name,
                "parameters": params,
                "reasoning": step_data.get("reasoning", "No step reasoning provided.")
            })
            if not authorized:
                print("[!] Execution blocked by user.")
                final_result = "Failed: Blocked by user"
                action_status = "DENIED_BY_HITL"
                if memory:
                    memory.log_audit_trail(tool_name, risk_level, params, action_status)
                break
            else:
                action_status = "APPROVED_BY_HITL"
                
        if memory and risk_level in ["HIGH", "MEDIUM"]:
            memory.log_audit_trail(tool_name, risk_level, params, action_status)
        
        # 5. Execute Tool (Milestone 2.4)
        print(f"[*] Executing {tool_name} via {active_agent}...")
        success, result = tool_func(params)
        
        if success:
            print(f"[OK] Success: {result}")
            state_manager.mark_step_complete(result)
        else:
            print(f"[X] Failed: {result}")
            print("[!] Aborting remaining steps due to failure.")
            final_result = f"Failed: {result}"
            break

    print("\n[END] Task Pipeline Complete.")
    
    # Milestone 3.5 - Log the session
    if memory:
        memory.log_session(active_agent if 'active_agent' in locals() else "unknown", user_prompt, final_result)
    
if __name__ == "__main__":
    print("A.U.R.A Control Plane - Stage 2 Testing")
    while True:
        prompt = input("\nEnter command (or 'quit'): ")
        if prompt.lower() in ['quit', 'exit', 'q']:
            break
        execute_pipeline(prompt)
