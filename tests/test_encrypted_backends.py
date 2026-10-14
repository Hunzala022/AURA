import hashlib
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from core.encrypted_memory import EncryptedMemoryManager
from core.encrypted_limits import EncryptedRateLimiter


class EncryptedBackends(unittest.TestCase):
    def test_numpy_embedding_query_roundtrip(self):
        import numpy as np
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root=Path(folder)
            kwargs=dict(db_path=root/'memory.aes',key_file=root/'key.dpapi',
                        embedding_function=lambda _:np.array([1.,0.,0.],dtype=np.float32))
            memory=EncryptedMemoryManager(**kwargs)
            memory.store_memory('numpy-fixture','retained query content')
            self.assertEqual(['retained query content'],EncryptedMemoryManager(**kwargs).retrieve_memory('query'))

    def test_real_pipeline_audits_before_approval_and_preserves_denied_file(self):
        from core.control_plane import execute_pipeline
        from tests.helpers import plan
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root=Path(folder);path=root/'fixture.txt';path.write_text('preserve')
            memory=EncryptedMemoryManager(root/'memory.aes',root/'key.dpapi',lambda _:[1.,0.])
            def deny(action):
                self.assertEqual('preserve',path.read_text())
                self.assertEqual('ATTEMPTED',memory.export_records()['audit_logs'][-1][-1])
                return False
            with patch('core.control_plane.generate_plan',return_value=plan(('delete_file',{'path':str(path)}))),patch('core.control_plane.authorize_high_risk_action',side_effect=deny):
                result=execute_pipeline('delete fixture',memory_factory=lambda:memory,allowed_agents={'os_agent'})
            self.assertEqual('BLOCKED',result['status']);self.assertEqual('preserve',path.read_text())
            reopened=EncryptedMemoryManager(root/'memory.aes',root/'key.dpapi',lambda _:[1.,0.])
            self.assertEqual(['ATTEMPTED','DENIED_BY_HITL'],[r[-1] for r in reopened.export_records()['audit_logs']])
            self.assertEqual(1,len(reopened.export_records()['session_logs']))

    def test_missing_shared_key_never_replaces_key_for_other_store(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'memory.aes').write_bytes(b'retained encrypted state')
            limits=EncryptedRateLimiter(root/'quota.aes',root/'missing.dpapi')
            self.assertFalse(limits.check_limit('fixture'))
            self.assertFalse((root/'missing.dpapi').exists())
    def test_complete_memory_restart_retrieval_and_metadata_confidentiality(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            kwargs = dict(db_path=root/'memory.aes', key_file=root/'key.dpapi',
                          embedding_function=lambda text: [1., 0., 0.])
            memory = EncryptedMemoryManager(**kwargs)
            memory.log_session('private-agent-canary', 'private-task-canary', 'private-result-canary')
            memory.log_audit_trail('private-tool-canary', 'HIGH', {'path': 'private-path-canary'}, 'PRIVATE_STATUS')
            memory.store_memory('private-id-canary', 'private-content-canary')
            expected = memory.export_records()
            reopened = EncryptedMemoryManager(**kwargs)
            self.assertEqual(expected, reopened.export_records())
            self.assertEqual(['private-content-canary'], reopened.retrieve_memory('query'))
            for path in root.rglob('*'):
                if path.is_file():
                    data = path.read_bytes()
                    for canary in (b'private-', b'PRIVATE_STATUS', b'SQLite format 3', b'[1.0, 0.0, 0.0]'):
                        self.assertNotIn(canary, data)
            self.assertFalse((root/'chroma').exists())

    def test_import_preserves_complete_records_and_rejects_nonempty_target(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            memory = EncryptedMemoryManager(root/'memory.aes', root/'key.dpapi', lambda _: [1., 0.])
            records = {'session_logs': [(7, '2026-10-13 00:00:00', 'os', 'task', 'result')],
                       'audit_logs': [(9, '2026-10-13 00:00:00', 'write_file', 'HIGH', '{"path": "fixture"}', 'DENIED')],
                       'memories': [('m', 'content', '[1.0, 0.0]', '{"source":"retained"}')]}
            memory.import_records(records)
            self.assertEqual(records, memory.export_records())
            with self.assertRaises(ValueError):
                memory.import_records(records)
            self.assertEqual(records, memory.export_records())
            memory.log_session('os', 'next', 'result')
            self.assertEqual(8, memory.export_records()['session_logs'][-1][0])

    def test_quota_restart_concurrency_corruption_and_rollback_clock(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            kwargs = dict(path=root/'quota.aes', key_file=root/'key.dpapi', hourly=20,
                          daily=2, global_daily=3, clock=lambda: 100000.)
            limiter = EncryptedRateLimiter(**kwargs)
            with ThreadPoolExecutor(max_workers=6) as pool:
                outcomes = list(pool.map(lambda i: EncryptedRateLimiter(**kwargs).check_limit(str(i)), range(12)))
            self.assertEqual(3, sum(outcomes))
            self.assertEqual(3, len(EncryptedRateLimiter(**kwargs).export_attempts()))
            self.assertFalse(EncryptedRateLimiter(**{**kwargs, 'clock': lambda: 90000.}).check_limit('x'))
            self.assertFalse(EncryptedRateLimiter(**kwargs).check_limit('x'))
            data = limiter.path.read_bytes()
            self.assertNotIn(hashlib.sha256(b'0').hexdigest().encode(), data)
            limiter.path.write_bytes(data[:-1]+bytes([data[-1]^1]))
            self.assertFalse(EncryptedRateLimiter(**kwargs).check_limit('x'))

    def test_imported_quota_limits_survive_restart_and_expire_normally(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            kwargs = dict(path=root/'quota.aes', key_file=root/'key.dpapi', daily=1, clock=lambda:100001.)
            limiter = EncryptedRateLimiter(**kwargs)
            rows = [(hashlib.sha256(b'fixture').hexdigest(), 100000.)]
            limiter.import_attempts(rows)
            self.assertEqual(rows, limiter.export_attempts())
            self.assertFalse(EncryptedRateLimiter(**kwargs).check_limit(' FIXTURE '))
            self.assertTrue(EncryptedRateLimiter(**{**kwargs, 'clock':lambda:186401.}).check_limit('fixture'))


if __name__ == '__main__':
    unittest.main()
