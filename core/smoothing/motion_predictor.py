from collections import deque

class MotionPredictor:
    """
    Linear motion predictor. Blends current position with predicted next position.
    
    blend_factor: 0.0 = no prediction (off), 1.0 = full prediction (overshoots).
    Use 0.20-0.30 in practice.
    """
    
    def __init__(self, blend_factor: float = 0.25, history_len: int = 3):
        self.blend_factor = blend_factor
        self._history = deque(maxlen=history_len)
    
    def update(self, current_x: float, current_y: float) -> tuple:
        self._history.append((current_x, current_y))
        
        if len(self._history) < 2:
            return (current_x, current_y)
        
        # Linear prediction: extrapolate from last two positions
        prev_x, prev_y = self._history[-2]
        
        vel_x = current_x - prev_x
        vel_y = current_y - prev_y
        
        predicted_x = current_x + vel_x
        predicted_y = current_y + vel_y
        
        # Blend: mostly current, slightly predicted
        blended_x = current_x * (1 - self.blend_factor) + predicted_x * self.blend_factor
        blended_y = current_y * (1 - self.blend_factor) + predicted_y * self.blend_factor
        
        return (blended_x, blended_y)
    
    def reset(self):
        self._history.clear()
