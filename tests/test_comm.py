import unittest
from unittest.mock import patch,Mock
from agents.comm_agent import send_message
from core.human_layer import RateLimiter
class Communication(unittest.TestCase):
    def test_recipient_mismatch_never_types_or_sends_message(self):
        window=Mock();window.Exists.return_value=True
        search=Mock();search.Exists.return_value=True
        recipient=Mock();recipient.Exists.return_value=True;recipient.Name='Wrong person'
        window.Control.side_effect=[search,recipient]
        with patch('uiautomation.WindowControl',return_value=window),patch('agents.comm_agent.human_delay'),patch('agents.comm_agent.COMM_RATE_LIMITER',RateLimiter(30)):
            ok,_=send_message({'app_name':'Fixture','contact':'Alice','text':'hello','recipient_control_name':'Alice'})
            self.assertFalse(ok);self.assertEqual(2,window.Control.call_count)
    def test_rate_limit_blocks_before_ui(self):
        limiter=RateLimiter(0)
        with patch('agents.comm_agent.COMM_RATE_LIMITER',limiter),patch('uiautomation.WindowControl') as window:
            self.assertFalse(send_message({'app_name':'Fixture','contact':'Alice','text':'hello','recipient_control_name':'Alice'})[0])
            window.assert_not_called()
    def test_missing_explicit_recipient_fails(self):
        self.assertFalse(send_message({'app_name':'Fixture','contact':'Alice','text':'hello'})[0])
