import cv2
import numpy as np
import time
from ui.theme import *

class ClickTestMode:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.is_active = False
        self.is_finished = False
        
        self.left_clicks = 0
        self.right_clicks = 0
        self.drags = 0
        
        self.TARGET = 10
        
        self._last_action = ""
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.is_active = True
        self.is_finished = False
        self.left_clicks = 0
        self.right_clicks = 0
        self.drags = 0
        self._last_action = ""
        self.start_time = time.time()

    def stop(self):
        self.is_active = False

    def update(self, current_action: str):
        if not self.is_active or self.is_finished:
            return

        if current_action and current_action != self._last_action:
            if current_action == "LEFT CLICK" and self.left_clicks < self.TARGET:
                self.left_clicks += 1
            elif current_action == "RIGHT CLICK" and self.right_clicks < self.TARGET:
                self.right_clicks += 1
            elif current_action == "DRAGGING" and self.drags < self.TARGET:
                self.drags += 1

        self._last_action = current_action

        if self.left_clicks >= self.TARGET and self.right_clicks >= self.TARGET and self.drags >= self.TARGET:
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
            self._render_text_center(overlay, "VALIDATION COMPLETE", self.h // 2 - 60, GREEN, 2.0)
            self._render_text_center(overlay, f"Time: {duration:.1f}s", self.h // 2, WHITE, 1.0)
            self._render_text_center(overlay, "Success Rate: 100%", self.h // 2 + 50, GREEN, 1.0)
            self._render_text_center(overlay, "Press [V] to exit", self.h - 50, GRAY, 0.7)
            return cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)
            
        # Draw Progress
        self._render_text_center(overlay, "AURA VALIDATION TEST", 100, WHITE, 1.5)
        self._render_text_center(overlay, "Perform the following actions to validate Interaction Engine V2", 150, GRAY, 0.8)
        
        self._draw_progress_bar(overlay, "Left Clicks (Index Curl)", self.left_clicks, 250)
        self._draw_progress_bar(overlay, "Right Clicks (Middle Curl)", self.right_clicks, 350)
        self._draw_progress_bar(overlay, "Drags (Index Hold 300ms)", self.drags, 450)
        
        if self._last_action:
            self._render_text_center(overlay, f"LAST ACTION: {self._last_action}", self.h - 150, AMBER, 1.0)
            
        self._render_text_center(overlay, "Press [V] to cancel", self.h - 50, GRAY, 0.7)
        
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
