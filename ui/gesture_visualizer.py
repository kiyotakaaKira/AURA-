import cv2
import time
import math
from .theme import *
from core.intelligence.activation_manager import ActivationState

# MediaPipe hand connection pairs (landmark indices)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # Index
    (0, 9), (9, 10), (10, 11), (11, 12),      # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),    # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),    # Pinky
    (5, 9), (9, 13), (13, 17),                # Palm connections
]

FINGERTIP_INDICES = [4, 8, 12, 16, 20]

class GestureVisualizer:
    def __init__(self, config):
        self.config = config
        self._click_flash_timer = 0
        self._last_click_state = "IDLE"
        
    def render(self, frame, fused_state, activation_state, click_state):
        if not fused_state.hand.detected:
            return frame
            
        if click_state in ("CLICK_PENDING", "DRAG_MODE", "CLICK") and self._last_click_state not in ("CLICK_PENDING", "DRAG_MODE", "CLICK"):
            self._click_flash_timer = time.time()
        self._last_click_state = click_state
        
        landmarks = fused_state.hand.landmarks
        h, w = frame.shape[:2]
        
        # Convert normalized landmarks to pixel coords
        pixel_landmarks = [(int(lm[0] * w), int(lm[1] * h)) 
                           for lm in landmarks]
        
        # Draw skeleton lines
        self._draw_skeleton(frame, pixel_landmarks, activation_state)
        
        # Draw fingertip dots
        self._draw_fingertips(frame, pixel_landmarks, fused_state.hand, click_state)
        
        # Draw wrist ring
        self._draw_wrist_ring(frame, pixel_landmarks[0], activation_state)
        
        # Draw pinch indicator
        self._draw_pinch_indicator(frame, pixel_landmarks[4], pixel_landmarks[8],
                                   fused_state.hand.pinch_distance)
                                   
        return frame
    
    def _draw_skeleton(self, frame, pixel_landmarks, activation_state):
        is_active = activation_state == ActivationState.ACTIVE
        line_color = SKELETON_LINE if is_active else tuple(c // 2 for c in SKELETON_LINE)
        
        for start_idx, end_idx in HAND_CONNECTIONS:
            if start_idx < len(pixel_landmarks) and end_idx < len(pixel_landmarks):
                cv2.line(frame, pixel_landmarks[start_idx], pixel_landmarks[end_idx],
                         line_color, 1, cv2.LINE_AA)
    
    def _draw_fingertips(self, frame, pixel_landmarks, hand, click_state):
        for i, tip_idx in enumerate(FINGERTIP_INDICES):
            pos = pixel_landmarks[tip_idx]
            
            # Index finger (cursor control) gets special treatment
            if tip_idx == 8:
                color = ACTIVE_FINGER
                radius = 6
                
                # Click flash: brief white flash on click
                if click_state in ("CLICK_PENDING", "DRAG_MODE") and time.time() - self._click_flash_timer < (CLICK_FLASH_MS / 1000.0):
                    color = ACCENT_WHITE
                    radius = 8
            else:
                color = FINGERTIP_DOT
                radius = 4
            
            # Outer ring (glow effect using larger dim circle)
            cv2.circle(frame, pos, radius + 3, tuple(c // 4 for c in color), 1, cv2.LINE_AA)
            # Inner filled dot
            cv2.circle(frame, pos, radius, color, -1, cv2.LINE_AA)
    
    def _draw_wrist_ring(self, frame, wrist_pos, activation_state):
        """Breathing pulse ring at wrist. Pulses at 1Hz when active."""
        is_active = activation_state == ActivationState.ACTIVE
        
        if not is_active:
            cv2.circle(frame, wrist_pos, 12, tuple(c // 3 for c in WRIST_RING), 1, cv2.LINE_AA)
            return
        
        # Compute breathing pulse: oscillate opacity using sine wave
        t = time.time()
        pulse = (math.sin(t * 2 * math.pi / (PULSE_PERIOD_MS / 1000)) + 1) / 2  # 0.0 to 1.0
        
        ring_alpha = 0.3 + pulse * 0.5   # 0.3 to 0.8
        ring_color = tuple(int(c * ring_alpha) for c in WRIST_RING)
        
        cv2.circle(frame, wrist_pos, 12, ring_color, 1, cv2.LINE_AA)
        cv2.circle(frame, wrist_pos, 18, tuple(c // 2 for c in ring_color), 1, cv2.LINE_AA)
    
    def _draw_pinch_indicator(self, frame, thumb_pos, index_pos, pinch_distance):
        """Line from thumb to index. Green as distance approaches click threshold."""
        click_threshold = 0.04
        safe_threshold = 0.12
        
        # Map distance to color: gray (far) → green (close) → bright green (click)
        t = 1.0 - min(1.0, max(0.0, (pinch_distance - click_threshold) / (safe_threshold - click_threshold)))
        
        r = int(PINCH_LINE_SAFE[0] + t * (PINCH_LINE_CLOSE[0] - PINCH_LINE_SAFE[0]))
        g = int(PINCH_LINE_SAFE[1] + t * (PINCH_LINE_CLOSE[1] - PINCH_LINE_SAFE[1]))
        b = int(PINCH_LINE_SAFE[2] + t * (PINCH_LINE_CLOSE[2] - PINCH_LINE_SAFE[2]))
        
        cv2.line(frame, thumb_pos, index_pos, (r, g, b), 1, cv2.LINE_AA)
