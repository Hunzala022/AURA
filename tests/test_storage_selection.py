import json
import tempfile
import unittest
from pathlib import Path
from core.storage_selection import encrypted_paths


class StorageSelection(unittest.TestCase):
    def test_missing_marker_uses_legacy_but_invalid_selection_never_falls_back(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);private=root/'.aura-private';private.mkdir()
            self.assertIsNone(encrypted_paths(root))
            marker=private/'storage-selection.json'
            for content in ('broken', '{"version":2,"directory":".aura-private/new"}',
                            '{"version":1,"directory":"../outside"}'):
                marker.write_text(content)
                with self.assertRaises(ValueError):encrypted_paths(root)
            marker.write_text(json.dumps({'version':1,'directory':'.aura-private/new'}))
            with self.assertRaises(RuntimeError):encrypted_paths(root)
            target=private/'new';target.mkdir()
            for name in ('memory.aes','quota.aes','aes256-key.dpapi'):(target/name).write_bytes(b'fixture')
            self.assertEqual(target/'memory.aes',encrypted_paths(root)['memory'])
