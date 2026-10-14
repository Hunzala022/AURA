"""Accessibility-first location only. Location success never implies a click."""
import base64
import io
import json
from pathlib import Path
import requests
from PIL import Image
from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, ValidationError
OLLAMA_API='http://localhost:11434'
MODEL_NAME='aura-qwen:latest'
class VisionResult(BaseModel):
    model_config=ConfigDict(extra='forbid')
    found: StrictBool
    x: StrictInt | None=None
    y: StrictInt | None=None
def _take_screenshot(region=None):
    try:
        import mss
        import mss.tools
        with mss.mss() as sct:
            shot=sct.grab(region if region is not None else sct.monitors[1])
            return base64.b64encode(mss.tools.to_png(shot.rgb,shot.size)).decode()
    except Exception:return None
def test_model_vision(screenshot_b64,element_description):
    """Return true only for validated, in-image coordinates with found=true."""
    try:
        with Image.open(io.BytesIO(base64.b64decode(screenshot_b64,validate=True))) as picture:
            width,height=picture.size
        response=requests.post(OLLAMA_API+'/api/chat',json={
            'model':MODEL_NAME,'messages':[{'role':'user','content':
                f'Locate the center of {element_description!r}. Return JSON with found boolean and integer x,y in normalized coordinates from 0 to 1000 relative to image width and height. If absent return {{"found":false}}.',
                'images':[screenshot_b64]}],'stream':False,'think':False,'format':VisionResult.model_json_schema(),
            'options':{'temperature':0.0}},timeout=60)
        response.raise_for_status()
        parsed=VisionResult.model_validate_json(response.json()['message']['content'])
        if not parsed.found:return False,'Element not found'
        if parsed.x is None or parsed.y is None or not (0<=parsed.x<=1000 and 0<=parsed.y<=1000):
            return False,'Invalid image coordinates'
        x=round(parsed.x*(width-1)/1000)
        y=round(parsed.y*(height-1)/1000)
        return True,json.dumps({'backend':'model','found':True,'x':x,'y':y,'coordinate_space':'image_pixels','action_executed':False})
    except requests.Timeout:return False,'Vision backend timeout'
    except requests.RequestException:return False,'Vision backend HTTP/connection error'
    except (ValueError,KeyError,TypeError,OSError,ValidationError):return False,'Invalid vision response or image'
def _find_by_color_heuristic(screenshot_b64,element_hint):
    return False,'Template matching is not implemented; no location claimed'

def _is_foreground(handle):
    import ctypes
    from ctypes import wintypes
    user32=ctypes.WinDLL('user32',use_last_error=True)
    user32.GetForegroundWindow.restype=wintypes.HWND
    return user32.GetForegroundWindow()==handle

def _foreground_rectangle(window):
    window.SetActive()
    if not _is_foreground(window.NativeWindowHandle):return None
    rectangle=window.BoundingRectangle
    region={'left':rectangle.left,'top':rectangle.top,'width':rectangle.right-rectangle.left,'height':rectangle.bottom-rectangle.top}
    if not all(type(value) is int for value in region.values()) or region['width']<=0 or region['height']<=0:return None
    return region
def vision_locate_element(parameters):
    title=parameters.get('window_title','');description=parameters.get('element_description','')
    if not title or not description:return False,'Missing window_title or element_description'
    try:
        import uiautomation as auto
        window=auto.WindowControl(searchDepth=1,Name=title)
        if not window.Exists(3,1):return False,'Exact target window not found'
        target=window.Control(searchDepth=10,Name=description)
        try:accessible=target.Exists(2,1)
        except Exception:accessible=False
        if accessible:
            return True,json.dumps({'backend':'accessibility','found':True,'element':description,'action_executed':False})
        region=_foreground_rectangle(window)
        if region is None:return False,'Target window could not be foregrounded'
        screenshot=_take_screenshot(region)
        if not screenshot:return False,'Screenshot unavailable'
        if not _is_foreground(window.NativeWindowHandle):return False,'Target window changed during capture'
    except Exception:return False,'Exact target window unavailable for safe capture'
    success,output=test_model_vision(screenshot,description)
    if success:
        located=json.loads(output)
        located.update(window_origin={'x':region['left'],'y':region['top']},screen_x=region['left']+located['x'],screen_y=region['top']+located['y'])
        return True,json.dumps(located)
    return False,output
def capture_screenshot(parameters):
    try:
        shot=_take_screenshot()
        if not shot:return False,'Screenshot unavailable'
        path=Path(parameters['output_path']);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(base64.b64decode(shot))
        with Image.open(path) as image:image.verify()
        return True,'Screenshot saved and decoded successfully'
    except Exception:return False,'Screenshot save/verification failed'
TOOL_REGISTRY={'vision_locate_element':vision_locate_element,'capture_screenshot':capture_screenshot}
