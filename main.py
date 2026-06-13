import cv2
import time
import queue
import threading
import yaml
import numpy as np
from pathlib import Path
import ctypes

# V4 Imports
from core.tracker.tracker_fusion import TrackerFusion
from core.control.mouse_controller import MouseController
from core.control.click_engine import ClickEngine
from core.control.scroll_engine import ScrollEngine
from core.gesture.gesture_engine import GestureEngine, WindowControlManager, OpenPalmRecognizer
from core.intelligence.tracking_recovery import TrackingRecoveryManager
from core.control.audio_feedback import AudioFeedback

# UI Imports
from ui.tutorial_manager import TutorialManager
from ui.tutorial_illustrator import TutorialIllustrator
from ui.hud_components import HUDComponents
from ui.floating_camera_window import FloatingCameraWindow
from ui.click_test_mode import ClickTestMode
from ui.window_control_test import WindowControlTestMode
from ui.splash_screen import SplashScreen
from ui.theme import WINDOW_WIDTH, WINDOW_HEIGHT, BG_MAIN

def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(config_path, 'r', encoding='cp1252') as f:
            return yaml.safe_load(f)

def tracking_thread(config, tracker, frame_queue, shutdown_event,
                    mouse, recovery_manager, click_engine, scroll_engine, gesture_engine, window_engine, open_palm):
    import traceback
    try:
        cap = cv2.VideoCapture(config['tracking']['camera_index'], cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, config['tracking']['target_fps'])
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while not shutdown_event.is_set():
            ret, frame = cap.read()
            if not ret: continue
            
            now = time.time()
            frame = cv2.flip(frame, 1)
            fused = tracker.update(frame)
            
            control_hand = fused.control_hand
            
            # CORE LOGIC - MOVED OFF MAIN THREAD TO PREVENT WINDOW DRAG FREEZES
            rec_state = recovery_manager.update(control_hand)
            
            # TRACKING PERSISTENCE: Inject the last good hand if we are holding during an occlusion
            if recovery_manager.state == "HOLDING" and recovery_manager.last_good_hand is not None:
                control_hand = recovery_manager.last_good_hand
                fused.control_hand = control_hand
                
            scroll_engine.update(control_hand, control_hand.index_tip, control_hand.middle_tip)
            is_scrolling = scroll_engine.is_scrolling
            
            action_text = ""
            tracker_state_str = "ABSENT"
            click_state = click_engine.state
            
            is_clicking = click_state in ["HELD", "DRAGGING", "CLICKED"]
            
            # Window Control Engine update
            win_msg, win_prog = window_engine.update(control_hand, now, is_clicking, is_scrolling)
            
            # Open Palm Recognizer
            op_data = open_palm.update(control_hand, now)
            
            if rec_state == "TRACKING":
                tracker_state_str = "READY"
                if win_msg:
                    action_text = "WINDOW CONTROL MODE"
                elif op_data["active"]:
                    action_text = "OPEN PALM DETECTED"
                elif is_scrolling:
                    action_text = "Scrolling"
                else:
                    click_action = click_engine.update(control_hand)
                    if click_action:
                        action_text = click_action
                    else:
                        action_text = "Moving"
                    
                    if not win_msg: # Don't move mouse if we are trying to control window
                        mouse.update(control_hand.palm_center, now)
            else:
                if not control_hand.detected:
                    click_engine.update(control_hand)
                    
            click_state = click_engine.state
            
            # Send everything to UI
            ui_state = {
                "action_text": action_text,
                "tracker_state_str": tracker_state_str,
                "is_scrolling": is_scrolling,
                "click_state": click_state,
                "rec_state": rec_state,
                "win_msg": win_msg,
                "win_prog": win_prog,
                "op_data": op_data
            }
            
            if frame_queue.full():
                try: frame_queue.get_nowait()
                except queue.Empty: pass
            try: frame_queue.put_nowait((frame.copy(), fused, ui_state))
            except queue.Full: pass
            
        cap.release()
    except Exception as e:
        print(f"CRITICAL TRACKING THREAD ERROR: {e}")
        traceback.print_exc()

