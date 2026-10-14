"""Exact accessibility targets; sending requires control-plane HITL."""
from core.human_layer import COMM_RATE_LIMITER, human_delay, move_pointer_to, typing_pause

# Chromium's window/browser/page wrappers place observed chat controls below
# depth 10. Keep traversal bounded while including the native page subtree.
UI_DEPTH = 30

def composer_value(box, parameters):
    value = box.GetValuePattern().Value
    # Observed Chromium WhatsApp contenteditable ValuePattern includes a final
    # line-feed even when the DOM composer is empty. Remove only this adapter
    # terminator, never strip spaces or arbitrary whitespace from a draft.
    if 'WhatsApp Business - Google Chrome' in parameters['app_name'] and parameters.get('message_box_name','').startswith('Type a message to ') and value.endswith('\n'):
        return value[:-1]
    return value

def enter_literal_message(auto, box, parameters, window=None):
    text=parameters['text']
    box.GetValuePattern().SetValue(text)
    human_delay()
    actual=composer_value(box,parameters)
    if actual==text:return True
    if actual or 'WhatsApp Business - Google Chrome' not in parameters['app_name']:
        return False
    # Chromium may expose ValuePattern but ignore SetValue on contenteditable.
    # Fallback only from a verified empty composer. Never parse user text as
    # hotkeys; control characters and unsupported supplementary codepoints deny.
    if any(ord(char)<32 or ord(char)>0xFFFF for char in text):return False
    if not move_pointer_to(auto,box):return False
    box.Click();box.SetFocus()
    for char in text:
        current = window.EditControl(searchDepth=UI_DEPTH,Name=parameters['message_box_name']) if window is not None else box
        if not auto.ControlsAreSame(auto.GetFocusedControl(),current):return False
        # Installed uiautomation sends down/up separately and returns the last
        # event count (1), despite documenting a combined count. Exact final
        # readback remains authoritative, not the injection return count.
        if auto.SendUnicodeChar(char)<1:return False
        typing_pause()
    human_delay()
    current = window.EditControl(searchDepth=UI_DEPTH,Name=parameters['message_box_name']) if window is not None else box
    return composer_value(current,parameters)==text

def select_business_self_result(auto,window,parameters):
    """Select one observed self-chat row, never the first fuzzy search result."""
    if 'WhatsApp Business - Google Chrome' not in parameters['app_name'] or parameters['recipient_control_name']!=parameters['contact']+' (You) Message yourself':
        return False
    label=parameters['contact']+' (You)'
    rows=[(c,d) for c,d in auto.WalkControl(window,maxDepth=UI_DEPTH)
          if c.ControlTypeName=='DataItemControl' and (c.Name==label or c.Name.startswith(label+' '))]
    if not rows:return False
    depth=min(d for c,d in rows);outer=[c for c,d in rows if d==depth]
    if len(outer)!=1:return False
    target=outer[0]
    # Chromium exposes nested selectable DataItems for one visual row. Accept
    # those only when every match belongs to the same observed ancestor row.
    for control,_ in rows:
        current=control
        for _ in range(UI_DEPTH):
            if current is None:break
            if auto.ControlsAreSame(current,target):break
            current=current.GetParentControl()
        else:return False
        if current is None or not auto.ControlsAreSame(current,target):return False
    if not move_pointer_to(auto,target):return False
    target.Click();human_delay()
    return True
def send_message(parameters):
    required=('app_name','contact','text','recipient_control_name')
    if not all(parameters.get(k) for k in required):return False,'Missing explicit recipient parameters'
    from core.tools import validate_parameters
    try:parameters=validate_parameters('send_message',parameters)
    except ValueError:return False,'Recipient contract rejected'
    if not COMM_RATE_LIMITER.check_limit(parameters['app_name']):return False,'Communication rate limit exceeded or storage unavailable'
    try:
        import uiautomation as auto
        win=auto.WindowControl(searchDepth=1,Name=parameters['app_name'])
        if not win.Exists(3,1):return False,'Exact application window not found'
        recipient=win.Control(searchDepth=UI_DEPTH,Name=parameters['recipient_control_name'])
        # Do not navigate away from an already verified conversation. Search
        # widgets can change their labels and selection when text is replaced.
        if not recipient.Exists(1,1):
            search=win.EditControl(searchDepth=UI_DEPTH,Name=parameters.get('search_bar_name','Search'))
            if not search.Exists(2,1):return False,'Exact search control not found'
            search.GetValuePattern().SetValue(parameters['contact'])
            if search.GetValuePattern().Value!=parameters['contact']:return False,'Recipient search text readback failed'
            if 'WhatsApp Business - Google Chrome' in parameters['app_name'] and parameters['recipient_control_name']==parameters['contact']+' (You) Message yourself':
                human_delay()
                if not select_business_self_result(auto,win,parameters):return False,'Unique self-chat search result not verified; message not sent'
            else:
                search.SendKeys('{Enter}')
                human_delay()
            recipient=win.Control(searchDepth=UI_DEPTH,Name=parameters['recipient_control_name'])
        if not recipient.Exists(2,1) or recipient.Name!=parameters['recipient_control_name']:
            return False,'Recipient identity not verified; message not sent'
        box=win.EditControl(searchDepth=UI_DEPTH,Name=parameters.get('message_box_name','Type a message'))
        if not box.Exists(2,1):return False,'Exact message input not found'
        def messages():
            return [c.Name for c,d in auto.WalkControl(win,maxDepth=UI_DEPTH) if c.ControlTypeName=='TextControl' and c.Name==parameters['text']]
        before=len(messages())
        if composer_value(box,parameters):
            return False,'Existing message draft preserved; composer must be empty'
        if not enter_literal_message(auto,box,parameters,win):return False,'Message text readback failed; any partial draft preserved'
        recipient=win.Control(searchDepth=UI_DEPTH,Name=parameters['recipient_control_name'])
        if not recipient.Exists(0,0) or recipient.Name!=parameters['recipient_control_name']:
            return False,'Recipient changed before send; draft preserved'
        box=win.EditControl(searchDepth=UI_DEPTH,Name=parameters.get('message_box_name','Type a message'))
        if composer_value(box,parameters)!=parameters['text']:return False,'Draft changed before send; preserved'
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
        texts=[c.Name for c,d in auto.WalkControl(win,maxDepth=UI_DEPTH) if c.ControlTypeName=='TextControl' and c.Name]
        return (True,'Recent visible text (not a guaranteed message API):\n'+'\n'.join(texts[-5:])) if texts else (False,'No readable text found')
    except Exception as error:return False,'Communication read failed: '+type(error).__name__
TOOL_REGISTRY={'send_message':send_message,'read_latest_message':read_latest_message}
