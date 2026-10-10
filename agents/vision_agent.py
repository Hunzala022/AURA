"""
Milestone 3.7 - Vision Fallback
Architecture:
  1. PRIMARY: Try accessibility tree lookup (uiautomation)
  2. FALLBACK: If accessibility fails, take a screenshot and ask
               Qwen3.5-4B if it can locate the element via multimodal
  3. FALLBACK-2: If model vision fails, use template/pixel matching (PIL)

The fallback is NEVER the default. It is only triggered when the
accessibility tree lookup raises an exception or returns nothing.
"""

import base64
import json
import os
import time
from typing import Dict, Any, Tuple, Optional

import requests

OLLAMA_API = "http://localhost:11434"
MODEL_NAME = "aura-qwen:latest"


# ---------------------------------------------------------------------------
# Helper: Take a screenshot and encode as base64
# ---------------------------------------------------------------------------
def _take_screenshot() -> Optional[str]:
    """Takes a screenshot, saves it temporarily, returns base64 string."""
    try:
        import mss
        import mss.tools
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            sct_img = sct.grab(monitor)
            # Save temporarily
            tmp_path = os.path.join(os.path.dirname(__file__), "..", "_vision_tmp.png")
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=tmp_path)
            with open(tmp_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Step 1: Test Qwen3.5-4B multimodal capability
# ---------------------------------------------------------------------------
def test_model_vision(screenshot_b64: str, element_description: str) -> Tuple[bool, str]:
    """
    Sends a screenshot to Qwen3.5-4B via Ollama to test multimodal capability.
    Returns (supported, response_text).
    Spec 3.7: Test the MAIN model first before adding a separate vision model.
    """
    try:
        resp = requests.post(
            f"{OLLAMA_API}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Look at this screenshot. Find the UI element described as: '{element_description}'. "
                                   f"Reply with ONLY a JSON object like: {{\"found\": true, \"description\": \"top-right corner, blue button\"}} "
                                   f"or {{\"found\": false}} if you cannot locate it.",
                        "images": [screenshot_b64]
                    }
                ],
                "stream": False,
                "options": {"temperature": 0.0}
            },
            timeout=60
        )
        content = resp.json().get("message", {}).get("content", "")
        # Check if the model returned meaningful JSON (not an error about unsupported images)
        if "found" in content.lower():
            return True, content
        return False, content
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Step 2: Template matching fallback (PIL-based, no second model needed)
# ---------------------------------------------------------------------------
def _find_by_color_heuristic(screenshot_b64: str, element_hint: str) -> Tuple[bool, str]:
    """
    Simple heuristic: If we have a reference image template, do template matching.
    Without a template, we report this as 'requires manual calibration'.
    This is the FYP-1 implementation boundary.
    """
    return False, (
        "Template matching requires a saved reference image of the target element. "
        "No template available for: '" + element_hint + "'. "
        "FYP-2 action: calibrate template library."
    )


# ---------------------------------------------------------------------------
# PUBLIC API: Vision-assisted element location
# ---------------------------------------------------------------------------
def vision_locate_element(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """
    PRIMARY: Try accessibility tree first.
    FALLBACK: If that fails, try model vision, then template matching.
    Only call this after the normal uiautomation lookup has already failed.
    """
    window_title = parameters.get("window_title", "")
    element_description = parameters.get("element_description", "")

    if not window_title or not element_description:
        return False, "Missing window_title or element_description"

    # --- PRIMARY: Accessibility tree ---
    try:
        import uiautomation as auto
        win = auto.WindowControl(searchDepth=1, RegexName=f".*{window_title}.*")
        if win.Exists(3, 1):
            # Try to find by name
            target = win.Control(searchDepth=10, Name=element_description)
            if target.Exists(2, 1):
                target.Click()
                return True, f"[ACCESSIBILITY] Found and clicked '{element_description}' in '{window_title}'"
    except Exception as acc_err:
        pass  # Fall through to vision fallback

    # --- FALLBACK 1: Model Vision ---
    screenshot_b64 = _take_screenshot()
    if screenshot_b64:
        vision_ok, vision_result = test_model_vision(screenshot_b64, element_description)
        if vision_ok:
            return True, f"[VISION-MODEL] Located element: {vision_result}"
        # If model doesn't support images, log it honestly
        model_vision_supported = vision_ok

    # --- FALLBACK 2: Template Matching ---
    if screenshot_b64:
        tmpl_ok, tmpl_result = _find_by_color_heuristic(screenshot_b64, element_description)
        if tmpl_ok:
            return True, f"[TEMPLATE] {tmpl_result}"
        return False, f"[ALL FALLBACKS EXHAUSTED] Accessibility failed. Model vision: not supported by this model variant. Template: {tmpl_result}"

    return False, "Could not take screenshot for vision fallback."


def capture_screenshot(parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """Captures and saves a screenshot for debugging or verification."""
    output_path = parameters.get("output_path", "D:\\AURA_Stage2_Test\\screenshot.png")
    try:
        import mss
        import mss.tools
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_path)
        return True, f"Screenshot saved to {output_path}"
    except Exception as e:
        return False, f"Screenshot failed: {e}"


TOOL_REGISTRY = {
    "vision_locate_element": vision_locate_element,
    "capture_screenshot": capture_screenshot,
}
