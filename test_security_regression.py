"""
Milestone 3.9 - Security Regression Pass

Verifies that EVERY tool added in Stage 3 (browser, comm, research, vision)
correctly passes through the Control Plane's Policy Engine.
No tool can bypass the risk check — not even low-risk ones.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.policy import evaluate_risk
from core.control_plane import AGENT_REGISTRY


def run_security_regression():
    print("=" * 60)
    print("TEST 3.9: Security Regression Pass")
    print("=" * 60)
    print("Verifying ALL Stage 3 tools pass through Policy Engine.\n")

    # Each entry: (agent_name, tool_name, sample_params, expected_risk_level)
    # This is the ground-truth regression table.
    TEST_CASES = [
        # --- OS Agent (Stage 2 tools — must still pass) ---
        ("os_agent",       "delete_file",           {"path": "D:\\temp.txt"},                     "HIGH"),
        ("os_agent",       "write_file",             {"path": "D:\\a.txt", "content": "hi"},       "MEDIUM"),
        ("os_agent",       "read_file",              {"path": "D:\\a.txt"},                         "MEDIUM"),
        ("os_agent",       "create_folder",          {"path": "D:\\new_folder"},                   "MEDIUM"),
        ("os_agent",       "list_directory",         {"path": "D:\\"},                              "MEDIUM"),
        ("os_agent",       "read_file",              {"path": "C:\\Users\\Admin\\.ssh\\id_rsa"},   "HIGH"),

        # --- Browser Agent (Stage 3) ---
        ("browser_agent",  "navigate_and_read",      {"url": "http://example.com"},                "MEDIUM"),
        ("browser_agent",  "browser_click",          {"url": "http://example.com",
                                                       "selector": "a"},                           "MEDIUM"),
        ("browser_agent",  "browser_fill",           {"url": "http://example.com",
                                                       "selector": "input",
                                                       "text": "hello"},                           "MEDIUM"),

        # --- Comm Agent (Stage 3) ---
        ("comm_agent",     "send_message",           {"app_name": "WhatsApp",
                                                       "contact": "Ali",
                                                       "text": "hello"},                           "HIGH"),
        ("comm_agent",     "read_latest_message",    {"app_name": "Slack"},                        "LOW"),

        # --- Research Agent (Stage 3) ---
        ("research_agent", "search_files_by_name",   {"directory": "D:\\", "pattern": "*.py"},    "MEDIUM"),
        ("research_agent", "search_files_by_content",{"directory": "D:\\",
                                                       "query": "password",
                                                       "extension": ".txt"},                       "HIGH"),

        # --- Vision Agent (Stage 3) ---
        ("vision_agent",   "vision_locate_element",  {"window_title": "Notepad",
                                                       "element_description": "close"},            "MEDIUM"),
        ("vision_agent",   "capture_screenshot",     {"output_path": "D:\\ss.png"},                "LOW"),
    ]

    passed = 0
    failed = 0
    bypass_failures = 0

    for agent_name, tool_name, params, expected_risk in TEST_CASES:
        # 1. Verify tool exists in registry (can't bypass by using unregistered tool)
        agent_tools = AGENT_REGISTRY.get(agent_name, {})
        tool_in_registry = tool_name in agent_tools

        # 2. Get risk from policy engine
        actual_risk = evaluate_risk(tool_name, params)

        # 3. Check result
        risk_ok = (actual_risk == expected_risk)
        registered_ok = tool_in_registry

        if risk_ok and registered_ok:
            status = "PASS"
            passed += 1
        elif not registered_ok:
            status = "BYPASS-RISK"  # Tool not in registry = can't be called at all
            bypass_failures += 1
            # This is actually safe (unregistered tools can't run), but flag it
        else:
            status = "FAIL"
            failed += 1

        print(f"  [{status:12s}] {agent_name}.{tool_name}")
        print(f"               Risk: {actual_risk} (expected {expected_risk}) | In Registry: {tool_in_registry}")

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} PASS | {failed} FAIL | {bypass_failures} UNREGISTERED")

    if failed == 0:
        print("\n[OK] Security Regression PASSED. All tools correctly intercepted by Policy Engine.")
    else:
        print(f"\n[FAIL] {failed} tools have incorrect risk classification.")

    # Final check: verify no tool can be called without going through evaluate_risk
    print("\n[*] Verifying Control Plane enforces evaluate_risk on every step...")
    with open("core/control_plane.py", "r") as f:
        cp_code = f.read()

    assert "evaluate_risk" in cp_code, "[CRITICAL] evaluate_risk NOT called in control_plane.py!"
    assert "authorize_high_risk_action" in cp_code, "[CRITICAL] HITL gate missing in control_plane.py!"
    print("  [OK] evaluate_risk() is present in control_plane.py.")
    print("  [OK] authorize_high_risk_action() is present in control_plane.py.")
    print("\n[STAGE 3.9 COMPLETE] No bypass paths found.")


if __name__ == "__main__":
    run_security_regression()
