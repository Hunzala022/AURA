"""Exact secret scans emit counts only. Never print object bodies or key values."""
import base64,json,subprocess,sqlite3
from contextlib import closing
from pathlib import Path

def git(*args):return subprocess.check_output(['git',*args])

def run():
    root=Path(__file__).resolve().parent
    disposition=root/'reports/legacy_disposition.json'
    if disposition.exists() and json.loads(disposition.read_text(encoding='utf-8-sig')).get('phase')=='retired':
        from validate_legacy_disposition import run as validate_retained_archives
        return validate_retained_archives()
    old=root.parents[1]/'.aura-private/containment-20261010/.keys/aura_aes.key'
    current=root/'.keys/aura_aes.key'
    keys=[old.read_bytes().strip(),current.read_bytes().strip()]
    if any(not k for k in keys):raise RuntimeError('Empty scan material')
    # Include every prepared real AES key without logging it or its encodings.
    from core.encrypted_storage import storage_key
    aes_keys=[storage_key(p) for p in (root/'.aura-private').glob('encryption-*/aes256-key.dpapi')]
    scan_material=keys+[value for key in aes_keys for value in (key,key.hex().encode(),base64.b64encode(key))]
    names=set(git('ls-files','-co','--exclude-standard','-z').decode().split('\0'))-{''}
    matches=0
    for name in names:
        path=root/name
        if path.is_file():matches+=sum(k in path.read_bytes() for k in scan_material)
    entries=git('rev-list','--objects','--all').decode().splitlines()
    forbidden=lambda p:p.startswith(('.keys/','aura_chroma/','.aura-private/')) or p.startswith('aura_memory.db')
    forbidden_history=sum(forbidden(line.split(' ',1)[1]) for line in entries if ' ' in line)
    ids=[line.split(' ',1)[0] for line in entries]
    batch=subprocess.run(['git','cat-file','--batch'],input=('\n'.join(ids)+'\n').encode(),capture_output=True,check=True).stdout
    position=0;history_matches=0
    for _ in ids:
        end=batch.index(b'\n',position);header=batch[position:end].split();size=int(header[-1]);position=end+1
        payload=batch[position:position+size];position+=size+1
        history_matches+=sum(k in payload for k in scan_material)
    tracked=git('ls-files','-z').decode().split('\0')
    report={'candidate_files':len(names),'candidate_key_matches':matches,'reachable_objects':len(ids),'reachable_key_matches':history_matches,'forbidden_reachable_paths':forbidden_history,'forbidden_tracked_paths':sum(forbidden(p) for p in tracked),'current_key_ignored':subprocess.run(['git','check-ignore','-q','.keys/aura_aes.key']).returncode==0,'private_limits_ignored':subprocess.run(['git','check-ignore','-q','.aura-private/communication_limits.db']).returncode==0,'private_acceptance_ignored':subprocess.run(['git','check-ignore','-q','.aura-private/acceptance/whatsapp-self-message.png']).returncode==0,'scope':'normal locally reachable refs and candidate files; no GitHub cache-erasure claim'}
    report['passed']=all(report[k]==0 for k in ('candidate_key_matches','reachable_key_matches','forbidden_reachable_paths','forbidden_tracked_paths')) and all(report[k] for k in ('current_key_ignored','private_limits_ignored','private_acceptance_ignored'))
    report['prepared_aes_keys_scanned']=len(aes_keys)
    from cryptography.fernet import Fernet,InvalidToken
    old_cipher,current_cipher=map(Fernet,keys)
    retained={'sqlite_fields':0,'chroma_documents':0,'current_decryption_failures':0,'old_key_acceptances':0}
    def check(token,kind):
        retained[kind]+=1
        try:current_cipher.decrypt(token.encode())
        except (InvalidToken,ValueError):retained['current_decryption_failures']+=1
        try:old_cipher.decrypt(token.encode());retained['old_key_acceptances']+=1
        except (InvalidToken,ValueError):pass
    with closing(sqlite3.connect('file:'+(root/'aura_memory.db').as_posix()+'?mode=ro',uri=True)) as db:
        for columns,table in [('encrypted_task,encrypted_result','session_logs'),('encrypted_params','audit_logs')]:
            for row in db.execute('SELECT '+columns+' FROM '+table):
                for token in row:
                    if token:check(token,'sqlite_fields')
    # Read historical metadata without constructing a writable persistent Chroma
    # client: opening that client can rewrite indexes even during a scan.
    with closing(sqlite3.connect('file:'+(root/'aura_chroma/chroma.sqlite3').as_posix()+'?mode=ro',uri=True)) as db:
        for (token,) in db.execute("SELECT string_value FROM embedding_metadata WHERE key='cipher'"):
            if token:check(token,'chroma_documents')
    report['retained_rotation']=retained
    report['passed']=report['passed'] and retained['sqlite_fields']>0 and retained['chroma_documents']>0 and retained['current_decryption_failures']==0 and retained['old_key_acceptances']==0
    Path('reports/security_exit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report));return report['passed']

if __name__=='__main__':raise SystemExit(0 if run() else 1)
