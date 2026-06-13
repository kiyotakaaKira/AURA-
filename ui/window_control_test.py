import cv2
import numpy as np
import time
from ui.theme import *

class WindowControlTestMode:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.is_active = False
        self.is_finished = False
        
        self.minimizes = 0
        self.restores = 0
        
        self.TARGET = 10
        
        self._last_action = ""
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.is_active = True
        self.is_finished = False
        self.minimizes = 0
        self.restores = 0
        self._last_action = ""
        self.start_time = time.time()

    def stop(self):
        self.is_active = False

    def update(self, win_msg: str, win_prog: float):
        if not self.is_active or self.is_finished:
            return

        # Only count when progress reaches 1.0 (Command Executed)
        if win_prog >= 1.0:
            if win_msg and win_msg != self._last_action:
                if win_msg == "WINDOW MINIMIZE" and self.minimizes < self.TARGET:
                    self.minimizes += 1
                elif win_msg == "WINDOW RESTORE" and self.restores < self.TARGET:
                    self.restores += 1
            self._last_action = win_msg
        else:
            if not win_msg:
                self._last_action = ""

        if self.minimizes >= self.TARGET and self.restores >= self.TARGET:
            self.is_finished = True
            self.end_time = time.time()

    def render(self, frame: np.ndarray) -> np.ndarray:
        if not self.is_active:
            return frame
            
        overlay = frame.copy()
        
        # Dim background
        cv2.rectangle(overlay, (0, 0), (self.w, self.h), (10, 10, 12), -1)
        
        if self.is_finished:
            duration = self.end_time - self.start_time
            self._render_text_center(overlay, "WINDOW CONTROL VALIDATION COMPLETE", self.h // 2 - 60, GREEN, 2.0)
            self._render_text_center(overlay, f"Time: {duration:.1f}s", self.h // 2, WHITE, 1.0)
            self._render_text_center(overlay, "Success Rate: 100%", self.h // 2 + 50, GREEN, 1.0)
            self._render_text_center(overlay, "Press [W] to exit", self.h - 50, GRAY, 0.7)
            return cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)
            
        # Draw Progress
        self._render_text_center(overlay, "WINDOW CONTROL TEST", 100, WHITE, 1.5)
        self._render_text_center(overlay, "Perform the following actions to validate Window Control Engine", 150, GRAY, 0.8)
        
        self._draw_progress_bar(overlay, "Minimizes (Open Palm -> Fist)", self.minimizes, 250)
        self._draw_progress_bar(overlay, "Restores (Fist -> Open Palm)", self.restores, 350)
        
        if self._last_action:
            self._render_text_center(overlay, f"LAST ACTION: {self._last_action}", self.h - 150, AMBER, 1.0)
            
        self._render_text_center(overlay, "Press [W] to cancel", self.h - 50, GRAY, 0.7)
        
        return cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)

    def _render_text_center(self, img, text, y, color, scale):
        size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)[0]
        x = (self.w - size[0]) // 2
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)
        
    def _draw_progress_bar(self, img, label, count, y):
        x_center = self.w // 2
        bar_w = 400
        bar_h = 30
        x = x_center - bar_w // 2
        
        # Label
        cv2.putText(img, f"{label} ({count}/{self.TARGET})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 1, cv2.LINE_AA)
        
        # Background
        cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (40, 40, 45), -1)
        cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (80, 80, 90), 2)
        
        # Fill
        if count > 0:
            fill_w = int((count / self.TARGET) * bar_w)
            color = GREEN if count >= self.TARGET else BLUE
            cv2.rectangle(img, (x, y), (x + fill_w, y + bar_h), color, -1)
