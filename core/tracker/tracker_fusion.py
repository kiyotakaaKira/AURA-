import time
from dataclasses import dataclass
from .hand_tracker import HandTracker, TrackingResult
from .face_tracker import FaceTracker, AttentionState
from .motion_analyzer import MotionAnalyzer, MotionState
import numpy as np
from typing import List, Optional

@dataclass
class FusedState:
    control_hand: TrackingResult
    hands: List[TrackingResult]
    attention: AttentionState
    motion: MotionState
    overall_confidence: float
    interaction_quality: float
    timestamp: float
    frame_index: int

class TrackerFusion:
    def __init__(self, config: dict):
        self.hand_tracker = HandTracker(config.get('tracking', {}))
        self.face_tracker = FaceTracker(config.get('tracking', {}))
        self.motion_analyzer = MotionAnalyzer()
        self.frame_index = 0
        
    def update(self, frame: np.ndarray) -> FusedState:
        self.frame_index += 1
        timestamp = time.time()
        
        hands = self.hand_tracker.process(frame)
        attention = self.face_tracker.process(frame)
        
        empty_hand = TrackingResult(
            detected=False, confidence=0.0, handedness="Unknown",
            landmarks=[], normalized_landmarks=[], fingers_extended=[],
            pinch_distance=0.0, palm_normal=(0,0,0), palm_center=(0,0),
            wrist=(0,0,0), thumb_tip=(0,0,0), index_tip=(0,0,0),
            middle_tip=(0,0,0), ring_tip=(0,0,0), pinky_tip=(0,0,0), all_tips=[],
            palm_width=1.0
        )
        
        control_hand = self.hand_tracker.get_control_hand(hands)
        if not control_hand:
            control_hand = empty_hand
            
        index_pos = None
        if control_hand.detected:
            index_pos = (control_hand.index_tip[0], control_hand.index_tip[1])
            
        motion = self.motion_analyzer.update(index_pos)
        
        interaction_quality = 0.0
        if control_hand.detected:
            interaction_quality += control_hand.confidence * 0.5
            interaction_quality += attention.attention_confidence * 0.3
            interaction_quality += (1.0 if not motion.is_tremor else 0.0) * 0.2
            
        overall_confidence = (control_hand.confidence * 0.7) + (attention.attention_confidence * 0.3)
        if not control_hand.detected:
            overall_confidence = 0.0
            
        return FusedState(
            control_hand=control_hand,
            hands=hands,
            attention=attention,
            motion=motion,
            overall_confidence=overall_confidence,
            interaction_quality=interaction_quality,
            timestamp=timestamp,
            frame_index=self.frame_index
        )
        
    def release(self):
        self.hand_tracker.release()
        self.face_tracker.release()
