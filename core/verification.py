"""Observable postconditions for file and accessibility actions."""
import hashlib
from pathlib import Path
def digest(path):
    path=Path(path)
    if path.is_file():
        with path.open('rb') as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()
    if path.is_dir():
        return {str(p.relative_to(path)):digest(p) for p in path.rglob('*') if p.is_file()}
    return None
def before_action(tool,params):
    if tool in ('copy_file','move_file'): return digest(params['source'])
    return None
def verify_action(tool,params,result,before=None):
    if tool=='write_file': return Path(params['path']).read_text(encoding='utf-8')==params['content']
    if tool=='create_folder': return Path(params['path']).is_dir()
    if tool=='delete_file': return not Path(params['path']).exists()
    if tool in ('copy_file','move_file'):
        destination=Path(params['destination'])
        if destination.is_dir() and isinstance(before,str):
            destination=destination/Path(params['source']).name
        ok=before is not None and digest(destination)==before
        return ok and (tool!='move_file' or not Path(params['source']).exists())
    if tool=='capture_screenshot':
        p=Path(params['output_path'])
        return p.is_file() and p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    if tool in ('open_application','type_in_window'):
        from agents.os_agent import verify_window
        check={'window_title':params['window_title']}
        if tool=='type_in_window':check['expected_text']=params['text']
        return verify_window(check)[0] is True
    # Remaining tools must perform their own read-back/observation before returning True.
    return result is not None
