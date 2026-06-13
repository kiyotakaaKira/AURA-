import cv2
import numpy as np
import time
import math
from ui.theme import *

class TutorialIllustrator:
    def __init__(self):
        # Base normalized hand skeleton (Palm facing away)
        self.base_hand = {
            0: (0.5, 0.9), 
            1: (0.35, 0.8), 2: (0.25, 0.65), 3: (0.15, 0.55), 4: (0.1, 0.45), # Thumb
            5: (0.35, 0.5), 6: (0.3, 0.3), 7: (0.3, 0.15), 8: (0.3, 0.05), # Index
            9: (0.5, 0.48), 10: (0.5, 0.25), 11: (0.5, 0.1), 12: (0.5, 0.0), # Middle
            13: (0.65, 0.5), 14: (0.7, 0.3), 15: (0.7, 0.15), 16: (0.7, 0.05), # Ring
            17: (0.8, 0.55), 18: (0.85, 0.4), 19: (0.85, 0.3), 20: (0.85, 0.2) # Pinky
        }
        
        self.connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
        ]

    def render(self, canvas: np.ndarray, step_id: str, cx: int, cy: int, w: int, h: int, start_time: float):
        t = time.time() - start_time
        pts = dict(self.base_hand)
        
        # Physics / Animation variables
        cycle = (math.sin(t * 3.0) + 1.0) / 2.0  # 0.0 to 1.0
        
        offset_x, offset_y = 0.0, 0.0
        
        if step_id == "cursor":
            # Hand moves around slightly
            offset_x = math.sin(t * 2.0) * 0.15
            offset_y = math.cos(t * 2.5) * 0.1
            
        elif step_id == "click":
            # Index curls rapidly
            curl_amt = max(0.0, math.sin(t * 4.0))
            pts[6] = self._lerp(self.base_hand[6], (0.35, 0.4), curl_amt)
            pts[7] = self._lerp(self.base_hand[7], (0.4, 0.5), curl_amt)
            pts[8] = self._lerp(self.base_hand[8], (0.4, 0.6), curl_amt)
            
        elif step_id == "drag":
            # Curls, holds, moves, releases
            phase = (t % 3.0) / 3.0
            curl_amt = 1.0 if 0.1 < phase < 0.8 else 0.0
            if phase > 0.2 and phase < 0.7:
                offset_x = math.sin((phase - 0.2) * math.pi * 2) * 0.2
            
            pts[6] = self._lerp(self.base_hand[6], (0.35, 0.4), curl_amt)
            pts[7] = self._lerp(self.base_hand[7], (0.4, 0.5), curl_amt)
            pts[8] = self._lerp(self.base_hand[8], (0.4, 0.6), curl_amt)
            
        elif step_id == "right_click":
            # Middle curls
            curl_amt = max(0.0, math.sin(t * 4.0))
            pts[10] = self._lerp(self.base_hand[10], (0.5, 0.45), curl_amt)
            pts[11] = self._lerp(self.base_hand[11], (0.55, 0.55), curl_amt)
            pts[12] = self._lerp(self.base_hand[12], (0.55, 0.65), curl_amt)
            
        elif step_id == "scroll":
            # Two fingers out, others curled
            # Curl ring and pinky permanently
            for i in [14, 15, 16, 18, 19, 20]:
                pts[i] = self._lerp(self.base_hand[i], (self.base_hand[i][0]-0.1, self.base_hand[i][1]+0.2), 1.0)
            
            offset_y = math.sin(t * 3.0) * 0.15

        # Render background glass
        cv2.rectangle(canvas, (cx, cy), (cx + w, cy + h), (18, 18, 22), -1)
        cv2.rectangle(canvas, (cx, cy), (cx + w, cy + h), (60, 60, 70), 1)

        # Draw Skeleton
        scale_x = w * 0.6
        scale_y = h * 0.6
        base_x = cx + w * 0.2 + (offset_x * w)
        base_y = cy + h * 0.2 + (offset_y * h)
        
        # Connections
        for p1, p2 in self.connections:
            x1 = int(base_x + pts[p1][0] * scale_x)
            y1 = int(base_y + pts[p1][1] * scale_y)
            x2 = int(base_x + pts[p2][0] * scale_x)
            y2 = int(base_y + pts[p2][1] * scale_y)
            cv2.line(canvas, (x1, y1), (x2, y2), (180, 180, 200), 3, cv2.LINE_AA)
            
        # Joints
        for i, pt in pts.items():
            x = int(base_x + pt[0] * scale_x)
            y = int(base_y + pt[1] * scale_y)
            
            color = (220, 220, 240)
            radius = 5
            
            if step_id in ["click", "drag"] and i in [6, 7, 8]:
                color = GREEN
                radius = 7
            elif step_id == "right_click" and i in [10, 11, 12]:
                color = BLUE
                radius = 7
            elif step_id == "scroll" and i in [6, 7, 8, 10, 11, 12]:
                color = AMBER
                radius = 6
                
            cv2.circle(canvas, (x, y), radius, color, -1, cv2.LINE_AA)

    def _lerp(self, p1, p2, t):
        return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)
