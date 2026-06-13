from core.tracker.hand_tracker import TrackingResult
import time
import math
from collections import deque

class OpenPalmRecognizer:
    def __init__(self):
        self.frame_buffer = deque(maxlen=15)
        self.is_active = False
        self.last_detected_time = 0.0
        self.HYSTERESIS_MS = 300
        
    def update(self, hand_result, now) -> dict:
        if not hand_result or not hand_result.detected:
            self.frame_buffer.append(False)
            fingers = [False]*5
            raw_conf = 0.0
        else:
            fingers = hand_result.fingers_extended
            if len(fingers) == 5:
                # All 5 fingers must be extended
                is_open_palm = all(fingers)
                self.frame_buffer.append(is_open_palm)
            else:
                self.frame_buffer.append(False)
                fingers = [False]*5
            raw_conf = hand_result.confidence
            
        frames_stable = sum(self.frame_buffer)
        
        if frames_stable == 15:
            self.is_active = True
            self.last_detected_time = now
        else:
            if self.is_active:
                if (now - self.last_detected_time) * 1000 > self.HYSTERESIS_MS:
                    self.is_active = False
                    
        # Calculate custom confidence
        # Base confidence from mediapipe (0.0 to 1.0)
        # Ratio of fingers extended (0.0 to 1.0)
        finger_ratio = sum(fingers) / 5.0
        stability_ratio = frames_stable / 15.0
        
        # If active, confidence is high. If not, it builds up.
        if self.is_active:
            conf_score = max(0.95, raw_conf)
        else:
            conf_score = (raw_conf * 0.3) + (finger_ratio * 0.4) + (stability_ratio * 0.3)
            
        return {
            "active": self.is_active,
            "confidence": conf_score,
            "frames_stable": frames_stable,
            "fingers": fingers
        }

class GestureEngine:
    """
    V4 Gesture Engine.
    Only handles static checks for:
    - Cursor Control (Index Pointing)
    - Scroll Mode (Two Fingers)
    
    Click logic is handled natively in ClickEngine based on distances.
    """
    
    def __init__(self):
        pass
        
    def is_index_pointing(self, hand_result: TrackingResult) -> bool:
        """
        Returns True when ONLY the index finger is extended.
        
        This is the cursor control condition.
        
        Rules:
        - Index finger MUST be extended
        - Middle, ring, pinky MUST NOT be extended (they can be neutral/curved)
        - Thumb state: don't care (it moves for click detection)
        """
        if not hand_result or not hand_result.detected:
            return False
        
        fingers = hand_result.fingers_extended
        if len(fingers) < 5:
            return False
            
        # fingers = [thumb, index, middle, ring, pinky]
        index_up = fingers[1]          # Index must be extended
        middle_down = not fingers[2]   # Middle must be closed
        ring_down = not fingers[3]     # Ring must be closed
        pinky_down = not fingers[4]    # Pinky must be closed
        
        return index_up and middle_down and ring_down and pinky_down

    def is_scroll_gesture(self, hand_result: TrackingResult) -> bool:
        """
        Two fingers up = scroll mode.
        
        Conditions:
        - Index finger extended: YES
        - Middle finger extended: YES
        - Ring finger extended: NO
        - Pinky extended: NO
        - Thumb: don't care
        """
        if not hand_result or not hand_result.detected:
            return False
        
        fingers = hand_result.fingers_extended
        if len(fingers) < 5:
            return False
            
        return (
            fingers[1] and      # Index up
            fingers[2] and      # Middle up
            not fingers[3] and  # Ring down
            not fingers[4]      # Pinky down
        )

