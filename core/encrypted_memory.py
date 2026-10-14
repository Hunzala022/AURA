"""Whole-store AES-256 memory backend, activated by private storage selection.

All retained records, vectors and retrieval metadata live in one authenticated
encrypted SQLite snapshot. Chroma indexes are ephemeral and rebuilt in RAM.
"""
import json
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings

from core.encrypted_storage import EncryptedSQLite, storage_key


class EncryptedMemoryManager:
    def __init__(self, db_path, key_file, embedding_function=None):
        self.db_path = Path(db_path)
        self.embedding_function = embedding_function
        self.store = EncryptedSQLite(self.db_path,
                                    storage_key(key_file, (self.db_path, self.db_path.parent/'quota.aes')), 'memory')
        with self.store.transaction(write=True) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    agent_type TEXT, task TEXT, result TEXT);
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    tool_name TEXT, risk_level TEXT, params TEXT, action_status TEXT);
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY, content TEXT NOT NULL,
                    embedding TEXT NOT NULL, metadata TEXT NOT NULL);
            ''')

    def log_session(self, agent_type, task, result):
        with self.store.transaction(write=True) as db:
            db.execute('INSERT INTO session_logs(agent_type,task,result) VALUES (?,?,?)',
                       (agent_type, task, result))

    def log_audit_trail(self, tool_name, risk_level, params, action_status):
        with self.store.transaction(write=True) as db:
            db.execute('INSERT INTO audit_logs(tool_name,risk_level,params,action_status) VALUES (?,?,?,?)',
                       (tool_name, risk_level, json.dumps(params), action_status))

    def _get_embedding(self, text):
        if self.embedding_function is not None:
            return list(self.embedding_function(text))
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        return list(DefaultEmbeddingFunction()([text])[0])

    def store_memory(self, memory_id, content):
        embedding = [float(value) for value in self._get_embedding(content)]
        with self.store.transaction(write=True) as db:
            # Match Chroma add semantics: an existing identity is not overwritten.
            db.execute('INSERT OR IGNORE INTO memories VALUES (?,?,?,?)',
                       (memory_id, content, json.dumps(embedding), '{}'))

    def retrieve_memory(self, query, n_results=2):
        if not isinstance(n_results, int) or n_results < 1:
            raise ValueError('A positive result count is required')
        with self.store.transaction() as db:
            records = db.execute('SELECT id,content,embedding FROM memories ORDER BY id').fetchall()
        if not records:
            return []
        client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        name = 'aura_ephemeral_' + uuid.uuid4().hex
        collection = client.create_collection(name=name, embedding_function=None)
        try:
            collection.add(ids=[r[0] for r in records], documents=[r[1] for r in records],
                           embeddings=[json.loads(r[2]) for r in records])
            found = collection.query(query_embeddings=[[float(value) for value in self._get_embedding(query)]],
                                     n_results=min(n_results, len(records)), include=['documents'])
            return found['documents'][0]
        finally:
            client.delete_collection(name)

    def export_records(self):
        """In-memory migration verification only. Never log the returned values."""
        with self.store.transaction() as db:
            return {table: db.execute(f'SELECT * FROM {table} ORDER BY id').fetchall()
                    for table in ('session_logs', 'audit_logs', 'memories')}

    def import_records(self, records):
        """One transaction into an empty target; preserves IDs and timestamps."""
        with self.store.transaction(write=True) as db:
            for table, columns in (('session_logs', 5), ('audit_logs', 6), ('memories', 4)):
                if db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]:
                    raise ValueError('Migration target must be empty')
                db.executemany(f'INSERT INTO {table} VALUES ({",".join("?" for _ in range(columns))})',
                               records[table])
