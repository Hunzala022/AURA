import multiprocessing,os,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from core.encrypted_storage import EncryptedSQLite,storage_key

def crash_before_replace(path,key):
    store=EncryptedSQLite(path,key,'fixture')
    with patch('core.encrypted_storage.os.replace',side_effect=lambda *args:os._exit(19)):
        with store.transaction(write=True) as db:db.execute('INSERT INTO records VALUES (?,?)',('uncommitted','crash canary'))

class EncryptedStorage(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.root=Path(self.folder.name)
        self.key=AESGCM.generate_key(bit_length=256);self.path=self.root/'state.aes'
        self.store=EncryptedSQLite(self.path,self.key,'fixture')
        with self.store.transaction(write=True) as db:
            db.execute('CREATE TABLE records (identity TEXT, payload TEXT)')
            db.execute('INSERT INTO records VALUES (?,?)',('metadata canary','payload canary'))
    def tearDown(self):self.folder.cleanup()
    def test_full_database_roundtrip_and_no_plaintext_artifacts(self):
        again=EncryptedSQLite(self.path,self.key,'fixture')
        with again.transaction() as db:self.assertEqual([('metadata canary','payload canary')],db.execute('SELECT * FROM records').fetchall())
        for path in self.root.iterdir():
            raw=path.read_bytes()
            self.assertFalse(b'payload canary' in raw or b'metadata canary' in raw or b'SQLite format 3' in raw)
            self.assertFalse(self.key in raw,'Raw key bytes must never be persisted')
    def test_wrong_key_purpose_and_tampering_fail_closed(self):
        with self.assertRaises(InvalidTag):
            with EncryptedSQLite(self.path,AESGCM.generate_key(bit_length=256),'fixture').transaction():pass
        with self.assertRaises(ValueError):
            with EncryptedSQLite(self.path,self.key,'other').transaction():pass
        raw=bytearray(self.path.read_bytes());raw[-1]^=1;self.path.write_bytes(raw)
        with self.assertRaises(InvalidTag):
            with self.store.transaction():pass
    def test_exception_and_replace_failure_preserve_committed_state(self):
        before=self.path.read_bytes()
        with self.assertRaises(RuntimeError):
            with self.store.transaction(write=True) as db:
                db.execute('DELETE FROM records');raise RuntimeError('fixture rollback')
        self.assertTrue(before==self.path.read_bytes())
        with patch('core.encrypted_storage.os.replace',side_effect=OSError('fixture crash')),self.assertRaises(OSError):
            with self.store.transaction(write=True) as db:db.execute('DELETE FROM records')
        self.assertTrue(before==self.path.read_bytes());self.assertFalse(list(self.root.glob('.aura-cipher-*')))
    def test_concurrent_writers_do_not_lose_records(self):
        def add(i):
            with EncryptedSQLite(self.path,self.key,'fixture').transaction(write=True) as db:db.execute('INSERT INTO records VALUES (?,?)',(str(i),'concurrent'))
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(add,range(12)))
        with self.store.transaction() as db:self.assertEqual(13,db.execute('SELECT COUNT(*) FROM records').fetchone()[0])
    def test_process_crash_leaves_old_store_and_only_ciphertext_temp(self):
        before=self.path.read_bytes()
        process=multiprocessing.get_context('spawn').Process(target=crash_before_replace,args=(str(self.path),self.key))
        process.start();process.join(20)
        if process.is_alive():process.terminate();process.join();self.fail('Owned crash-test process timed out')
        self.assertEqual(19,process.exitcode);self.assertTrue(before==self.path.read_bytes())
        with self.store.transaction() as db:self.assertEqual(1,db.execute('SELECT COUNT(*) FROM records').fetchone()[0])
        for path in self.root.iterdir():self.assertFalse(b'crash canary' in path.read_bytes())
    @unittest.skipUnless(os.name=='nt','Windows DPAPI')
    def test_dpapi_key_roundtrip_and_missing_key_fail_closed(self):
        path=self.root/'protected.key'
        key=storage_key(path)
        self.assertTrue(key==storage_key(path,(self.path,)))
        self.assertFalse(key in path.read_bytes(),'Raw key bytes must never be persisted')
        with self.assertRaises(RuntimeError):storage_key(self.root/'missing.key',(self.path,))
        self.assertFalse((self.root/'missing.key').exists())
