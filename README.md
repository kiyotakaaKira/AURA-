<div align="center">

<!-- LOGO / BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a0f,50:1a1a3e,100:4D9EFF&height=200&section=header&text=AURA&fontSize=80&fontColor=ffffff&fontAlignY=38&desc=Adaptive%20User%20Reality%20Assistant&descAlignY=58&descSize=22&descColor=8888AA" width="100%"/>

<br/>

<!-- BADGES ROW 1 -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-00897B?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

<br/>

<!-- BADGES ROW 2 -->
[![Stars](https://img.shields.io/github/stars/kiyotakaaKira/AURA-?style=for-the-badge&color=FFD700&logo=github)](https://github.com/kiyotakaaKira/AURA-/stargazers)
[![Forks](https://img.shields.io/github/forks/kiyotakaaKira/AURA-?style=for-the-badge&color=4D9EFF&logo=github)](https://github.com/kiyotakaaKira/AURA-/network/members)
[![Issues](https://img.shields.io/github/issues/kiyotakaaKira/AURA-?style=for-the-badge&color=FF5555&logo=github)](https://github.com/kiyotakaaKira/AURA-/issues)
[![Last Commit](https://img.shields.io/github/last-commit/kiyotakaaKira/AURA-?style=for-the-badge&color=3DFFC0&logo=git&logoColor=white)](https://github.com/kiyotakaaKira/AURA-/commits)

<br/>

<!-- BADGES ROW 3 -->
![Status](https://img.shields.io/badge/Status-Active%20Development-4D9EFF?style=flat-square)
![Version](https://img.shields.io/badge/Version-0.4.0-3DFFC0?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-8888AA?style=flat-square)
![Research](https://img.shields.io/badge/Category-HCI%20Research-FFB84D?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)

<br/><br/>

<h3>
  <em>Your hand is the mouse. Your intent is the command.</em>
</h3>

<p align="center">
  <b>AURA</b> is an AI-powered Human-Computer Interaction platform that enables touchless, natural computer control<br/>
  through real-time hand gesture recognition — built on commodity hardware, no special equipment required.
</p>

<br/>

**[🚀 Quick Start](#-installation)** &nbsp;·&nbsp; **[📖 Documentation](#-usage)** &nbsp;·&nbsp; **[🗺️ Roadmap](#️-roadmap)** &nbsp;·&nbsp; **[🤝 Contribute](#-contributing)**

<br/>

<!-- DEMO PLACEHOLDER -->
> 📹 **Demo**
>
> ![AURA Demo](assets/demo/aura_demo.gif)
>
> *← Replace with your screen recording. Recommended: 800×500px, 15fps GIF showing cursor control, click, and scroll*

</div>

---

## 📋 Table of Contents

- [✨ Introduction](#-introduction)
- [🔍 Why AURA Exists](#-why-aura-exists)
- [🎯 Problem Statement](#-problem-statement)
- [💡 Solution Overview](#-solution-overview)
- [⚡ Core Features](#-core-features)
- [🏗️ Technical Architecture](#️-technical-architecture)
- [🔧 Technology Stack](#-technology-stack)
- [📦 Installation](#-installation)
- [📁 Project Structure](#-project-structure)
- [🖐️ Usage](#️-usage)
- [🤌 Gesture Reference](#-gesture-reference)
- [📸 Screenshots](#-screenshots)
- [🗺️ Roadmap](#️-roadmap)
- [🔬 Research Applications](#-research-applications)
- [♿ Accessibility Benefits](#-accessibility-benefits)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👤 Author](#-author)

---

## ✨ Introduction

<div align="center">

> *"Every major leap in human-computer interaction — from command lines to graphical interfaces to touchscreens — happened when the barrier between human intent and computer action was reduced. AURA is the next step in that progression."*

</div>

**AURA** (Adaptive User Reality Assistant) is an open-source research project at the intersection of **Computer Vision**, **Artificial Intelligence**, and **Human-Computer Interaction**. It transforms a standard webcam into an intelligent gesture-tracking system capable of replacing traditional mouse input with natural hand movements.

Unlike academic gesture recognition demos that require specialized depth cameras, motion gloves, or controlled environments — AURA runs on a standard laptop webcam in real-time, making advanced HCI research accessible to anyone.

The system is designed around a fundamental principle: **the computer should adapt to the human, not the other way around.**

---

## 🔍 Why AURA Exists

Most gesture control systems fail for the same reason: they force users to memorize commands and adapt their behavior to fit the machine. AURA inverts this relationship.

```
Traditional HCI:    Human → Input Device → Computer
                    (Human adapts to tools)

AURA's Approach:    Human Intent → AI Interpretation → Computer Response
                    (Computer adapts to human)
```

The goal is not to build another virtual mouse. The goal is to explore what human-computer interaction looks like when the interface disappears entirely — when using a computer feels as natural as pointing at something in the physical world.

---

## 🎯 Problem Statement

<table>
<tr>
<td>

### The Five Fundamental Failures of Existing Gesture Systems

**🦾 Fatigue** — Systems require continuous arm elevation. Within 60–90 seconds, shoulder fatigue makes extended use physically painful. This is documented in HCI literature as *Gorilla Arm Syndrome*.

**⚡ Accidental Triggers** — Systems activate on any hand appearance, causing unintended actions during normal desk use. This destroys user trust almost immediately.

**🧠 Rigid Vocabulary** — Users must memorize a fixed set of commands. If they forget, nothing works. The system makes no attempt to adapt.

**🎯 Cursor Instability** — Raw computer vision landmark data is noisy. Without professional-grade smoothing, cursors tremble and jump — making precision tasks impossible.

**🌐 No Context Awareness** — The same gesture does the same thing regardless of what application is active. Users must think in commands, not outcomes.

</td>
</tr>
</table>

---

## 💡 Solution Overview

AURA addresses each failure mode with targeted engineering decisions:

| Problem | AURA's Solution |
|---|---|
| **Fatigue** | Idle detection — cursor freezes when hand is still, user rests naturally, resumes instantly on movement |
| **Accidental Triggers** | Confidence-gated activation with frame confirmation buffer |
| **Rigid Vocabulary** | Context-aware gesture mapping — same gesture, different actions per application |
| **Cursor Instability** | 5-layer smoothing pipeline (Pre-filter → Dead Zone → 1€ Filter → Kalman → Adaptive Sensitivity) |
| **No Context Awareness** | Active application detection with intent resolution engine |

The result is a system that feels natural enough that users stop thinking about the gestures — they just interact.

---

## ⚡ Core Features

<div align="center">

| Feature | Status | Description |
|---|---|---|
| 🖱️ **Cursor Control** | ✅ Active | Index finger tracking with premium smoothing |
| 👆 **Left Click** | ✅ Active | Thumb-to-index contact |
| 🖱️ **Right Click** | ✅ Active | Thumb-to-middle contact |
| 🖱️ **Double Click** | ✅ Active | Double thumb-index contact within 450ms |
| ✊ **Drag & Drop** | ✅ Active | Contact hold → move → release |
| 📜 **Scroll** | ✅ Active | Two-finger mode with momentum physics |
| 💤 **Idle Detection** | ✅ Active | Auto-freeze cursor when hand stationary |
| 🔄 **Tracking Recovery** | ✅ Active | Smooth resume after tracking loss |
| 🎓 **Guided Tutorial** | ✅ Active | Interactive onboarding with live detection |
| 📷 **Floating Camera** | ✅ Active | Draggable, always-on-top camera overlay |
| 🧠 **Gesture Recording** | 🔄 In Progress | Custom gesture capture and labeling pipeline |
| 🤖 **AI Classification** | 🔜 Planned | LSTM/Transformer-based sequence recognition |
| 👁️ **Gaze Tracking** | 🔜 Planned | Eye position as attention confirmation signal |
| 🗣️ **Voice Fusion** | 🔜 Planned | Voice + gesture multimodal interaction |

</div>

---

## 🏗️ Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AURA SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    Thread 2 (Tracking)    ┌───────────────────┐   │
│   │   WEBCAM    │──────────────────────────▶│  PERCEPTION       │  │
│   │  (Sensor)   │                           │  ENGINE           │  │
│   └─────────────┘                           │                   │  │
│                                             │  • MediaPipe Hands│  │
│                                             │  • Face Mesh      │  │
│                                             │  • Motion Vectors │  │
│                                             └────────┬──────────┘  │
│                                                      │             │
│                                             ┌────────▼──────────┐  │
│                                             │  TRACKER FUSION   │  │
│                                             │                   │  │
│                                             │  FusedState {     │  │
│                                             │    hand,          │  │
│                                             │    attention,     │  │
│                                             │    motion         │  │
│                                             │  }                │  │
│                                             └────────┬──────────┘  │
│                                       Thread-safe    │             │
│                                       Queue          │             │
│   ┌───────────────────────────────────────┬──────────▼──────────┐  │
│   │            INTELLIGENCE LAYER         │  Thread 1 (Main)    │  │
│   │                                       │                     │  │
│   │  ┌─────────────┐  ┌───────────────┐  │  ┌───────────────┐   │  │
│   │  │  Presence   │  │    Gesture    │  │  │   Smoothing   │   │  │
│   │  │  Tracker    │  │    Engine     │  │  │   Pipeline    │   │  │
│   │  │             │  │               │  │  │               │   │  │
│   │  │  ABSENT     │  │  • Static     │  │  │  Pre-filter   │   │  │
│   │  │     ↕       │  │    Classifier │  │  │  Dead Zone    │   │  │
│   │  │  READY      │  │  • Temporal   │  │  │  1€ Filter    │   │  │
│   │  │             │  │    Classifier │  │  │  Kalman       │   │  │
│   │  └─────────────┘  └───────────────┘  │  │  Adaptive     │   │  │
│   │                                       │  │  Sensitivity  │  │  │
│   │  ┌─────────────┐  ┌───────────────┐  │  └───────┬───────┘   │  │
│   │  │    Idle     │  │   Context     │  │          │           │  │
│   │  │  Detector   │  │   Detector    │  │          │           │  │
│   │  │             │  │               │  │          ▼           │  │
│   │  │  Fatigue    │  │  Active App   │  │  pyautogui.moveTo()  │  │
│   │  │  Prevention │  │  Detection    │  │                      │  │
│   │  └─────────────┘  └───────────────┘  │                      │  │
│   └───────────────────────────────────────┘                     │  │
│                                                                 │  │
│   ┌──────────────────────────────────────────────────────────┐  │  │
│   │                    CONTROL LAYER                         │  │  │
│   │                                                          │  │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐    │  │  │
│   │   │    MOUSE     │  │    CLICK     │  │   SCROLL    │    │  │  │
│   │   │  CONTROLLER  │  │   ENGINE     │  │   ENGINE    │    │  │  │
│   │   │              │  │              │  │             │    │  │  │
│   │   │  5-layer     │  │  State       │  │  Velocity   │    │  │  │
│   │   │  smoothed    │  │  machine:    │  │  mapping +  │    │  │  │
│   │   │  cursor      │  │  click/drag  │  │  momentum   │    │  │  │
│   │   │  movement    │  │  /dblclick   │  │  physics    │    │  │  │
│   │   └──────────────┘  └──────────────┘  └─────────────┘    │  │  │
│   └──────────────────────────────────────────────────────────┘  │  │
│                                                                 │  │
│   ┌──────────────────────────────────────────────────────────┐  │  │
│   │                     UI LAYER                             │  │  │
│   │                                                          │  │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐    │  │  │
│   │   │     HUD      │  │   FLOATING   │  │  TUTORIAL   │    │  │  │
│   │   │  COMPOSITOR  │  │    CAMERA    │  │   MANAGER   │    │  │  │
│   │   └──────────────┘  └──────────────┘  └─────────────┘    │  │  │
│   └──────────────────────────────────────────────────────────┘  │  │
└────────────────────────────────────────────────────────────────────┘
```

### The 5-Layer Cursor Smoothing Pipeline

```
Raw MediaPipe Landmark Position (noisy, ±5px jitter)
          │
          ▼
┌─────────────────────┐
│  Stage 0            │  EMA pre-filter on raw landmark (α=0.6)
│  Landmark           │  Reduces MediaPipe's inherent detection noise
│  Pre-Filter         │  before any coordinate transformation
└──────────┬──────────┘
           │
           ▼  (Map to screen coordinates via calibrated interaction zone)
           │
┌─────────────────────┐
│  Stage 1            │  Suppress movements < 4px (screen space)
│  Dead Zone          │  Eliminates physiological micro-tremor
│  Filter             │  Invisible to user, kills resting jitter
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 2            │  Adaptive cutoff frequency based on speed
│  One Euro           │  Slow motion: heavy smoothing → no jitter at rest
│  Filter (1€)        │  Fast motion: light smoothing → immediate response
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 3            │  Models cursor as position + velocity state
│  Kalman             │  Prevents physically impossible direction changes
│  Filter             │  Makes trajectory feel "weighted" and natural
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 4            │  Non-linear velocity → cursor speed mapping
│  Adaptive           │  Precision zone (slow) + Fast zone (speed)
│  Sensitivity        │  Mirrors premium gaming mouse acceleration
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 5            │  Linear extrapolation from last 3 positions
│  Motion             │  Blends 75% current + 25% predicted next position
│  Prediction         │  Reduces perceived latency without actual latency
└──────────┬──────────┘
           │
           ▼
   pyautogui.moveTo()
   (Smooth, stable, natural cursor)
```

---

## 🔧 Technology Stack

<div align="center">

| Layer | Technology | Purpose |
|---|---|---|
| **Computer Vision** | [MediaPipe Hands](https://mediapipe.dev) | 21-point hand landmark detection at 30-60fps |
| **Image Processing** | [OpenCV 4.8+](https://opencv.org) | Camera capture, frame processing, UI rendering |
| **System Control** | [PyAutoGUI](https://pyautogui.readthedocs.io) | Cross-platform cursor movement and click simulation |
| **Input Events** | [pynput](https://pynput.readthedocs.io) | Low-level keyboard and mouse event injection |
| **Signal Processing** | [SciPy](https://scipy.org) | Filter implementations and signal analysis |
| **Linear Algebra** | [NumPy](https://numpy.org) | Vectorized landmark processing and filter math |
| **State Tracking** | [filterpy](https://filterpy.readthedocs.io) | Kalman filter library reference implementation |
| **Volume Control** | [pycaw](https://github.com/AndreMiras/pycaw) (Windows) | System audio control via Windows Core Audio |
| **Configuration** | [PyYAML](https://pyyaml.org) | Human-readable configuration management |
| **Language** | Python 3.10+ | Primary implementation language |

</div>

### Why These Choices?

**MediaPipe over custom CNN:** MediaPipe's hand model achieves <15ms inference on CPU, making it the only viable choice for real-time cursor control on commodity hardware. Custom models trained from scratch cannot match this latency without dedicated GPU acceleration.

**One Euro Filter over Kalman-only:** The 1€ filter's adaptive cutoff frequency is superior to fixed-parameter Kalman filters for cursor tracking because it independently optimizes smoothing for both resting (high smoothing) and moving (low smoothing) states. We use both in sequence — 1€ for noise, Kalman for trajectory consistency.

**OpenCV for UI:** Rather than adding a GUI framework dependency (Tkinter, PyQt), OpenCV's `imshow` is already required for camera processing. Building the HUD directly in OpenCV keeps dependencies minimal and latency low.

---

## 📦 Installation

### Prerequisites

```
Python 3.10 or higher
Webcam (built-in or USB)
Windows 10+ / macOS 11+ / Ubuntu 20.04+
```

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/kiyotakaaKira/AURA-.git
cd AURA-

# 2. Create virtual environment (recommended)
python -m venv aura-env

# Activate — Windows:
aura-env\Scripts\activate

# Activate — macOS/Linux:
source aura-env/bin/activate

# 3. Run the installer (handles all dependencies automatically)
python setup.py

# 4. Launch AURA
python main.py
```

### Manual Installation

```bash
# Install core dependencies
pip install mediapipe>=0.10.0 opencv-python>=4.8.0 pyautogui>=0.9.54
pip install numpy>=1.24.0 pynput>=1.7.6 PyYAML>=6.0
pip install scipy>=1.11.0 filterpy>=1.4.5

# Windows only (system volume control)
pip install pycaw>=20181228 pywin32>=306

# macOS only (window detection)
pip install pyobjc-framework-Quartz>=9.0
```

### Verify Installation

```bash
python -c "import mediapipe, cv2, pyautogui, numpy; print('All dependencies OK')"
```

> [!NOTE]
> If you see a camera permission prompt on macOS, grant access in System Preferences → Privacy & Security → Camera.

> [!TIP]
> For best results, use a webcam with at least 720p resolution in a well-lit environment. Avoid strong backlighting behind your hand.

---

## 📁 Project Structure

```
AURA/
│
├── main.py                          # Entry point & main loop orchestrator
├── config.yaml                      # All tuneable parameters (no hardcoded values)
├── setup.py                         # One-command dependency installer
├── requirements.txt                 # Pinned dependency versions
│
├── core/
│   ├── tracker/
│   │   ├── hand_tracker.py          # MediaPipe wrapper → clean TrackingResult dataclass
│   │   ├── face_tracker.py          # Face mesh, eye tracking, attention detection
│   │   ├── motion_analyzer.py       # Velocity, acceleration, jerk, trajectory analysis
│   │   └── tracker_fusion.py        # Combines all signals → unified FusedState
│   │
│   ├── gesture/
│   │   ├── gesture_engine.py        # Two-stage classifier (static + temporal)
│   │   ├── gesture_recorder.py      # Custom gesture capture pipeline (10 samples/gesture)
│   │   ├── gesture_library.py       # Load / save / manage gesture definitions
│   │   ├── gesture_definitions.py   # Built-in gesture rules as declarative data
│   │   └── sequence_buffer.py       # Ring buffer — ready for LSTM/Transformer drop-in
│   │
│   ├── control/
│   │   ├── mouse_controller.py      # Full 5-layer smoothing pipeline + cursor movement
│   │   ├── click_engine.py          # State machine: idle → pending → click/drag/drop
│   │   ├── scroll_engine.py         # Two-finger scroll with momentum physics
│   │   └── volume_controller.py     # Cross-platform volume (pycaw/osascript/pactl)
│   │
│   ├── intelligence/
│   │   ├── activation_manager.py    # Hand presence tracking (replaces gesture activation)
│   │   ├── idle_detector.py         # Fatigue prevention — freeze on stationary hand
│   │   ├── tracking_recovery.py     # Loss detection, freeze, smooth recovery
│   │   ├── context_detector.py      # Active app detection → context key
│   │   ├── intent_engine.py         # Context + gesture → intent → action
│   │   └── user_model.py            # Persistent preferences, calibration, habits
│   │
│   ├── smoothing/
│   │   ├── one_euro_filter.py       # 1€ adaptive filter (Casiez et al., CHI 2012)
│   │   ├── kalman_filter.py         # 2D Kalman filter for trajectory smoothing
│   │   ├── exponential_smoother.py  # EMA for volume and secondary signals
│   │   ├── dead_zone.py             # Micro-tremor suppression
│   │   └── adaptive_sensitivity.py  # Non-linear velocity → cursor speed mapping
│   │
│   └── ai/
│       ├── gesture_trainer.py       # Interface stub (LSTM/TCN architecture documented)
│       └── model_manager.py         # Load / save / version trained models
│
├── ui/
│   ├── hud.py                       # Main HUD compositor (owns OpenCV window)
│   ├── hud_components.py            # Status bar, action pill, volume bar, chips
│   ├── camera_renderer.py           # Camera feed with premium overlays
│   ├── gesture_visualizer.py        # Skeleton, fingertip dots, wrist ring, pinch line
│   ├── animation_engine.py          # Time-based state transition animations
│   ├── tutorial_manager.py          # Step-by-step onboarding with live detection
│   ├── tutorial_illustrator.py      # Animated hand drawings (OpenCV procedural)
│   ├── floating_camera_window.py    # Draggable always-on-top camera overlay
│   └── theme.py                     # All colors, fonts, dimensions as constants
│
├── data/
│   ├── gestures/                    # Recorded gesture samples (JSON per gesture)
│   ├── user_history/                # Session interaction logs
│   ├── models/                      # Trained gesture model files (Phase 2)
│   └── profiles/                    # Per-user calibration and preference files
│
├── assets/
│   ├── fonts/                       # JetBrains Mono for HUD text
│   ├── sounds/                      # Optional: subtle audio feedback
│   └── demo/                        # Screenshots, GIFs, demo videos
│
└── tests/
    ├── test_smoothing.py             # Filter noise reduction verification
    ├── test_activation.py            # State machine transition tests
    ├── test_click_engine.py          # Click / double-click / drag state tests
    ├── test_gesture_library.py       # Save / load round-trip tests
    └── test_user_model.py            # Persistence and preference tests
```

---

## 🖐️ Usage

### Starting AURA

```bash
python main.py
```

On first launch, AURA opens a guided tutorial that walks through all six core gestures interactively. The tutorial advances only when each gesture is successfully detected — not on a timer.

### Configuration

All behavior is tunable via `config.yaml`. No code changes required for common adjustments:

```yaml
# Cursor sensitivity (default 1.0, range 0.3–3.0)
cursor:
  sensitivity: 1.0
  interaction_zone: [0.20, 0.80, 0.10, 0.80]

# Smoothing (lower min_cutoff = smoother at rest)
smoothing:
  one_euro:
    min_cutoff: 1.0    # range 0.3–3.0
    beta: 0.007        # range 0.0–0.3

# Click timing
gestures:
  drag_hold_ms: 400
  double_click_window_ms: 450
```

### Keyboard Shortcuts (While Running)

| Key | Action |
|---|---|
| `Q` or `ESC` | Quit AURA |
| `R` | Record new custom gesture |
| `C` | Recalibrate interaction zone |
| `T` | Reopen tutorial |
| `D` | Toggle debug overlay |

---

## 🤌 Gesture Reference

<div align="center">

### Complete Gesture Vocabulary

| Gesture | Hand Shape | Thumb | Action |
|---|---|---|---|
| **Move Cursor** | ☝️ Index finger only raised | Free | Cursor tracks index fingertip |
| **Left Click** | ☝️ Index finger raised | Touches index tip | Single click |
| **Double Click** | ☝️ Index finger raised | Touch → release → touch (< 450ms) | Double click |
| **Drag** | ☝️ Index finger raised | Touches index (hold 400ms) then move | Mouse drag |
| **Drop** | ☝️ Index finger raised | Release contact | Mouse release |
| **Right Click** | ☝️ Index finger raised | Touches **middle** finger tip | Right click |
| **Scroll** | ✌️ Index + Middle raised | Free | Move hand up/down to scroll |

### Gesture Priority Order (Important)

```
Priority 1 → Right Click Check  (thumb-to-middle distance)
Priority 2 → Left Click Check   (thumb-to-index distance)
Priority 3 → Scroll Mode        (two fingers, no thumb contact)
Priority 4 → Cursor Mode        (index only)
Priority 5 → No Action          (any other configuration)
```

> [!IMPORTANT]
> The right-click check must run before the left-click check in code. The thumb is involved in both gestures — checking left-click first causes right-click attempts to misfire as left-clicks.

</div>

---


## 🗺️ Roadmap

```
████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░  CURRENT: V0.4.0
```

### ✅ Phase 1 — Foundation (Complete)
- [x] Real-time hand tracking via MediaPipe
- [x] 5-layer cursor smoothing pipeline (1€ + Kalman + Dead Zone + Adaptive Sensitivity + Prediction)
- [x] Left click, double click, drag & drop, right click
- [x] Two-finger scroll with momentum
- [x] Idle detection for fatigue prevention
- [x] Tracking loss recovery (freeze → smooth resume)
- [x] Screen-position-based hand identity (no left/right confusion)
- [x] Floating camera overlay window
- [x] Interactive tutorial with live gesture detection
- [x] User preference persistence
- [x] Cross-platform volume control

### 🔄 Phase 2 — Intelligence (In Progress)
- [ ] Custom gesture recording studio (10 samples/gesture)
- [ ] LSTM-based temporal gesture sequence classifier
- [ ] Context-aware action mapping (VS Code, Chrome, Spotify, etc.)
- [ ] Gaze tracking as attention confirmation signal
- [ ] Multi-monitor support
- [ ] Automated calibration with visual feedback

### 🔜 Phase 3 — Personalization (Planned)
- [ ] Temporal CNN gesture model (faster inference than LSTM)
- [ ] Per-user model fine-tuning from recorded samples
- [ ] Intent prediction engine (context + history → predicted action)
- [ ] Reinforcement learning from correction signals
- [ ] Air typing with word prediction
- [ ] Workflow macro recording (gesture → multi-step automation)

### 🌟 Phase 4 — Platform (Future Vision)
- [ ] Full system-wide OS gesture layer
- [ ] SDK for third-party gesture integrations
- [ ] AURA Dashboard web application (analytics, training, config)
- [ ] Cloud sync of gesture libraries and user models
- [ ] Voice + gesture multimodal fusion
- [ ] Vision Transformer-based gesture recognition

---

## 🔬 Research Applications

AURA is designed as an open research platform. The modular architecture makes it suitable for academic investigation across several domains:

<details>
<summary><b>👁️ HCI Research</b></summary>
<br/>

- Comparative studies of gesture vocabulary learnability
- Measurement of gesture-based vs. traditional mouse fatigue over extended sessions
- Investigation of activation barriers and their impact on first-use adoption
- Design of minimal gesture vocabularies sufficient for professional workflows

</details>

<details>
<summary><b>🤖 Computer Vision Research</b></summary>
<br/>

- Real-time landmark stabilization and noise reduction techniques
- Comparative evaluation of cursor smoothing algorithms (1€ vs Kalman vs learned filters)
- Gesture sequence classification on constrained edge-hardware
- Temporal segmentation of continuous hand motion into discrete gesture events

</details>

<details>
<summary><b>🧠 AI / Machine Learning Research</b></summary>
<br/>

- Few-shot gesture learning from small user-specific samples (10 samples/gesture)
- Transfer learning from large gesture datasets to personal interaction styles
- Online adaptation and reinforcement learning from implicit correction signals
- Architecture comparison: LSTM vs Temporal CNN vs Transformer for sub-10ms gesture inference

</details>

<details>
<summary><b>🏥 Assistive Technology Research</b></summary>
<br/>

- Non-contact input for sterile medical environments (surgical suites, ICUs)
- Alternative input for users with motor disabilities affecting traditional peripherals
- Reduced-precision gesture recognition adapted for users with tremor conditions
- Integration with eye-gaze systems for users with severe motor limitations

</details>

---

## ♿ Accessibility Benefits

AURA has meaningful potential for users who face challenges with traditional input devices:

**Motor Accessibility**
- Enables computer interaction without touching physical devices
- Configurable sensitivity accommodates users with limited fine motor control
- Idle detection prevents system from penalizing users with slower or unsteady motion

**Environmental Applications**
- Sterile control in medical settings (operating rooms, cleanrooms, laboratories)
- Touchless interaction in high-hygiene environments (food processing, pharmaceutical)
- Remote/field environments where keyboards and mice are impractical

**Ergonomic Benefits**
- Eliminates repetitive strain from mouse and keyboard use during regular breaks
- Natural motion patterns reduce potential for cursor-control related fatigue
- Configurable gesture vocabulary allows adaptation to existing motion capabilities

> [!NOTE]
> AURA is a research prototype. It is not currently certified as an assistive technology for medical or accessibility-critical applications. Research contributions in adaptive gesture recognition for accessibility use cases are especially welcome.

---

## 🤝 Contributing

Contributions are what make open-source research meaningful. AURA welcomes contributions of all kinds.

### Ways to Contribute

| Type | Examples |
|---|---|
| **Bug Reports** | Cursor instability, gesture misdetection, platform-specific crashes |
| **Feature Implementation** | Items from the Phase 2/3 roadmap |
| **Research** | Benchmark comparisons, algorithm improvements, dataset collection |
| **Documentation** | Setup guides, video tutorials, gesture reference improvements |
| **Testing** | Cross-platform verification, edge-case gesture testing |
| **Design** | HUD improvements, tutorial illustrations, demo materials |

### Getting Started

```bash
# 1. Fork the repository
# (Click "Fork" button on GitHub)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/AURA-.git
cd AURA-

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes
# Follow existing module structure and naming conventions

# 5. Run the test suite
python -m pytest tests/ -v

# 6. Commit with a clear message
git commit -m "feat: add temporal gesture classifier using LSTM"

# 7. Push and open a Pull Request
git push origin feature/your-feature-name
```

### Contribution Guidelines

- **One responsibility per module.** No file should import from more than 3 others.
- **No magic numbers.** All tuneable values go in `config.yaml`.
- **Tests for new filters.** Any new smoothing algorithm needs a noise-reduction test.
- **Clear PR descriptions.** Explain what the change does, why it was needed, and how to verify it.
- **Respect the scope.** V4 core is: cursor, click, scroll. Feature additions should have a clear use case.

### Commit Convention

```
feat:     New feature
fix:      Bug fix
perf:     Performance improvement
docs:     Documentation changes
test:     Adding or fixing tests
refactor: Code restructuring without behavior change
```

---

## 📄 License

```
MIT License

Copyright (c) 2024 kiyotakaaKira

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See [LICENSE](LICENSE) for full text.

---

## 👤 Author

<div align="center">

<img src="https://github.com/kiyotakaaKira.png" width="120px" style="border-radius: 50%"/>

### kiyotakaaKira

*Building the next generation of human-computer interaction*

[![GitHub](https://img.shields.io/badge/GitHub-kiyotakaaKira-181717?style=for-the-badge&logo=github)](https://github.com/kiyotakaaKira)

</div>

---

<div align="center">

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kiyotakaaKira/AURA-&type=Date)](https://star-history.com/#kiyotakaaKira/AURA-&Date)

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:4D9EFF,50:1a1a3e,100:0a0a0f&height=120&section=footer" width="100%"/>

**If AURA helped you or inspired your work, consider giving it a ⭐**

*AURA — Adaptive User Reality Assistant*  
*Built for humans. Not for demos.*

</div>
