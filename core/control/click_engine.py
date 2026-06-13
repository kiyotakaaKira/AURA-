import time
import pyautogui
from core.tracker.hand_tracker import TrackingResult

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class ClickEngine:
    def __init__(self, config: dict):
        self.state = "IDLE"
        self.right_state = "IDLE"
        self._last_action = ""
        self.feedback_start_time = 0.0
        
        # V2 Timings
        self.LEFT_CLICK_FEEDBACK_MS = 200
        self.DRAG_THRESHOLD_MS = 300
        self.curl_start_time = 0.0

    def reset(self):
        self.state = "IDLE"
        self.right_state = "IDLE"
        self._last_action = ""

    def update(self, hand: TrackingResult) -> str:
        now = time.time()
        
        if not hand or not hand.detected:
            if self.state in ["HELD", "DRAGGING"]:
                pyautogui.mouseUp(_pause=False)
                self.state = "IDLE"
                self._set_feedback("DROP", now)
            else:
                self.state = "IDLE"
            self.right_state = "IDLE"
            return self._get_feedback(now)
            
        # Index finger is at index 1, Middle at 2 in fingers_extended array
        index_extended = hand.fingers_extended[1]
        middle_extended = hand.fingers_extended[2]
        
        # --- Right Click (Middle Curl) ---
        if self.right_state == "IDLE":
            if not middle_extended:
                pyautogui.rightClick(_pause=False)
                self.right_state = "CURLED"
                self._set_feedback("RIGHT CLICK", now)
        elif self.right_state == "CURLED":
            if middle_extended:
                self.right_state = "IDLE"
                
        # --- Left Click / Drag (Index Curl) ---
        if self.state == "IDLE":
            if not index_extended:
                pyautogui.mouseDown(_pause=False)
                self.state = "HELD"
                self.curl_start_time = now
                self._set_feedback("LEFT CLICK", now)
        elif self.state == "HELD":
            if index_extended:
                pyautogui.mouseUp(_pause=False)
                self.state = "IDLE"
                # Keep the LEFT CLICK badge fading naturally, do not overwrite with drop.
            elif (now - self.curl_start_time) > (self.DRAG_THRESHOLD_MS / 1000.0):
                self.state = "DRAGGING"
                self._set_feedback("DRAGGING", now)
        elif self.state == "DRAGGING":
            if index_extended:
                pyautogui.mouseUp(_pause=False)
                self.state = "IDLE"
                self._set_feedback("DROP", now)
            else:
                # Keep showing dragging badge continuously
                self.feedback_start_time = now
                
        return self._get_feedback(now)

    def _set_feedback(self, action: str, now: float):
        self._last_action = action
        self.feedback_start_time = now

    def _get_feedback(self, now: float) -> str:
        if self.state == "DRAGGING":
            return "DRAGGING"
            
        elapsed = (now - self.feedback_start_time) * 1000.0
        if elapsed < self.LEFT_CLICK_FEEDBACK_MS:
            return self._last_action
        return ""
        
    def reset(self):
        if self.state in ["HELD", "DRAGGING"]:
            pyautogui.mouseUp(_pause=False)
        self.state = "IDLE"
        self.right_state = "IDLE"
        self._last_action = ""
        self.feedback_start_time = 0.0
