import cv2
import numpy as np
import time
from collections import deque
from typing import Optional
from .theme import *
from .hud_components import HUDComponents
from .gesture_visualizer import GestureVisualizer
from .animation_engine import AnimationEngine
from core.intelligence.activation_manager import ActivationState
from core.tracker.tracker_fusion import FusedState

class HUD:
    def __init__(self, config: dict):
        self.config = config
        self.window_name = "AURA"
        self.debug_mode = False
        
        self.canvas = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
        
        self.gesture_vis = GestureVisualizer(config)
        self.components = HUDComponents(config)
        self.animator = AnimationEngine()
        
        self.current_gesture_display = None
        self.gesture_display_timer = 0
        self._fps_history = deque(maxlen=30)
        self._last_frame_time = time.time()
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, WINDOW_WIDTH, WINDOW_HEIGHT)
        
    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        
    def render(self, 
               camera_frame: np.ndarray,
               fused_state: FusedState,
               activation_state: ActivationState,
               current_gesture: Optional[str],
               volume_level: float,
               is_scrolling: bool,
               click_state: str,
               recording_progress: Optional[float] = None,
               show_help: bool = False,
               state_entry_time: float = 0.0,
               first_activation_time: float = 0.0,
               has_moved: bool = False,
               has_clicked: bool = False,
               has_scrolled: bool = False,
               tutorial_state=None,
               debug_data=None,
               **kwargs):
        
        self.canvas[:] = BG_PRIMARY
        
        now = time.time()
        dt = now - self._last_frame_time
        self._last_frame_time = now
        self._fps_history.append(1.0 / max(dt, 0.001))
        fps = sum(self._fps_history) / len(self._fps_history)
        
        # Camera is now a PiP overlay, we prepare it first
        camera_with_overlays = camera_frame.copy()
        camera_with_overlays = self.gesture_vis.render(
            camera_with_overlays, fused_state, activation_state, click_state
        )
        
        # 1. Main Workspace
        # Background subtle gradient/texture
        cv2.putText(self.canvas, "AURA WORKSPACE", (DASHBOARD_X, DASHBOARD_Y - 10), FONT_FACE, FONT_SCALE_MD, TEXT_SECONDARY, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        
        # Persistent Status Panel
        cursor_enabled = (activation_state == ActivationState.ACTIVE or kwargs.get('dev_override_enabled', False)) and fused_state.hand.detected and current_gesture in ["index_point", "pinch", None]
        self.components.draw_persistent_status(
            self.canvas, fused_state, activation_state, cursor_enabled, 
            dev_mode=kwargs.get('dev_override_enabled', False)
        )
        
        # Tutorial Panel
        if tutorial_state:
            self.components.draw_tutorial_panel(self.canvas, tutorial_state)
            
        # Debug Panel
        if self.debug_mode and debug_data:
            self.components.draw_debug_panel(self.canvas, **debug_data)
        
        # 2. Place Camera PiP
        self._place_camera(camera_with_overlays, activation_state)
        
        # 3. Floating Bottom/Top Bars
        self.components.draw_status_bar(
            self.canvas, activation_state, fps, 
            fused_state.hand.confidence if fused_state.hand.detected else 0.0,
            debug_mode=self.debug_mode
        )
        
        self.components.draw_bottom_bar(
            self.canvas, current_gesture, volume_level, is_scrolling, click_state, self.animator
        )
        
        if current_gesture and current_gesture != self.current_gesture_display:
            self.current_gesture_display = current_gesture
            self.gesture_display_timer = time.time()
        
        if self.current_gesture_display:
            self.components.draw_gesture_chip(
                self.canvas, self.current_gesture_display,
                time.time() - self.gesture_display_timer,
                self.animator
            )
            
        # Help/Debug Icons
        self.components.draw_help_icon(self.canvas)
        
        if show_help:
            self.components.draw_help_card(self.canvas, activation_state=activation_state, confidence=fused_state.hand.confidence if fused_state.hand.detected else 0.0)
            
        # Center Activation Text Sequence
        if state_entry_time > 0:
            if activation_state == ActivationState.ACTIVATING:
                elapsed = now - state_entry_time
                if elapsed < 0.5:
                    text_size = cv2.getTextSize("TRACKING LOCKED", FONT_FACE, FONT_SCALE_MD, FONT_WEIGHT_BOLD)[0]
                    tx = WINDOW_WIDTH // 2 - text_size[0] // 2
                    ty = WINDOW_HEIGHT // 2
                    cv2.putText(self.canvas, "TRACKING LOCKED", (tx, ty), FONT_FACE, FONT_SCALE_MD, ACCENT_GREEN, FONT_WEIGHT_BOLD, cv2.LINE_AA)
            elif activation_state == ActivationState.ACTIVE:
                elapsed = now - state_entry_time
                if elapsed < 1.0:
                    alpha = max(0.0, 1.0 - (elapsed / 1.0))
                    if alpha > 0.01:
                        overlay = self.canvas.copy()
                        text_size = cv2.getTextSize("AURA ACTIVE", FONT_FACE, 1.5, FONT_WEIGHT_BOLD)[0]
                        tx = WINDOW_WIDTH // 2 - text_size[0] // 2
                        ty = WINDOW_HEIGHT // 2
                        cv2.putText(overlay, "AURA ACTIVE", (tx, ty), FONT_FACE, 1.5, ACCENT_BLUE, FONT_WEIGHT_BOLD, cv2.LINE_AA)
                        cv2.addWeighted(overlay, alpha, self.canvas, 1.0 - alpha, 0, self.canvas)
                    
                    
        # Recording Overlay
        if recording_progress is not None:
            self.components.draw_recording_overlay(self.canvas, recording_progress)
            
    def render_dismiss(self, dismiss_state: str, shutdown_alpha=0.0):
        if dismiss_state in ["DISMISS_STARTED", "DISMISS_CANCELLED"]:
            self.components.draw_dismiss_chip(self.canvas, dismiss_state)
            
        if shutdown_alpha > 0.0:
            self.components.draw_shutdown_overlay(self.canvas, alpha_fade=shutdown_alpha)
            
    def display(self):
        cv2.imshow(self.window_name, self.canvas)
        
    def _get_rounded_rect_mask(self, w, h, radius):
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.rectangle(mask, (radius, 0), (w - radius, h), 255, -1)
        cv2.rectangle(mask, (0, radius), (w, h - radius), 255, -1)
        cv2.circle(mask, (radius, radius), radius, 255, -1)
        cv2.circle(mask, (w - radius, radius), radius, 255, -1)
        cv2.circle(mask, (radius, h - radius), radius, 255, -1)
        cv2.circle(mask, (w - radius, h - radius), radius, 255, -1)
        return mask
        
    def _place_camera(self, camera_frame: np.ndarray, activation_state: ActivationState):
        resized = cv2.resize(camera_frame, (CAMERA_W, CAMERA_H))
        
        mask = self._get_rounded_rect_mask(CAMERA_W, CAMERA_H, CORNER_RADIUS)
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Draw fake drop shadow (depth)
        shadow_offset = 15
        shadow_rect = np.zeros_like(self.canvas)
        cv2.rectangle(shadow_rect, 
                      (CAMERA_X + shadow_offset, CAMERA_Y + shadow_offset), 
                      (CAMERA_X+CAMERA_W + shadow_offset, CAMERA_Y+CAMERA_H + shadow_offset),
                      (0,0,0), -1)
        shadow_rect = cv2.blur(shadow_rect, (25, 25))
        cv2.addWeighted(shadow_rect, 0.6, self.canvas, 1.0, 0, self.canvas)
        
        roi = self.canvas[CAMERA_Y:CAMERA_Y+CAMERA_H, CAMERA_X:CAMERA_X+CAMERA_W]
        np.copyto(roi, resized, where=mask_3ch==255)
        
        is_active = activation_state == ActivationState.ACTIVE
        
        if is_active:
            # Soft glow
            cv2.rectangle(self.canvas, 
                          (CAMERA_X-2, CAMERA_Y-2), 
                          (CAMERA_X+CAMERA_W+2, CAMERA_Y+CAMERA_H+2),
                          ACCENT_BLUE, 2)
            cv2.rectangle(self.canvas, 
                          (CAMERA_X, CAMERA_Y), 
                          (CAMERA_X+CAMERA_W, CAMERA_Y+CAMERA_H),
                          (255, 255, 255), 1)
        else:
            cv2.rectangle(self.canvas, 
                          (CAMERA_X, CAMERA_Y), 
                          (CAMERA_X+CAMERA_W, CAMERA_Y+CAMERA_H),
                          (40, 40, 40), 1)
