import time
from enum import Enum, auto
from core.tracker.tracker_fusion import FusedState

class DismissState(Enum):
    IDLE = auto()
    CLAP_1 = auto()
    CLAP_2 = auto()
    DISMISS_CONFIRMATION = auto()
    AURA_DISMISSED = auto()
    DISMISS_CANCELLED = auto()

class DismissManager:
    def __init__(self):
        self.state = DismissState.IDLE
        self._last_clap_time = 0.0
        self._timeout_sec = 2.0
        self._was_touching = False
        
        # Distance threshold (normalized coordinate distance) to count as touching
        self._touch_threshold = 0.15 
        
        # Shutdown timeline variables
        self.shutdown_triggered_time = 0.0

    def are_hands_touching(self, fused: FusedState) -> bool:
        if len(fused.hands) < 2:
            return False
            
        h1 = fused.hands[0]
        h2 = fused.hands[1]
        
        if h1.confidence < 0.8 or h2.confidence < 0.8:
            return False
            
        # Distance between palm centers
        c1 = np.array(h1.palm_center)
        c2 = np.array(h2.palm_center)
        distance = np.linalg.norm(c1 - c2)
        
        return distance < self._touch_threshold

    def update(self, fused: FusedState) -> DismissState:
        now = time.time()
        
        if self.state in [DismissState.AURA_DISMISSED, DismissState.DISMISS_CONFIRMATION]:
            return self.state

        if self.state == DismissState.DISMISS_CANCELLED:
            if now - self._last_clap_time > 1.5: 
                self.state = DismissState.IDLE
            return self.state

        # Timeout check for clap sequence
        if self.state in [DismissState.CLAP_1, DismissState.CLAP_2] and (now - self._last_clap_time) > self._timeout_sec:
            self.state = DismissState.DISMISS_CANCELLED
            self._last_clap_time = now
            return self.state

        import numpy as np # Import locally if needed or rely on main imports
        is_touching = self.are_hands_touching(fused)

        # Clap detection: hands were touching, and are now pulled apart (a complete clap)
        # We trigger the count when they *separate* after a touch, ensuring it's a full clap motion
        clap_completed = self._was_touching and not is_touching
        
        if clap_completed:
            if self.state == DismissState.IDLE:
                self.state = DismissState.CLAP_1
                self._last_clap_time = now
            elif self.state == DismissState.CLAP_1:
                # To prevent a single long touch triggering twice due to tracking noise,
                # ensure enough time has passed since the first clap (e.g. 0.2s)
                if now - self._last_clap_time > 0.2:
                    self.state = DismissState.DISMISS_CONFIRMATION
                    self.shutdown_triggered_time = now

        self._was_touching = is_touching

        return self.state
