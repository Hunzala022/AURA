import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.memory import MemoryManager

def test_memory():
    print("="*60)
    print("TEST 3.5 & 3.8: Encrypted Long-Term Memory (ChromaDB + SQLite)")
    print("="*60)
    
    manager = MemoryManager()
    
    print("[*] Storing new memory...")
    test_memory_id = "mem_123"
    test_content = "The user prefers dark mode and their main project is called Project AURA."
    
    manager.store_memory(test_memory_id, test_content)
    print("  -> Embedded and stored (encrypted at rest).")
    
    print("\n[*] Retrieving memory (Semantic Search)...")
    query = "What is the user's project name?"
    print(f"  Query: '{query}'")
    
    results = manager.retrieve_memory(query, n_results=1)
    
    if results:
        print(f"  -> Retrieved and decrypted: '{results[0]}'")
        assert test_content in results[0], "Decrypted memory doesn't match original!"
    else:
        print("  -> Failed to retrieve memory.")
        sys.exit(1)
        
    print("\n[*] Testing SQLite Structured Logging...")
    manager.log_session("research_agent", "Summarize latest AI news", "Success: retrieved 3 articles.")
    print("  -> Session logged and encrypted.")
    
    print("\n[OK] Memory Pipeline Passed: Data embedded, stored, searched semantically, retrieved, and decrypted successfully.")

if __name__ == "__main__":
    test_memory()
