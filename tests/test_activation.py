import pytest
from core.intelligence.activation_manager import ActivationManager, ActivationState
from core.tracker.tracker_fusion import FusedState
from core.tracker.hand_tracker import TrackingResult
from core.tracker.face_tracker import AttentionState
from core.tracker.motion_analyzer import MotionState

def make_fused_open_palm() -> FusedState:
    """Create FusedState with open palm gesture."""
    hand = TrackingResult(
        detected=True, confidence=0.95, handedness="Right",
        fingers_extended=[True, True, True, True, True],
        pinch_distance=0.2,
        wrist=(0.5, 0.5),
        index_tip=(0.5, 0.4),
        thumb_tip=(0.4, 0.5),
        middle_tip=(0.5, 0.3),
        landmarks=[(0,0)]*21,
        normalized_landmarks=[(0,0)]*21,
        all_tips=[(0,0)]*5
    )
    attention = AttentionState(looking_at_screen=True, attention_confidence=0.9, euler_angles=(0,0,0), eye_aspect_ratio=0.3)
    motion = MotionState(
        raw_position=(0.5, 0.5), velocity=(0,0), speed=0, acceleration=(0,0), jerk=0,
        trajectory_angle=0, is_tremor=False, motion_direction="NONE", swipe_confidence=0
    )
    return FusedState(hand, attention, motion, 0.9, 0.9, 0.0, 1)

def test_activation_manager():
    config = {'gestures': {'activation_hold_ms': 500, 'confirmation_frames': 5}}
    manager = ActivationManager(config)
    assert manager.state == ActivationState.SLEEP
    
    fused = make_fused_open_palm()
    
    for _ in range(5):
        manager.update(fused)
        
    assert manager.state == ActivationState.ACTIVATING
