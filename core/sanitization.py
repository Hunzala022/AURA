import re
from bs4 import BeautifulSoup

def sanitize_content(raw_html: str) -> str:
    """
    Milestone 3.6 - Zero-trust sanitization pipeline.
    Strips HTML and JavaScript before it reaches the model.
    Also strips known prompt injection trigger phrases.
    """
    if not raw_html:
        return ""
        
    # 1. Parse with BeautifulSoup to strip tags and scripts
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove script and style elements completely
    for element in soup(["script", "style", "iframe", "object", "embed"]):
        element.decompose()
        
    # Get text
    text = soup.get_text(separator="\n", strip=True)
    
    # 2. Heuristic prompt injection filtering
    # (In a production FYP, this would be a secondary classification model, 
    # but here we use regex for explicit instructions)
    injection_patterns = [
        r"(?i)ignore previous instructions",
        r"(?i)system prompt",
        r"(?i)you are now",
        r"(?i)disregard above",
        r"(?i)forget previous"
    ]
    
    for pattern in injection_patterns:
        text = re.sub(pattern, "[MALICIOUS CONTENT REMOVED]", text)
        
    return text
