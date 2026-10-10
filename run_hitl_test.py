import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.control_plane import execute_pipeline

def test_pipeline():
    # Model should say EXECUTE, Policy Engine should say HIGH risk, and prompt for HITL.
    prompt = "Delete the file D:\\temp.txt"
    print("Testing Pipeline with HITL test prompt:")
    print(f"'{prompt}'")
    execute_pipeline(prompt)

if __name__ == "__main__":
    test_pipeline()
