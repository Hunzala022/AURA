"""Seal/verify minimum recovery set using the approved AES-256 SQLite envelope.
No retirement is performed by this tool. All payload and key bytes stay private.
"""
import argparse,hashlib,json,os,sqlite3,psutil
from pathlib import Path
from contextlib import closing
from core.encrypted_storage import EncryptedSQLite,storage_key
from core.encrypted_memory import EncryptedMemoryManager
from core.encrypted_limits import EncryptedRateLimiter
from core.storage_selection import encrypted_paths
from prepare_encrypted_migration import inventory,digest
from inventory_legacy_disposition import legacy_rows,roots

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
RECOVERY=ROOT/'.aura-private/fyp1-sealed-recovery'
VERIFY=ROOT/'.aura-private/disposition-verification'
REPORT=ROOT/'reports/legacy_disposition.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def safe_files(path):
    path=Path(path)
    if path.is_symlink():raise RuntimeError('Symlink rejected')
    found=list(path.rglob('*')) if path.is_dir() else [path]
    if any(p.is_symlink() or (getattr(p.stat(),'st_file_attributes',0)&1024) for p in found):
        raise RuntimeError('Reparse point rejected')
    return sorted(p for p in found if p.is_file())
def quiet():
    for p in psutil.process_iter(['pid','name']):
        if p.pid==os.getpid() or 'python' not in (p.info['name'] or '').lower():continue
        try:
            if Path(p.cwd()).resolve().is_relative_to(PROJECT):raise RuntimeError('AURA Python writer may be active')
        except psutil.NoSuchProcess:pass
def current():
    paths=encrypted_paths();assert paths
    key=storage_key(paths['key'],(paths['memory'],paths['quota']))
    with EncryptedSQLite(paths['memory'],key,'memory').transaction() as db:
        records={table:db.execute('SELECT * FROM '+table+' ORDER BY id').fetchall() for table in ('session_logs','audit_logs','memories')}
    quota=EncryptedRateLimiter(paths['quota'],paths['key']).export_attempts()
    return paths,records,quota
def bundle(name,files,metadata,key):
    path=RECOVERY/(name+'.aes')
    if path.exists():raise RuntimeError('Archive already exists')
    manifest={n:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for n,p in files.items()}
    with EncryptedSQLite(path,key,'recovery-archive').transaction(write=True) as db:
        db.execute('CREATE TABLE files(path TEXT PRIMARY KEY, sha256 TEXT, payload BLOB)')
        db.execute('CREATE TABLE metadata(name TEXT PRIMARY KEY, value TEXT)')
        for n,p in files.items():
            payload=p.read_bytes()
            assert sha(payload)==manifest[n]['sha256']
            db.execute('INSERT INTO files VALUES (?,?,?)',(n,sha(payload),payload))
        for n,v in {'manifest':manifest,**metadata}.items():
            db.execute('INSERT INTO metadata VALUES (?,?)',(n,json.dumps(v,sort_keys=True)))
    assert all(sha(p.read_bytes())==manifest[n]['sha256'] for n,p in files.items())
    return {'archive':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'files':len(files),'bytes':sum(v['bytes'] for v in manifest.values())}
def seal():
    quiet()
    if RECOVERY.exists():raise RuntimeError('New recovery directory required')
    paths,records,quota=current();target=paths['memory'].parent
    semantic=json.loads((ROOT/'reports/legacy_semantic_inventory.json').read_text())
    assert all(not any(row['not_in_pre_cutover'].values()) for row in semantic)
    before=json.loads((target/'source-manifest.json').read_text())
    assert inventory(target/'legacy-backup')==before
    assert inventory(ROOT)==before
    # Confirm obsolete AES preparations contain no records absent from current state.
    redundant_aes=[]
    for d in [*sorted((ROOT/'.aura-private').glob('encryption-preparation-*')),target/'postcutover-recovery']:
        keyfile=d/'aes256-key.dpapi'
        key=storage_key(keyfile,(d/'memory.aes',d/'quota.aes'))
        with EncryptedSQLite(d/'memory.aes',key,'memory').transaction() as db:
            for table in records:
                assert all(row in records[table] for row in db.execute('SELECT * FROM '+table)), 'Unique prepared records'
        assert all(row in quota for row in EncryptedRateLimiter(d/'quota.aes',keyfile).export_attempts())
        redundant_aes.append(str(d))
    retire=[]
    def add(path,classification):
        if not path.exists():return
        resolved=path.resolve()
        assert resolved.is_relative_to(PROJECT) and resolved not in (PROJECT,ROOT,paths['memory'].parent)
        assert '.git' not in resolved.parts and not resolved.name.endswith(('.git','.bundle'))
        assert not any(p==resolved or p.is_relative_to(resolved) for p in paths.values())
        files=safe_files(resolved)
        retire.append({'path':str(resolved),'classification':classification,
                       'files':{str(p.relative_to(resolved)) if resolved.is_dir() else p.name:sha(p.read_bytes()) for p in files}})
    for base in (ROOT,PROJECT,PROJECT/'.aura-private/containment-20261010',PROJECT/'.aura-private/post-rotation-backup-20261010'):
        for name in ('aura_memory.db','aura_chroma','.keys','.aura-private/communication_limits.db'):
            add(base/name,'REDUNDANT LEGACY COPY')
        for p in base.glob('aura_memory.db-*'):add(p,'REDUNDANT LEGACY COPY')
    for d in sorted((ROOT/'.aura-private').glob('encryption-preparation-*')):add(d,'REDUNDANT LEGACY COPY')
    for name in ('legacy-backup','legacy-read-copy','postcutover-recovery'):
        add(target/name,'REQUIRED RECOVERY MATERIAL' if name=='legacy-backup' else 'REDUNDANT LEGACY COPY')
    add(target/'tamper-probes','TAMPER/TEST ARTIFACT')
    add(PROJECT/'.aura-private/containment-20261010/staged','REDUNDANT LEGACY COPY')
    # Hash witnesses support later exact known-Fernet-key scans without retaining raw old keys.
    key_hashes=sorted({sha((r/'.keys/aura_aes.key').read_bytes().strip()) for r in roots()})
    RECOVERY.mkdir()
    archive_key=storage_key(RECOVERY/'recovery-key.dpapi')
    prefiles={str(p.relative_to(target/'legacy-backup')).replace('\\','/'):p for p in safe_files(target/'legacy-backup')}
    prefiles['migration/source-manifest.json']=target/'source-manifest.json'
    prefiles['migration/preparation-report.json']=target/'preparation-report.json'
    pre=bundle('pre-cutover',prefiles,{'kind':'pre-cutover','expected':{'sessions':3,'audits':4,'documents':1,'vectors':1,'quota':4}},archive_key)
    postfiles={p.name:p for p in paths.values()}
    postfiles['storage-selection.json']=ROOT/'.aura-private/storage-selection.json'
    post=bundle('post-cutover',postfiles,{'kind':'post-cutover','record_digest':digest(records),'quota_digest':digest(quota),
                 'counts':{k:len(v) for k,v in records.items()},'quota_records':len(quota)},archive_key)
    # Only manifests/checksums and protected ciphertext are written outside the containers.
    report={'phase':'sealed-not-retired','archives':[pre,post],'recovery_directory':str(RECOVERY),
            'active_directory':str(target),'production_counts':{k:len(v) for k,v in records.items()},
            'quota_records':len(quota),'production_record_digest':digest(records),'production_quota_digest':digest(quota),
            'known_fernet_key_sha256':key_hashes,'retirement_candidates':retire,
            'git_recovery_retained':[str(PROJECT/'.git'),str(PROJECT/'.aura-private/history-clean.git'),
                                     str(PROJECT/'.aura-private/pre-rewrite.bundle'),str(PROJECT/'.aura-private/pre-rewrite-full.bundle')],
            'unknown_retirement_candidates':0,'physical_erasure_claimed':False}
    REPORT.write_text(json.dumps(report,indent=2))
    print(json.dumps({'sealed':True,'archives':report['archives'],'retirement_candidates':len(retire)}))
