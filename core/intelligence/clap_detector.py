import time
import math
from collections import deque

class DoubleClapDetector:
    """
    Detects a double-clap dismissal gesture.
    
    Requires both hands visible and two distinct clap events within 2 seconds.
    """
    
    def __init__(self, config: dict):
        dc_config = config.get('double_clap', {})
        self.CLAP_CLOSE_THRESHOLD = dc_config.get('close_threshold', 0.15)
        self.CLAP_RESET_THRESHOLD = dc_config.get('reset_threshold', 0.30)
        self.CLAP_WINDOW_SECONDS = dc_config.get('window_seconds', 2.0)
        self.MIN_VELOCITY_FOR_CLAP = 0.02
        
        self._state = "WAITING"         # WAITING -> CLAP1_DETECTED -> DISMISSED
        self._clap1_time = None
        self._hands_separated_since_clap1 = False
        self._last_distance = None
        self._distance_history = deque(maxlen=5)
    
    def update(self, hand_results: list) -> str:
        """
        hand_results: list of TrackingResult (one per hand, max 2).
        Returns: "NONE" | "CLAP1" | "DISMISSED"
        """
        now = time.time()
        
        if len(hand_results) < 2:
            if self._state == "CLAP1_DETECTED":
                if self._clap1_time and now - self._clap1_time > 0.5:
                    self._reset()
            return "NONE"
        
        palm1 = hand_results[0].palm_center
        palm2 = hand_results[1].palm_center
        
        distance = math.sqrt(
            (palm1[0] - palm2[0])**2 +
            (palm1[1] - palm2[1])**2
        )
        
        self._distance_history.append(distance)
        
        if self._last_distance is not None:
            velocity = distance - self._last_distance
        else:
            velocity = 0.0
        self._last_distance = distance
        
        is_close = distance < self.CLAP_CLOSE_THRESHOLD
        is_separating = velocity > self.MIN_VELOCITY_FOR_CLAP
        
        if self._state == "WAITING":
            if is_close and is_separating:
                self._state = "CLAP1_DETECTED"
                self._clap1_time = now
                self._hands_separated_since_clap1 = False
                return "CLAP1"
        
        elif self._state == "CLAP1_DETECTED":
            if now - self._clap1_time > self.CLAP_WINDOW_SECONDS:
                self._reset()
                return "NONE"
            
            if distance > self.CLAP_RESET_THRESHOLD:
                self._hands_separated_since_clap1 = True
            
            if (self._hands_separated_since_clap1 and
                is_close and is_separating):
                self._reset()
                return "DISMISSED"
        
        return "NONE"
    
    def _reset(self):
        self._state = "WAITING"
        self._clap1_time = None
        self._hands_separated_since_clap1 = False
        self._last_distance = None
        self._distance_history.clear()
