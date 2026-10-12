import unittest
from unittest.mock import patch,Mock
from agents.comm_agent import send_message, composer_value, enter_literal_message
from core.human_layer import RateLimiter
class Communication(unittest.TestCase):
    def test_literal_fallback_never_parses_braces_and_stops_on_focus_loss(self):
        auto=Mock();auto.ControlsAreSame.return_value=True;auto.SendUnicodeChar.return_value=1
        box=Mock();params={'app_name':'WhatsApp Business - Google Chrome','text':'{Enter}'}
        with patch('agents.comm_agent.composer_value',side_effect=['','{Enter}']),patch('agents.comm_agent.human_delay'):
            self.assertTrue(enter_literal_message(auto,box,params))
        self.assertEqual(list('{Enter}'),[c.args[0] for c in auto.SendUnicodeChar.call_args_list])
        box.SendKeys.assert_not_called()
        auto.SendUnicodeChar.reset_mock();auto.ControlsAreSame.return_value=False
        with patch('agents.comm_agent.composer_value',return_value=''),patch('agents.comm_agent.human_delay'):
            self.assertFalse(enter_literal_message(auto,box,params))
        auto.SendUnicodeChar.assert_not_called()
    def test_literal_fallback_preserves_partial_text_and_rejects_controls(self):
        for actual,text in [('partial','hello'),('','line\nnext')]:
            auto=Mock();box=Mock()
            with patch('agents.comm_agent.composer_value',return_value=actual),patch('agents.comm_agent.human_delay'):
                self.assertFalse(enter_literal_message(auto,box,{'app_name':'WhatsApp Business - Google Chrome','text':text}))
            auto.SendUnicodeChar.assert_not_called();box.Click.assert_not_called()
    def test_chromium_composer_terminator_preserves_whitespace_drafts(self):
        box=Mock();params={'app_name':'(14) WhatsApp Business - Google Chrome','message_box_name':'Type a message to Alice'}
        for raw,expected in [('\n',''),(' \n',' '),('\n\n','\n'),('literal {Enter}\n','literal {Enter}')]:
            box.GetValuePattern.return_value.Value=raw
            self.assertEqual(expected,composer_value(box,params))
        box.GetValuePattern.return_value.Value='\n'
        self.assertEqual('\n',composer_value(box,{'app_name':'Other app'}))
    def test_recipient_mismatch_never_types_or_sends_message(self):
        window=Mock();window.Exists.return_value=True
        search=Mock();search.Exists.return_value=True
        recipient=Mock();recipient.Exists.return_value=True;recipient.Name='Wrong person'
        window.EditControl.return_value=search;window.Control.return_value=recipient
        with patch('uiautomation.WindowControl',return_value=window),patch('agents.comm_agent.human_delay'),patch('agents.comm_agent.COMM_RATE_LIMITER',RateLimiter(30)):
            ok,_=send_message({'app_name':'Fixture','contact':'Alice','text':'hello','recipient_control_name':'Alice'})
            self.assertFalse(ok);self.assertEqual(1,window.Control.call_count)
            window.EditControl.assert_not_called()
    def test_rate_limit_blocks_before_ui(self):
        limiter=RateLimiter(0)
        with patch('agents.comm_agent.COMM_RATE_LIMITER',limiter),patch('uiautomation.WindowControl') as window:
            self.assertFalse(send_message({'app_name':'Fixture','contact':'Alice','text':'hello','recipient_control_name':'Alice'})[0])
            window.assert_not_called()
    def test_missing_explicit_recipient_fails(self):
        self.assertFalse(send_message({'app_name':'Fixture','contact':'Alice','text':'hello'})[0])
    def test_unrelated_header_rejects_before_ui(self):
        with patch('uiautomation.WindowControl') as window:
            self.assertFalse(send_message({'app_name':'Fixture','contact':'Alice','recipient_control_name':'Search','text':'hello'})[0])
            window.assert_not_called()
    def test_existing_draft_is_not_overwritten(self):
        window=Mock();window.Exists.return_value=True
        search=Mock();search.Exists.return_value=True
        recipient=Mock();recipient.Exists.return_value=True;recipient.Name='Alice (You)'
        box=Mock();box.Exists.return_value=True;box.GetValuePattern.return_value.Value='existing draft'
        window.EditControl.return_value=box;window.Control.return_value=recipient
        with patch('uiautomation.WindowControl',return_value=window),patch('uiautomation.WalkControl',return_value=[]),patch('agents.comm_agent.human_delay'),patch('agents.comm_agent.COMM_RATE_LIMITER',RateLimiter(30)):
            ok,_=send_message({'app_name':'Fixture','contact':'Alice','recipient_control_name':'Alice (You)','text':'hello'})
            self.assertFalse(ok);box.GetValuePattern.return_value.SetValue.assert_not_called();box.SendKeys.assert_not_called()
