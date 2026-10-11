from urllib.parse import urlsplit
from core.sanitization import sanitize_content
def _run_browser_task(url,action,selector=None,text=None,expected_selector=None):
    if urlsplit(url).scheme not in ('http','https') or not urlsplit(url).hostname:
        return False,'Only explicit HTTP(S) URLs are supported'
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                page=browser.new_page()
                page.goto(url,timeout=15000)
                if action=='read':return True,sanitize_content(page.content())
                target=page.locator(selector)
                if target.count()!=1:return False,'Selector must identify exactly one element'
                if action=='fill':
                    target.fill(text,timeout=5000)
                    return target.input_value()==text,'Input value read back'
                if action=='click':
                    if not expected_selector:return False,'Expected postcondition selector required'
                    post=page.locator(expected_selector)
                    if post.is_visible():return False,'Postcondition already true; cannot verify transition'
                    target.click(timeout=5000)
                    post.wait_for(state='visible',timeout=5000)
                    return post.is_visible(),'Expected UI transition observed'
                return False,'Unsupported browser action'
            finally:browser.close()
    except Exception as error:return False,'Browser action failed: '+type(error).__name__
def navigate_and_read(parameters):
    return _run_browser_task(parameters.get('url',''),'read')
def click_element(parameters):
    return _run_browser_task(parameters.get('url',''),'click',parameters.get('selector'),expected_selector=parameters.get('expected_selector'))
def fill_element(parameters):
    return _run_browser_task(parameters.get('url',''),'fill',parameters.get('selector'),parameters.get('text'))
TOOL_REGISTRY={'navigate_and_read':navigate_and_read,'browser_click':click_element,'browser_fill':fill_element}
