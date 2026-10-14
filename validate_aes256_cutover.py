"""Post-cutover verification. Counts only; never exports plaintext or keys."""
import argparse,json,shutil,subprocess,sys,time,hashlib
from pathlib import Path
from core.storage_selection import encrypted_paths,production_memory
from core.encrypted_memory import EncryptedMemoryManager
from core.encrypted_limits import EncryptedRateLimiter
from cryptography.exceptions import InvalidTag
from prepare_encrypted_migration import inventory,digest

ROOT=Path(__file__).resolve().parent
REPORT=ROOT/'reports/aes256_cutover_validation.json'
CANARY='AURA_AES_POSTCUTOVER_CANARY_20261014'
def snapshot():
    from core.human_layer import COMM_RATE_LIMITER
    paths=encrypted_paths()
    assert paths and isinstance(COMM_RATE_LIMITER,EncryptedRateLimiter)
    memory=production_memory()
    assert isinstance(memory,EncryptedMemoryManager)
    records=memory.export_records()
    quota=COMM_RATE_LIMITER.export_attempts()
    return paths,memory,records,quota

def run(initialize=False):
    disposition=ROOT/'reports/legacy_disposition.json'
    if disposition.exists() and json.loads(disposition.read_text(encoding='utf-8-sig')).get('phase')=='retired':
        if initialize:raise RuntimeError('Cutover already closed; no reinitialization')
        from validate_legacy_disposition import run as validate_final_storage
        return validate_final_storage()
    paths,memory,records,quota=snapshot()
    target=paths['memory'].parent
    prep=json.loads((target/'preparation-report.json').read_text())
    manifest=json.loads((target/'source-manifest.json').read_text())
    checks={'selected_backend':True,'legacy_source_unchanged':inventory(ROOT)==manifest,
            'legacy_backup_unchanged':inventory(target/'legacy-backup')==manifest}
    if initialize:
        checks['migration_records_exact']=digest(records)==prep['record_digest_before']
        checks['migration_quota_exact']=digest(quota)==prep['quota_digest_before']
        assert all(checks.values()),'Cutover initial invariant failed'
        private=target/'postcutover-recovery'
        private.mkdir(exist_ok=False)
        for name,path in paths.items():shutil.copy2(path,private/path.name)
        # Real selected-store writes: keep them as documented validation records.
        memory.log_session('cutover-validation',CANARY,CANARY)
        memory.log_audit_trail('cutover-validation','LOW',{'canary':CANARY},'VERIFIED')
        from core.human_layer import COMM_RATE_LIMITER
        now=time.time()
        surviving=sum(row[1]>now-86400 for row in quota)
        assert COMM_RATE_LIMITER.check_limit('AURA cutover validation - no message sent')
        report={'backend':'AES-256-GCM; Windows current-user DPAPI','initial_counts':{k:len(v) for k,v in records.items()},
                'initial_quota_records':len(quota),'expected_quota_after_reservation':surviving+1,
                'synthetic_session_additions':1,'synthetic_audit_additions':1,'checks':checks}
    else:report=json.loads(REPORT.read_text())
    paths,memory,records,quota=snapshot()
    checks={**report['checks'],**checks}
    checks['quota_restart']=len(quota)==report['expected_quota_after_reservation']
    checks['canary_restart']=any(CANARY in row for row in records['session_logs'])
    recovery=target/'postcutover-recovery'
    retained=EncryptedMemoryManager(recovery/'memory.aes',recovery/'aes256-key.dpapi').export_records()
    checks['all_migrated_records_preserved']=all(all(row in records[table] for row in rows) for table,rows in retained.items())
    if records['memories']:
        first=records['memories'][0]
        checks['real_text_embedding_retrieval']=bool(memory.retrieve_memory('project code word',len(records['memories'])))
        memory.embedding_function=lambda _:json.loads(first[2])
        checks['retained_vector_retrieval']=first[1] in memory.retrieve_memory('retained-vector check',len(records['memories']))
    # Only ciphertext copies are damaged; production and all legacy stores intact.
    probe=target/'tamper-probes'
    probe.mkdir(exist_ok=True)
    shutil.copy2(paths['key'],probe/'aes256-key.dpapi')
    for name in ('memory','quota'):
        data=bytearray(paths[name].read_bytes());data[-1]^=1
        (probe/(name+'.aes')).write_bytes(data)
    try:EncryptedMemoryManager(probe/'memory.aes',probe/'aes256-key.dpapi')
    except InvalidTag:checks['memory_tamper_rejected']=True
    else:checks['memory_tamper_rejected']=False
    checks['quota_tamper_rejected']=not EncryptedRateLimiter(probe/'quota.aes',probe/'aes256-key.dpapi').check_limit('probe')
    active_files=[p for p in target.iterdir() if p.is_file() and (p.suffix in ('.aes','.dpapi','.lock') or p.name.startswith('.aura-cipher-'))]
    checks['plaintext_canary_absent']=all(CANARY.encode() not in p.read_bytes() and b'SQLite format 3' not in p.read_bytes() for p in active_files)
    report.update(checks=checks,current_counts={k:len(v) for k,v in records.items()},current_quota_records=len(quota),
                  count_deltas={k:len(v)-report['initial_counts'][k] for k,v in records.items()},
                  legacy_paths=sorted(manifest),selected_directory=target.relative_to(ROOT).as_posix(),
                  passed=all(checks.values()),legacy_disposal_performed=False)
    REPORT.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report['passed']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');a=p.parse_args()
    raise SystemExit(0 if run(a.initialize) else 1)
