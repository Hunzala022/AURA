"""Opt-in encrypted quota store; reservation semantics match production."""
import hashlib
import time
from pathlib import Path
from core.encrypted_storage import EncryptedSQLite, storage_key


class EncryptedRateLimiter:
    def __init__(self, path, key_file, hourly=30, daily=100, clock=time.time, global_daily=100):
        self.path = Path(path)
        self.key_file = Path(key_file)
        self.hourly = hourly
        self.daily = daily
        self.global_daily = global_daily
        self.clock = clock

    def _store(self):
        return EncryptedSQLite(self.path, storage_key(self.key_file, (self.path, self.path.parent/'memory.aes')), 'communication-quota')

    def check_limit(self, platform='default'):
        try:
            with self._store().transaction(write=True) as db:
                db.execute('CREATE TABLE IF NOT EXISTS attempts(platform TEXT, timestamp REAL)')
                now = self.clock()
                last = db.execute('SELECT MAX(timestamp) FROM attempts').fetchone()[0]
                if last is not None and now < last:
                    return False
                name = hashlib.sha256(platform.strip().casefold().encode()).hexdigest()
                hour = db.execute('SELECT COUNT(*) FROM attempts WHERE timestamp>?', (now-3600,)).fetchone()[0]
                day = db.execute('SELECT COUNT(*) FROM attempts WHERE platform=? AND timestamp>?', (name, now-86400)).fetchone()[0]
                total = db.execute('SELECT COUNT(*) FROM attempts WHERE timestamp>?', (now-86400,)).fetchone()[0]
                if hour >= self.hourly or day >= self.daily or total >= self.global_daily:
                    return False
                db.execute('DELETE FROM attempts WHERE timestamp<=?', (now-86400,))
                db.execute('INSERT INTO attempts VALUES (?,?)', (name, now))
                return True
        except Exception:
            # Authentication, DPAPI, serialization, locking and I/O all fail closed.
            return False

    def import_attempts(self, rows):
        with self._store().transaction(write=True) as db:
            db.execute('CREATE TABLE IF NOT EXISTS attempts(platform TEXT, timestamp REAL)')
            if db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]:
                raise ValueError('Quota migration target must be empty')
            db.executemany('INSERT INTO attempts VALUES (?,?)', rows)

    def export_attempts(self):
        with self._store().transaction() as db:
            return db.execute('SELECT platform,timestamp FROM attempts ORDER BY timestamp,platform').fetchall()
