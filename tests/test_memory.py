import gc,tempfile,unittest,sqlite3
from pathlib import Path
from core.memory import MemoryManager
class Memory(unittest.TestCase):
    def test_real_chroma_and_sqlite_persistence(self):
        # Deterministic test embedding: no remote model downloads.
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root=Path(folder);kwargs={'db_path':root/'memory.db','chroma_path':root/'chroma','key_file':root/'.keys/key','embedding_function':lambda text:[1.0,0.0,0.0]}
            m=MemoryManager(**kwargs)
            m.store_memory('fixture','private persistence fixture')
            m.log_session('os_agent','private task','private result')
            m.log_audit_trail('delete_file','HIGH',{'path':'private path'},'DENIED_BY_HITL')
            again=MemoryManager(**kwargs)
            self.assertEqual(['private persistence fixture'],again.retrieve_memory('query',1))
            with sqlite3.connect(root/'memory.db') as c:
                task=c.execute('SELECT encrypted_task FROM session_logs').fetchone()[0]
                self.assertEqual('private task',again._decrypt(task));self.assertNotIn('private task',task)
                self.assertEqual('DENIED_BY_HITL',c.execute('SELECT action_status FROM audit_logs').fetchone()[0])
            m=None;again=None;gc.collect()