def main():
    print("[AURA] Booting...")
    config = load_config()
    
    cv2.namedWindow("AURA - Workspace", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("AURA - Workspace", WINDOW_WIDTH, WINDOW_HEIGHT)
    
    splash = SplashScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # 1. Run Cinematic Intro V2 (Lightweight, 60 FPS)
    while not splash.is_finished():
        cv2.imshow("AURA - Workspace", splash.render())
        cv2.waitKey(16) # ~60 FPS
        
    # 2. Heavy AI Initialization happens AFTER intro
    mouse = MouseController(config)
    recovery_manager = TrackingRecoveryManager(mouse)
    
    click_engine = ClickEngine(config)
    scroll_engine = ScrollEngine(config)
    gesture_engine = GestureEngine()
    window_engine = WindowControlManager()
    open_palm = OpenPalmRecognizer()
    
    frame_queue = queue.Queue(maxsize=2)
    shutdown_event = threading.Event()
    
    tracker = TrackerFusion(config)
    t_thread = threading.Thread(target=tracking_thread, args=(config, tracker, frame_queue, shutdown_event,
                                                              mouse, recovery_manager, click_engine, scroll_engine, gesture_engine, window_engine, open_palm), daemon=True)
    t_thread.start()
    
    tutorial = TutorialManager(config)
    illustrator = TutorialIllustrator()
    hud_comp = HUDComponents(config)
    
    camera_window = FloatingCameraWindow(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        config
    )
    
    AudioFeedback.play_startup()
    
    main_canvas = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
    
    def key_handler(k):
        if k == 27: return True
        elif k == ord('n') or k == 13: tutorial.next_step()  # 13 is Enter
        elif k == ord('p'): tutorial.previous_step()
        elif k == ord('s'): tutorial.skip()
        elif k == ord('r'): tutorial.restart()
        elif k == ord('c'):
            calib_manager.reset()
            test_screen.reset()
        elif k == ord('v'):
            if test_mode.is_active:
                test_mode.stop()
            else:
                win_test_mode.stop()
                test_mode.start()
        elif k == ord('w'):
            if win_test_mode.is_active:
                win_test_mode.stop()
            else:
                test_mode.stop()
                win_test_mode.start()
        return False
        
    print("[AURA] Workspace Active. Hand is Mouse.")
    
    test_mode = ClickTestMode(WINDOW_WIDTH, WINDOW_HEIGHT)
    win_test_mode = WindowControlTestMode(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Force unfreeze mouse just in case
    if mouse._frozen:
        mouse.unfreeze()
        
    while True:
        try:
            item = frame_queue.get(timeout=0.5)
            if len(item) == 2:
                frame, fused = item
                ui_state = {
                    "action_text": "",
                    "tracker_state_str": "ABSENT",
                    "is_scrolling": False,
                    "click_state": "IDLE",
                    "rec_state": "SEARCHING",
                    "win_msg": "",
                    "win_prog": 0.0
                }
            else:
                frame, fused, ui_state = item
        except queue.Empty:
            k = cv2.waitKey(1) & 0xFF
            if key_handler(k):
                break
            continue
            
        now = time.time()
        main_canvas[:] = BG_MAIN
        
        control_hand = fused.control_hand
        
        try:
            # 1. State from tracking thread
            action_text = ui_state["action_text"]
            tracker_state_str = ui_state["tracker_state_str"]
            is_scrolling = ui_state["is_scrolling"]
            click_state = ui_state["click_state"]
            rec_state = ui_state["rec_state"]
            win_msg = ui_state.get("win_msg", "")
            win_prog = ui_state.get("win_prog", 0.0)
            op_data = ui_state.get("op_data", None)
                    
            # 4. UI Rendering
            if test_mode.is_active:
                test_mode.update(action_text)
                main_canvas = test_mode.render(main_canvas)
            elif win_test_mode.is_active:
                win_test_mode.update(win_msg, win_prog)
                main_canvas = win_test_mode.render(main_canvas)
            elif tutorial.enabled and not tutorial.is_completed:
                tutorial.update(control_hand, mouse.position, click_engine, scroll_engine, "None", fused.hands)
                hud_comp.draw_tutorial_ui(main_canvas, tutorial, illustrator, click_engine, control_hand, mouse.position)
            else:
                hud_comp.draw_dashboard(main_canvas, control_hand, tracker_state_str, is_scrolling, action_text, click_engine.state, fused.overall_confidence, win_prog, op_data)
                
            camera_window.render(frame, control_hand, rec_state, action_text, False)
            cv2.imshow("AURA - Workspace", main_canvas)
        except Exception as e:
            import traceback
            with open("error_log.txt", "w") as f:
                f.write(traceback.format_exc())
            break
        
        k = cv2.waitKey(1) & 0xFF
        if key_handler(k):
            break

    shutdown_event.set()
    t_thread.join(timeout=2.0)
    tracker.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
