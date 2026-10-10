"""
Stage 2 - Comprehensive Pipeline Tests
Tests: HITL flow, pywinauto UI, policy-level refusal, verification
"""
import sys
import os
import time
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.control_plane import execute_pipeline, generate_plan, TaskStateManager
from core.policy import evaluate_risk, authorize_high_risk_action
from agents.os_agent import TOOL_REGISTRY

# ============================================================
# TEST 1: Low-Risk Auto-Execute (create + verify)
# ============================================================
def test_low_risk():
    print("\n" + "="*60)
    print("TEST 1: Low-Risk Auto-Execute")
    print("="*60)
    
    # Clean up if exists
    test_path = "D:\\AURA_Stage2_Test"
    if os.path.exists(test_path):
        import shutil
        shutil.rmtree(test_path)
    
    execute_pipeline("Create a folder called 'AURA_Stage2_Test' on D:\\ and verify it exists.")
    
    # Post-test verification (independent of model)
    if os.path.exists(test_path):
        print(f"\n[INDEPENDENT CHECK] PASSED: {test_path} exists on disk.")
    else:
        print(f"\n[INDEPENDENT CHECK] FAILED: {test_path} does NOT exist.")

# ============================================================
# TEST 2: HITL Flow (delete_file -> HIGH risk -> approval prompt)
# ============================================================
def test_hitl_flow():
    print("\n" + "="*60)
    print("TEST 2: HITL Approval Flow (Policy-Level Block)")
    print("="*60)
    print("This test BYPASSES the model and directly tests the")
    print("Policy Engine -> HITL -> Execution -> Verification chain.")
    print("="*60)
    
    # Create a dummy file to delete
    test_file = "D:\\AURA_Stage2_Test\\hitl_test.txt"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("This file will be deleted via HITL approval.")
    print(f"[SETUP] Created test file: {test_file}")
    
    # Simulate a model plan that says EXECUTE with delete_file
    tool_name = "delete_file"
    params = {"path": test_file}
    
    # Step 1: Policy Engine evaluates risk
    risk = evaluate_risk(tool_name, params)
    print(f"\n[POLICY ENGINE] Tool: {tool_name} | Risk: {risk}")
    
    if risk == "HIGH":
        print("[POLICY ENGINE] HIGH RISK detected. Triggering HITL...")
        
        # Step 2: HITL approval gate
        authorized = authorize_high_risk_action({
            "tool": tool_name,
            "parameters": params,
            "reasoning": "User requested deletion of a file."
        })
        
        if authorized:
            # Step 3: Execute
            print(f"[EXECUTE] Running {tool_name}...")
            tool_func = TOOL_REGISTRY[tool_name]
            success, result = tool_func(params)
            print(f"[RESULT] Success={success} | {result}")
            
            # Step 4: Verification
            if not os.path.exists(test_file):
                print("[VERIFY] PASSED: File was successfully deleted.")
            else:
                print("[VERIFY] FAILED: File still exists after deletion.")
        else:
            print("[HITL] User DENIED the action. Execution blocked.")
            # Verify file still exists (block worked)
            if os.path.exists(test_file):
                print("[VERIFY] PASSED: File was correctly preserved (block worked).")
            else:
                print("[VERIFY] FAILED: File was deleted despite block!")
    else:
        print(f"[ERROR] Expected HIGH risk, got {risk}")

