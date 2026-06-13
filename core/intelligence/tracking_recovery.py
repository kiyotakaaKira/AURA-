import pyautogui
import time

class TrackingRecoveryManager:
    """
    Manages tracking stability. 
    Holds the last known position for 500ms during occlusions to prevent jitter.
    """
    
    TIMEOUT_MS = 500
    CONFIDENCE_THRESHOLD = 0.50
    
    def __init__(self, mouse_controller):
        self.mouse = mouse_controller
        self.state = "TRACKING"
        self._lost_time = None
        self.last_good_hand = None
        
    def update(self, hand_result) -> str:
        now = time.time()
        
        is_good = hand_result and hand_result.detected and hand_result.confidence >= self.CONFIDENCE_THRESHOLD
        
        if self.state == "TRACKING":
            if not is_good:
                self.state = "HOLDING"
                self._lost_time = now
                self.mouse.freeze()
                return "TRACKING" # Still report tracking to UI to prevent flicker
            self.last_good_hand = hand_result
            return "TRACKING"
            
        elif self.state == "HOLDING":
            if is_good:
                self.state = "TRACKING"
                self._lost_time = None
                self.last_good_hand = hand_result
                self.mouse.unfreeze()
                return "TRACKING"
            else:
                elapsed_ms = (now - self._lost_time) * 1000
                if elapsed_ms > self.TIMEOUT_MS:
                    self.state = "LOST"
                    self.last_good_hand = None
                    self.mouse.reset_all_filters()
                return "TRACKING" # Still holding last pos
                
        elif self.state == "LOST":
            if is_good:
                self.state = "TRACKING"
                self._lost_time = None
                self.last_good_hand = hand_result
                # Warp to prevent jumping from a far old position
                screen_x, screen_y = self.mouse._normalize(
                    hand_result.palm_center[0], hand_result.palm_center[1]
                )
                pyautogui.moveTo(screen_x, screen_y, _pause=False)
                self.mouse._last_cursor_pos = (screen_x, screen_y)
                self.mouse.position = (int(screen_x), int(screen_y))
                self.mouse.unfreeze()
                return "TRACKING"
            return "LOST"
            
        return self.state
