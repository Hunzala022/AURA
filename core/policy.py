import os
from typing import Dict, Any

def authorize_high_risk_action(action_details: Dict[str, Any]) -> bool:
    """
    Milestone 2.3 - Simulated HITL approval interface.
    For FYP-1, this is a terminal prompt. For FYP-2, it will hit the biometric Pi.
    """
    print("\n" + "="*50)
    print("!!! HIGH RISK ACTION DETECTED !!!")
    print("="*50)
    print(f"Tool: {action_details.get('tool')}")
    print("Parameters:")
    for k, v in action_details.get('parameters', {}).items():
        print(f"  - {k}: {v}")
    print(f"Reasoning: {action_details.get('reasoning')}")
    print("="*50)
    
    while True:
        resp = input("Authorize this action? (y/n/pin): ").strip().lower()
        if resp in ['y', 'yes']:
            print("[OK] Action authorized.")
            return True
        elif resp in ['n', 'no']:
            print("[BLOCK] Action denied.")
            return False
        elif resp.isdigit() and len(resp) >= 4:
            # Simulated PIN check
            print("[OK] PIN accepted. Action authorized.")
            return True
        else:
            print("Invalid input. Please enter 'y', 'n', or a mock PIN (e.g. 1234).")

def evaluate_risk(tool_name: str, parameters: Dict[str, Any]) -> str:
    """
    Milestone 2.2 - Risk / Policy Engine.
    Hardcoded deterministic risk classification.
    """
    # 1. Inherently High Risk Tools
    if tool_name in ["delete_file", "ssh_deploy", "modify_content", "type_text"]:
        return "HIGH"
        
    # 2. Parameter-based Risk Analysis
    if tool_name in ["read_file", "write_file", "list_directory", "move_file", "copy_file", "create_folder"]:
        path = parameters.get("path") or parameters.get("source") or parameters.get("destination") or ""
        path = str(path).lower()
        
        # Accessing system folders or sensitive files is HIGH risk
        high_risk_paths = ["c:\\windows", "system32", ".ssh", "id_rsa", "password", "secret", "c:\\"]
        for hr_path in high_risk_paths:
            if hr_path in path:
                return "HIGH"
                
    # 3. Inherently Low Risk Tools (assuming parameters passed checks)
    if tool_name in ["get_system_info", "list_processes"]:
        return "LOW"
        
    # Default fallback: Treat unknown things as MEDIUM to force review but not hard block
    return "MEDIUM"
