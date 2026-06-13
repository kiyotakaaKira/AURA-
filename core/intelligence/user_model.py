import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class CalibrationData:
    interaction_zone: List[float] = field(default_factory=lambda: [0.2, 0.8, 0.2, 0.8])
    cursor_sensitivity: float = 1.0
    click_threshold: float = 0.035
    activation_hold_time_ms: int = 500
    scroll_sensitivity: float = 1.0

@dataclass  
class UserPreferences:
    smoothing_algorithm: str = "one_euro"
    one_euro_min_cutoff: float = 1.0
    one_euro_beta: float = 0.007
    scroll_speed: float = 1.0
    volume_sensitivity: float = 1.0
    hud_opacity: float = 0.92
    dominant_hand: str = "right"
    auto_sleep_timeout_s: float = 3.0

@dataclass
class UserHabits:
    most_used_gestures: List[str] = field(default_factory=list)
    gesture_use_counts: Dict[str, int] = field(default_factory=dict)
    most_used_apps: List[str] = field(default_factory=list)
    session_count: int = 0
    total_interaction_minutes: float = 0.0
    false_trigger_count: int = 0

class UserModel:
    DATA_DIR = Path("data/profiles")
    
    def __init__(self, user_id: str = "user_001"):
        self.user_id = user_id
        self.calibration = CalibrationData()
        self.preferences = UserPreferences()
        self.habits = UserHabits()
        self._session_start = time.time()
        self.load()
    
    def load(self):
        profile_path = self.DATA_DIR / f"{self.user_id}.json"
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'calibration' in data:
                    self.calibration = CalibrationData(**data['calibration'])
                if 'preferences' in data:
                    self.preferences = UserPreferences(**data['preferences'])
                if 'habits' in data:
                    self.habits = UserHabits(**data['habits'])
            except (json.JSONDecodeError, TypeError):
                pass
    
    def save(self):
        session_minutes = (time.time() - self._session_start) / 60
        self.habits.total_interaction_minutes += session_minutes
        self.habits.session_count += 1
        
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        profile_path = self.DATA_DIR / f"{self.user_id}.json"
        
        data = {
            "user_id": self.user_id,
            "last_updated": time.time(),
            "calibration": asdict(self.calibration),
            "preferences": asdict(self.preferences),
            "habits": asdict(self.habits)
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def record_gesture_use(self, gesture_name: str):
        counts = self.habits.gesture_use_counts
        counts[gesture_name] = counts.get(gesture_name, 0) + 1
        sorted_gestures = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        self.habits.most_used_gestures = [g[0] for g in sorted_gestures[:5]]
    
    def record_false_trigger(self):
        self.habits.false_trigger_count += 1
