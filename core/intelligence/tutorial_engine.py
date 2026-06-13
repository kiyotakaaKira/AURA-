import time
from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass

class TutorialStep(Enum):
    WELCOME = 0
    DETECTION = 1
    CURSOR = 2
    CLICK = 3
    SCROLL = 4
    DISMISS = 5
    DONE = 6

@dataclass
class TutorialState:
    step: TutorialStep
    title: str
    instruction: str
    is_completed: bool = False
    progress: float = 0.0

class TutorialEngine:
    def __init__(self):
        self.current_step = TutorialStep.WELCOME
        self._step_start_time = time.time()
        
        self.min_duration = 8.0
        self.max_duration = 15.0
        self._completion_time = None
        
        self.enabled = True

    def get_state(self) -> Optional[TutorialState]:
        if not self.enabled or self.current_step == TutorialStep.DONE:
            return None
            
        return TutorialState(
            step=self.current_step,
            title=self._get_title(self.current_step),
            instruction=self._get_instruction(self.current_step),
            is_completed=(self._completion_time is not None),
            progress=self._get_progress()
        )
        
    def _get_title(self, step: TutorialStep) -> str:
        titles = {
            TutorialStep.WELCOME: "Welcome to AURA",
            TutorialStep.DETECTION: "Hand Detection",
            TutorialStep.CURSOR: "Cursor Control",
            TutorialStep.CLICK: "Clicking",
            TutorialStep.SCROLL: "Scrolling",
            TutorialStep.DISMISS: "Dismiss Gesture"
        }
        return titles.get(step, "")
        
    def _get_instruction(self, step: TutorialStep) -> str:
        instructions = {
            TutorialStep.WELCOME: "AURA is your AI mouse. Let's learn the basics.",
            TutorialStep.DETECTION: "Show your hand to AURA",
            TutorialStep.CURSOR: "Point with your index finger",
            TutorialStep.CLICK: "Pinch thumb and index finger",
            TutorialStep.SCROLL: "Raise two fingers and move up or down",
            TutorialStep.DISMISS: "Clap twice with both hands to close AURA"
        }
        return instructions.get(step, "")
        
    def _get_progress(self) -> float:
        if self._completion_time is not None:
            return 1.0
        elapsed = time.time() - self._step_start_time
        # Progress bar represents the max duration
        return min(elapsed / self.max_duration, 1.0)
        
    def update(self, fused, activation, current_gesture, has_moved, has_clicked, has_scrolled):
        if not self.enabled or self.current_step == TutorialStep.DONE:
            return
            
        now = time.time()
        elapsed = now - self._step_start_time
        
        if self._completion_time is not None:
            # We wait until min_duration is hit before advancing, even if completed early
            if elapsed >= self.min_duration:
                self.next_step()
            return
            
        # Hard timeout
        if elapsed >= self.max_duration:
            self.next_step()
            return
            
        # Welcome screen auto-progresses after min_duration
        if self.current_step == TutorialStep.WELCOME:
            if elapsed >= self.min_duration:
                self._completion_time = now
            return
            
        is_completed = False
        
        if self.current_step == TutorialStep.DETECTION:
            if fused.hand.detected:
                is_completed = True
                
        elif self.current_step == TutorialStep.CURSOR:
            if activation.is_controlling and current_gesture == "index_point":
                is_completed = True
                
        elif self.current_step == TutorialStep.CLICK:
            if has_clicked:
                is_completed = True
                
        elif self.current_step == TutorialStep.SCROLL:
            if has_scrolled:
                is_completed = True
                
        elif self.current_step == TutorialStep.DISMISS:
            # Dismiss step just runs out its clock or is skipped
            pass
            
        if is_completed:
            self._completion_time = now
            
    def next_step(self):
        next_val = self.current_step.value + 1
        if next_val <= TutorialStep.DONE.value:
            self.current_step = TutorialStep(next_val)
            self._step_start_time = time.time()
            self._completion_time = None
            
    def previous_step(self):
        prev_val = self.current_step.value - 1
        if prev_val >= 0:
            self.current_step = TutorialStep(prev_val)
            self._step_start_time = time.time()
            self._completion_time = None
            
    def skip(self):
        self.enabled = False
