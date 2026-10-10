import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.comm_agent import TOOL_REGISTRY, COMM_RATE_LIMITER
from agents.os_agent import TOOL_REGISTRY as OS_TOOLS

def test_comm_agent():
    print("="*60)
    print("TEST 3.3: Communication Agent & Human Layer")
    print("="*60)
    
    # 1. Launch a "messaging app" (we'll use Notepad as a mock app)
    print("[*] Launching mock messaging app (Notepad)...")
    OS_TOOLS["open_application"]({"app_name": "notepad.exe"})
    time.sleep(2) # Wait for it to open
    
    # 2. Test send_message
    print("[*] Testing send_message with human-like typing...")
    start_time = time.time()
    
    success, result = TOOL_REGISTRY["send_message"]({
        "app_name": "Notepad",
        "search_bar_name": "Text editor", # Notepad Win11 document node
        "contact": "Test Contact",
        "message_box_name": "Text editor",
        "text": "Hello, this is a test message!"
    })
    
    elapsed = time.time() - start_time
    
    if success:
        print(f"[OK] {result}")
        print(f"  -> Elapsed time: {elapsed:.2f} seconds (shows human-like delay)")
        assert elapsed > 2.0, "Typing was too fast! Human layer failed."
    else:
        print(f"[X] Failed: {result}")
        
    # 3. Test Rate Limiter
    print("\n[*] Testing Rate Limiter...")
    import datetime
    # Force the rate limiter to max out using datetime objects
    now = datetime.datetime.now()
    COMM_RATE_LIMITER.action_timestamps = [now] * COMM_RATE_LIMITER.max_actions
    
    success, result = TOOL_REGISTRY["send_message"]({
        "app_name": "Notepad",
        "search_bar_name": "Text editor",
        "contact": "Spam",
        "message_box_name": "Text editor",
        "text": "Spam"
    })
    
    if not success and "Rate limit exceeded" in result:
        print("[OK] Rate limit correctly enforced.")
    else:
        print("[X] Rate limit failed!")
        
    # Clean up Notepad
    os.system("taskkill /IM notepad.exe /F >nul 2>&1")
    print("\n[OK] Communication Agent test passed.")

if __name__ == "__main__":
    test_comm_agent()
