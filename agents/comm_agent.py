"""Exact accessibility targets; sending requires control-plane HITL."""
from core.human_layer import COMM_RATE_LIMITER, human_delay
def send_message(parameters):
    required=('app_name','contact','text','recipient_control_name')
    if not all(parameters.get(k) for k in required):return False,'Missing explicit recipient parameters'
    if not COMM_RATE_LIMITER.check_limit():return False,'Communication rate limit exceeded'
    try:
        import uiautomation as auto
        win=auto.WindowControl(searchDepth=1,Name=parameters['app_name'])
        if not win.Exists(3,1):return False,'Exact application window not found'
        search=win.Control(searchDepth=10,Name=parameters.get('search_bar_name','Search'))
        if not search.Exists(2,1):return False,'Exact search control not found'
        search.GetValuePattern().SetValue(parameters['contact'])
        search.SendKeys('{Enter}')
        human_delay()
        recipient=win.Control(searchDepth=10,Name=parameters['recipient_control_name'])
        if not recipient.Exists(2,1) or recipient.Name!=parameters['contact']:
            return False,'Recipient identity not verified; message not sent'
        box=win.Control(searchDepth=10,Name=parameters.get('message_box_name','Type a message'))
        if not box.Exists(2,1):return False,'Exact message input not found'
        def messages():
            return [c.Name for c,d in auto.WalkControl(win,maxDepth=10) if c.ControlTypeName=='TextControl' and c.Name==parameters['text']]
        before=len(messages())
        box.GetValuePattern().SetValue(parameters['text'])
        if box.GetValuePattern().Value!=parameters['text']:return False,'Message text readback failed'
        box.SendKeys('{Enter}')
        human_delay()
        if len(messages())<=before:return False,'Send attempted but new message was not observed; do not retry automatically'
        return True,'New message observed in verified recipient UI; server delivery not independently confirmed'
    except Exception as error:return False,'Communication failed: '+type(error).__name__
def read_latest_message(parameters):
    try:
        import uiautomation as auto
        win=auto.WindowControl(searchDepth=1,Name=parameters['app_name'])
        if not win.Exists(3,1):return False,'Exact application not found'
        texts=[c.Name for c,d in auto.WalkControl(win,maxDepth=10) if c.ControlTypeName=='TextControl' and c.Name]
        return (True,'Recent visible text (not a guaranteed message API):\n'+'\n'.join(texts[-5:])) if texts else (False,'No readable text found')
    except Exception as error:return False,'Communication read failed: '+type(error).__name__
TOOL_REGISTRY={'send_message':send_message,'read_latest_message':read_latest_message}
