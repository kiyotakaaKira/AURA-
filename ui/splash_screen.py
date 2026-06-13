import cv2
import numpy as np
import time
import math
import random
from ui.theme import *

class SplashScreen:
    """
    Renders an Apple Vision Pro style premium splash screen using OpenCV.
    Handles the initialization sequence visually.
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.start_time = time.time()
        self.duration = 10.0
        
        self.checks = [
            ("Cursor Engine", False),
            ("Interaction Engine", False),
            ("User Interface", False),
            ("Workspace", False)
        ]
        
    def set_check_complete(self, index: int):
        pass # Ignored in V2, we time-base it for cinematic effect
        
    def is_finished(self) -> bool:
        return (time.time() - self.start_time) > self.duration

    def _create_glow_text(self, img, text, pos, font, scale, color, thickness, glow_intensity=0.5):
        # Extremely lightweight fake glow (just draw a thicker, dimmer text behind it)
        cv2.putText(img, text, pos, font, scale, (int(color[0]*glow_intensity), int(color[1]*glow_intensity), int(color[2]*glow_intensity)), thickness + 4, cv2.LINE_AA)
        cv2.putText(img, text, pos, font, scale, color, thickness, cv2.LINE_AA)

    def render(self) -> np.ndarray:
        now = time.time()
        elapsed = now - self.start_time
        
        canvas = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        cx, cy = self.w // 2, self.h // 2
        
        # Calculate Global Fade Out (Scene 6)
        global_alpha = 1.0
        if elapsed > 9.0:
            global_alpha = max(0.0, 1.0 - (elapsed - 9.0))
            
        # Scene 1: Ambient Glow (0.0s - 10.0s, fades in 0-1s)
        glow_alpha = min(1.0, elapsed / 1.0) * global_alpha
        if glow_alpha > 0 and elapsed < 7.0: # Turn off glow for Hero Moment
            # Very lightweight glow: draw a single circle, no blur
            cv2.circle(canvas, (cx, cy), 400, (int(15 * glow_alpha), int(12 * glow_alpha), int(10 * glow_alpha)), -1)
            
        # Scene 2 & 3: Logo and Tagline (1.0s - 5.0s)
        # Fades out during Scene 4
        logo_scene_alpha = 1.0
        if elapsed > 4.5:
            logo_scene_alpha = max(0.0, 1.0 - (elapsed - 4.5) / 0.5)
            
        if elapsed >= 1.0 and logo_scene_alpha > 0:
            # Logo fade in (1.0s - 3.0s)
            logo_alpha = min(1.0, (elapsed - 1.0) / 2.0) * logo_scene_alpha
            logo_color = (int(TEXT_PRIMARY[0] * logo_alpha), int(TEXT_PRIMARY[1] * logo_alpha), int(TEXT_PRIMARY[2] * logo_alpha))
            
            text_size = cv2.getTextSize("AURA", FONT_FACE, 3.0, 3)[0]
            text_x = cx - text_size[0] // 2
            text_y = cy - 20
            self._create_glow_text(canvas, "AURA", (text_x, text_y), FONT_FACE, 3.0, logo_color, 2, 0.5)
            
        if elapsed >= 3.0 and logo_scene_alpha > 0:
            # Tagline fade in (3.0s - 5.0s)
            tag_alpha = min(1.0, (elapsed - 3.0) / 2.0) * logo_scene_alpha
            tag_color = (int(TEXT_SECONDARY[0] * tag_alpha), int(TEXT_SECONDARY[1] * tag_alpha), int(TEXT_SECONDARY[2] * tag_alpha))
            
            tag_text = "The Future of Human Interaction"
            tag_size = cv2.getTextSize(tag_text, FONT_FACE, 0.8, 1)[0]
            self._create_glow_text(canvas, tag_text, (cx - tag_size[0] // 2, cy + 40), FONT_FACE, 0.8, tag_color, 1, 0.3)
            
            # Very fast light sweep on tagline
            sweep = (elapsed - 3.0) * 1000 - 200
            if -200 < sweep < 800:
                cv2.line(canvas, (cx - 200 + int(sweep), cy + 50), (cx - 100 + int(sweep), cy + 50), (100, 100, 100), 1)

        # Scene 4: Initialization Sequence (5.0s - 7.0s)
        init_scene_alpha = 1.0
        if elapsed > 6.5:
            init_scene_alpha = max(0.0, 1.0 - (elapsed - 6.5) / 0.5)
            
        if elapsed >= 5.0 and init_scene_alpha > 0:
            init_alpha = min(1.0, (elapsed - 5.0) / 0.5) * init_scene_alpha
            init_color = (int(TEXT_MUTED[0] * init_alpha), int(TEXT_MUTED[1] * init_alpha), int(TEXT_MUTED[2] * init_alpha))
            
            cv2.putText(canvas, "Vision Engine", (cx - 60, cy - 80), FONT_FACE, 0.8, init_color, 1, cv2.LINE_AA)
            cv2.putText(canvas, "Initializing...", (cx - 60, cy - 50), FONT_FACE, 0.6, init_color, 1, cv2.LINE_AA)
            
            check_start_y = cy - 10
            for i, (name, _) in enumerate(self.checks):
                # Animate in sequentially
                appear_time = 5.5 + i * 0.2
                if elapsed >= appear_time:
                    c_alpha = min(1.0, (elapsed - appear_time) / 0.2) * init_scene_alpha
                    color = (int(TEXT_PRIMARY[0] * c_alpha), int(TEXT_PRIMARY[1] * c_alpha), int(TEXT_PRIMARY[2] * c_alpha))
                    check_c = (int(GREEN[0] * c_alpha), int(GREEN[1] * c_alpha), int(GREEN[2] * c_alpha))
                    
                    y = check_start_y + i * 30
                    x = cx - 60
                    
                    cv2.putText(canvas, "V", (x, y), FONT_FACE, 0.5, check_c, 1, cv2.LINE_AA)
                    cv2.putText(canvas, name, (x + 30, y), FONT_FACE, 0.6, color, 1, cv2.LINE_AA)

        # Scene 5: Hero Moment (7.0s - 9.0s)
        if elapsed >= 7.0:
            hero_alpha = min(1.0, (elapsed - 7.0) / 1.0) * global_alpha
            
            logo_c = (int(TEXT_PRIMARY[0] * hero_alpha), int(TEXT_PRIMARY[1] * hero_alpha), int(TEXT_PRIMARY[2] * hero_alpha))
            text_size = cv2.getTextSize("AURA", FONT_FACE, 3.0, 3)[0]
            text_x = cx - text_size[0] // 2
            text_y = cy - 20
            self._create_glow_text(canvas, "AURA", (text_x, text_y), FONT_FACE, 3.0, logo_c, 2, 0.8)
            
            tag_c = (int(TEXT_SECONDARY[0] * hero_alpha), int(TEXT_SECONDARY[1] * hero_alpha), int(TEXT_SECONDARY[2] * hero_alpha))
            tag_text = "Human Computer Interface Reimagined"
            tag_size = cv2.getTextSize(tag_text, FONT_FACE, 0.8, 1)[0]
            self._create_glow_text(canvas, tag_text, (cx - tag_size[0] // 2, cy + 40), FONT_FACE, 0.8, tag_c, 1, 0.3)
            
        return canvas
