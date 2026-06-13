import cv2
import numpy as np
import time
from .theme import *

class StartupState:
    SPLASH = 0
    DIAGNOSTICS = 1
    WELCOME = 2
    DONE = 3

def ease_out_cubic(x):
    return 1 - pow(1 - x, 3)

def ease_in_out_sine(x):
    return -(np.cos(np.pi * x) - 1) / 2

class StartupRenderer:
    def __init__(self, window_width, window_height):
        self.w = window_width
        self.h = window_height
        self.state = StartupState.SPLASH
        self.start_time = time.time()
        self.state_start_time = self.start_time
        
        self.tasks = []
        self.completed_tasks = set()
        
        # Glassmorphism base
        self.base_canvas = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.base_canvas[:] = (10, 10, 12) # Deep dark background
        
        # Pre-render a subtle gradient background
        for y in range(self.h):
            ratio = y / self.h
            color = (
                int(10 + ratio * 15), 
                int(10 + ratio * 20), 
                int(12 + ratio * 25)
            )
            self.base_canvas[y, :] = color

    def add_task(self, task_name):
        if task_name not in self.tasks:
            self.tasks.append(task_name)

    def complete_task(self, task_name):
        self.completed_tasks.add(task_name)
        
    def transition_to(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()

    def render(self) -> np.ndarray:
        canvas = self.base_canvas.copy()
        now = time.time()
        state_elapsed = now - self.state_start_time
        
        if self.state == StartupState.SPLASH:
            # 2.5 second splash
            if state_elapsed > 2.5:
                self.transition_to(StartupState.DIAGNOSTICS)
                
            # Fade in logo and subtitle
            alpha = min(state_elapsed / 1.0, 1.0)
            alpha = ease_in_out_sine(alpha)
            
            # Subtle scale up effect
            scale = 1.0 + (state_elapsed * 0.05)
            
            text = "AURA"
            font_scale = 2.5 * scale
            font_thickness = 3
            
            size, _ = cv2.getTextSize(text, FONT_FACE, font_scale, font_thickness)
            text_x = self.w // 2 - size[0] // 2
            text_y = self.h // 2 - 20
            
            color = tuple(int(c * alpha) for c in (255, 255, 255))
            
            # Soft glow (draw thick blurred, then sharp)
            glow_color = tuple(int(c * alpha * 0.5) for c in ACCENT_BLUE)
            cv2.putText(canvas, text, (text_x, text_y), FONT_FACE, font_scale, glow_color, font_thickness + 4, cv2.LINE_AA)
            cv2.putText(canvas, text, (text_x, text_y), FONT_FACE, font_scale, color, font_thickness, cv2.LINE_AA)
            
            # Tagline
            if state_elapsed > 1.0:
                tag_alpha = min((state_elapsed - 1.0) / 1.0, 1.0)
                tag_alpha = ease_in_out_sine(tag_alpha)
                tag_color = tuple(int(c * tag_alpha) for c in (180, 180, 180))
                tag_text = "The Future of Human Interaction"
                tag_scale = 0.7 * scale
                tag_size, _ = cv2.getTextSize(tag_text, FONT_FACE, tag_scale, 1)
                tag_x = self.w // 2 - tag_size[0] // 2
                tag_y = text_y + 50
                cv2.putText(canvas, tag_text, (tag_x, tag_y), FONT_FACE, tag_scale, tag_color, 1, cv2.LINE_AA)
                
        elif self.state == StartupState.DIAGNOSTICS:
            # Title
            cv2.putText(canvas, "Initializing AURA", (40, 60), FONT_FACE, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Draw tasks list
            start_y = 120
            for i, task in enumerate(self.tasks):
                y = start_y + (i * 40)
                
                # Simple slide in animation for list items
                item_delay = i * 0.1
                if state_elapsed < item_delay:
                    continue
                    
                item_alpha = min((state_elapsed - item_delay) / 0.5, 1.0)
                
                is_done = task in self.completed_tasks
                color = ACCENT_GREEN if is_done else (150, 150, 150)
                icon = "[✓]" if is_done else "[...]"
                
                draw_color = tuple(int(c * item_alpha) for c in color)
                cv2.putText(canvas, f"{icon}  {task}", (40, y), FONT_FACE, 0.7, draw_color, 1, cv2.LINE_AA)
                
            # Check if all done
            if len(self.tasks) > 0 and len(self.completed_tasks) == len(self.tasks):
                if not hasattr(self, 'diag_done_time'):
                    self.diag_done_time = now
                elif now - self.diag_done_time > 1.0: # Wait 1s after all checked
                    self.transition_to(StartupState.WELCOME)
                    
        elif self.state == StartupState.WELCOME:
            alpha = min(state_elapsed / 1.0, 1.0)
            
            text = "Welcome Back"
            size, _ = cv2.getTextSize(text, FONT_FACE, 2.0, 2)
            text_x = self.w // 2 - size[0] // 2
            text_y = self.h // 2 - 20
            
            color = tuple(int(c * alpha) for c in (255, 255, 255))
            cv2.putText(canvas, text, (text_x, text_y), FONT_FACE, 2.0, color, 2, cv2.LINE_AA)
            
            if state_elapsed > 2.0:
                self.transition_to(StartupState.DONE)
                
        return canvas
