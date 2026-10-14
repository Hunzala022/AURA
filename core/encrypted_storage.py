"""Versioned AES-256-GCM persistence; plaintext SQLite exists only in memory.

This module does not change the active storage backend. Key bytes are never
logged. Windows DPAPI protects the dedicated storage key for the current user.
"""
import ctypes
import os
import sqlite3
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC=b'AURA-AES256-GCM-SQLITE-v1\x00'
KEY_MAGIC=b'AURA-DPAPI-KEY-v1\x00'
MAX_BYTES=256*1024*1024
_locks={};_locks_guard=threading.Lock()

def _thread_lock(path):
    name=str(Path(path).resolve()).casefold()
    with _locks_guard:return _locks.setdefault(name,threading.RLock())

@contextmanager
def exclusive_lock(path,timeout=10):
    """Cross-thread/process lock. Only a constant lock byte reaches disk."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with _thread_lock(path):
        with path.open('a+b') as stream:
            stream.seek(0,2)
            if stream.tell()==0:stream.write(b'\x00');stream.flush()
            deadline=time.monotonic()+timeout;locked=False
            while not locked:
                try:
                    stream.seek(0)
                    if os.name=='nt':
                        import msvcrt
                        msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
                    else:
                        import fcntl
                        fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
                    locked=True
                except OSError:
                    if time.monotonic()>=deadline:raise TimeoutError('Encrypted storage is busy')
                    time.sleep(.025)
            try:yield
            finally:
                stream.seek(0)
                if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
                else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

def _dpapi(data,protect):
    if os.name!='nt':raise RuntimeError('Current-user Windows DPAPI is required')
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
    source_buffer=ctypes.create_string_buffer(data)
    source=Blob(len(data),ctypes.cast(source_buffer,ctypes.POINTER(ctypes.c_ubyte)));target=Blob()
    crypt=ctypes.WinDLL('crypt32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
    function=crypt.CryptProtectData if protect else crypt.CryptUnprotectData
    function.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
    function.restype=wintypes.BOOL
    if not function(ctypes.byref(source),None,None,None,None,1,ctypes.byref(target)):
        raise OSError('Current-user key protection failed')
    try:return ctypes.string_at(target.data,target.size)
    finally:kernel.LocalFree(target.data)

def storage_key(path,data_paths=()):
    path=Path(path)
    with exclusive_lock(path.with_name(path.name+'.lock')):
        if path.exists():
            if path.stat().st_size>65536:raise ValueError('Protected key envelope exceeds supported size')
            protected=path.read_bytes()
            if not protected.startswith(KEY_MAGIC):raise ValueError('Unsupported protected key format')
            key=_dpapi(protected[len(KEY_MAGIC):],False)
            if len(key)!=32:raise ValueError('Invalid AES-256 key length')
            return key
        if any(Path(p).exists() for p in data_paths):raise RuntimeError('Storage key missing for retained encrypted data')
        key=AESGCM.generate_key(bit_length=256)
        wrapped=KEY_MAGIC+_dpapi(key,True)
        with path.open('xb') as stream:stream.write(wrapped);stream.flush();os.fsync(stream.fileno())
        return key

class EncryptedSQLite:
    def __init__(self,path,key,purpose):
        if len(key)!=32:raise ValueError('AES-256 requires a 32-byte key')
        if not purpose or len(purpose)>64 or not purpose.isascii() or '\x00' in purpose:raise ValueError('Invalid storage purpose')
        self.path=Path(path);self.key=key;self.header=MAGIC+purpose.encode('ascii')+b'\x00'

    def _load(self):
        if self.path.stat().st_size>MAX_BYTES+256:raise ValueError('Encrypted store exceeds supported size')
        data=self.path.read_bytes();offset=len(self.header)
        if not data.startswith(self.header) or len(data)<offset+12+16:raise ValueError('Invalid encrypted store envelope')
        return AESGCM(self.key).decrypt(data[offset:offset+12],data[offset+12:],self.header)

    def _save(self,data):
        if len(data)>MAX_BYTES:raise ValueError('Store exceeds supported size')
        nonce=os.urandom(12);encrypted=self.header+nonce+AESGCM(self.key).encrypt(nonce,data,self.header)
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(prefix='.aura-cipher-',dir=self.path.parent,delete=False) as stream:
                temporary=Path(stream.name);stream.write(encrypted);stream.flush();os.fsync(stream.fileno())
            os.replace(temporary,self.path);temporary=None
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)

    @contextmanager
    def transaction(self,write=False):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with exclusive_lock(self.path.with_name(self.path.name+'.lock')):
            db=sqlite3.connect(':memory:')
            try:
                if self.path.exists():db.deserialize(self._load())
                db.execute('PRAGMA temp_store=MEMORY');db.execute('PRAGMA journal_mode=MEMORY');db.execute('PRAGMA trusted_schema=OFF')
                if not write:db.execute('PRAGMA query_only=ON')
                yield db
                if write:
                    db.commit();self._save(db.serialize())
            except Exception:
                db.rollback();raise
            finally:db.close()
