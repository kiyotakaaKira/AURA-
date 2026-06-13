from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GestureRule:
    name: str
    display_name: str
    
    # Finger extension requirements: [thumb, index, middle, ring, pinky]
    # True = must be extended, False = must be closed, None = don't care
    fingers_required: List[Optional[bool]]
    
    # Distance constraints
    pinch_distance_max: Optional[float] = None
    pinch_distance_min: Optional[float] = None
    
    # Hold duration
    requires_hold_ms: Optional[int] = None
    
    # Motion requirements
    requires_motion: Optional[str] = None
    min_swipe_speed: float = 0.0
    
    # Classification
    is_static: bool = True
    confidence_threshold: float = 0.85
    
    # Description for UI
    description: str = ""
    icon: str = ""

# Built-in gesture library
BUILT_IN_GESTURES = [
    GestureRule(
        name="open_palm",
        display_name="Open Palm",
        fingers_required=[True, True, True, True, True],
        requires_hold_ms=500,
        description="Activates AURA",
        icon="✋"
    ),
    GestureRule(
        name="closed_fist",
        display_name="Closed Fist",
        fingers_required=[False, False, False, False, False],
        requires_hold_ms=500,
        description="Deactivates AURA",
        icon="✊"
    ),
    GestureRule(
        name="index_point",
        display_name="Index Point",
        fingers_required=[None, True, False, False, False],
        description="Cursor control",
        icon="☝️"
    ),
    GestureRule(
        name="pinch",
        display_name="Pinch",
        fingers_required=[None, True, False, False, False],
        pinch_distance_max=0.04,
        description="Left click",
        icon="🤌"
    ),
    GestureRule(
        name="two_fingers",
        display_name="Two Fingers",
        fingers_required=[None, True, True, False, False],
        description="Scroll mode",
        icon="✌️"
    ),
    GestureRule(
        name="thumb_span",
        display_name="Thumb Span",
        fingers_required=[True, True, False, False, False],
        pinch_distance_min=0.05,
        description="Volume control",
        icon="👌"
    ),
    GestureRule(
        name="swipe_right",
        display_name="Swipe Right",
        fingers_required=[False, False, False, False, False],
        is_static=False,
        requires_motion="RIGHT",
        min_swipe_speed=0.08,
        description="Next (context aware)",
        icon="→"
    ),
    GestureRule(
        name="swipe_left",
        display_name="Swipe Left",
        fingers_required=[False, False, False, False, False],
        is_static=False,
        requires_motion="LEFT",
        min_swipe_speed=0.08,
        description="Previous (context aware)",
        icon="←"
    ),
    GestureRule(
        name="four_fingers_down",
        display_name="Four Down",
        fingers_required=[False, True, True, True, True],
        is_static=False,
        requires_motion="DOWN",
        min_swipe_speed=0.06,
        description="Minimize window",
        icon="↓"
    ),
    GestureRule(
        name="spread",
        display_name="Spread",
        fingers_required=[True, True, True, True, True],
        pinch_distance_min=0.15,
        description="Show desktop",
        icon="🖐"
    ),
]
