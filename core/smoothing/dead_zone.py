class DeadZoneFilter:
    """
    Suppresses micro-movements below threshold.
    
    IMPORTANT: threshold_px is in SCREEN pixels, not normalized coordinates.
    Apply this AFTER mapping to screen space, not before.
    
    Recommended threshold: 3–5px.
    - Below 3px: cursor still visibly trembles
    - Above 7px: precision targeting becomes difficult (can't click small buttons)
    - 4px is the sweet spot for most setups
    """
    
    def __init__(self, threshold_px: float = 4.0):
        self.threshold = threshold_px
        self._held_position = None
    
    def filter(self, new_x: float, new_y: float) -> tuple:
        import math
        if self._held_position is None:
            self._held_position = (new_x, new_y)
            return (new_x, new_y)
        
        held_x, held_y = self._held_position
        distance = math.sqrt((new_x - held_x)**2 + (new_y - held_y)**2)
        
        if distance < self.threshold:
            # Suppress: return held position, do not update held position
            return self._held_position
        
        # Movement is large enough — update held position and pass through
        self._held_position = (new_x, new_y)
        return (new_x, new_y)
    
    def reset(self):
        """Call when tracking is lost or cursor is forcibly repositioned."""
        self._held_position = None
