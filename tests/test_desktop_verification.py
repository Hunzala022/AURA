import unittest
from unittest.mock import Mock,patch
from agents.os_agent import type_in_window
from core.verification import before_action,verify_action

class DesktopVerification(unittest.TestCase):
    def test_title_change_preserves_exact_control_verification(self):
        window=Mock();window.Exists.return_value=True
        target=window.DocumentControl.return_value;target.Exists.return_value=True
        value=target.GetValuePattern.return_value;value.Value=''
        def enter(text):
            window.Name='*Changed title - Notepad';value.Value=text
        value.SetValue.side_effect=enter
        params={'window_title':'Untitled - Notepad','text':'alpha {Enter}'}
        with patch('uiautomation.WindowControl',return_value=window),patch('time.sleep'):
            before=before_action('type_in_window',params)
            self.assertTrue(type_in_window(params)[0])
            self.assertTrue(verify_action('type_in_window',params,'readback',before))
            value.Value='prefix alpha {Enter}'
            self.assertFalse(verify_action('type_in_window',params,'readback',before))
