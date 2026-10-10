from typing import Dict, Any, Tuple
from core.sanitization import sanitize_content

# Playwright requires an event loop. For simplicity in a synchronous pipeline, 
# we use the sync_playwright context manager.
# However, launching a browser per tool call is slow. 
# For FYP-1, we'll keep it simple: open, act, close, or maintain a global instance.
# Maintaining a global sync instance is tricky with threads. Let's do simple open-act-close for now.

def _run_browser_task(url: str, action: str, selector: str = None, text: str = None) -> Tuple[bool, str]:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            
            result = ""
            if action == "read":
                raw_html = page.content()
                result = sanitize_content(raw_html)
            elif action == "click":
                if selector:
                    page.locator(selector).first.click(timeout=5000)
                    result = f"Clicked '{selector}' on {url}"
                else:
                    result = "No selector provided."
            elif action == "fill":
                if selector and text is not None:
                    page.locator(selector).first.fill(text, timeout=5000)
                    result = f"Filled '{selector}' with text on {url}"
                else:
                    result = "Missing selector or text."
            
            browser.close()
            return True, result
    except Exception as e:
        return False, f"Browser error: {e}"

def navigate_and_read(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    url = parameters.get("url")
    if not url: return False, "Missing url parameter"
    return _run_browser_task(url, "read")

def click_element(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    url = parameters.get("url")
    selector = parameters.get("selector")
    if not url or not selector: return False, "Missing url or selector"
    return _run_browser_task(url, "click", selector=selector)

def fill_element(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    url = parameters.get("url")
    selector = parameters.get("selector")
    text = parameters.get("text")
    if not url or not selector or text is None: return False, "Missing parameters"
    return _run_browser_task(url, "fill", selector=selector, text=text)

TOOL_REGISTRY = {
    "navigate_and_read": navigate_and_read,
    "browser_click": click_element,
    "browser_fill": fill_element
}
