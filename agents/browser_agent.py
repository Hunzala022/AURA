from urllib.parse import urlsplit
from contextlib import contextmanager
from contextvars import ContextVar
import logging
from core.sanitization import sanitize_content

_session=ContextVar('aura_browser_session',default=None)

@contextmanager
def browser_session():
    state={}
    token=_session.set(state)
    try:yield state
    finally:
        try:
            if 'browser' in state:
                try:state['browser'].close()
                except Exception as error:logging.getLogger(__name__).warning('Browser cleanup failed: %s',type(error).__name__)
        finally:
            try:
                if 'driver' in state:
                    try:state['driver'].stop()
                    except Exception as error:logging.getLogger(__name__).warning('Browser driver cleanup failed: %s',type(error).__name__)
            finally:_session.reset(token)
def _run_browser_task(url,action,selector=None,text=None,expected_selector=None):
    if urlsplit(url).scheme not in ('http','https') or not urlsplit(url).hostname:
        return False,'Only explicit HTTP(S) URLs are supported'
    if _session.get() is None:
        with browser_session():return _run_browser_task(url,action,selector,text,expected_selector)
    try:
        state=_session.get()
        if 'page' not in state:
            from playwright.sync_api import sync_playwright
            state['driver']=sync_playwright().start()
            state['browser']=state['driver'].chromium.launch(headless=True)
            state['page']=state['browser'].new_page()
        page=state['page']
        if state.get('requested_url')!=url:
            page.goto(url,timeout=15000)
            state['requested_url']=url
        if action=='read':return True,sanitize_content(page.content())
        target=page.locator(selector)
        if target.count()!=1:return False,'Selector must identify exactly one element'
        if action=='fill':
            target.fill(text,timeout=5000)
            return target.input_value()==text,'Input value read back'
        if action=='click':
            if not expected_selector:return False,'Expected postcondition selector required'
            post=page.locator(expected_selector)
            if post.count()!=1:return False,'Postcondition must identify exactly one element'
            if post.is_visible():return False,'Postcondition already true; cannot verify transition'
            target.click(timeout=5000)
            post.wait_for(state='visible',timeout=5000)
            return post.is_visible(),'Expected UI transition observed'
        return False,'Unsupported browser action'
    except Exception as error:return False,'Browser action failed: '+type(error).__name__
def navigate_and_read(parameters):
    return _run_browser_task(parameters.get('url',''),'read')
def click_element(parameters):
    return _run_browser_task(parameters.get('url',''),'click',parameters.get('selector'),expected_selector=parameters.get('expected_selector'))
def fill_element(parameters):
    return _run_browser_task(parameters.get('url',''),'fill',parameters.get('selector'),parameters.get('text'))
TOOL_REGISTRY={'navigate_and_read':navigate_and_read,'browser_click':click_element,'browser_fill':fill_element}
