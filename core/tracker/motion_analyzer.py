from collections import deque
import math
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class MotionState:
    raw_position: Optional[Tuple[float, float]]       # Current raw normalized position
    velocity: Tuple[float, float]           # pixels/frame velocity vector
    speed: float                             # Scalar speed magnitude
    acceleration: Tuple[float, float]       # Change in velocity
    jerk: float                              # Change in acceleration magnitude
    trajectory_angle: float                  # Angle of motion in degrees (0-360)
    is_tremor: bool                          # True if jerk > TREMOR_JERK_THRESHOLD
    motion_direction: str                    # "UP" | "DOWN" | "LEFT" | "RIGHT" | "NONE"
    swipe_confidence: float                  # Confidence this is an intentional swipe

class MotionAnalyzer:
    def __init__(self):
        self._position_history = deque(maxlen=10)
        self._velocity_history = deque(maxlen=5)
        self._accel_history = deque(maxlen=5)
        
        self.TREMOR_JERK_THRESHOLD = 0.01
        self.LOW_SPEED_THRESHOLD = 0.005
    
    def update(self, raw_position: Optional[Tuple[float, float]]) -> MotionState:
        if raw_position is None:
            self._position_history.clear()
            self._velocity_history.clear()
            self._accel_history.clear()
            return MotionState(
                raw_position=None, velocity=(0.0, 0.0), speed=0.0,
                acceleration=(0.0, 0.0), jerk=0.0, trajectory_angle=0.0,
                is_tremor=False, motion_direction="NONE", swipe_confidence=0.0
            )
            
        self._position_history.append(raw_position)
        
        velocity = (0.0, 0.0)
        if len(self._position_history) >= 2:
            prev = self._position_history[-2]
            curr = self._position_history[-1]
            velocity = (curr[0] - prev[0], curr[1] - prev[1])
            
        self._velocity_history.append(velocity)
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
        
        acceleration = (0.0, 0.0)
        if len(self._velocity_history) >= 2:
            prev_v = self._velocity_history[-2]
            curr_v = self._velocity_history[-1]
            acceleration = (curr_v[0] - prev_v[0], curr_v[1] - prev_v[1])
            
        self._accel_history.append(acceleration)
        accel_mag = math.sqrt(acceleration[0]**2 + acceleration[1]**2)
        
        jerk = 0.0
        if len(self._accel_history) >= 2:
            prev_a_mag = math.sqrt(self._accel_history[-2][0]**2 + self._accel_history[-2][1]**2)
            curr_a_mag = accel_mag
            jerk = abs(curr_a_mag - prev_a_mag)
            
        is_tremor = jerk > self.TREMOR_JERK_THRESHOLD and speed < self.LOW_SPEED_THRESHOLD
        
        trajectory_angle = math.degrees(math.atan2(velocity[1], velocity[0])) % 360
        
        # Detect direction
        motion_direction = "NONE"
        if speed > self.LOW_SPEED_THRESHOLD:
            if 45 <= trajectory_angle < 135:
                motion_direction = "DOWN"
            elif 135 <= trajectory_angle < 225:
                motion_direction = "LEFT"
            elif 225 <= trajectory_angle < 315:
                motion_direction = "UP"
            else:
                motion_direction = "RIGHT"
                
        # Swipe confidence (sustained direction over last 5 frames)
        swipe_confidence = 0.0
        if len(self._velocity_history) == 5 and speed > self.LOW_SPEED_THRESHOLD:
            dirs = []
            for v in self._velocity_history:
                s = math.sqrt(v[0]**2 + v[1]**2)
                if s > self.LOW_SPEED_THRESHOLD:
                    angle = math.degrees(math.atan2(v[1], v[0])) % 360
                    if 45 <= angle < 135: dirs.append("DOWN")
                    elif 135 <= angle < 225: dirs.append("LEFT")
                    elif 225 <= angle < 315: dirs.append("UP")
                    else: dirs.append("RIGHT")
            
            if len(dirs) == 5 and all(d == dirs[0] for d in dirs):
                swipe_confidence = min(1.0, speed / 0.05)
        
        return MotionState(
            raw_position=raw_position,
            velocity=velocity,
            speed=speed,
            acceleration=acceleration,
            jerk=jerk,
            trajectory_angle=trajectory_angle,
            is_tremor=is_tremor,
            motion_direction=motion_direction,
            swipe_confidence=swipe_confidence
        )
