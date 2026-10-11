"""Deterministic risk decisions. Model-supplied risk never authorizes execution."""
import ntpath
import os
from pathlib import Path
from urllib.parse import urlsplit
from core.tools import TOOLS
WORKSPACE = Path(__file__).resolve().parent.parent
PATH_FIELDS = ('path','source','destination','directory','output_path')
HIGH_TOOLS = {'delete_file','send_message','read_latest_message','open_application',
              'type_in_window','click_ui_element','browser_click','browser_fill',
              'navigate_and_read','capture_screenshot'}
def normalized_path(value):
    # Resolve links/junctions on the native Windows host, then normalize spelling.
    return ntpath.normcase(ntpath.normpath(os.path.realpath(os.path.abspath(str(value)))))
def sensitive_path(value, workspace=None):
    path = normalized_path(value)
    root = normalized_path(workspace or WORKSPACE)
    if ':' in ntpath.splitdrive(path)[1]: return True  # Windows alternate data streams.
    try:
        if ntpath.commonpath([root,path]) != root: return True
    except ValueError: return True
    relative = ntpath.relpath(path,root)
    tokens = relative.replace('\\','/').lower()
    # A planner must not silently rewrite its own execution/security code.
    if ntpath.splitext(path)[1] in ('.py','.pyw','.ps1','.bat','.cmd','.exe','.dll','.pyd'):
        return True
    return any(word in tokens for word in ('.keys','.ssh','.git','.aura-private','aura_memory.db','aura_chroma','password','secret','credential','id_rsa','token','system32'))
def evaluate_risk(tool_name, parameters, workspace=None):
    if tool_name not in TOOLS: raise PermissionError('Unknown tool is not authorized')
    if tool_name in HIGH_TOOLS: return 'HIGH'
    if tool_name in ('copy_file','move_file') and Path(parameters.get('source','')).is_dir():
        return 'HIGH'  # A directory may contain keys or sensitive descendant files.
    # Every path is checked independently, including both copy/move endpoints.
    if any(sensitive_path(parameters[field],workspace) for field in PATH_FIELDS if field in parameters):
        return 'HIGH'
    if tool_name.startswith('search_files_'):
        query = str(parameters.get('query',parameters.get('pattern',''))).lower()
        if any(t in query for t in ('password','secret','token','api_key','id_rsa','credential','.key')):
            return 'HIGH'
        # Recursive search may encounter sensitive descendants despite a benign root.
        return 'HIGH'
    return 'MEDIUM'
def authorize_high_risk_action(action_details):
    """FYP-1 local confirmation, not identity authentication or a biometric check."""
    print('HIGH RISK action requires approval:', action_details.get('tool'))
    print('Review parameters locally:', action_details.get('parameters'))
    try:
        return input('Authorize this exact action? [y/N]: ').strip().lower() in ('y','yes')
    except (EOFError,KeyboardInterrupt):
        return False
