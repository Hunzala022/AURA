"""Explicit versioned storage selection; absence preserves the legacy backend.

The cutover marker is private operator configuration, never model-controlled.
Malformed or missing encrypted state fails closed instead of falling back.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def encrypted_paths(root=ROOT):
    root = Path(root).resolve()
    marker = root/'.aura-private/storage-selection.json'
    if not marker.exists():
        return None
    data = json.loads(marker.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'version', 'directory'} or data['version'] != 1:
        raise ValueError('Unsupported storage selection')
    if not isinstance(data['directory'], str):
        raise ValueError('Invalid encrypted store location')
    directory = (root/data['directory']).resolve()
    if not directory.is_relative_to(root/'.aura-private'):
        raise ValueError('Encrypted stores must remain in the private directory')
    paths = {name: directory/file for name,file in
             (('memory','memory.aes'), ('quota','quota.aes'), ('key','aes256-key.dpapi'))}
    if not all(path.is_file() for path in paths.values()):
        raise RuntimeError('Selected encrypted state is incomplete; restore it before startup')
    return paths


def production_memory():
    paths = encrypted_paths()
    if paths is None:
        from core.memory import MemoryManager
        return MemoryManager()
    from core.encrypted_memory import EncryptedMemoryManager
    return EncryptedMemoryManager(paths['memory'], paths['key'])
