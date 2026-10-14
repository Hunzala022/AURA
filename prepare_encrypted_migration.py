"""Non-destructive migration rehearsal. Never switches the production backend.

Creates a private, hash-verified legacy backup and a separate AES-256 target.
Only counts, hashes and booleans may be printed or written to the public report.
"""
import argparse
import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

import chromadb
from chromadb.config import Settings
from cryptography.fernet import Fernet
from core.encrypted_memory import EncryptedMemoryManager
from core.encrypted_limits import EncryptedRateLimiter

LEGACY = ('aura_memory.db', 'aura_chroma', '.keys/aura_aes.key', '.aura-private/communication_limits.db')


def inventory(root):
    files = []
    for name in LEGACY:
        path = root/name
        if path.is_dir():
            files.extend(p for p in path.rglob('*') if p.is_file())
        elif path.is_file():
            files.append(path)
        if name == 'aura_memory.db':
            files.extend(p for p in root.glob('aura_memory.db-*') if p.is_file())
        if name == '.aura-private/communication_limits.db':
            files.extend(p for p in path.parent.glob('communication_limits.db-*') if p.is_file())
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def digest(records):
    return hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def prepare(root, target):
    root = Path(root).resolve()
    target = Path(target).resolve()
    private = root/'.aura-private'
    if not target.is_relative_to(private) or target == private or target.exists():
        raise ValueError('A new directory inside this checkout private area is required')
    before = inventory(root)
    if not all(p in before for p in ('aura_memory.db', '.keys/aura_aes.key')):
        raise ValueError('Retained memory and its key are required')
    target.mkdir(parents=True)
    backup = target/'legacy-backup'
    for name in before:
        out = backup/name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root/name, out)
    if inventory(root) != before or inventory(backup) != before:
        raise RuntimeError('Source changed or backup verification failed; no activation permitted')
    # Chroma may maintain its own files even during reads. Open a disposable
    # private copy, keeping the verified recovery backup untouched.
    working = target/'legacy-read-copy'
    shutil.copytree(backup, working)
    cipher = Fernet((working/'.keys/aura_aes.key').read_bytes())
    decode = lambda value: cipher.decrypt(value.encode()).decode()
    with closing(sqlite3.connect('file:'+(working/'aura_memory.db').as_posix()+'?mode=ro', uri=True)) as db:
        sessions = [(i,t,a,decode(task),decode(result)) for i,t,a,task,result in
                    db.execute('SELECT id,timestamp,agent_type,encrypted_task,encrypted_result FROM session_logs ORDER BY id')]
        audits = [(i,t,tool,risk,decode(params),status) for i,t,tool,risk,params,status in
                  db.execute('SELECT id,timestamp,tool_name,risk_level,encrypted_params,action_status FROM audit_logs ORDER BY id')]
    client = chromadb.PersistentClient(path=str(working/'aura_chroma'), settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection('aura_long_term_memory')
    found = collection.get(include=['metadatas','embeddings'])
    memories = []
    for index, identity in enumerate(found['ids']):
        metadata = dict(found['metadatas'][index])
        content = decode(metadata.pop('cipher'))
        vector = [float(value) for value in found['embeddings'][index]]
        memories.append((identity, content, json.dumps(vector), json.dumps(metadata, sort_keys=True)))
    records = {'session_logs': sessions, 'audit_logs': audits, 'memories': sorted(memories)}
    attempts = []
    quota = working/'.aura-private/communication_limits.db'
    if quota.exists():
        with closing(sqlite3.connect('file:'+quota.as_posix()+'?mode=ro', uri=True)) as db:
            attempts = db.execute('SELECT platform,timestamp FROM attempts ORDER BY timestamp,platform').fetchall()
    key = target/'aes256-key.dpapi'
    memory = EncryptedMemoryManager(target/'memory.aes', key)
    memory.import_records(records)
    limits = EncryptedRateLimiter(target/'quota.aes', key)
    limits.import_attempts(attempts)
    reopened = EncryptedMemoryManager(target/'memory.aes', key)
    after = reopened.export_records()
    after_quota = EncryptedRateLimiter(target/'quota.aes', key).export_attempts()
    exact = digest(records) == digest(after) and digest(attempts) == digest(after_quota)
    retrieval = True
    if memories:
        # Exercise real ephemeral Chroma using the retained vector; no re-embedding
        # or semantic-memory change is introduced by migration verification.
        reopened.embedding_function = lambda _: json.loads(memories[0][2])
        retrieval = memories[0][1] in reopened.retrieve_memory('migration verification', len(memories))
    unchanged = inventory(root) == before and inventory(backup) == before
    report = {'active_backend_changed': False, 'backup_matches_source': unchanged,
              'complete_records_equal_after_restart': exact, 'retained_vector_retrieval': retrieval,
              'counts': {name: len(rows) for name, rows in records.items()}, 'quota_records': len(attempts),
              'record_digest_before': digest(records), 'record_digest_after': digest(after),
              'quota_digest_before': digest(attempts), 'quota_digest_after': digest(after_quota),
              'target': target.relative_to(root).as_posix(), 'source_file_count': len(before),
              'key_protection': 'Windows current-user DPAPI; dedicated AES-256 key',
              'passed': exact and unchanged and retrieval}
    (target/'source-manifest.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
    (target/'preparation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target',required=True)
    parser.add_argument('--report',default='reports/encryption_preparation.json')
    args = parser.parse_args()
    result = prepare(Path(__file__).resolve().parent, args.target)
    Path(args.report).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
