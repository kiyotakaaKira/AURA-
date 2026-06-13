import time
from datetime import datetime
from enum import Enum, auto
from ..tracker.tracker_fusion import FusedState
from .gesture_library import GestureLibrary

class RecordingState(Enum):
    IDLE = auto()
    AWAITING_NAME = auto()      # Waiting for user to type gesture name
    DEMO_MODE = auto()          # "Show us your gesture" — user previewing
    COUNTDOWN = auto()          # 3... 2... 1...
    RECORDING = auto()          # Actively capturing frames
    BETWEEN_SAMPLES = auto()    # Brief pause between sample captures
    COMPLETE = auto()           # All samples captured, saved

class GestureRecorder:
    TARGET_SAMPLES = 10         # Samples per gesture
    FRAMES_PER_SAMPLE = 30      # Frames per sample (1 second at 30fps)
    COUNTDOWN_SECONDS = 3
    BETWEEN_SAMPLE_PAUSE_MS = 800
    
    def __init__(self, gesture_library: GestureLibrary):
        self.library = gesture_library
        self.state = RecordingState.IDLE
        self._gesture_name = None
        self._current_sample = 0
        self._current_frames = []
        self._all_samples = []
        self._state_entry_time = None
        self._countdown_remaining = 0
    
    def start_recording(self, gesture_name: str):
        """Begin recording a new gesture."""
        self._gesture_name = gesture_name
        self._current_sample = 0
        self._all_samples = []
        self._transition_to(RecordingState.DEMO_MODE)
        
    def _transition_to(self, state: RecordingState):
        self.state = state
        self._state_entry_time = time.time()
    
    def update(self, fused_state: FusedState) -> RecordingState:
        """Call every frame. Returns current recording state."""
        now = time.time()
        
        if self.state == RecordingState.DEMO_MODE:
            # Just display the prompt — wait for SPACE key press
            pass
        
        elif self.state == RecordingState.COUNTDOWN:
            elapsed = now - self._state_entry_time
            self._countdown_remaining = max(0, self.COUNTDOWN_SECONDS - int(elapsed))
            
            if elapsed >= self.COUNTDOWN_SECONDS:
                self._current_frames = []
                self._transition_to(RecordingState.RECORDING)
        
        elif self.state == RecordingState.RECORDING:
            # Capture this frame's landmark data
            if fused_state.hand.detected:
                frame_data = {
                    "timestamp": now - self._state_entry_time,
                    "landmarks": [list(lm) for lm in fused_state.hand.landmarks],
                    "normalized_landmarks": [list(lm) for lm in fused_state.hand.normalized_landmarks],
                    "fingers_extended": fused_state.hand.fingers_extended,
                    "pinch_distance": fused_state.hand.pinch_distance,
                    "velocity": fused_state.motion.speed,
                    "acceleration": fused_state.motion.speed,   # simplified
                    "confidence": fused_state.hand.confidence
                }
                self._current_frames.append(frame_data)
            
            if len(self._current_frames) >= self.FRAMES_PER_SAMPLE:
                self._all_samples.append({
                    "sample_id": self._current_sample,
                    "frame_count": len(self._current_frames),
                    "frames": self._current_frames
                })
                
                self._current_sample += 1
                
                if self._current_sample >= self.TARGET_SAMPLES:
                    self._save_gesture()
                    self._transition_to(RecordingState.COMPLETE)
                else:
                    self._transition_to(RecordingState.BETWEEN_SAMPLES)
        
        elif self.state == RecordingState.BETWEEN_SAMPLES:
            if (now - self._state_entry_time) * 1000 > self.BETWEEN_SAMPLE_PAUSE_MS:
                self._transition_to(RecordingState.COUNTDOWN)
        
        elif self.state == RecordingState.COMPLETE:
            if (now - self._state_entry_time) > 2.0:
                self._transition_to(RecordingState.IDLE)
        
        return self.state
    
    def _save_gesture(self):
        """Persist all samples to data/gestures/{name}/samples.json"""
        gesture_data = {
            "gesture_name": self._gesture_name,
            "created_at": datetime.now().isoformat(),
            "sample_count": len(self._all_samples),
            "metadata": {
                "dominant_hand": "right",   # From user model
                "aura_version": "0.1.0",
                "frames_per_sample": self.FRAMES_PER_SAMPLE
            },
            "samples": self._all_samples
        }
        self.library.save_gesture(self._gesture_name, gesture_data)
    
    def handle_key(self, key: int) -> bool:
        """Returns True if key was consumed."""
        if key == ord(' ') and self.state == RecordingState.DEMO_MODE:
            self._transition_to(RecordingState.COUNTDOWN)
            return True
        if key == 27 and self.state != RecordingState.IDLE:  # ESC
            self._transition_to(RecordingState.IDLE)
            return True
        return False
    
    @property
    def progress(self) -> float:
        """0.0-1.0 progress through all samples."""
        return self._current_sample / max(1, self.TARGET_SAMPLES)
    
    @property
    def countdown_display(self) -> int:
        return self._countdown_remaining
