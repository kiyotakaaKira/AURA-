import time
import math
from collections import deque

class IdleDetector:
    """
    Detects when the user's hand is present but stationary.
    """
    
    SPEED_HISTORY_FRAMES = 20
    
    def __init__(self, config: dict):
        idle_config = config.get('idle_detection', {})
        self.enabled = idle_config.get('enabled', True)
        self.IDLE_ENTRY_DELAY_MS = idle_config.get('entry_delay_ms', 500)
        self.IDLE_SPEED_THRESHOLD = idle_config.get('speed_threshold', 2.0)
        self.WAKE_SPEED_THRESHOLD = idle_config.get('wake_threshold', 4.0)
        self.WAKE_CONFIRMATION_FRAMES = idle_config.get('wake_confirmation_frames', 3)
        
        self._is_idle = False
        self._speed_history = deque(maxlen=self.SPEED_HISTORY_FRAMES)
        self._idle_entry_time = None
        self._candidate_idle = False
        self._wake_frame_count = 0
        self._last_pos = None
    
    def update(self, current_x: float, current_y: float) -> bool:
        if not self.enabled:
            return False
            
        now = time.time()
        
        if self._last_pos is None:
            speed = 0.0
        else:
            dx = current_x - self._last_pos[0]
            dy = current_y - self._last_pos[1]
            speed = math.sqrt(dx*dx + dy*dy)
        
        self._last_pos = (current_x, current_y)
        self._speed_history.append(speed)
        
        avg_speed = sum(self._speed_history) / len(self._speed_history)
        
        if not self._is_idle:
            if avg_speed < self.IDLE_SPEED_THRESHOLD:
                if not self._candidate_idle:
                    self._candidate_idle = True
                    self._idle_entry_time = now
                elif (now - self._idle_entry_time) * 1000 >= self.IDLE_ENTRY_DELAY_MS:
                    self._is_idle = True
                    self._wake_frame_count = 0
            else:
                self._candidate_idle = False
                self._idle_entry_time = None
        
        else:
            if speed > self.WAKE_SPEED_THRESHOLD:
                self._wake_frame_count += 1
                if self._wake_frame_count >= self.WAKE_CONFIRMATION_FRAMES:
                    self._is_idle = False
                    self._candidate_idle = False
                    self._wake_frame_count = 0
            else:
                self._wake_frame_count = 0
        
        return self._is_idle
    
    def force_wake(self):
        self._is_idle = False
        self._candidate_idle = False
        self._wake_frame_count = 0
        self._speed_history.clear()
    
    @property
    def is_idle(self) -> bool:
        return self._is_idle
