import math
import time

class LowPassFilter:
    def __init__(self):
        self._y = None
        self._s = None
    
    def filter(self, x: float, alpha: float) -> float:
        if self._y is None:
            self._y = x
            self._s = x
            return x
        
        self._y = alpha * x + (1.0 - alpha) * self._s
        self._s = self._y
        return self._y
    
    def last_value(self) -> float:
        return self._y if self._y is not None else 0.0

class OneEuroFilter:
    def __init__(self, freq: float = 30.0, min_cutoff: float = 1.0,
                 beta: float = 0.007, d_cutoff: float = 1.0):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self._x_filter = LowPassFilter()
        self._dx_filter = LowPassFilter()
        self._last_time = None
    
    def _alpha(self, cutoff: float) -> float:
        te = 1.0 / self.freq
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / te)
    
    def filter(self, x: float, timestamp: float = None) -> float:
        if timestamp is None:
            timestamp = time.time()
        
        # Update sample frequency from actual timing
        if self._last_time is not None:
            dt = timestamp - self._last_time
            if dt > 0:
                self.freq = 1.0 / dt
                # Clamp to reasonable range
                self.freq = max(10.0, min(120.0, self.freq))
        
        self._last_time = timestamp
        
        # Estimate speed of input change
        prev_x = self._x_filter.last_value()
        dx = (x - prev_x) * self.freq
        
        # Smooth the speed estimate
        edx = self._dx_filter.filter(dx, self._alpha(self.d_cutoff))
        
        # Adaptive cutoff: increases with speed
        cutoff = self.min_cutoff + self.beta * abs(edx)
        
        # Filter the input with adaptive cutoff
        return self._x_filter.filter(x, self._alpha(cutoff))

class OneEuroFilter2D:
    def __init__(self, freq: float = 30.0, min_cutoff: float = 1.0,
                 beta: float = 0.007, d_cutoff: float = 1.0):
        self.x_filter = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)
        self.y_filter = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)
    
    def filter(self, x: float, y: float, timestamp: float = None) -> tuple:
        t = timestamp or time.time()
        return (
            self.x_filter.filter(x, t),
            self.y_filter.filter(y, t)
        )
    
    def reset(self):
        self.x_filter = OneEuroFilter(
            self.x_filter.freq,
            self.x_filter.min_cutoff,
            self.x_filter.beta,
            self.x_filter.d_cutoff
        )
        self.y_filter = OneEuroFilter(
            self.y_filter.freq,
            self.y_filter.min_cutoff,
            self.y_filter.beta,
            self.y_filter.d_cutoff
        )
