import cv2
import numpy as np
import time
from .theme import *
from core.intelligence.activation_manager import ActivationState

class OnboardingState:
    DETECT = 0
    DETECT_SUCCESS = 1
    ACTIVATE = 2
    ACTIVATE_SUCCESS = 3
    POINT = 4
    POINT_SUCCESS = 5
    CLICK = 6
    CLICK_SUCCESS = 7
    READY = 8
    DONE = 9

def ease_in_out_sine(x):
    return -(np.cos(np.pi * x) - 1) / 2

class OnboardingEngine:
    def __init__(self, window_width, window_height):
        self.w = window_width
        self.h = window_height
        self.state = OnboardingState.DETECT
        self.state_start_time = time.time()
        self.is_active = True
        self.fade_out_start = 0.0

    def _transition(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()
            if new_state == OnboardingState.READY:
                self.fade_out_start = time.time()

    def update(self, fused_state, activation_state, current_gesture, click_state):
        if not self.is_active:
            return

        now = time.time()
        elapsed = now - self.state_start_time
        
        # Debounce standard states to ensure readability
        if self.state in [OnboardingState.DETECT, OnboardingState.ACTIVATE, OnboardingState.POINT, OnboardingState.CLICK]:
            if elapsed < 1.0:
                return

        if self.state == OnboardingState.DETECT:
            if fused_state.hand.detected:
                self._transition(OnboardingState.DETECT_SUCCESS)
        elif self.state == OnboardingState.DETECT_SUCCESS:
            if elapsed > 1.5:
                self._transition(OnboardingState.ACTIVATE)
                
        elif self.state == OnboardingState.ACTIVATE:
            if activation_state == ActivationState.ACTIVE:
                self._transition(OnboardingState.ACTIVATE_SUCCESS)
        elif self.state == OnboardingState.ACTIVATE_SUCCESS:
            if elapsed > 1.5:
                self._transition(OnboardingState.POINT)
                
        elif self.state == OnboardingState.POINT:
            if current_gesture == "index_point":
                self._transition(OnboardingState.POINT_SUCCESS)
        elif self.state == OnboardingState.POINT_SUCCESS:
            if elapsed > 1.5:
                self._transition(OnboardingState.CLICK)
                
        elif self.state == OnboardingState.CLICK:
            if click_state in ["CLICK", "CLICK_PENDING"]:
                self._transition(OnboardingState.CLICK_SUCCESS)
        elif self.state == OnboardingState.CLICK_SUCCESS:
            if elapsed > 1.5:
                self._transition(OnboardingState.READY)
                
        elif self.state == OnboardingState.READY:
            if now - self.fade_out_start > 2.0:
                self.is_active = False
                self.state = OnboardingState.DONE

    def render(self, canvas: np.ndarray):
        if not self.is_active:
            return

        now = time.time()
        elapsed = now - self.state_start_time

        global_alpha = 1.0
        if self.state == OnboardingState.READY:
            global_alpha = max(0.0, 1.0 - ((now - self.fade_out_start) / 1.5))

        dim = np.zeros_like(canvas)
        cv2.addWeighted(dim, 0.5 * global_alpha, canvas, 1.0 - (0.5 * global_alpha), 0, canvas)

        card_w, card_h = 500, 200
        card_x = self.w // 2 - card_w // 2
        card_y = self.h - card_h - 40

        overlay = canvas.copy()
        cv2.rectangle(overlay, (card_x, card_y), (card_x + card_w, card_y + card_h), BG_SURFACE, -1)
        cv2.rectangle(overlay, (card_x, card_y), (card_x + card_w, card_y + card_h), BORDER_DEFAULT, 1)
        cv2.addWeighted(overlay, 0.95 * global_alpha, canvas, 1.0 - (0.95 * global_alpha), 0, canvas)

        title = ""
        instruction = ""
        status_text = ""
        icon_color = ACCENT_BLUE

        if self.state == OnboardingState.DETECT:
            title = "STEP 1"
            instruction = "Raise your hand in front of the camera."
            status_text = "Waiting for hand..."
        elif self.state == OnboardingState.DETECT_SUCCESS:
            title = "STEP 1"
            instruction = "Raise your hand in front of the camera."
            status_text = "✓ Hand Detected"
            icon_color = ACCENT_GREEN
        elif self.state == OnboardingState.ACTIVATE:
            title = "STEP 2"
            instruction = "Open your palm to activate AURA."
            status_text = "Waiting for activation gesture..."
        elif self.state == OnboardingState.ACTIVATE_SUCCESS:
            title = "STEP 2"
            instruction = "Open your palm to activate AURA."
            status_text = "✓ Activation Gesture Detected"
            icon_color = ACCENT_GREEN
        elif self.state == OnboardingState.POINT:
            title = "STEP 3"
            instruction = "Point with your index finger."
            status_text = "Waiting for pointer gesture..."
        elif self.state == OnboardingState.POINT_SUCCESS:
            title = "STEP 3"
            instruction = "Point with your index finger."
            status_text = "✓ Pointer Active"
            icon_color = ACCENT_GREEN
        elif self.state == OnboardingState.CLICK:
            title = "STEP 4"
            instruction = "Pinch thumb and index finger."
            status_text = "Try clicking now."
        elif self.state == OnboardingState.CLICK_SUCCESS:
            title = "STEP 4"
            instruction = "Pinch thumb and index finger."
            status_text = "✓ Click Recognized"
            icon_color = ACCENT_GREEN
        elif self.state == OnboardingState.READY:
            title = ""
            instruction = "AURA READY"
            status_text = ""
            icon_color = ACCENT_GREEN

        # Pulse animation for the icon
        pulse = (np.sin(now * 4) + 1) / 2 # 0 to 1
        icon_r = int(12 + 4 * pulse)

        icon_center = (card_x + 60, card_y + card_h // 2 - 10)
        cv2.circle(canvas, icon_center, icon_r, icon_color, -1)
        cv2.circle(canvas, icon_center, icon_r + 8, tuple(int(c * 0.3) for c in icon_color), 1)

        t_color = tuple(int(c * global_alpha) for c in TEXT_PRIMARY)
        s_color = tuple(int(c * global_alpha) for c in TEXT_SECONDARY)
        status_color = ACCENT_GREEN if "✓" in status_text else s_color

        if self.state == OnboardingState.READY:
            cv2.putText(canvas, instruction, (card_x + 120, card_y + 110), FONT_FACE, 1.2, t_color, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        else:
            cv2.putText(canvas, title, (card_x + 120, card_y + 60), FONT_FACE, FONT_SCALE_SM, s_color, FONT_WEIGHT_BOLD, cv2.LINE_AA)
            cv2.putText(canvas, instruction, (card_x + 120, card_y + 100), FONT_FACE, FONT_SCALE_MD, t_color, FONT_WEIGHT_NORMAL, cv2.LINE_AA)
            cv2.putText(canvas, status_text, (card_x + 120, card_y + 140), FONT_FACE, FONT_SCALE_SM, status_color, FONT_WEIGHT_NORMAL, cv2.LINE_AA)

        # Draw progress dots at the bottom
        dot_y = card_y + card_h - 25
        dot_spacing = 25
        total_dots = 4
        start_x = self.w // 2 - ((total_dots - 1) * dot_spacing) // 2
        
        # Map sub-states to the 4 main dots
        logical_step = self.state // 2
        if logical_step > 3: logical_step = 3
        
        for i in range(total_dots):
            dx = start_x + (i * dot_spacing)
            if i < logical_step:
                color = ACCENT_GREEN
            elif i == logical_step:
                color = ACCENT_BLUE if self.state % 2 == 0 else ACCENT_GREEN
            else:
                color = (60, 60, 60)
                
            if self.state == OnboardingState.READY:
                color = ACCENT_GREEN
            
            r = 5 if i == logical_step else 3
            cv2.circle(canvas, (dx, dot_y), r, tuple(int(c * global_alpha) for c in color), -1)
