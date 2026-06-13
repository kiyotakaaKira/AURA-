import ctypes
import time

# Virtual Key Codes
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_TAB = 0x09
VK_LWIN = 0x5B
VK_DOWN = 0x28
VK_UP = 0x26

KEYEVENTF_KEYUP = 0x0002

class KeyboardEngine:
    def __init__(self):
        self._last_action_time = 0
        self.debounce_ms = 800  # Prevent rapid-fire double triggers

    def _press(self, keycode):
        ctypes.windll.user32.keybd_event(keycode, 0, 0, 0)

    def _release(self, keycode):
        ctypes.windll.user32.keybd_event(keycode, 0, KEYEVENTF_KEYUP, 0)

    def next_tab(self):
        now = time.time() * 1000
        if now - self._last_action_time < self.debounce_ms: return
        self._last_action_time = now
        
        # CTRL + TAB
        self._press(VK_CONTROL)
        self._press(VK_TAB)
        self._release(VK_TAB)
        self._release(VK_CONTROL)

    def prev_tab(self):
        now = time.time() * 1000
        if now - self._last_action_time < self.debounce_ms: return
        self._last_action_time = now
        
        # CTRL + SHIFT + TAB
        self._press(VK_CONTROL)
        self._press(VK_SHIFT)
        self._press(VK_TAB)
        self._release(VK_TAB)
        self._release(VK_SHIFT)
        self._release(VK_CONTROL)

    def minimize_window(self):
        now = time.time() * 1000
        if now - self._last_action_time < self.debounce_ms: return
        self._last_action_time = now
        
        # Win + Down x2 (first restores down, second minimizes)
        self._press(VK_LWIN)
        self._press(VK_DOWN)
        self._release(VK_DOWN)
        self._press(VK_DOWN)
        self._release(VK_DOWN)
        self._release(VK_LWIN)

    def restore_window(self):
        now = time.time() * 1000
        if now - self._last_action_time < self.debounce_ms: return
        self._last_action_time = now
        
        # Win + Up x2 (first restores up, second maximizes)
        self._press(VK_LWIN)
        self._press(VK_UP)
        self._release(VK_UP)
        self._press(VK_UP)
        self._release(VK_UP)
        self._release(VK_LWIN)
