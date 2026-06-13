import json
from pathlib import Path

class GestureLibrary:
    def __init__(self):
        self.base_dir = Path("data/gestures")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def save_gesture(self, gesture_name: str, gesture_data: dict):
        gesture_dir = self.base_dir / gesture_name
        gesture_dir.mkdir(parents=True, exist_ok=True)
        samples_file = gesture_dir / "samples.json"
        
        existing_data = []
        if samples_file.exists():
            try:
                with open(samples_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f).get("samples", [])
            except:
                pass
                
        existing_data.extend(gesture_data["samples"])
        gesture_data["samples"] = existing_data
        gesture_data["sample_count"] = len(existing_data)
        
        with open(samples_file, 'w', encoding='utf-8') as f:
            json.dump(gesture_data, f, indent=2)
