import os
import fnmatch
from typing import Dict, Any, Tuple

def search_files_by_name(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Search for files matching a specific name pattern."""
    root_dir = parameters.get("directory", "D:\\")
    pattern = parameters.get("pattern", "")
    
    if not pattern:
        return False, "Missing pattern parameter."
    if not os.path.exists(root_dir):
        return False, f"Directory {root_dir} does not exist."
        
    matches = []
    try:
        # We cap the search to prevent infinite loops / taking too long
        max_files = 100
        count = 0
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if fnmatch.fnmatchcase(filename.lower(), pattern.lower()):
                    matches.append(os.path.join(dirpath, filename))
                    count += 1
                if count >= max_files:
                    break
            if count >= max_files:
                break
                
        if not matches:
            return True, f"No files found matching '{pattern}' in {root_dir}"
        return True, "Found files:\n" + "\n".join(matches[:20]) + (f"\n...and {len(matches)-20} more." if len(matches) > 20 else "")
    except Exception as e:
        return False, f"Error searching files: {e}"

def search_files_by_content(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Search for a specific string inside files in a directory."""
    root_dir = parameters.get("directory", "D:\\")
    query = parameters.get("query", "")
    extension = parameters.get("extension", ".txt")
    
    if not query:
        return False, "Missing query parameter."
    if not os.path.isdir(root_dir):
        return False, 'Search directory does not exist'
        
    matches = []
    try:
        max_files_to_read = 500
        files_read = 0
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(extension):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                matches.append(filepath)
                    except Exception:
                        pass
                    files_read += 1
                if files_read >= max_files_to_read:
                    break
            if files_read >= max_files_to_read:
                break
                
        if not matches:
            return True, f"No files found containing '{query}' in {root_dir}"
        return True, "Found string in files:\n" + "\n".join(matches[:10])
    except Exception as e:
        return False, f"Error searching file contents: {e}"

TOOL_REGISTRY = {
    "search_files_by_name": search_files_by_name,
    "search_files_by_content": search_files_by_content
}
