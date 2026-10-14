"""Explicit operator cutover. Do not run --activate without owner approval."""
import argparse
import json
import os
from pathlib import Path
import psutil

from core.encrypted_memory import EncryptedMemoryManager
from core.encrypted_limits import EncryptedRateLimiter
from prepare_encrypted_migration import inventory, digest


def activate(root,target,commit=False):
    root=Path(root).resolve();target=Path(target).resolve()
    if not target.is_relative_to(root/'.aura-private'):
        raise ValueError('Private prepared target required')
    manifest=json.loads((target/'source-manifest.json').read_text())
    report=json.loads((target/'preparation-report.json').read_text())
    if not report['passed'] or inventory(root)!=manifest or inventory(target/'legacy-backup')!=manifest:
        raise RuntimeError('Source or backup changed; prepare and review a fresh migration')
    memory=EncryptedMemoryManager(target/'memory.aes',target/'aes256-key.dpapi')
    limits=EncryptedRateLimiter(target/'quota.aes',target/'aes256-key.dpapi')
    if digest(memory.export_records())!=report['record_digest_before'] or digest(limits.export_attempts())!=report['quota_digest_before']:
        raise RuntimeError('Prepared encrypted records changed')
    active=[]
    for process in psutil.process_iter(['pid','name']):
        if process.pid==os.getpid() or 'python' not in (process.info['name'] or '').lower():continue
        try:
            cwd=Path(process.cwd()).resolve()
            if cwd==root or cwd.is_relative_to(root):active.append(process.pid)
        except psutil.NoSuchProcess:continue
        except psutil.AccessDenied:
            raise RuntimeError('Cannot establish that other Python processes are quiescent')
    if active:raise RuntimeError('Other Python processes use this checkout; close them before cutover')
    marker=root/'.aura-private/storage-selection.json'
    if marker.exists():raise RuntimeError('Storage selection already exists; no overwrite permitted')
    selection={'version':1,'directory':target.relative_to(root).as_posix()}
    if commit:
        # Exclusive marker creation avoids replacing another operator's selection.
        # Startup treats a partial marker as an error, never as a legacy fallback.
        with marker.open('x',encoding='utf-8') as stream:
            json.dump(selection,stream);stream.flush();os.fsync(stream.fileno())
    return {'preconditions_passed':True,'activated':commit,'selection':selection,
            'legacy_retirement_performed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--activate',action='store_true')
    args=p.parse_args()
    print(json.dumps(activate(Path(__file__).resolve().parent,args.target,args.activate),indent=2))
