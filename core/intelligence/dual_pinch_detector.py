import time

class DualPinchDetector:
    """
    Detects a dual-pinch dismissal gesture.
    
    Sequence:
    1. Both hands visible.
    2. Both hands pinch (distance < 0.04) -> PINCH_1
    3. Both hands release (distance > 0.08)
    4. Both hands pinch again within 2 seconds of PINCH_1 -> DISMISSED
    """
    
    PINCH_THRESHOLD = 0.05
    RELEASE_THRESHOLD = 0.08
    WINDOW_SECONDS = 2.0
    
    def __init__(self, config: dict):
        self._state = "WAITING"
        self._pinch1_time = None
        self._released_since_pinch1 = False
        
    def update(self, left_hand, right_hand) -> str:
        """
        Returns: "NONE" | "PINCH_1" | "DISMISSED"
        """
        now = time.time()
        
        # Must have both hands detected
        if not left_hand.detected or not right_hand.detected:
            # If we were in the middle of a sequence, we don't necessarily reset immediately 
            # unless the time window expires. But we can't trigger state changes without both hands.
            self._check_timeout(now)
            return "NONE"
            
        # Both hands are visible. Check their pinch distances.
        left_pinch = left_hand.pinch_distance
        right_pinch = right_hand.pinch_distance
        
        both_pinched = (left_pinch < self.PINCH_THRESHOLD) and (right_pinch < self.PINCH_THRESHOLD)
        both_released = (left_pinch > self.RELEASE_THRESHOLD) and (right_pinch > self.RELEASE_THRESHOLD)
        
        if self._state == "WAITING":
            if both_pinched:
                self._state = "PINCH_1"
                self._pinch1_time = now
                self._released_since_pinch1 = False
                return "PINCH_1"
                
        elif self._state == "PINCH_1":
            if self._check_timeout(now):
                return "NONE"
                
            if both_released:
                self._released_since_pinch1 = True
                
            if self._released_since_pinch1 and both_pinched:
                self._reset()
                return "DISMISSED"
                
        return "NONE"
        
    def _check_timeout(self, now: float) -> bool:
        if self._state == "PINCH_1" and self._pinch1_time:
            if now - self._pinch1_time > self.WINDOW_SECONDS:
                self._reset()
                return True
        return False
        
    def _reset(self):
        self._state = "WAITING"
        self._pinch1_time = None
        self._released_since_pinch1 = False
