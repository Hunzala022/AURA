"""Counts-only legacy inventory and semantic comparison; no secret output."""
import json,sqlite3,hashlib
from pathlib import Path
from contextlib import closing
from cryptography.fernet import Fernet
from core.storage_selection import encrypted_paths
from core.encrypted_storage import storage_key,EncryptedSQLite
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def legacy_rows(root):
    cipher=Fernet((root/'.keys/aura_aes.key').read_bytes().strip())
    def dec(x):return cipher.decrypt(x.encode()).decode() if x else x
    out={}
    with closing(sqlite3.connect('file:'+(root/'aura_memory.db').as_posix()+'?mode=ro',uri=True)) as db:
        out['sessions']=[(i,t,a,dec(x),dec(y)) for i,t,a,x,y in db.execute('SELECT * FROM session_logs ORDER BY id')]
        out['audits']=[(i,t,a,r,dec(x),s) for i,t,a,r,x,s in db.execute('SELECT * FROM audit_logs ORDER BY id')]
    with closing(sqlite3.connect('file:'+(root/'aura_chroma/chroma.sqlite3').as_posix()+'?mode=ro',uri=True)) as db:
        out['documents']=[dec(x) for (x,) in db.execute("SELECT string_value FROM embedding_metadata WHERE key='cipher'")]
        out['vectors']=[(i,sha(v),e) for i,v,e in db.execute('SELECT id,vector,encoding FROM embeddings_queue WHERE vector IS NOT NULL')]
    quota=root/'.aura-private/communication_limits.db'
    out['quota']=[]
    if quota.exists():
        with closing(sqlite3.connect('file:'+quota.as_posix()+'?mode=ro',uri=True)) as db:
            out['quota']=db.execute('SELECT platform,timestamp FROM attempts ORDER BY timestamp,platform').fetchall()
    return out
def roots():
    return [ROOT,PROJECT,PROJECT/'.aura-private/containment-20261010',PROJECT/'.aura-private/post-rotation-backup-20261010']+[p/k for p in (ROOT/'.aura-private').glob('encryption-*') for k in ('legacy-backup','legacy-read-copy') if (p/k).exists()]
def run():
    TARGET=encrypted_paths()['memory'].parent
    baseline=legacy_rows(TARGET/'legacy-backup')
    report=[]
    for root in roots():
        rows=legacy_rows(root)
        unique={k:sum(row not in baseline[k] for row in v) for k,v in rows.items()}
        report.append({'root':str(root),'counts':{k:len(v) for k,v in rows.items()},'not_in_pre_cutover':unique})
    staged=PROJECT/'.aura-private/containment-20261010/staged/aura_chroma/chroma.sqlite3'
    if staged.exists():
        with closing(sqlite3.connect('file:'+staged.as_posix()+'?mode=ro',uri=True)) as db:
            vectors=[(i,sha(v),e) for i,v,e in db.execute('SELECT id,vector,encoding FROM embeddings_queue WHERE vector IS NOT NULL')]
            docs=[]
            keys=[Fernet((r/'.keys/aura_aes.key').read_bytes().strip()) for r in (ROOT,PROJECT)]
            for (token,) in db.execute("SELECT string_value FROM embedding_metadata WHERE key='cipher'"):
                for key in keys:
                    try:docs.append(key.decrypt(token.encode()).decode());break
                    except Exception:continue
                else:raise RuntimeError('Staged document cannot be verified')
        report.append({'root':str(staged.parent),'counts':{'documents':len(docs),'vectors':len(vectors)},
                       'not_in_pre_cutover':{'documents':sum(v not in baseline['documents'] for v in docs),'vectors':sum(v not in baseline['vectors'] for v in vectors)}})
    else:
        assert not list(staged.parent.iterdir()), 'Unknown staged files'
        report.append({'root':str(staged.parent),'counts':{},'not_in_pre_cutover':{}})
    assert all(not any(r['not_in_pre_cutover'].values()) for r in report),'Unique legacy data requires review'
    print(json.dumps(report,indent=2))
    (ROOT/'reports/legacy_semantic_inventory.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':run()
