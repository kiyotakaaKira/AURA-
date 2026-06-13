from typing import Optional
import pyautogui

CONTEXT_ACTION_MAP = {
    "swipe_right": {
        "vscode": {"action": "next_tab", "keys": ["ctrl", "tab"]},
        "chrome": {"action": "next_tab", "keys": ["ctrl", "tab"]},
        "firefox": {"action": "next_tab", "keys": ["ctrl", "tab"]},
        "spotify": {"action": "next_track", "keys": ["ctrl", "right"]},
        "explorer": {"action": "forward", "keys": ["alt", "right"]},
        "sublime": {"action": "next_tab", "keys": ["ctrl", "tab"]},
        "terminal": {"action": "next_tab", "keys": ["ctrl", "shift", "right"]},
        "default": {"action": "next_tab", "keys": ["ctrl", "tab"]}
    },
    "swipe_left": {
        "vscode": {"action": "prev_tab", "keys": ["ctrl", "shift", "tab"]},
        "chrome": {"action": "prev_tab", "keys": ["ctrl", "shift", "tab"]},
        "firefox": {"action": "prev_tab", "keys": ["ctrl", "shift", "tab"]},
        "spotify": {"action": "prev_track", "keys": ["ctrl", "left"]},
        "explorer": {"action": "back", "keys": ["alt", "left"]},
        "default": {"action": "prev_tab", "keys": ["ctrl", "shift", "tab"]}
    },
    "four_fingers_down": {
        "default": {"action": "minimize", "keys": ["win", "down"]}
    },
    "spread": {
        "default": {"action": "show_desktop", "keys": ["win", "d"]}
    }
}

class IntentEngine:
    def resolve(self, gesture_name: str, context: str) -> Optional[dict]:
        if gesture_name not in CONTEXT_ACTION_MAP:
            return None
        
        gesture_map = CONTEXT_ACTION_MAP[gesture_name]
        return gesture_map.get(context) or gesture_map.get("default")
        
    def execute(self, action: dict):
        keys = action.get("keys", [])
        if not keys: return
        
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
