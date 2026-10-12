import os
import shutil
import pathlib
from typing import Dict, Any, Tuple

# ---------------------------------------------------------------------------
# File/OS Tools (Milestone 2.4)
# ---------------------------------------------------------------------------

def list_directory(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    path = parameters.get("path")
    if not path or not os.path.exists(path):
        return False, f"Path does not exist: {path}"
    if not os.path.isdir(path):
        return False, f"Path is not a directory: {path}"
    try:
        items = os.listdir(path)
        return True, f"Contents of {path}: {', '.join(items) if items else 'Empty directory'}"
    except Exception as e:
        return False, str(e)

def read_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    path = parameters.get("path")
    if not path or not os.path.exists(path):
        return False, f"File does not exist: {path}"
    if not os.path.isfile(path):
        return False, f"Path is not a file: {path}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return True, content
    except Exception as e:
        return False, str(e)

def write_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    path = parameters.get("path")
    content = parameters.get("content", "")
    if not path:
        return False, "Missing path parameter"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f"Successfully wrote to {path}"
    except Exception as e:
        return False, str(e)

def delete_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    path = parameters.get("path")
    if not path or not os.path.exists(path):
        return False, f"Path does not exist: {path}"
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True, f"Successfully deleted {path}"
    except Exception as e:
        return False, str(e)

def create_folder(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    path = parameters.get("path")
    if not path:
        return False, "Missing path parameter"
    try:
        os.makedirs(path, exist_ok=True)
        return True, f"Successfully created folder {path}"
    except Exception as e:
        return False, str(e)

def move_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    source = parameters.get("source")
    destination = parameters.get("destination")
    if not source or not os.path.exists(source):
        return False, f"Source does not exist: {source}"
    if not destination:
        return False, "Missing destination parameter"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        shutil.move(source, destination)
        return True, f"Successfully moved {source} to {destination}"
    except Exception as e:
        return False, str(e)

def copy_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    source = parameters.get("source")
    destination = parameters.get("destination")
    if not source or not os.path.exists(source):
        return False, f"Source does not exist: {source}"
    if not destination:
        return False, "Missing destination parameter"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)
        return True, f"Successfully copied {source} to {destination}"
    except Exception as e:
        return False, str(e)

def verify_file(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Milestone 2.6 - Verification Step (file/folder existence + optional content check)."""
    path = parameters.get("path")
    if not path:
        return False, "Missing path parameter"
    if not os.path.exists(path):
        return False, f"Verification FAILED: {path} does NOT exist."
    
    expected_content = parameters.get("expected_content")
    if expected_content is not None and not os.path.isfile(path):
        return False, 'Verification FAILED: expected file content but path is not a file.'
    if expected_content is not None and os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                actual = f.read()
            if expected_content == actual:
                return True, f"Verification PASSED: {path} exists and contains expected content."
            else:
                return False, f"Verification FAILED: {path} exists but does NOT contain expected content."
        except Exception as e:
            return False, f"Verification FAILED: Could not read {path}: {e}"
    
    return True, f"Verification PASSED: {path} exists."

# ---------------------------------------------------------------------------
# UI / Accessibility Tools via uiautomation (Milestone 2.4)
# ---------------------------------------------------------------------------

def open_application(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Open an application by name or path."""
    app_name = parameters.get("app_name") or parameters.get("path", "")
    if not app_name:
        return False, "Missing app_name parameter"
    try:
        import subprocess
        subprocess.Popen([app_name], shell=False)
        return verify_window({'window_title': parameters['window_title']})
    except Exception as e:
        return False, f"Failed to launch {app_name}: {e}"

def type_in_window(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Type text into the focused control of a running application."""
    window_title = parameters.get("window_title", "")
    text = parameters.get("text", "")
    if not window_title:
        return False, "Missing window_title parameter"
    if not text:
        return False, "Missing text parameter"
    try:
        import uiautomation as auto
        import time
        time.sleep(1)  # Give the app a moment to be ready
        
        # Find the window by partial name
        win = auto.WindowControl(searchDepth=1, Name=window_title)
        if not win.Exists(3, 1):
            return False, f"Window matching '{window_title}' not found."
            
        win.SetActive()
        win.SetFocus()
        
        # Try Document control first (Windows 11 Notepad), then Edit
        target = win.DocumentControl()
        if not target.Exists(1):
            target = win.EditControl()
            
        if target.Exists(1):
            target.Click()
            # If it supports ValuePattern, set it directly, else SendKeys
            try:
                target.GetValuePattern().SetValue(text)
            except Exception:
                return False, 'Control does not support safe literal text entry'
        else:
            # Fallback: just type into the window itself
            return False, 'No exact editable target found'
        
        # Modern Notepad changes its title after entry. Read the same control,
        # rather than looking up the obsolete title or accepting a substring.
        return (target.GetValuePattern().Value == text, 'Literal text read back from the same editable control')
    except Exception as e:
        return False, f"Failed to type into '{window_title}': {e}"

def read_ui_tree(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Read the accessibility tree of a window."""
    window_title = parameters.get("window_title", "")
    if not window_title:
        return False, "Missing window_title parameter"
    try:
        import uiautomation as auto
        win = auto.WindowControl(searchDepth=1, Name=window_title)
        if not win.Exists(3, 1):
            return False, f"Window matching '{window_title}' not found."
        
        # Get child elements (top 2 levels to avoid flooding)
        tree_info = []
        for child, depth in auto.WalkControl(win, maxDepth=2):
            if depth > 0:
                indent = "  " * depth
                tree_info.append(f"{indent}[{child.ControlTypeName}] '{child.Name}'")
        
        result = f"UI Tree for '{window_title}':\n" + "\n".join(tree_info) if tree_info else "No children found."
        return True, result
    except Exception as e:
        return False, f"Failed to read UI tree for '{window_title}': {e}"

def click_ui_element(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Click a specific UI element by title and control type."""
    window_title = parameters.get("window_title", "")
    element_name = parameters.get("element_name", "")
    if not window_title:
        return False, "Missing window_title parameter"
    if not element_name:
        return False, "Missing element_name parameter"
    try:
        import uiautomation as auto
        win = auto.WindowControl(searchDepth=1, Name=window_title)
        if not win.Exists(3, 1):
            return False, f"Window matching '{window_title}' not found."
            
        target = win.Control(Name=element_name)
        if target.Exists(3, 1):
            expected = parameters.get('expected_element')
            if not expected:
                return False, 'Expected post-action element required'
            post = win.Control(Name=expected)
            if post.Exists(0, 0):
                return False, 'Postcondition already true; cannot verify transition'
            target.Click()
            return (True, 'Expected UI transition observed') if post.Exists(3, 1) else (False, 'Action verification failed')
        else:
            return False, f"Element '{element_name}' not found in '{window_title}'"
    except Exception as e:
        return False, f"Failed to click '{element_name}' in '{window_title}': {e}"

def verify_window(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Milestone 2.6 - Verify a window exists and optionally contains specific text."""
    window_title = parameters.get("window_title", "")
    expected_text = parameters.get("expected_text", "")
    if not window_title:
        return False, "Missing window_title parameter"
    try:
        import uiautomation as auto
        win = auto.WindowControl(searchDepth=1, Name=window_title)
        if not win.Exists(3, 1):
            return False, f"Verification FAILED: Window '{window_title}' not found."
        
        if expected_text:
            actual_text = ""
            target = win.DocumentControl()
            if not target.Exists(1):
                target = win.EditControl()
                
            if target.Exists(1):
                try:
                    actual_text = target.GetValuePattern().Value
                except:
                    try:
                        actual_text = target.GetTextPattern().DocumentRange.GetText(-1)
                    except:
                        pass
                        
            if expected_text in actual_text:
                return True, f"Verification PASSED: '{window_title}' contains '{expected_text}'"
            else:
                return False, f"Verification FAILED: '{window_title}' does NOT contain '{expected_text}'. Found: '{actual_text[:100]}'"
        
        return True, f"Verification PASSED: Window '{window_title}' exists and is ready."
    except Exception as e:
        return False, f"Verification FAILED: Window '{window_title}' error: {e}"


# ---------------------------------------------------------------------------
# Tool Registry - maps tool names to functions
# ---------------------------------------------------------------------------
TOOL_REGISTRY = {
    # File/OS
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
    "delete_file": delete_file,
    "create_folder": create_folder,
    "move_file": move_file,
    "copy_file": copy_file,
    "verify_file": verify_file,
    # UI / pywinauto
    "open_application": open_application,
    "type_in_window": type_in_window,
    "read_ui_tree": read_ui_tree,
    "click_ui_element": click_ui_element,
    "verify_window": verify_window,
}
