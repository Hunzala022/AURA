"""Isolated containment checks; never open the user's live memory stores."""
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from core.key_management import get_or_create_key


class LocalKeyTests(unittest.TestCase):
    def test_fresh_install_and_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.keys' / 'aura_aes.key'
            stores = [Path(folder) / 'aura_memory.db', Path(folder) / 'aura_chroma']
            first = get_or_create_key(path, stores)
            self.assertEqual(first, get_or_create_key(path, stores))
            self.assertEqual(b'private test', Fernet(first).decrypt(Fernet(first).encrypt(b'private test')))

    def test_missing_key_does_not_strand_retained_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '.keys' / 'aura_aes.key'
            database = Path(folder) / 'aura_memory.db'
            database.write_bytes(b'retained data')
            with self.assertRaises(RuntimeError):
                get_or_create_key(path, [database])
            self.assertFalse(path.exists())
            self.assertEqual(b'retained data', database.read_bytes())

    def test_corrupt_key_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'aura_aes.key'
            path.write_bytes(b'invalid placeholder')
            with self.assertRaises(ValueError):
                get_or_create_key(path, [])
            self.assertEqual(b'invalid placeholder', path.read_bytes())

    def test_incomplete_rotation_blocks_key_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'aura_aes.key'
            path.write_bytes(Fernet.generate_key())
            path.with_name('rotation-in-progress').touch()
            with self.assertRaises(RuntimeError):
                get_or_create_key(path, [])


if __name__ == '__main__':
    unittest.main()
