import cv2
import numpy as np
from ui.theme import *

class HUDComponents:
    def __init__(self, config: dict):
        self.config = config
        self.window_w = WINDOW_WIDTH
        self.window_h = WINDOW_HEIGHT

    def _draw_rounded_rect(self, img, pt1, pt2, color, thickness, r, d=0):
        x1, y1 = pt1
        x2, y2 = pt2
        if thickness < 0:
            cv2.rectangle(img, (x1+r, y1), (x2-r, y2), color, thickness)
            cv2.rectangle(img, (x1, y1+r), (x2, y2-r), color, thickness)
            cv2.circle(img, (x1+r, y1+r), r, color, thickness)
            cv2.circle(img, (x2-r, y1+r), r, color, thickness)
            cv2.circle(img, (x1+r, y2-r), r, color, thickness)
            cv2.circle(img, (x2-r, y2-r), r, color, thickness)
        else:
            cv2.line(img, (x1+r, y1), (x2-r, y1), color, thickness)
            cv2.line(img, (x1+r, y2), (x2-r, y2), color, thickness)
            cv2.line(img, (x1, y1+r), (x1, y2-r), color, thickness)
            cv2.line(img, (x2, y1+r), (x2, y2-r), color, thickness)
            cv2.ellipse(img, (x1+r, y1+r), (r, r), 180, 0, 90, color, thickness)
            cv2.ellipse(img, (x2-r, y1+r), (r, r), 270, 0, 90, color, thickness)
            cv2.ellipse(img, (x1+r, y2-r), (r, r), 90, 0, 90, color, thickness)
            cv2.ellipse(img, (x2-r, y2-r), (r, r), 0, 0, 90, color, thickness)
        
    def _draw_glass_panel(self, canvas, x, y, w, h, alpha=0.85):
        panel_layer = canvas[y:y+h, x:x+w].copy()
        cv2.rectangle(panel_layer, (0, 0), (w, h), (20, 20, 25), -1)
        cv2.addWeighted(panel_layer, alpha, canvas[y:y+h, x:x+w], 1 - alpha, 0, canvas[y:y+h, x:x+w])
        self._draw_rounded_rect(canvas, (x, y), (x+w, y+h), (50, 50, 60), 1, 12)

    def draw_dashboard(self, canvas, hand, tracker_state, is_scrolling, action_text, click_state, confidence, win_prog=0.0, op_data=None):
        # 1. Top Left - AURA Logo
        cv2.putText(canvas, "AURA", (40, 60), FONT_FACE, 1.4, TEXT_PRIMARY, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        cv2.putText(canvas, "WORKSPACE", (145, 58), FONT_FACE, 0.7, BLUE, 1, cv2.LINE_AA)
        
        # 2. Digital Twin (Center)
        cx = self.window_w // 2
        cy = self.window_h // 2
        
        if hand and hand.detected:
            # Scale hand up significantly
            scale = 4.0
            ox, oy = cx - 200, cy - 200
            
            # Glowing background for hand based on action
            glow_color = None
            if action_text == "DRAGGING":
                glow_color = (0, 100, 255)
            elif action_text == "LEFT CLICK":
                glow_color = (0, 255, 0)
            elif action_text == "WINDOW CONTROL MODE":
                glow_color = (0, 165, 255) # Orange glow
            elif action_text == "OPEN PALM DETECTED":
                glow_color = (0, 255, 0) # Green glow
                
            if glow_color:
                # Add subtle background glow
                glow = np.zeros_like(canvas)
                cv2.circle(glow, (cx, cy), 150, glow_color, -1)
                glow = cv2.GaussianBlur(glow, (0,0), 50)
                cv2.addWeighted(glow, 0.3, canvas, 1.0, 0, canvas)
                
            # Window Control Progress Ring
            if win_prog > 0:
                palm_x = int(ox + hand.palm_center[0] * 400)
                palm_y = int(oy + hand.palm_center[1] * 400)
                radius = 120
                thickness = 6
                
                # Background track
                cv2.circle(canvas, (palm_x, palm_y), radius, (40, 40, 45), thickness, cv2.LINE_AA)
                
                # Foreground progress
                angle = int(360 * win_prog)
                if angle > 0:
                    cv2.ellipse(canvas, (palm_x, palm_y), (radius, radius), -90, 0, angle, (0, 165, 255), thickness, cv2.LINE_AA)
                    
                # Progress Text
                pct_str = f"{int(win_prog * 100)}%"
                tsize = cv2.getTextSize(pct_str, FONT_FACE, 0.8, 2)[0]
                cv2.putText(canvas, pct_str, (palm_x - tsize[0]//2, palm_y + tsize[1]//2), FONT_FACE, 0.8, TEXT_PRIMARY, 2, cv2.LINE_AA)
            # Draw bones
            HAND_CONNECTIONS = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (5, 9), (9, 10), (10, 11), (11, 12),
                (9, 13), (13, 14), (14, 15), (15, 16),
                (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
            ]
            
            for conn in HAND_CONNECTIONS:
                p1 = hand.landmarks[conn[0]]
                p2 = hand.landmarks[conn[1]]
                pt1 = (int(ox + p1[0] * 400), int(oy + p1[1] * 400))
                pt2 = (int(ox + p2[0] * 400), int(oy + p2[1] * 400))
                cv2.line(canvas, pt1, pt2, (100, 100, 110), 3, cv2.LINE_AA)
                
            # Draw joints
            for i, p in enumerate(hand.landmarks):
                px = int(ox + p[0] * 400)
                py = int(oy + p[1] * 400)
                color = (200, 200, 210)
                radius = 6
                
                # Active Element Highlighting
                if i == 8: # Index tip
                    if action_text in ["MOVING", "Moving", "Scrolling"]:
                        color = BLUE
                        radius = 10
                    elif click_state in ["HELD", "DRAGGING"]:
                        color = GREEN
                        radius = 12
                elif i == 12: # Middle tip
                    if is_scrolling or action_text == "Scrolling":
                        color = BLUE
                        radius = 10
                        
                cv2.circle(canvas, (px, py), radius, color, -1, cv2.LINE_AA)
        else:
            text_size = cv2.getTextSize("Waiting for Hand", FONT_FACE, 1.5, 2)[0]
            cv2.putText(canvas, "Waiting for Hand", (cx - text_size[0]//2, cy), FONT_FACE, 1.5, TEXT_MUTED, 2, cv2.LINE_AA)

        # 3. Top Right - Status Panel
        rx = self.window_w - 320
        ry = 40
        rw = 280
        rh = 160
        self._draw_glass_panel(canvas, rx, ry, rw, rh, alpha=0.9)
        
        cv2.putText(canvas, "SYSTEM STATUS", (rx + 20, ry + 30), FONT_FACE, 0.6, TEXT_MUTED, 1, cv2.LINE_AA)
        
        trk_color = GREEN if tracker_state == "READY" else RED
        cv2.circle(canvas, (rx + 25, ry + 65), 5, trk_color, -1, cv2.LINE_AA)
        cv2.putText(canvas, "Tracking Active" if tracker_state == "READY" else "No Hand Detected", (rx + 45, ry + 70), FONT_FACE, 0.6, TEXT_PRIMARY, 1, cv2.LINE_AA)
        
        conf_str = f"Confidence: {int(confidence * 100)}%" if tracker_state == "READY" else "Confidence: --"
        cv2.putText(canvas, conf_str, (rx + 20, ry + 105), FONT_FACE, 0.5, TEXT_SECONDARY, 1, cv2.LINE_AA)
        
        action_str = action_text if action_text else "Idle"
        cv2.putText(canvas, f"Action: {action_str}", (rx + 20, ry + 135), FONT_FACE, 0.5, BLUE if action_text else TEXT_SECONDARY, 1, cv2.LINE_AA)
        
        # 4. Top Left Below Logo - Open Palm Debug Mode
        if op_data is not None:
            dx = 40
            dy = 120
            dw = 280
            dh = 220
            self._draw_glass_panel(canvas, dx, dy, dw, dh, alpha=0.9)
            
            cv2.putText(canvas, "GESTURE DEBUG", (dx + 20, dy + 30), FONT_FACE, 0.6, TEXT_MUTED, 1, cv2.LINE_AA)
            
            finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            fingers = op_data.get("fingers", [False]*5)
            
            for i, fname in enumerate(finger_names):
                is_ext = fingers[i]
                c = GREEN if is_ext else TEXT_MUTED
                t = "Extended" if is_ext else "Curved"
                cv2.putText(canvas, f"{fname}: {t}", (dx + 20, dy + 65 + i * 20), FONT_FACE, 0.5, c, 1, cv2.LINE_AA)
                
            f_stable = op_data.get("frames_stable", 0)
            cv2.putText(canvas, f"Frames Stable: {f_stable}/15", (dx + 20, dy + 180), FONT_FACE, 0.5, BLUE if f_stable > 0 else TEXT_MUTED, 1, cv2.LINE_AA)
            
            conf = int(op_data.get("confidence", 0.0) * 100)
            cv2.putText(canvas, f"Confidence: {conf}%", (dx + 20, dy + 200), FONT_FACE, 0.5, TEXT_SECONDARY, 1, cv2.LINE_AA)

    def draw_tutorial_ui(self, canvas, tutorial, illustrator, click_engine, hand, mouse_pos):
        step = tutorial.current_step
        if not step: return
        
        # Transparent overlay
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), (10, 10, 10), -1)
        cv2.addWeighted(overlay, 0.85, canvas, 0.15, 0, canvas)
        
        # Header
        cv2.putText(canvas, "AURA", (40, 60), FONT_FACE, 1.2, TEXT_PRIMARY, FONT_WEIGHT_BOLD, cv2.LINE_AA)
        cv2.putText(canvas, "SETUP ASSISTANT", (150, 60), FONT_FACE, 0.8, BLUE, 1, cv2.LINE_AA)
        
        # Main Glass Card
        cx, cy = 100, 150
        cw, ch = 1080, 460
        cv2.rectangle(canvas, (cx, cy), (cx + cw, cy + ch), BG_PANEL, -1)
        cv2.rectangle(canvas, (cx, cy), (cx + cw, cy + ch), BORDER, 1)
        
        # Left Side: Procedural Animator
        aw, ah = 400, 400
        illustrator.render(canvas, step["id"], cx + 30, cy + 30, aw, ah, tutorial.step_start_time)
        
        # Right Side: Instructions
        tx = cx + 460
        ty = cy + 60
        cv2.putText(canvas, step["title"], (tx, ty), FONT_FACE, 1.4, TEXT_PRIMARY, 2, cv2.LINE_AA)
        cv2.putText(canvas, step["desc"], (tx, ty + 50), FONT_FACE, 0.7, TEXT_SECONDARY, 1, cv2.LINE_AA)
        
        ty += 110
        cv2.putText(canvas, "Detection Checklist:", (tx, ty), FONT_FACE, 0.6, TEXT_MUTED, 1, cv2.LINE_AA)
        
        # Checklist
        c_items = step["checklist"]
        c_states = [tutorial.check_1, tutorial.check_2, tutorial.check_3]
        
        cy_list = ty + 35
        for idx, (item, state) in enumerate(zip(c_items, c_states)):
            icon = "Y" if state else "X"
            color = GREEN if state else TEXT_MUTED
            cv2.putText(canvas, icon, (tx, cy_list), FONT_FACE, 0.6, color, 2 if state else 1, cv2.LINE_AA)
            cv2.putText(canvas, item, (tx + 30, cy_list), FONT_FACE, 0.6, TEXT_PRIMARY if state else TEXT_MUTED, 1, cv2.LINE_AA)
            cy_list += 35
            
        # Diagnostic Error
        if not tutorial.can_proceed:
            cv2.putText(canvas, f"Error: {tutorial.diagnostic}", (tx, cy_list + 10), FONT_FACE, 0.6, RED, 1, cv2.LINE_AA)
        else:
            cv2.putText(canvas, "Step Complete! Hold Next to continue.", (tx, cy_list + 10), FONT_FACE, 0.6, GREEN, 1, cv2.LINE_AA)

        # Buttons Panel
        by = cy + ch - 70
        bx = tx
        
        # Skip
        cv2.rectangle(canvas, (bx, by), (bx + 100, by + 40), (40, 30, 30), -1)
        cv2.putText(canvas, "Skip", (bx + 25, by + 25), FONT_FACE, 0.6, TEXT_MUTED, 1, cv2.LINE_AA)
        
        # Replay
        cv2.rectangle(canvas, (bx + 120, by), (bx + 240, by + 40), (30, 40, 50), -1)
        cv2.putText(canvas, "Replay", (bx + 140, by + 25), FONT_FACE, 0.6, BLUE, 1, cv2.LINE_AA)
        
        # Next
        nx = bx + 260
        nw = 160
        btn_color = (60, 140, 80) if tutorial.can_proceed else (40, 50, 40)
        cv2.rectangle(canvas, (nx, by), (nx + nw, by + 40), btn_color, -1)
        cv2.putText(canvas, "Next ->", (nx + 40, by + 25), FONT_FACE, 0.6, TEXT_PRIMARY, 1, cv2.LINE_AA)
        
        if tutorial.next_hover_progress > 0:
            pw = int(nw * tutorial.next_hover_progress)
            cv2.rectangle(canvas, (nx, by + 36), (nx + pw, by + 40), GREEN, -1)
            
        # Hover logic
        mx, my = mouse_pos
        is_hovering_next = (nx <= mx <= nx + nw) and (by <= my <= by + 40)
        is_clicking = click_engine.state == "CLICKED" or click_engine.state == "HELD"
        
        if tutorial.process_next_button_hover(is_hovering_next, is_clicking):
            click_engine.reset()
            
        # Progress dots
        px = WINDOW_WIDTH // 2 - 40
        py = 100
        for i in range(len(tutorial.STEPS)):
            color = GREEN if i < tutorial.current_step_index else TEXT_MUTED
            cv2.circle(canvas, (px + i * 20, py), 4, color, -1, cv2.LINE_AA)
        cv2.putText(canvas, f"Step {tutorial.current_step_index+1} of {len(tutorial.STEPS)}", (px - 10, py - 20), FONT_FACE, 0.6, TEXT_SECONDARY, 1, cv2.LINE_AA)
