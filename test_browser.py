import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents.browser_agent import TOOL_REGISTRY

def test_browser():
    print("="*60)
    print("TEST 3.2: Browser Agent Tools & Sanitization")
    print("="*60)
    
    # We will navigate to a known safe page (like example.com) 
    print("[*] Navigating to example.com...")
    success, result = TOOL_REGISTRY["navigate_and_read"]({"url": "http://example.com"})
    
    if not success:
        print(f"[X] Browser navigation failed: {result}")
        sys.exit(1)
        
    print("[*] Returned Sanitized Content:")
    print(result.encode("ascii", "ignore").decode())
    
    # Verify sanitization stripped HTML tags
    assert "<html" not in result.lower(), "HTML tags were not stripped!"
    assert "example domain" in result.lower(), "Expected text not found on example.com!"
    
    print("\n[OK] Browser Agent test passed (headless Playwright + Sanitization).")

if __name__ == "__main__":
    test_browser()
