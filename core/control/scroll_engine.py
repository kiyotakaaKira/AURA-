import ctypes
import time

MOUSEEVENTF_WHEEL = 0x0800

class ScrollEngine:
    def __init__(self, config: dict):
        self.scroll_sensitivity = config.get('preferences', {}).get('scroll_speed', 2.0)
        self._last_y = None
        self._velocity = 0.0
        self._last_time = time.time()
        self._momentum_alpha = 0.9  # Decay factor for momentum
        self.is_scrolling = False
        
    def update(self, hand, index_tip: tuple, middle_tip: tuple):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now
        
        # In MediaPipe, y=0 is top, y=1 is bottom. Scroll up when fingers move up (smaller y).
        avg_y = (index_tip[1] + middle_tip[1]) / 2.0
        
        # Index and Middle must be extended. Ring and Pinky must be curled.
        if hand and hand.detected:
            index_ext = hand.fingers_extended[1]
            middle_ext = hand.fingers_extended[2]
            ring_ext = hand.fingers_extended[3]
            pinky_ext = hand.fingers_extended[4]
            is_scroll_gesture = index_ext and middle_ext and not ring_ext and not pinky_ext
        else:
            is_scroll_gesture = False

        if is_scroll_gesture:
            self.is_scrolling = True
            if self._last_y is not None and dt > 0:
                dy = avg_y - self._last_y
                
                scroll_amount = -dy * self.scroll_sensitivity * 10000
                self._velocity = scroll_amount
                
                if abs(scroll_amount) > 1:
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(scroll_amount), 0)
            
            self._last_y = avg_y
        else:
            self.is_scrolling = False
            self._last_y = None
            
            # Apply momentum if not scrolling anymore
            if abs(self._velocity) > 1:
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(self._velocity), 0)
                self._velocity *= self._momentum_alpha
            else:
                self._velocity = 0.0
                
    def reset(self):
        self._last_y = None
        self._velocity = 0.0
        self.is_scrolling = False
