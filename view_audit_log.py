import sqlite3
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.memory import MemoryManager
from core.control_plane import execute_pipeline

def view_audit_log():
    mem = MemoryManager()
    conn = sqlite3.connect(mem.db_path)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, tool_name, risk_level, encrypted_params, action_status FROM audit_logs")
    rows = c.fetchall()
    
    print("\n--- A.U.R.A Audit Log ---")
    if not rows:
        print("No audit logs found.")
        return
        
    for r in rows:
        try:
            params_str = mem._decrypt(r[4])
        except:
            params_str = "<decryption failed>"
            
        print(f"[{r[1]}] Tool: {r[2]} | Risk: {r[3]} | Status: {r[5]}")
        print(f"  Params: {params_str}")
        
if __name__ == "__main__":
    view_audit_log()
