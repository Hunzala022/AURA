import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.control_plane import execute_pipeline

def test_pipeline():
    prompt = "Create a folder called 'AURA_Test' on D:\\ and then verify it exists."
    print("Testing Pipeline with prompt:")
    print(f"'{prompt}'")
    execute_pipeline(prompt)

if __name__ == "__main__":
    test_pipeline()
