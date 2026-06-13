class ExponentialSmoother:
    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha
        self._last_value = None
        
    def filter(self, value: float) -> float:
        if self._last_value is None:
            self._last_value = value
            return value
        
        smoothed = self.alpha * value + (1.0 - self.alpha) * self._last_value
        self._last_value = smoothed
        return smoothed
