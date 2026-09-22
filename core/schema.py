from pydantic import BaseModel, Field
from typing import Dict, Any, List

class ToolCallSchema(BaseModel):
    tool_name: str = Field(..., description="The exact name of the tool you want to execute.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="A dictionary of parameters required by the tool. If no parameters are needed, provide an empty dictionary.")
    reasoning: str = Field(..., description="Step-by-step reasoning explaining exactly why this tool is being called and how it helps achieve the user's goal.")
    risk_hint: str = Field(..., description="Risk classification of the action. Must be one of: 'LOW', 'MEDIUM', 'HIGH'. High-risk actions involve deletion, credentials, or significant system changes.")

# 1.3 - 5 to 10 Manual Examples (Ground Truth)
EXAMPLE_TOOL_CALLS = [
    {
        "tool_name": "read_file",
        "parameters": {"file_path": "C:\\logs\\error.log"},
        "reasoning": "The user asked to check the latest errors. I need to read the error.log file first to extract the relevant information.",
        "risk_hint": "LOW"
    },
    {
        "tool_name": "list_directory",
        "parameters": {"dir_path": "D:\\Project AURA"},
        "reasoning": "The user asked to find the project proposal. I need to list the directory contents to locate the exact filename.",
        "risk_hint": "LOW"
    },
    {
        "tool_name": "web_search",
        "parameters": {"query": "latest Qwen model benchmarks 2026"},
        "reasoning": "The user wants to know the performance of the latest Qwen models. I need to search the web for recent benchmark data.",
        "risk_hint": "LOW"
    },
    {
        "tool_name": "delete_file",
        "parameters": {"file_path": "C:\\Users\\Admin\\Documents\\sensitive_data.csv"},
        "reasoning": "The user explicitly requested to permanently delete the sensitive data file.",
        "risk_hint": "HIGH"
    },
    {
        "tool_name": "click_ui_element",
        "parameters": {"element_id": "btn_submit", "window_title": "Login"},
        "reasoning": "The credentials have been entered. I now need to click the submit button to log in.",
        "risk_hint": "MEDIUM"
    },
    {
        "tool_name": "extract_text_from_vision",
        "parameters": {"window_id": "whatsapp_main"},
        "reasoning": "Accessibility hooks failed to read the chat history. I am falling back to vision to extract the text from the WhatsApp window.",
        "risk_hint": "LOW"
    },
    {
        "tool_name": "ssh_deploy",
        "parameters": {"server_ip": "192.168.1.100", "key_path": "~/.ssh/id_rsa"},
        "reasoning": "The user asked to deploy the codebase to the production server. This requires accessing the private SSH key.",
        "risk_hint": "HIGH"
    },
    {
        "tool_name": "store_memory",
        "parameters": {"key": "user_preference", "value": "Prefers dark mode in all apps."},
        "reasoning": "The user mentioned they always prefer dark mode. I should store this in the long-term vector memory for future reference.",
        "risk_hint": "LOW"
    }
]
