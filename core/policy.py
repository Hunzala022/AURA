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
    Milestone 2.2 / 3.9 - Risk / Policy Engine (updated for all Stage 3 agents).
    Hardcoded deterministic risk classification. No LLM involved here.
    """
    # -------------------------------------------------------
    # 1. Inherently HIGH Risk Tools (any parameters)
    # -------------------------------------------------------
    HIGH_RISK_TOOLS = [
        "delete_file",
        "ssh_deploy",
        "modify_content",
        "type_text",
        "send_message",            # Comm Agent — sends data externally
    ]
    if tool_name in HIGH_RISK_TOOLS:
        return "HIGH"

    # -------------------------------------------------------
    # 2. Parameter-based Risk (OS tools)
    # -------------------------------------------------------
    if tool_name in ["read_file", "write_file", "list_directory",
                     "move_file", "copy_file", "create_folder"]:
        import os
        path = (parameters.get("path") or parameters.get("source")
                or parameters.get("destination") or "")
        path = str(path).replace("/", "\\").lower()
        
        try:
            path = os.path.normpath(path)
        except:
            pass

        high_risk_paths = ["c:\\windows", "system32", ".ssh",
                           "id_rsa", "password", "secret", "c:\\"]
        for hr_path in high_risk_paths:
            if hr_path in path:
                return "HIGH"

    # -------------------------------------------------------
    # 3. Research Agent — content search for sensitive keywords = HIGH
    # -------------------------------------------------------
    if tool_name == "search_files_by_content":
        query = str(parameters.get("query", "")).lower()
        sensitive_terms = ["password", "secret", "token", "api_key", "id_rsa", "credential"]
        for term in sensitive_terms:
            if term in query:
                return "HIGH"

    # -------------------------------------------------------
    # 4. Inherently LOW Risk Tools
    # -------------------------------------------------------
    LOW_RISK_TOOLS = [
        "get_system_info",
        "list_processes",
        "read_latest_message",     # Comm Agent — read only
        "capture_screenshot",      # Vision Agent — read only
    ]
    if tool_name in LOW_RISK_TOOLS:
        return "LOW"

    # -------------------------------------------------------
    # 5. Default: MEDIUM (requires logging but no HITL)
    # -------------------------------------------------------
    return "MEDIUM"
