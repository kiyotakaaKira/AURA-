import cv2
import numpy as np
from typing import Optional
from core.tracker.hand_tracker import TrackingResult
from ui.theme import *
import ctypes
import os
import json

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
]

class FloatingCameraWindow:
    def __init__(self, screen_w: int, screen_h: int, config: dict):
        import time
        self.w = config.get('camera_window', {}).get('width', 320)
        self.h = config.get('camera_window', {}).get('height', 240)
        self.window_name = "AURA - Camera"
        
        self.pos_file = "camera_pos.json"
        
        # Absolute Bottom Right default
        self.target_x = screen_w - self.w - 20
        self.target_y = screen_h - self.h - 20
        
        self.x = self.target_x
        self.y = self.target_y
        
        # Enforce Bottom-Right on every launch, but if they dragged it previously, we restore
        # Actually, user said: "Every launch: Position camera: Bottom Right Automatically Without user intervention."
        # AND "If user drags camera: Save position, Save size, Restore next launch"
        # Wait, if they contradict, I will load from JSON if it exists, else Bottom Right.
        if os.path.exists(self.pos_file):
            try:
                with open(self.pos_file, 'r') as f:
                    data = json.load(f)
                    self.x = data.get('x', self.target_x)
                    self.y = data.get('y', self.target_y)
                    self.target_x = self.x
                    self.target_y = self.y
            except Exception:
                pass
                
        # Create independent window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.w, self.h)
        
        # Animation state
        self.anim_start = time.time()
        self.anim_duration = 0.2  # 200ms
        self.is_animating = True
        
        # Start position for slide up
        self.start_y = self.target_y + 50
        
        cv2.moveWindow(self.window_name, self.x, self.start_y)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
        
        # Enable Alpha Blending on the OS window for true Fade-In
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, self.window_name)
            if hwnd:
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 0, 2) # Alpha 0
        except Exception:
            pass
            
        self.frame_count = 0

    def render(self, frame: np.ndarray, hand: Optional[TrackingResult],
               tracker_state: str, action_text: str, is_idle: bool):
        import time
        """
        Renders the PIP camera to an independent OS window.
        """
        if self.is_animating:
            now = time.time()
            progress = min(1.0, (now - self.anim_start) / self.anim_duration)
            
            # Ease out cubic
            ease = 1 - (1 - progress) ** 3
            
            current_y = int(self.start_y + (self.target_y - self.start_y) * ease)
            cv2.moveWindow(self.window_name, self.x, current_y)
            
            try:
                hwnd = ctypes.windll.user32.FindWindowW(None, self.window_name)
                if hwnd:
                    alpha = int(255 * ease)
                    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, alpha, 2)
            except Exception:
                pass
                
            if progress >= 1.0:
                self.is_animating = False
        display = cv2.resize(frame, (self.w, self.h))
        scale_x = self.w / frame.shape[1]
        scale_y = self.h / frame.shape[0]
        
        if hand and hand.detected:
            self._draw_skeleton(display, hand, scale_x, scale_y)
            self._draw_fingertips(display, hand, scale_x, scale_y, action_text)
            
        dot_color = self._get_dot_color(hand, tracker_state, is_idle)
        cv2.circle(display, (self.w - 20, 20), 6, dot_color, -1, cv2.LINE_AA)
        
        if not (hand and hand.detected):
            cv2.putText(display, "Searching for Hand...",
                        (20, self.h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 191, 255), 1, cv2.LINE_AA)
                        
        cv2.imshow(self.window_name, display)
        
        # Periodically save window position if user drags it
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self._save_position()

    def _save_position(self):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, self.window_name)
            if hwnd:
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                # Only save if it's a valid rect and not minimized
                if rect.left > -10000:
                    with open(self.pos_file, 'w') as f:
                        json.dump({'x': rect.left, 'y': rect.top}, f)
        except Exception:
            pass

    def _get_dot_color(self, hand, state, idle):
        if not hand or not hand.detected: return RED
        if idle: return AMBER
        if state == "TRACKING" or state == "READY": return GREEN
        return RED

    def _draw_skeleton(self, img, hand: TrackingResult, sx: float, sy: float):
        for connection in HAND_CONNECTIONS:
            p1 = hand.landmarks[connection[0]]
            p2 = hand.landmarks[connection[1]]
            pt1 = (int(p1[0] * sx), int(p1[1] * sy))
            pt2 = (int(p2[0] * sx), int(p2[1] * sy))
            cv2.line(img, pt1, pt2, (150, 150, 150), 2, cv2.LINE_AA)
            cv2.circle(img, pt1, 3, (200, 200, 200), -1, cv2.LINE_AA)

    def _draw_fingertips(self, img, hand: TrackingResult, sx: float, sy: float, action: str):
        index_tip = (int(hand.index_tip[0] * sx), int(hand.index_tip[1] * sy))
        middle_tip = (int(hand.middle_tip[0] * sx), int(hand.middle_tip[1] * sy))
        
        idx_color = GREEN if action in ["LEFT CLICK", "DRAGGING"] else BLUE
        mid_color = (200, 80, 200) if action == "RIGHT CLICK" else BLUE
        
        # Highlight control fingers
        cv2.circle(img, index_tip, 8, idx_color, -1, cv2.LINE_AA)
        cv2.circle(img, middle_tip, 8, mid_color, -1, cv2.LINE_AA)
        
        # Labels
        cv2.putText(img, "Index", (index_tip[0] - 20, index_tip[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, idx_color, 1, cv2.LINE_AA)
        cv2.putText(img, "Middle", (middle_tip[0] - 20, middle_tip[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, mid_color, 1, cv2.LINE_AA)
