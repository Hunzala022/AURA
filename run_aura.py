import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.control_plane import execute_pipeline

def main():
    print("="*60)
    print(" A.U.R.A. (Air-Gapped Unified Responsive Agent) - Stage 2")
    print("="*60)
    print("Type a command to test the end-to-end execution pipeline.")
    print("Examples:")
    print("  - Create a folder called 'TestDir' on my Desktop.")
    print("  - Read the file C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("  - Write 'Hello AURA' to D:\\test_file.txt")
    print("  - Delete D:\\test_file.txt")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            prompt = input("AURA> ")
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Shutting down...")
                break
            if not prompt.strip():
                continue
                
            execute_pipeline(prompt)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"\n[X] Unexpected Error: {e}")

if __name__ == "__main__":
    main()