class WindowControlManager:
    def __init__(self):
        import collections
        self.state = "IDLE"
        self.hold_start_time = 0.0
        self.HOLD_DURATION = 0.5
        
        self.history = collections.deque(maxlen=10)
        self.VELOCITY_THRESHOLD = 0.02
        
        self.mode = None # "MINIMIZE" or "RESTORE"
        self.progress = 0.0
        
        # Stability Shield variables
        self.persistence_start = 0.0
        self.PERSISTENCE_DURATION = 0.5
        
    def _is_open_palm(self, hand: TrackingResult) -> bool:
        if not hand or not hand.detected: return False
        f = hand.fingers_extended
        return f[1] and f[2] and f[3] and f[4]
        
    def _is_fist(self, hand: TrackingResult) -> bool:
        if not hand or not hand.detected: return False
        f = hand.fingers_extended
        return not f[1] and not f[2] and not f[3] and not f[4]

    def _is_moving(self, hand: TrackingResult) -> bool:
        import math
        self.history.append(hand.palm_center)
        if len(self.history) < 5: return True
        
        min_x = min(p[0] for p in self.history)
        max_x = max(p[0] for p in self.history)
        min_y = min(p[1] for p in self.history)
        max_y = max(p[1] for p in self.history)
        
        dist = math.hypot(max_x - min_x, max_y - min_y)
        return dist > self.VELOCITY_THRESHOLD

    def update(self, hand: TrackingResult, now: float, is_clicking: bool, is_scrolling: bool) -> tuple[str, float]:
        import ctypes
        
        self.progress = 0.0
        
        open_palm = self._is_open_palm(hand)
        fist = self._is_fist(hand)
        
        # 500ms Stability Shield: Don't instantly drop if tracking glitches
        if not hand or not hand.detected or hand.confidence < 0.85 or is_clicking or is_scrolling:
            if self.state in ["HOLDING", "SAW_PALM", "SAW_FIST"]:
                if now - self.persistence_start > self.PERSISTENCE_DURATION:
                    print(f"[WINDOW CONTROL] GESTURE ABORTED (Tracking Lost > {self.PERSISTENCE_DURATION}s)")
                    self.state = "IDLE"
                    self.mode = None
                elif self.state == "HOLDING":
                    # Keep progressing slightly or hold progress
                    elapsed = now - self.hold_start_time
                    self.progress = min(1.0, elapsed / self.HOLD_DURATION)
                    msg = f"WINDOW {self.mode}" if self.mode else ""
                    return msg, self.progress
                return "", 0.0
            else:
                self.state = "IDLE"
                self.mode = None
                return "", 0.0
                
        # If we have a good frame, reset the persistence timer
        self.persistence_start = now
            
        is_moving = self._is_moving(hand)
        
        if self.state == "IDLE":
            if open_palm and not is_moving:
                self.state = "SAW_PALM"
                print("[WINDOW CONTROL] GESTURE DETECTED: OPEN PALM")
            elif fist and not is_moving:
                self.state = "SAW_FIST"
                print("[WINDOW CONTROL] GESTURE DETECTED: FIST")
                
        elif self.state == "SAW_PALM":
            if fist and not is_moving:
                self.state = "HOLDING"
                self.mode = "MINIMIZE"
                self.hold_start_time = now
                print("[WINDOW CONTROL] GESTURE CONFIRMED: FIST (Mode: MINIMIZE)")
            elif not open_palm and (now - self.persistence_start > self.PERSISTENCE_DURATION):
                self.state = "IDLE"
                
        elif self.state == "SAW_FIST":
            if open_palm and not is_moving:
                self.state = "HOLDING"
                self.mode = "RESTORE"
                self.hold_start_time = now
                print("[WINDOW CONTROL] GESTURE CONFIRMED: OPEN PALM (Mode: RESTORE)")
            elif not fist and (now - self.persistence_start > self.PERSISTENCE_DURATION):
                self.state = "IDLE"
                
        elif self.state == "HOLDING":
            # Check if gesture breaks
            if (self.mode == "MINIMIZE" and not fist) or (self.mode == "RESTORE" and not open_palm) or is_moving:
                if now - self.persistence_start > self.PERSISTENCE_DURATION:
                    print("[WINDOW CONTROL] GESTURE ABORTED (Pose Broken)")
                    self.state = "IDLE"
                    self.mode = None
                    return "", 0.0
            else:
                # Still holding properly, update persistence
                self.persistence_start = now

            elapsed = now - self.hold_start_time
            self.progress = min(1.0, elapsed / self.HOLD_DURATION)
            
            if self.progress >= 1.0:
                print(f"[WINDOW CONTROL] ACTION TRIGGERED: {self.mode}")
                
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                
                if self.mode == "MINIMIZE":
                    self.last_minimized_hwnd = hwnd
                    user32.ShowWindow(hwnd, 6) # SW_MINIMIZE
                    print(f"[WINDOW CONTROL] OS COMMAND EXECUTED: Minimize (HWND: {hwnd})")
                else:
                    target_hwnd = getattr(self, "last_minimized_hwnd", hwnd)
                    user32.ShowWindow(target_hwnd, 9) # SW_RESTORE
                    print(f"[WINDOW CONTROL] OS COMMAND EXECUTED: Restore (HWND: {target_hwnd})")
                
                self.state = "COOLDOWN"
                self.progress = 1.0
                
        elif self.state == "COOLDOWN":
            self.progress = 1.0
            if (self.mode == "MINIMIZE" and not fist) or (self.mode == "RESTORE" and not open_palm):
                self.state = "IDLE"
                self.mode = None
                
        msg = f"WINDOW {self.mode}" if self.mode else ""
        return msg, self.progress
