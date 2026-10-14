import tempfile
import unittest
from pathlib import Path
from core.memory import MemoryManager
from core.human_layer import PersistentRateLimiter
from core.storage_selection import encrypted_paths
from prepare_encrypted_migration import prepare
from activate_encrypted_storage import activate


class Migration(unittest.TestCase):
    def fixture(self, root):
        memory=MemoryManager(root/'aura_memory.db',root/'aura_chroma',root/'.keys/aura_aes.key',lambda _:[1.,0.,0.])
        memory.log_session('fixture','task','result')
        memory.log_audit_trail('delete_file','HIGH',{'path':'fixture'},'DENIED_BY_HITL')
        memory.store_memory('fixture-memory','migration content')
        self.assertTrue(PersistentRateLimiter(root/'.aura-private/communication_limits.db',clock=lambda:100000.).check_limit('fixture'))
        return memory

    def test_complete_rehearsal_explicit_activation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root=Path(folder);memory=self.fixture(root);target=root/'.aura-private/prepared'
            report=prepare(root,target)
            self.assertTrue(report['passed']);self.assertEqual(1,report['quota_records'])
            self.assertIsNone(encrypted_paths(root))
            self.assertFalse(activate(root,target)['activated'])
            self.assertIsNone(encrypted_paths(root))
            self.assertTrue(activate(root,target,True)['activated'])
            self.assertEqual(target/'memory.aes',encrypted_paths(root)['memory'])
            with self.assertRaises(RuntimeError):activate(root,target,True)

    def test_changed_retained_state_requires_new_rehearsal(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root=Path(folder);memory=self.fixture(root);target=root/'.aura-private/prepared'
            self.assertTrue(prepare(root,target)['passed'])
            memory.log_session('fixture','new task','new result')
            with self.assertRaises(RuntimeError):activate(root,target,True)
            self.assertIsNone(encrypted_paths(root))