# ============================================================
# TEST 3: Policy Catches What Model Misses
# ============================================================
def test_policy_override():
    print("\n" + "="*60)
    print("TEST 3: Policy Engine Override (Model says EXECUTE, Policy says FREEZE)")
    print("="*60)
    print("Simulating: Model returned EXECUTE for a dangerous delete_file.")
    print("Policy Engine must independently catch this as HIGH risk.")
    print("="*60)
    
    # These are all cases where model might say EXECUTE but policy must block
    test_cases = [
        {"tool": "delete_file", "params": {"path": "C:\\Windows\\System32\\test.dll"}, "expected_risk": "HIGH"},
        {"tool": "delete_file", "params": {"path": "D:\\safe_file.txt"}, "expected_risk": "HIGH"},  # delete_file is always HIGH
        {"tool": "modify_content", "params": {"path": "config.json", "key": "port"}, "expected_risk": "HIGH"},
        {"tool": "read_file", "params": {"path": "C:\\Users\\Admin\\.ssh\\id_rsa"}, "expected_risk": "HIGH"},
        {"tool": "list_directory", "params": {"path": "D:\\MyFiles"}, "expected_risk": "MEDIUM"},
        {"tool": "get_system_info", "params": {}, "expected_risk": "LOW"},
    ]
    
    passed = 0
    for tc in test_cases:
        risk = evaluate_risk(tc["tool"], tc["params"])
        ok = risk == tc["expected_risk"]
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {tc['tool']}({tc['params']}) -> {risk} (expected {tc['expected_risk']})")
        if ok:
            passed += 1
    
    print(f"\nPolicy Engine: {passed}/{len(test_cases)} cases correct.")

# ============================================================
# TEST 4: pywinauto - Open Notepad, Type, Verify
# ============================================================
def test_pywinauto():
    print("\n" + "="*60)
    print("TEST 4: pywinauto - Open Notepad, Type Text, Verify")
    print("="*60)
    
    # Step 1: Open Notepad
    print("\n[STEP 1] Opening Notepad...")
    success, result = TOOL_REGISTRY.get("open_application", lambda p: (False, "Not found"))({"app_name": "notepad.exe"})
    print(f"  Result: {result}")
    if not success:
        print("[ABORT] Cannot proceed without Notepad.")
        return
    
    time.sleep(2)  # Wait for Notepad to fully load
    
    # Step 2: Read the UI tree
    print("\n[STEP 2] Reading UI tree...")
    success, tree = TOOL_REGISTRY.get("read_ui_tree", lambda p: (False, "Not found"))({"window_title": "Notepad"})
    if success:
        # Print first 15 lines to keep it readable
        lines = tree.split("\n")[:15]
        for line in lines:
            print(f"  {line}")
        if len(tree.split("\n")) > 15:
            print(f"  ... ({len(tree.split(chr(10)))} total elements)")
    else:
        print(f"  [WARN] {tree}")
    
    # Step 3: Type text
    test_text = "Hello from A.U.R.A. Stage 2!"
    print(f"\n[STEP 3] Typing: '{test_text}'")
    success, result = TOOL_REGISTRY.get("type_in_window", lambda p: (False, "Not found"))(
        {"window_title": "Notepad", "text": test_text}
    )
    print(f"  Result: {result}")
    
    time.sleep(1)
    
    # Step 4: Verify the window exists
    print("\n[STEP 4] Verifying window...")
    success, result = TOOL_REGISTRY.get("verify_window", lambda p: (False, "Not found"))(
        {"window_title": "Notepad"}
    )
    print(f"  Result: {result}")
    
    # Step 5: Close Notepad (without saving)
    print("\n[STEP 5] Closing Notepad...")
    try:
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True, timeout=5)
        print("  Notepad closed.")
    except:
        print("  [WARN] Could not close Notepad automatically.")

# ============================================================
# TEST 5: Full Model-Driven Pipeline (Write + Verify)
# ============================================================
def test_write_and_verify():
    print("\n" + "="*60)
    print("TEST 5: Full Pipeline - Write File + Verify")
    print("="*60)
    
    test_file = "D:\\AURA_Stage2_Test\\hello.txt"
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    execute_pipeline(f"Write 'Hello AURA' to {test_file} and verify the file exists.")
    
    # Independent check
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"\n[INDEPENDENT CHECK] File exists. Content: '{content}'")
    else:
        print(f"\n[INDEPENDENT CHECK] FAILED: {test_file} does NOT exist.")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print(" A.U.R.A. Stage 2 - Comprehensive Pipeline Tests")
    print("="*60)
    
    # Tests that don't need the model (fast, deterministic)
    test_policy_override()
    test_hitl_flow()
    test_pywinauto()
    
    # Tests that need the model (slow, ~30-60s each)
    test_low_risk()
    test_write_and_verify()
    
    print("\n" + "="*60)
    print(" ALL TESTS COMPLETE")
    print("="*60)
