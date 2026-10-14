"""Targeted post-disposition validation; no model/UI execution."""
import base64,hashlib,json,os,re,subprocess
from pathlib import Path
from core.storage_selection import encrypted_paths,production_memory
from core.encrypted_limits import EncryptedRateLimiter
from core.encrypted_storage import EncryptedSQLite,storage_key
from prepare_encrypted_migration import digest
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def run():
    disposition=json.loads((ROOT/'reports/legacy_disposition.json').read_text(encoding='utf-8-sig'))
    assert disposition['phase']=='retired'
    paths=encrypted_paths();assert paths
    memory=production_memory()
    records=memory.export_records()
    quota=EncryptedRateLimiter(paths['quota'],paths['key']).export_attempts()
    checks={'production_aes_selected':type(memory).__name__=='EncryptedMemoryManager',
            'records_unchanged':digest(records)==disposition['production_record_digest'],
            'quota_unchanged':digest(quota)==disposition['production_quota_digest']}
    checks['restart_retrieval']=bool(memory.retrieve_memory('project code word'))
    recovery=Path(disposition['recovery_directory'])
    archivekey=storage_key(recovery/'recovery-key.dpapi',(recovery/'pre-cutover.aes',recovery/'post-cutover.aes'))
    archives=[]
    for item in disposition['archives']:
        path=ROOT/item['archive'];assert sha(path.read_bytes())==item['sha256']
        with EncryptedSQLite(path,archivekey,'recovery-archive').transaction() as db:
            manifest=json.loads(db.execute("SELECT value FROM metadata WHERE name='manifest'").fetchone()[0])
            rows=db.execute('SELECT path,sha256,payload FROM files').fetchall()
        assert len(rows)==item['files']==len(manifest)
        assert all(sha(payload)==expected==manifest[name]['sha256'] for name,expected,payload in rows)
        archives.append({'archive':item['archive'],'authenticated':True,'files_verified':len(rows)})
    checks['archives_verified']=True
    checks['retired_targets_absent']=all(not Path(row['path']).exists() for row in disposition['retirement_candidates'])
    checks['verification_extraction_absent']=not Path(disposition['verification_extraction']).exists()
    checks['git_recovery_present']=all(Path(p).exists() for p in disposition['git_recovery_retained'])
    found=[]
    for directory,dirs,files in os.walk(PROJECT,followlinks=False):
        dirs[:]=[d for d in dirs if d not in ('.git','history-clean.git','node_modules','__pycache__')]
        for name in files:
            if name in ('aura_memory.db','chroma.sqlite3','aura_aes.key','communication_limits.db') or name.startswith(('aura_memory.db-','communication_limits.db-')):
                found.append(str(Path(directory)/name))
    checks['no_known_unsealed_runtime_stores']=not found
    # Check hashes of known legacy Fernet keys, never recover or print their values.
    keyhashes=set(disposition['known_fernet_key_sha256'])
    aeskeys=[archivekey,storage_key(paths['key'],(paths['memory'],paths['quota']))]
    patterns=[v for key in aeskeys for v in (key,key.hex().encode(),base64.b64encode(key))]
    def matches(data):
        return sum(sha(m.group()) in keyhashes for m in re.finditer(rb'[A-Za-z0-9_-]{43}=',data))+sum(v in data for v in patterns)
    candidates=set(git('ls-files','-co','--exclude-standard','-z').decode().split('\0'))-{''}
    candidate_matches=sum(matches((ROOT/n).read_bytes()) for n in candidates if (ROOT/n).is_file())
    entries=git('rev-list','--objects','--all').decode().splitlines()
    ids=[line.split(' ',1)[0] for line in entries]
    raw=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(ids)+'\n').encode(),capture_output=True,check=True).stdout
    offset=0;history_matches=0
    for _ in ids:
        end=raw.index(b'\n',offset);size=int(raw[offset:end].split()[-1]);offset=end+1
        history_matches+=matches(raw[offset:offset+size]);offset+=size+1
    forbidden=lambda p:p.startswith(('.keys/','.aura-private/','aura_chroma/','aura_memory.db'))
    tracked=git('ls-files','-z').decode().split('\0')
    history_paths=sum(forbidden(line.split(' ',1)[1]) for line in entries if ' ' in line)
    ignored=[str(p.relative_to(ROOT)) for p in [*paths.values(),ROOT/'.aura-private/storage-selection.json',
              recovery/'pre-cutover.aes',recovery/'post-cutover.aes',recovery/'recovery-key.dpapi']]
    checks['private_storage_ignored']=all(subprocess.run(['git','check-ignore','-q',p],cwd=ROOT).returncode==0 for p in ignored)
    checks['no_known_key_leak']=candidate_matches==history_matches==0
    checks['no_private_tracked_or_reachable_paths']=not any(forbidden(p) for p in tracked) and history_paths==0
    report={'checks':checks,'passed':all(checks.values()),'counts':{k:len(v) for k,v in records.items()},
            'quota_records':len(quota),'archives':archives,'remaining_known_legacy_runtime_paths':found,
            'candidate_files':len(candidates),'candidate_key_matches':candidate_matches,
            'reachable_objects':len(ids),'reachable_key_matches':history_matches,
            'forbidden_reachable_paths':history_paths,'retired_targets':len(disposition['retirement_candidates']),
            'git_recovery_scope':'Original repository, mirror and bundles preserved separately; no history/cache-erasure claim',
            'physical_erasure_claimed':False}
    (ROOT/'reports/legacy_disposition_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report['passed']
if __name__=='__main__':raise SystemExit(0 if run() else 1)
