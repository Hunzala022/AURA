"""Live Qwen grounding of a real desktop canvas, with independent pixel truth.

The screenshot is captured by the production adapter, never synthesized or
substituted. Only the controlled fixture is foregrounded; no clicking is tested.
"""
import base64,hashlib,io,json,tempfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from core import control_plane as cp
from core.memory import MemoryManager
from core.schema import ToolCallSchema
from core.planning_trace import collect_planning_trace
from agents import vision_agent as vision

HTML='''<html><head><title>AURA Vision Fixture</title></head><body style="margin:0;background:#18202b"><canvas width="900" height="600"></canvas><script>const c=document.querySelector('canvas').getContext('2d');c.fillStyle='rgb(255,128,0)';c.fillRect(320,230,240,100);c.fillStyle='black';c.font='24px sans-serif';c.fillText('ORANGE TARGET',338,287);</script></body></html>'''

def run(output='reports/desktop_vision_live.json'):
    import uiautomation as auto
    from playwright.sync_api import sync_playwright
    rows=[];original=cp.generate_plan;capture=vision._take_screenshot
    with tempfile.TemporaryDirectory(prefix='aura_vision_',ignore_cleanup_errors=True) as folder, sync_playwright() as driver:
        root=Path(folder)
        memory=MemoryManager(db_path=root/'state/memory.db',chroma_path=root/'state/chroma',key_file=root/'state/key')
        browser=driver.chromium.launch(headless=False,args=['--start-fullscreen','--window-position=0,0'])
        try:
            page=browser.new_page(no_viewport=True);page.set_content(HTML);page.bring_to_front()
            page.wait_for_timeout(1000)
            windows=[w for w in auto.GetRootControl().GetChildren() if w.Name.startswith('AURA Vision Fixture')]
            if len(windows)!=1:raise RuntimeError('Unique controlled canvas window not observed')
            window=windows[0];title=window.Name
            for description,expected_found in [('ORANGE TARGET',True),('PURPLE TRIANGLE',False)]:
                frames=[];plans=[];rejected=[]
                def real_capture(*args,**kwargs):
                    frame=capture(*args,**kwargs)
                    if frame:frames.append(frame)
                    return frame
                def guarded(user,context=''):
                    raw=original(user,context);plans.append(raw)
                    try:
                        p=ToolCallSchema.model_validate(raw)
                        if len(p.plan)!=1 or p.plan[0].tool!='vision_locate_element' or p.plan[0].parameters!={'window_title':title,'element_description':description}:
                            raise ValueError('Unexpected location plan')
                        if window.Name!=title:raise ValueError('Fixture changed')
                        return raw
                    except (ValueError,TypeError):rejected.append('Plan outside fixture scope');return None
                prompt=f'Locate but do not click the element named {json.dumps(description)} in the existing window with exact title {json.dumps(title)}.'
                with patch.object(cp,'generate_plan',side_effect=guarded),patch.object(vision,'_take_screenshot',side_effect=real_capture),collect_planning_trace() as inference:
                    result=cp.execute_pipeline(prompt,memory_factory=lambda:memory,allowed_agents={'vision_agent'})
                observation=None;box=None;sha=None
                if frames:
                    data=base64.b64decode(frames[-1]);sha=hashlib.sha256(data).hexdigest()
                    picture=Image.open(io.BytesIO(data)).convert('RGB')
                    # Exact fixture color identifies independent target bounds on
                    # the actual captured screen. No model coordinates feed truth.
                    mask=Image.new('1',picture.size)
                    mask.putdata([pixel==(255,128,0) for pixel in picture.get_flattened_data()]);box=mask.getbbox()
                if result.get('steps') and result['steps'][0].get('result'):
                    try:observation=json.loads(result['steps'][0]['result'])
                    except (ValueError,TypeError):pass
                if expected_found:
                    passed=bool(frames and box and result['success'] and observation and observation.get('backend')=='model' and
                                box[0]<=observation.get('x',-1)<box[2] and box[1]<=observation.get('y',-1)<box[3] and observation.get('action_executed') is False)
                else:
                    passed=bool(frames and box and result['status']=='FAILED' and result.get('error')=='Element not found')
                rows.append({'target':description,'expected_found':expected_found,'raw_plan':plans[-1] if plans else None,'result':result,
                             'real_screenshot_count':len(frames),'screenshot_sha256':sha,'independent_target_bbox':box,'observation':observation,
                             'guard_rejections':rejected,'inference':inference,'passed':passed and not rejected})
                Path(output).write_text(json.dumps({'mode':'Real model planning, real desktop screenshot and local model vision; independent canvas pixel ground truth; no click','results':rows},indent=2),encoding='utf-8')
                print(description,rows[-1]['passed'],result['status'],flush=True)
        finally:browser.close()
    return len(rows)==2 and all(r['passed'] for r in rows)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',default='reports/desktop_vision_live.json');a=p.parse_args()
    raise SystemExit(0 if run(a.output) else 1)
