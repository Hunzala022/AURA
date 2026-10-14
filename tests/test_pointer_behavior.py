import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from core.human_layer import cursor_curve,move_pointer_to

class PointerBehavior(unittest.TestCase):
    def test_curve_preserves_endpoints_and_is_nonlinear(self):
        points=cursor_curve((0,0),(200,0),rng=SimpleNamespace(choice=lambda _:1))
        self.assertEqual((0,0),points[0]);self.assertEqual((200,0),points[-1])
        self.assertTrue(any(y>0 for x,y in points[1:-1]))
        self.assertTrue(all(0<=x<=200 and 0<=y<=40 for x,y in points))
    def test_actual_pointer_readback_required_and_no_click(self):
        auto=Mock();auto.GetCursorPos.side_effect=[(0,0),(110,110)]
        control=Mock();control.BoundingRectangle=SimpleNamespace(left=100,top=100,right=120,bottom=120)
        with patch('core.human_layer.time.sleep'):
            self.assertTrue(move_pointer_to(auto,control))
        self.assertEqual((110,110),auto.SetCursorPos.call_args.args);control.Click.assert_not_called()
        auto.GetCursorPos.side_effect=[(0,0),(5,5)]
        with patch('core.human_layer.time.sleep'):
            self.assertFalse(move_pointer_to(auto,control))
    def test_invalid_rectangle_prevents_movement(self):
        auto=Mock();control=Mock();control.BoundingRectangle=SimpleNamespace(left=10,top=10,right=0,bottom=0)
        self.assertFalse(move_pointer_to(auto,control));auto.SetCursorPos.assert_not_called()
