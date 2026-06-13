import math

class AdaptiveSensitivity:
    def __init__(self,
                 sensitivity: float = 1.2,
                 low_threshold: float = 5.0,
                 high_threshold: float = 20.0,
                 precision_factor: float = 0.5,
                 max_factor: float = 2.0):
        self.sensitivity = sensitivity
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.precision_factor = precision_factor
        self.max_factor = max_factor
    
    def apply(self, dx: float, dy: float) -> tuple:
        speed = math.sqrt(dx * dx + dy * dy)
        
        if speed < 0.001:
            return (0.0, 0.0)
        
        if speed <= self.low_threshold:
            factor = self.precision_factor
        elif speed >= self.high_threshold:
            factor = self.max_factor
        else:
            # Smooth interpolation between precision and max factors
            t = (speed - self.low_threshold) / (self.high_threshold - self.low_threshold)
            # Use smoothstep for natural feel (not linear)
            t = t * t * (3.0 - 2.0 * t)
            factor = self.precision_factor + t * (self.max_factor - self.precision_factor)
        
        scale = factor * self.sensitivity
        return (dx * scale, dy * scale)
