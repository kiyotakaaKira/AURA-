import time

class TutorialManager:
    STEPS = [
        {
            "id": "cursor",
            "title": "Control Your Cursor",
            "desc": "Keep your hand relaxed. Move it around to steer the cursor on screen.",
            "tips": ["Keep your fingers straight", "Move your whole hand"],
            "action": "Move Cursor",
            "checklist": ["Hand Visible", "Fingers Relaxed", "Cursor Moved"]
        },
        {
            "id": "click",
            "title": "Left Click",
            "desc": "Quickly curl your index finger inward, like pulling a trigger.",
            "tips": ["A subtle bend works perfectly", "Don't move your whole hand"],
            "action": "Curl Index Finger",
            "checklist": ["Hand Visible", "Index Extended", "Click Executed"]
        },
        {
            "id": "drag",
            "title": "Hold to Drag",
            "desc": "Curl your index finger and HOLD it. Move your hand to drag, then release.",
            "tips": ["Hold the curl steady", "Move your hand while curling"],
            "action": "Hold Curl for 300ms",
            "checklist": ["Hand Visible", "Hold Started", "Drag Completed"]
        },
        {
            "id": "right_click",
            "title": "Right Click",
            "desc": "Curl your middle finger inward quickly.",
            "tips": ["Only bend the middle finger", "Keep index straight"],
            "action": "Curl Middle Finger",
            "checklist": ["Hand Visible", "Middle Extended", "Right Click Executed"]
        },
        {
            "id": "scroll",
            "title": "Two Finger Scroll",
            "desc": "Keep both index and middle fingers straight. Move hand up/down.",
            "tips": ["Keep other fingers curled", "Move hand vertically"],
            "action": "Scroll Page",
            "checklist": ["Hand Visible", "Two Fingers Up", "Scroll Executed"]
        }
    ]

    def __init__(self, config: dict):
        self.enabled = config.get('tutorial', {}).get('show_on_first_launch', True)
        self.current_step_index = 0
        self.is_completed = not self.enabled
        
        self.step_start_time = time.time()
        
        self.step_state = "WAITING"
        self.diagnostic = "Move Hand Into Camera"
        self.can_proceed = False
        
        self.last_mouse_pos = (0, 0)
        self.drag_start_pos = (0, 0)
        
        self.next_hover_start = 0.0
        self.next_hover_progress = 0.0
        
        # Checklist states
        self.check_1 = False
        self.check_2 = False
        self.check_3 = False

    @property
    def current_step(self):
        if 0 <= self.current_step_index < len(self.STEPS):
            return self.STEPS[self.current_step_index]
        return None

    def update(self, control_hand, mouse_pos, click_engine, scroll_engine, right_gesture, all_hands):
        step = self.current_step
        if not step:
            self.is_completed = True
            return

        sid = step["id"]
        
        # Base checks
        self.check_1 = control_hand is not None and control_hand.detected
        
        if not self.check_1:
            self.step_state = "WAITING"
            self.diagnostic = "Hand Missing -> Move Hand Into Camera"
            return
            
        self.diagnostic = "Tracking Active"

        if sid == "cursor":
            # Check 2: Fingers relaxed (index extended)
            self.check_2 = control_hand.fingers_extended[1]
            if not self.check_2:
                self.diagnostic = "Index Finger Not Extended -> Raise Index Finger"
                
            dx = abs(mouse_pos[0] - self.last_mouse_pos[0])
            dy = abs(mouse_pos[1] - self.last_mouse_pos[1])
            if dx > 5 or dy > 5:
                self.check_3 = True
                
            if self.check_2 and self.check_3:
                self.step_state = "SUCCESS"
                self.diagnostic = "Step Complete"
                self.can_proceed = True
                
        elif sid == "click":
            self.check_2 = control_hand.fingers_extended[1] or self.check_3
            if not self.check_2:
                self.diagnostic = "Index Finger Not Extended -> Raise Index Finger"
                
            if click_engine._last_action == "LEFT CLICK":
                self.check_3 = True
                
            if self.check_3:
                self.step_state = "SUCCESS"
                self.diagnostic = "Step Complete"
                self.can_proceed = True
                
        elif sid == "drag":
            if click_engine.state == "DRAGGING":
                self.check_2 = True
                self.diagnostic = "Hold detected, now move..."
                if self.drag_start_pos == (0,0):
                    self.drag_start_pos = mouse_pos
                dist = ((mouse_pos[0] - self.drag_start_pos[0])**2 + (mouse_pos[1] - self.drag_start_pos[1])**2)**0.5
                if dist > 50:
                    self.check_3 = True
            else:
                self.drag_start_pos = (0,0)
                if not self.can_proceed:
                    self.diagnostic = "Curl and hold index finger..."
                    
            if self.check_3:
                self.step_state = "SUCCESS"
                self.diagnostic = "Step Complete"
                self.can_proceed = True
                    
        elif sid == "right_click":
            self.check_2 = control_hand.fingers_extended[2] or self.check_3
            if click_engine.right_state == "CURLED":
                self.check_3 = True
                
            if self.check_3:
                self.step_state = "SUCCESS"
                self.diagnostic = "Step Complete"
                self.can_proceed = True
                
        elif sid == "scroll":
            self.check_2 = control_hand.fingers_extended[1] and control_hand.fingers_extended[2]
            if scroll_engine.is_scrolling:
                self.check_3 = True
                
            if self.check_3:
                self.step_state = "SUCCESS"
                self.diagnostic = "Step Complete"
                self.can_proceed = True

        self.last_mouse_pos = mouse_pos

    def process_next_button_hover(self, is_hovering: bool, is_clicking: bool):
        if not self.can_proceed:
            self.next_hover_progress = 0.0
            return False
            
        if is_clicking and is_hovering:
            self.next_step()
            return True
            
        if is_hovering:
            if self.next_hover_start == 0.0:
                self.next_hover_start = time.time()
            self.next_hover_progress = min(1.0, (time.time() - self.next_hover_start) / 1.0)
            if self.next_hover_progress >= 1.0:
                self.next_step()
                return True
        else:
            self.next_hover_start = 0.0
            self.next_hover_progress = max(0.0, self.next_hover_progress - 0.05)
            
        return False

    def next_step(self):
        if not self.can_proceed: return
        self.current_step_index += 1
        self.reset_step_state()
        if self.current_step_index >= len(self.STEPS):
            self.is_completed = True

    def reset_step_state(self):
        self.step_state = "WAITING"
        self.diagnostic = "Move Hand Into Camera"
        self.can_proceed = False
        self.next_hover_start = 0.0
        self.next_hover_progress = 0.0
        self.check_1 = False
        self.check_2 = False
        self.check_3 = False
        self.step_start_time = time.time()

    def previous_step(self):
        self.current_step_index = max(0, self.current_step_index - 1)
        self.reset_step_state()

    def restart(self):
        self.current_step_index = 0
        self.reset_step_state()
        self.is_completed = False

    def skip(self):
        self.is_completed = True
