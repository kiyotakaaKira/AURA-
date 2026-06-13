# V4 Color System

# Backgrounds
BG_MAIN         = (15, 10, 10)      # Near-black (OpenCV is BGR)
BG_PANEL        = (24, 18, 18)      # Card background
BG_ELEVATED     = (34, 26, 26)      # Hovered / elevated element
BG_SURFACE      = (34, 26, 26)      # Surface alias

# Text
TEXT_PRIMARY    = (248, 242, 242)   # Off-white
TEXT_SECONDARY  = (160, 140, 140)   # Muted
TEXT_MUTED      = (95, 80, 80)      # Very muted

# Accent Colors (BGR for OpenCV)
GREEN           = (80, 230, 120)    # Active, success, tracking
BLUE            = (255, 165, 80)    # Information, cursor
AMBER           = (60, 180, 255)    # Warning, idle
RED             = (80, 80, 230)     # Error
WHITE           = (255, 255, 255)   # Highlights

# Borders
BORDER          = (45, 35, 35)      # Subtle border
BORDER_DEFAULT  = BORDER

# Skeleton overlay colors
SKELETON_COLOR  = (160, 110, 60)    # Blue-ish
TIP_COLOR       = (200, 140, 80)    # Fingertip dots
ACTIVE_TIP      = (255, 200, 100)   # Index finger when active
DRAG_TIP        = (80, 140, 255)    # Orange when dragging
PINCH_SAFE      = (100, 100, 100)   # Thumb-index line when far
PINCH_CLOSE     = (80, 200, 80)     # Line when near threshold
PINCH_ACTIVE    = (100, 255, 100)   # Line when touching

import cv2
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_LG = 0.8
FONT_SCALE_MD = 0.6
FONT_SCALE_SM = 0.4
FONT_WEIGHT_BOLD = 2

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
