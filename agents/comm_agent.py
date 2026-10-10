from typing import Dict, Any, Tuple
import uiautomation as auto
from core.human_layer import COMM_RATE_LIMITER, human_typing, human_delay

def send_message(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Generic tool to send a message via ANY desktop messaging app (WhatsApp, Slack, Discord).
    Parameters:
    - app_name: "WhatsApp", "Slack", "Discord", etc.
    - search_bar_name: The accessibility name of the search bar (e.g. "Search or start new chat")
    - contact: The name of the person/channel.
    - message_box_name: The accessibility name of the text input box.
    - text: The message to send.
    """
    app_name = parameters.get("app_name", "")
    search_bar_name = parameters.get("search_bar_name", "Search")
    contact = parameters.get("contact", "")
    message_box_name = parameters.get("message_box_name", "Type a message")
    text = parameters.get("text", "")

    if not all([app_name, contact, text]):
        return False, "Missing required parameters (app_name, contact, text)."

    if not COMM_RATE_LIMITER.check_limit():
        return False, "Rate limit exceeded. Too many communication actions in the last hour."

    try:
        # 1. Find the application window
        win = auto.WindowControl(searchDepth=1, RegexName=f".*{app_name}.*")
        if not win.Exists(3, 1):
            return False, f"{app_name} is not open or cannot be found."
        
        win.SetActive()
        win.SetFocus()
        human_delay()

        # 2. Search for the contact
        search_box = win.Control(searchDepth=10, Name=search_bar_name)
        if not search_box.Exists(2, 1):
            # Fallback to generic EditControl if name doesn't match perfectly
            search_box = win.EditControl()
            
        if search_box.Exists(1):
            human_typing(search_box, contact)
            human_delay()
            search_box.SendKeys('{Enter}')
            human_delay()
        else:
            return False, f"Could not find search bar in {app_name}."

        # 3. Type and send the message
        msg_box = win.Control(searchDepth=10, Name=message_box_name)
        if not msg_box.Exists(2, 1):
            # Try to find the last edit control on the screen (often the chat box)
            edits = win.GetChildren() # Simplified heuristic
            msg_box = win.EditControl(searchDepth=5) 
            
        if msg_box.Exists(1):
            human_typing(msg_box, text)
            human_delay()
            msg_box.SendKeys('{Enter}')
            return True, f"Successfully sent message to {contact} via {app_name}."
        else:
            return False, f"Could not find message input box in {app_name}."
            
    except Exception as e:
        return False, f"Error interacting with {app_name}: {e}"

def read_latest_message(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Reads the latest message from the currently open chat in the specified app."""
    app_name = parameters.get("app_name", "")
    if not app_name:
        return False, "Missing app_name parameter"
        
    try:
        win = auto.WindowControl(searchDepth=1, RegexName=f".*{app_name}.*")
        if not win.Exists(3, 1):
            return False, f"{app_name} is not open or cannot be found."
            
        # A generic heuristic: find all TextControls in the window, grab the last few.
        # This varies wildly between apps, but is a reasonable generic fallback.
        texts = []
        for control, depth in auto.WalkControl(win, maxDepth=10):
            if control.ControlTypeName == "TextControl" and control.Name:
                texts.append(control.Name)
                
        if not texts:
            return False, f"Could not find any readable text in {app_name}."
            
        # Return the last 5 distinct text nodes
        recent = texts[-5:]
        return True, "Recent messages:\n" + "\n".join(recent)
        
    except Exception as e:
        return False, f"Error reading from {app_name}: {e}"

TOOL_REGISTRY = {
    "send_message": send_message,
    "read_latest_message": read_latest_message
}
