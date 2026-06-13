import cv2
import numpy as np
import time
from .theme import *
from core.intelligence.activation_manager import ActivationState

class TutorialState:
    WELCOME = 0
    STEP1 = 1
    STEP1_SUCCESS = 2
    STEP2 = 3
    STEP2_SUCCESS = 4
    STEP3 = 5
    STEP3_SUCCESS = 6
    STEP4 = 7
    STEP4_SUCCESS = 8
    STEP5 = 9
    STEP5_SUCCESS = 10
    STEP6 = 11
    STEP6_SUCCESS = 12
    COMPLETE = 13
    DONE = 14

class TutorialEngine:
    def __init__(self, window_width, window_height):
        self.w = window_width
        self.h = window_height
        self.state = TutorialState.WELCOME
        self.state_start_time = time.time()
        self.is_active = True
        
        # Bounding boxes for physical mouse clicks
        self.btn_start_rect = None
        self.btn_skip_rect = None
        self.btn_launch_rect = None
        
        self.fade_out_start = 0.0

    def handle_mouse_click(self, x, y):
        if not self.is_active:
            return False
            
        def in_rect(rx, ry, rw, rh):
            return rx <= x <= rx + rw and ry <= y <= ry + rh
            
        if self.state == TutorialState.WELCOME:
            if self.btn_start_rect and in_rect(*self.btn_start_rect):
                self._transition(TutorialState.STEP1)
                return True
            if self.btn_skip_rect and in_rect(*self.btn_skip_rect):
                self.is_active = False
                self.state = TutorialState.DONE
                return True
                
        elif self.state == TutorialState.COMPLETE:
            if self.btn_launch_rect and in_rect(*self.btn_launch_rect):
                self.fade_out_start = time.time()
                return True
                
        return False

    def _transition(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()

    def update(self, fused_state, activation_state, current_gesture, click_state, is_scrolling, dismiss_state):
        if not self.is_active:
            return

        now = time.time()
        elapsed = now - self.state_start_time
        
        if self.state in [TutorialState.STEP1, TutorialState.STEP2, TutorialState.STEP3, TutorialState.STEP4, TutorialState.STEP5, TutorialState.STEP6]:
            if elapsed < 1.0: return
            
        if self.state == TutorialState.STEP1:
            if fused_state.hand.detected:
                self._transition(TutorialState.STEP1_SUCCESS)
        elif self.state == TutorialState.STEP1_SUCCESS:
            if elapsed > 1.5: self._transition(TutorialState.STEP2)
            
        elif self.state == TutorialState.STEP2:
            if activation_state == ActivationState.ACTIVE:
                self._transition(TutorialState.STEP2_SUCCESS)
        elif self.state == TutorialState.STEP2_SUCCESS:
            if elapsed > 3.0: self._transition(TutorialState.STEP3)
            
        elif self.state == TutorialState.STEP3:
            if current_gesture == "index_point" and fused_state.motion.speed > 0.1:
                self._transition(TutorialState.STEP3_SUCCESS)
        elif self.state == TutorialState.STEP3_SUCCESS:
            if elapsed > 3.0: self._transition(TutorialState.STEP4)
            
        elif self.state == TutorialState.STEP4:
            if click_state in ["CLICK", "CLICK_PENDING"]:
                self._transition(TutorialState.STEP4_SUCCESS)
        elif self.state == TutorialState.STEP4_SUCCESS:
            if elapsed > 2.0: self._transition(TutorialState.STEP5)
            
        elif self.state == TutorialState.STEP5:
            if is_scrolling or current_gesture == "two_fingers":
                self._transition(TutorialState.STEP5_SUCCESS)
        elif self.state == TutorialState.STEP5_SUCCESS:
            if elapsed > 2.0: self._transition(TutorialState.STEP6)
            
        elif self.state == TutorialState.STEP6:
            if dismiss_state in ["DISMISS_STARTED", "DISMISS_CONFIRMATION"]:
                self._transition(TutorialState.STEP6_SUCCESS)
        elif self.state == TutorialState.STEP6_SUCCESS:
            if elapsed > 2.0: self._transition(TutorialState.COMPLETE)
            
        elif self.state == TutorialState.COMPLETE:
            if self.fade_out_start > 0 and now - self.fade_out_start > 1.0:
                self.is_active = False
                self.state = TutorialState.DONE

    def render(self, canvas: np.ndarray, confidence: float):
        if not self.is_active:
            return

        now = time.time()
        elapsed = now - self.state_start_time

        global_alpha = 1.0
        if self.fade_out_start > 0:
            global_alpha = max(0.0, 1.0 - (now - self.fade_out_start))

        # Dim background
        dim = np.zeros_like(canvas)
        dim_amount = 0.8 if self.state in [TutorialState.WELCOME, TutorialState.COMPLETE] else 0.5
        cv2.addWeighted(dim, dim_amount * global_alpha, canvas, 1.0 - (dim_amount * global_alpha), 0, canvas)

        if self.state == TutorialState.WELCOME:
            self._render_welcome(canvas, global_alpha)
        elif self.state == TutorialState.COMPLETE:
            self._render_complete(canvas, global_alpha)
        else:
            self._render_step(canvas, global_alpha, confidence)

    def _render_welcome(self, canvas, alpha):
        cv2.putText(canvas, "Welcome to AURA", (self.w//2 - 250, self.h//2 - 80), FONT_FACE, 1.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, "Adaptive User Reality Assistant", (self.w//2 - 200, self.h//2 - 20), FONT_FACE, FONT_SCALE_MD, TEXT_SECONDARY, 1, cv2.LINE_AA)
        cv2.putText(canvas, "The Future of Human Interaction", (self.w//2 - 180, self.h//2 + 15), FONT_FACE, FONT_SCALE_SM, ACCENT_BLUE, 1, cv2.LINE_AA)
        
        btn_w, btn_h = 200, 50
        
        # Start button
        start_x = self.w//2 - btn_w - 20
        start_y = self.h//2 + 100
        self.btn_start_rect = (start_x, start_y, btn_w, btn_h)
        cv2.rectangle(canvas, (start_x, start_y), (start_x+btn_w, start_y+btn_h), ACCENT_BLUE, -1)
        cv2.putText(canvas, "Start Tutorial", (start_x + 35, start_y + 32), FONT_FACE, FONT_SCALE_SM, (255,255,255), FONT_WEIGHT_BOLD, cv2.LINE_AA)
        
        # Skip button
        skip_x = self.w//2 + 20
        skip_y = self.h//2 + 100
        self.btn_skip_rect = (skip_x, skip_y, btn_w, btn_h)
        cv2.rectangle(canvas, (skip_x, skip_y), (skip_x+btn_w, skip_y+btn_h), BG_ELEVATED, -1)
        cv2.rectangle(canvas, (skip_x, skip_y), (skip_x+btn_w, skip_y+btn_h), TEXT_SECONDARY, 1)
        cv2.putText(canvas, "Skip Tutorial", (skip_x + 35, skip_y + 32), FONT_FACE, FONT_SCALE_SM, TEXT_PRIMARY, FONT_WEIGHT_NORMAL, cv2.LINE_AA)

    def _render_complete(self, canvas, alpha):
        t_alpha = tuple(int(c * alpha) for c in (255, 255, 255))
        s_alpha = tuple(int(c * alpha) for c in ACCENT_GREEN)
        
        cv2.putText(canvas, "Congratulations", (self.w//2 - 150, self.h//2 - 60), FONT_FACE, 1.3, t_alpha, 2, cv2.LINE_AA)
        cv2.putText(canvas, "You are ready to use AURA.", (self.w//2 - 160, self.h//2 - 10), FONT_FACE, FONT_SCALE_MD, TEXT_SECONDARY, 1, cv2.LINE_AA)
        cv2.putText(canvas, "AURA READY", (self.w//2 - 80, self.h//2 + 40), FONT_FACE, FONT_SCALE_MD, s_alpha, 2, cv2.LINE_AA)
        
        btn_w, btn_h = 240, 50
        launch_x = self.w//2 - btn_w//2
        launch_y = self.h//2 + 100
        self.btn_launch_rect = (launch_x, launch_y, btn_w, btn_h)
        
        overlay = canvas.copy()
        cv2.rectangle(overlay, (launch_x, launch_y), (launch_x+btn_w, launch_y+btn_h), ACCENT_BLUE, -1)
        cv2.addWeighted(overlay, alpha, canvas, 1.0 - alpha, 0, canvas)
        cv2.putText(canvas, "Launch Workspace", (launch_x + 40, launch_y + 32), FONT_FACE, FONT_SCALE_SM, t_alpha, FONT_WEIGHT_BOLD, cv2.LINE_AA)

    def _render_step(self, canvas, alpha, confidence):
        card_w, card_h = 600, 240
        card_x = self.w // 2 - card_w // 2
        card_y = self.h - card_h - 40

        overlay = canvas.copy()
        cv2.rectangle(overlay, (card_x, card_y), (card_x + card_w, card_y + card_h), BG_SURFACE, -1)
        cv2.rectangle(overlay, (card_x, card_y), (card_x + card_w, card_y + card_h), BORDER_DEFAULT, 1)
        cv2.addWeighted(overlay, 0.95 * alpha, canvas, 1.0 - (0.95 * alpha), 0, canvas)

        step_num = ""
        instruction = ""
        status = ""
        explanation = ""
        icon_color = ACCENT_BLUE
        
        is_success = "SUCCESS" in [k for k, v in TutorialState.__dict__.items() if v == self.state][0]

        if self.state in [TutorialState.STEP1, TutorialState.STEP1_SUCCESS]:
            step_num = "Step 1 of 6"
            instruction = "Raise your hand in front of the camera."
            status = "Waiting for hand..." if not is_success else "✓ Hand Detected"
            
        elif self.state in [TutorialState.STEP2, TutorialState.STEP2_SUCCESS]:
            step_num = "Step 2 of 6"
            instruction = "AURA activates when tracking > 80%."
            status = f"Confidence: {int(confidence*100)}%" if not is_success else "✓ AURA ACTIVE"
            explanation = "When AURA is active, your gestures control the system." if is_success else ""
            
        elif self.state in [TutorialState.STEP3, TutorialState.STEP3_SUCCESS]:
            step_num = "Step 3 of 6"
            instruction = "Point with your index finger. Move gently."
            status = "Waiting for pointer gesture..." if not is_success else "✓ Cursor Control Detected"
            explanation = "Small movements provide precision. Large movements move faster." if is_success else ""
            
        elif self.state in [TutorialState.STEP4, TutorialState.STEP4_SUCCESS]:
            step_num = "Step 4 of 6"
            instruction = "Pinch your thumb and index finger together."
            status = "Try clicking now." if not is_success else "✓ Click Detected"
            explanation = "Pinch = Left Click" if is_success else ""
            
        elif self.state in [TutorialState.STEP5, TutorialState.STEP5_SUCCESS]:
            step_num = "Step 5 of 6"
            instruction = "Raise two fingers. Move hand up and down."
            status = "Waiting for scroll..." if not is_success else "✓ Scroll Detected"
            explanation = "Two Fingers + Movement = Scroll" if is_success else ""
            
        elif self.state in [TutorialState.STEP6, TutorialState.STEP6_SUCCESS]:
            step_num = "Step 6 of 6"
            instruction = "To exit: Point toward camera, Open Palm -> Fist -> Open Palm -> Fist"
            status = "Waiting for dismiss sequence..." if not is_success else "✓ Dismiss Gesture Learned"
            explanation = "This safely closes AURA." if is_success else ""

        if is_success:
            icon_color = ACCENT_GREEN

        pulse = (np.sin(time.time() * 4) + 1) / 2
        icon_r = int(12 + 4 * pulse)
        icon_center = (card_x + 60, card_y + 80)
        
        cv2.circle(canvas, icon_center, icon_r, icon_color, -1)
        cv2.circle(canvas, icon_center, icon_r + 8, tuple(int(c * 0.3) for c in icon_color), 1)

        t_color = TEXT_PRIMARY
        s_color = TEXT_SECONDARY
        status_color = ACCENT_GREEN if is_success else s_color

        cv2.putText(canvas, step_num, (card_x + 120, card_y + 50), FONT_FACE, FONT_SCALE_SM, s_color, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        cv2.putText(canvas, instruction, (card_x + 120, card_y + 90), FONT_FACE, FONT_SCALE_MD, t_color, FONT_WEIGHT_NORMAL, cv2.LINE_AA)
        cv2.putText(canvas, status, (card_x + 120, card_y + 130), FONT_FACE, FONT_SCALE_SM, status_color, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        
        if explanation:
            cv2.putText(canvas, explanation, (card_x + 120, card_y + 170), FONT_FACE, FONT_SCALE_SM, ACCENT_BLUE, FONT_WEIGHT_NORMAL, cv2.LINE_AA)