def verify(offline=False):
    quiet()
    report=json.loads(REPORT.read_text())
    if VERIFY.exists():raise RuntimeError('Existing verification extraction must be reviewed')
    VERIFY.mkdir()
    key=storage_key(RECOVERY/'recovery-key.dpapi',(RECOVERY/'pre-cutover.aes',RECOVERY/'post-cutover.aes'))
    results=[]
    for item in report['archives']:
        archive=ROOT/item['archive']
        assert sha(archive.read_bytes())==item['sha256'],'Archive checksum mismatch'
        with EncryptedSQLite(archive,key,'recovery-archive').transaction() as db:
            meta={n:json.loads(v) for n,v in db.execute('SELECT * FROM metadata')}
            rows=db.execute('SELECT * FROM files').fetchall()
        dest=VERIFY/meta['kind'];dest.mkdir()
        assert len(rows)==item['files']==len(meta['manifest'])
        for name,expected,payload in rows:
            out=(dest/name).resolve()
            assert out.is_relative_to(dest.resolve()),'Unsafe archived path'
            assert expected==sha(payload)==meta['manifest'][name]['sha256']
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as f:f.write(payload)
            assert sha(out.read_bytes())==expected
        if meta['kind']=='pre-cutover':
            data=legacy_rows(dest)
            assert {k:len(v) for k,v in data.items()}==meta['expected']
            # Exercise actual Chroma index recovery from the extracted snapshot.
            import chromadb
            from chromadb.config import Settings
            from cryptography.fernet import Fernet
            client=chromadb.PersistentClient(path=str(dest/'aura_chroma'),settings=Settings(anonymized_telemetry=False))
            col=client.get_collection('aura_long_term_memory')
            found=col.get(include=['embeddings','metadatas'])
            assert len(found['ids'])==1
            hit=col.query(query_embeddings=[[float(x) for x in found['embeddings'][0]]],n_results=1,include=['metadatas'])
            cipher=Fernet((dest/'.keys/aura_aes.key').read_bytes())
            assert cipher.decrypt(hit['metadatas'][0][0]['cipher'].encode()).decode() in data['documents']
        else:
            memory=EncryptedMemoryManager(dest/'memory.aes',dest/'aes256-key.dpapi')
            records=memory.export_records();quota=EncryptedRateLimiter(dest/'quota.aes',dest/'aes256-key.dpapi').export_attempts()
            assert digest(records)==meta['record_digest'] and digest(quota)==meta['quota_digest']
            first=records['memories'][0]
            memory.embedding_function=lambda _:json.loads(first[2])
            assert first[1] in memory.retrieve_memory('recovery verification',1)
        results.append({'kind':meta['kind'],'files_hash_verified':len(rows),'recovery_passed':True})
    if not offline:
        _,records,quota=current()
        assert digest(records)==report['production_record_digest'] and digest(quota)==report['production_quota_digest']
    report.update(archive_verification=results,verified=True,
                  phase='retired' if report['phase']=='retired' else 'verified-not-retired',verification_extraction=str(VERIFY))
    REPORT.write_text(json.dumps(report,indent=2))
    print(json.dumps({'verified':True,'results':results,'production_checked':not offline,'verification_extraction':str(VERIFY)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['seal','verify']);p.add_argument('--offline',action='store_true');a=p.parse_args()
    if a.action=='seal':
        if a.offline:raise ValueError('Offline is only for recovery verification')
        seal()
    else:verify(a.offline)
