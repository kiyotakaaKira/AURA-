import ctypes
import pyautogui

from ..smoothing.one_euro_filter import OneEuroFilter2D

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self, config: dict):
        self.screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Load from calibration profile
        zone = config.get('calibration', {}).get('interaction_zone', [0.2, 0.8, 0.2, 0.8])
        self.zone_x_min, self.zone_x_max = zone[0], zone[1]
        self.zone_y_min, self.zone_y_max = zone[2], zone[3]
        
        # One Euro Filter is the gold standard for zero-lag, zero-jitter cursor tracking
        self.one_euro = OneEuroFilter2D(
            min_cutoff=1.0,
            beta=0.007,
            d_cutoff=1.0
        )
        
        self.position = (self.screen_w // 2, self.screen_h // 2)
        self._frozen = False

    def freeze(self):
        self._frozen = True
        
    def unfreeze(self):
        self._frozen = False

    def reset_all_filters(self):
        self.one_euro.reset()
        
    def _normalize(self, nx: float, ny: float) -> tuple:
        px = (nx - self.zone_x_min) / (self.zone_x_max - self.zone_x_min)
        py = (ny - self.zone_y_min) / (self.zone_y_max - self.zone_y_min)
        
        px = max(0.0, min(1.0, px))
        py = max(0.0, min(1.0, py))
        
        return px * self.screen_w, py * self.screen_h

    def update(self, raw_point: tuple, timestamp: float):
        if self._frozen:
            return

        # 1. Map to screen strictly (Absolute)
        screen_x, screen_y = self._normalize(raw_point[0], raw_point[1])
        
        # 2. OneEuroFilter (Zero lag, zero jitter)
        filtered_x, filtered_y = self.one_euro.filter(screen_x, screen_y, timestamp)
        
        # 3. Apply
        final_x = max(0, min(self.screen_w - 1, int(filtered_x)))
        final_y = max(0, min(self.screen_h - 1, int(filtered_y)))
        
        try:
            ctypes.windll.user32.SetCursorPos(final_x, final_y)
        except:
            pass
            
        self.position = (final_x, final_y)
