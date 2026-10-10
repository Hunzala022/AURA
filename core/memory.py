import os
import json
import sqlite3
from typing import List, Dict, Any
from cryptography.fernet import Fernet
import chromadb
from chromadb.config import Settings

# ---------------------------------------------------------
# Milestone 3.8: Encryption Key Management
# ---------------------------------------------------------
KEY_FILE = os.path.join(os.path.dirname(__file__), "..", ".keys", "aura_aes.key")

def get_or_create_key() -> bytes:
    """Gets the existing AES key or creates a new one. Key never leaves device."""
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

# ---------------------------------------------------------
# Milestone 3.5 & 3.8: Encrypted Long-Term Memory
# ---------------------------------------------------------
class MemoryManager:
    def __init__(self, db_path: str = "aura_memory.db", chroma_path: str = "aura_chroma"):
        self.key = get_or_create_key()
        self.fernet = Fernet(self.key)
        
        # SQLite for structured state/session logging
        self.db_path = db_path
        self._init_sqlite()
        
        # ChromaDB for vector-based memory
        self.chroma_client = chromadb.PersistentClient(path=chroma_path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.chroma_client.get_or_create_collection(name="aura_long_term_memory")

    def _encrypt(self, text: str) -> str:
        return self.fernet.encrypt(text.encode()).decode()

    def _decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent_type TEXT,
                encrypted_task TEXT,
                encrypted_result TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT,
                risk_level TEXT,
                encrypted_params TEXT,
                action_status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    # ---- Structured Logs (SQLite) ----
    def log_session(self, agent_type: str, task: str, result: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO session_logs (agent_type, encrypted_task, encrypted_result) VALUES (?, ?, ?)",
            (agent_type, self._encrypt(task), self._encrypt(result))
        )
        conn.commit()
        conn.close()
        
    def log_audit_trail(self, tool_name: str, risk_level: str, params: Dict[str, Any], action_status: str):
        """Milestone 4.5 - Audit trail for high-risk actions."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        enc_params = self._encrypt(json.dumps(params))
        c.execute(
            "INSERT INTO audit_logs (tool_name, risk_level, encrypted_params, action_status) VALUES (?, ?, ?, ?)",
            (tool_name, risk_level, enc_params, action_status)
        )
        conn.commit()
        conn.close()

    # ---- Vector Memory (ChromaDB) ----
    def _get_embedding(self, text: str) -> List[float]:
        from chromadb.utils import embedding_functions
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        return default_ef([text])[0]

    def store_memory(self, memory_id: str, content: str):
        """Stores a memory. Embeds plaintext locally, stores ENCRYPTED document in Chroma."""
        embedding = self._get_embedding(content)
        enc_content = self._encrypt(content)
        
        self.collection.add(
            embeddings=[embedding],
            documents=["[ENCRYPTED_PAYLOAD]"], # Dummy document to avoid plaintext on disk
            metadatas=[{"cipher": enc_content}],
            ids=[memory_id]
        )

    def retrieve_memory(self, query: str, n_results: int = 2) -> List[str]:
        """Retrieves memories by semantic search, then decrypts them."""
        query_emb = self._get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=n_results
        )
        
        decrypted_results = []
        if results['metadatas'] and results['metadatas'][0]:
            for meta in results['metadatas'][0]:
                if meta and "cipher" in meta:
                    decrypted = self._decrypt(meta["cipher"])
                    decrypted_results.append(decrypted)
                    
        return decrypted_results
