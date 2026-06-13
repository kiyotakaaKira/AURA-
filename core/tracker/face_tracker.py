import cv2
import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AttentionState:
    face_detected: bool
    attention_confidence: float      
    left_eye_open: float             
    right_eye_open: float
    blink_detected: bool             
    gaze_direction: Tuple[float, float]   
    looking_at_screen: bool               
    head_yaw: float                  
    head_pitch: float                
    head_roll: float                 

class DummyLandmarkList:
    def __init__(self, lms):
        self.landmark = lms

class FaceTracker:
    def __init__(self, config: dict):
        base_options = python.BaseOptions(model_asset_path='data/models/face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=True
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        self.was_blinking = False
        
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             
            (0.0, -330.0, -65.0),        
            (-225.0, 170.0, -135.0),     
            (225.0, 170.0, -135.0),      
            (-150.0, -150.0, -125.0),    
            (150.0, -150.0, -125.0)      
        ], dtype=np.float64)
        
    def process(self, frame: np.ndarray) -> AttentionState:
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.detector.detect(mp_image)
        
        if not results.face_landmarks:
            self.was_blinking = False
            return AttentionState(
                face_detected=False, attention_confidence=0.0,
                left_eye_open=0.0, right_eye_open=0.0, blink_detected=False,
                gaze_direction=(0.0, 0.0), looking_at_screen=False,
                head_yaw=0.0, head_pitch=0.0, head_roll=0.0
            )
            
        landmarks = DummyLandmarkList(results.face_landmarks[0])
        
        left_ear = self._compute_ear(landmarks, [33, 160, 158, 133, 153, 144], w, h)
        right_ear = self._compute_ear(landmarks, [362, 385, 387, 263, 373, 380], w, h)
        
        is_blinking = left_ear < 0.2 and right_ear < 0.2
        blink_detected = is_blinking and not self.was_blinking
        self.was_blinking = is_blinking
        
        pitch, yaw, roll = self._estimate_head_pose(landmarks, w, h)
        
        looking_at_screen = abs(yaw) < 30 and abs(pitch) < 25
        
        both_eyes_open = 1.0 if not is_blinking else 0.0
        attention_confidence = (0.3 * 1.0) + (0.5 * float(looking_at_screen)) + (0.2 * both_eyes_open)
        
        gaze_direction = self._approximate_gaze(landmarks, w, h)
        
        return AttentionState(
            face_detected=True,
            attention_confidence=attention_confidence,
            left_eye_open=left_ear,
            right_eye_open=right_ear,
            blink_detected=blink_detected,
            gaze_direction=gaze_direction,
            looking_at_screen=looking_at_screen,
            head_yaw=yaw,
            head_pitch=pitch,
            head_roll=roll
        )
        
    def _compute_ear(self, landmarks, indices, w, h) -> float:
        pts = [np.array([landmarks.landmark[i].x * w, landmarks.landmark[i].y * h]) for i in indices]
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        h1 = np.linalg.norm(pts[0] - pts[3])
        if h1 == 0:
            return 0.0
        return (v1 + v2) / (2.0 * h1)
        
    def _estimate_head_pose(self, landmarks, w, h) -> Tuple[float, float, float]:
        selected_indices = [1, 152, 33, 263, 61, 291]
        image_points = np.array([
            (landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h)
            for idx in selected_indices
        ], dtype=np.float64)
        
        focal_length = 1.0 * w
        cam_matrix = np.array([
            [focal_length, 0, w / 2],
            [0, focal_length, h / 2],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        
        success, rot_vec, trans_vec = cv2.solvePnP(self.model_points, image_points, cam_matrix, dist_matrix, flags=cv2.SOLVEPNP_ITERATIVE)
        if not success:
            return 0.0, 0.0, 0.0
            
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        
        pitch = angles[0]
        yaw = angles[1]
        roll = angles[2]
        
        return pitch, yaw, roll

    def _approximate_gaze(self, landmarks, w, h) -> Tuple[float, float]:
        iris = landmarks.landmark[468]
        eye_inner = landmarks.landmark[133]
        eye_outer = landmarks.landmark[33]
        
        eye_center_x = (eye_inner.x + eye_outer.x) / 2.0
        eye_center_y = (eye_inner.y + eye_outer.y) / 2.0
        
        dx = (iris.x - eye_center_x) * 10.0 
        dy = (iris.y - eye_center_y) * 10.0
        
        return (dx, dy)

    def release(self):
        if self.detector:
            self.detector.close()
