import base64,io,json,unittest
from unittest.mock import Mock,patch
from PIL import Image
import requests
from agents import vision_agent as vision
class Vision(unittest.TestCase):
    def setUp(self):
        b=io.BytesIO();Image.new('RGB',(32,32),'red').save(b,format='PNG');self.image=base64.b64encode(b.getvalue()).decode()
    def response(self,content):
        return Mock(json=lambda:{'message':{'content':json.dumps(content)}})
    def test_not_found_is_failure(self):
        with patch.object(vision.requests,'post',return_value=self.response({'found':False})):
            self.assertFalse(vision.test_model_vision(self.image,'button')[0])
    def test_bad_coordinates_and_types(self):
        for response in ({'found':True,'x':-1,'y':2},{'found':True,'x':1001,'y':2},{'found':True,'x':'1','y':2},{'found':True},{'found':'true','x':2,'y':2}):
            with self.subTest(response=response),patch.object(vision.requests,'post',return_value=self.response(response)):
                self.assertFalse(vision.test_model_vision(self.image,'button')[0])
    def test_http_error(self):
        r=self.response({});r.raise_for_status.side_effect=requests.HTTPError()
        with patch.object(vision.requests,'post',return_value=r):
            self.assertFalse(vision.test_model_vision(self.image,'button')[0])
    def test_timeout(self):
        with patch.object(vision.requests,'post',side_effect=requests.Timeout()):
            self.assertFalse(vision.test_model_vision(self.image,'button')[0])
    def test_valid_found_does_not_claim_action(self):
        with patch.object(vision.requests,'post',return_value=self.response({'found':True,'x':12,'y':8})):
            ok,output=vision.test_model_vision(self.image,'button')
            self.assertTrue(ok);self.assertFalse(json.loads(output)['action_executed'])
    def test_accessibility_precedes_vision_without_click(self):
        target=Mock();target.Exists.return_value=True
        window=Mock();window.Exists.return_value=True;window.Control.return_value=target
        with patch('uiautomation.WindowControl',return_value=window),patch.object(vision,'test_model_vision') as backend:
            self.assertTrue(vision.vision_locate_element({'window_title':'test','element_description':'button'})[0])
            target.Click.assert_not_called();backend.assert_not_called()
    def test_fallback_on_accessibility_failure(self):
        with patch('uiautomation.WindowControl',side_effect=RuntimeError()),patch.object(vision,'_take_screenshot',return_value=self.image),patch.object(vision,'test_model_vision',return_value=(False,'not found')) as backend:
            self.assertFalse(vision.vision_locate_element({'window_title':'test','element_description':'button'})[0])
            backend.assert_called_once()
    def test_click_verification_failure(self):
        from agents.os_agent import click_ui_element
        window=Mock();window.Exists.return_value=True
        target=Mock();target.Exists.return_value=True
        post=Mock();post.Exists.return_value=False
        window.Control.side_effect=[target,post]
        with patch('uiautomation.WindowControl',return_value=window):
            self.assertFalse(click_ui_element({'window_title':'test','element_name':'go','expected_element':'done'})[0])
            target.Click.assert_called_once()
