import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class TrackingResult:
    detected: bool                        
    confidence: float                     
    handedness: str                       
    landmarks: List[Tuple[float, float, float]]
    normalized_landmarks: List[Tuple[float, float, float]]
    fingers_extended: List[bool]          
    pinch_distance: float                 
    palm_normal: Tuple[float, float, float]  
    palm_center: Tuple[float, float]      
    wrist: Tuple[float, float, float]           
    thumb_tip: Tuple[float, float, float]        
    index_tip: Tuple[float, float, float]        
    middle_tip: Tuple[float, float, float]       
    ring_tip: Tuple[float, float, float]         
    pinky_tip: Tuple[float, float, float]        
    all_tips: List[Tuple[float, float, float]]   
    palm_width: float = 1.0

class HandPreFilter:
    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha
        self._last_lms = None
        
    def filter(self, landmarks):
        if self._last_lms is None:
            self._last_lms = landmarks
            return landmarks
        smoothed = []
        for i, (x, y, z) in enumerate(landmarks):
            lx, ly, lz = self._last_lms[i]
            sx = self.alpha * x + (1 - self.alpha) * lx
            sy = self.alpha * y + (1 - self.alpha) * ly
            sz = self.alpha * z + (1 - self.alpha) * lz
            smoothed.append((sx, sy, sz))
        self._last_lms = smoothed
        return smoothed

class HandTracker:
    def __init__(self, config: dict):
        base_options = python.BaseOptions(model_asset_path='data/models/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=config.get('min_detection_confidence', 0.5),
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=config.get('min_tracking_confidence', 0.5)
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        alpha = config.get('smoothing', {}).get('landmark_prefilter_alpha', 0.6)
        self.prefilters = [HandPreFilter(alpha), HandPreFilter(alpha)]

    def process(self, frame: np.ndarray) -> List[TrackingResult]:
        import cv2
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.detector.detect(mp_image)
        
        if not results.hand_landmarks:
            # Reset filters when hands are lost
            self.prefilters[0]._last_lms = None
            self.prefilters[1]._last_lms = None
            return []
            
        hands_out = []
        for i in range(len(results.hand_landmarks)):
            hand_landmarks = results.hand_landmarks[i]
            handedness_info = results.handedness[i][0]
            
            raw_landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
            
            # Apply Stage 0: Landmark Pre-Filtering
            landmarks = self.prefilters[i].filter(raw_landmarks)
            
            confidence = handedness_info.score
            handedness = handedness_info.category_name
            
            normalized_landmarks = self._normalize_landmarks(landmarks)
            fingers_extended = self._compute_fingers_extended(landmarks, handedness)
            
            thumb_tip = np.array(normalized_landmarks[4])
            index_tip = np.array(normalized_landmarks[8])
            pinch_distance = float(np.linalg.norm(thumb_tip - index_tip))
            
            palm_normal = self._compute_palm_normal(landmarks)
            
            palm_indices = [0, 1, 5, 9, 13, 17]
            cx = sum(landmarks[i][0] for i in palm_indices) / len(palm_indices)
            cy = sum(landmarks[i][1] for i in palm_indices) / len(palm_indices)
            palm_center = (cx, cy)
            
            res = TrackingResult(
                detected=True,
                confidence=confidence,
                handedness=handedness,
                landmarks=landmarks,
                normalized_landmarks=normalized_landmarks,
                fingers_extended=fingers_extended,
                pinch_distance=pinch_distance,
                palm_normal=palm_normal,
                palm_center=palm_center,
                wrist=landmarks[0],
                thumb_tip=landmarks[4],
                index_tip=landmarks[8],
                middle_tip=landmarks[12],
                ring_tip=landmarks[16],
                pinky_tip=landmarks[20],
                all_tips=[landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
            )
            wrist_np = np.array(landmarks[0])
            middle_mcp_np = np.array(landmarks[9])
            palm_w = np.linalg.norm(middle_mcp_np - wrist_np)
            res.palm_width = float(palm_w if palm_w > 0 else 1.0)
            hands_out.append(res)
            
        return hands_out

    def get_control_hand(self, all_results: List[TrackingResult]) -> Optional[TrackingResult]:
        if not all_results:
            return None
            
        # Strictly pick the right-most hand (highest X coordinate)
        return max(all_results, key=lambda h: h.palm_center[0])

    def _compute_fingers_extended(self, landmarks, handedness: str) -> List[bool]:
        extended = []
        thumb_tip_x = landmarks[4][0]
        thumb_ip_x = landmarks[3][0]
        if handedness == "Right":
            extended.append(thumb_tip_x < thumb_ip_x)
        else:
            extended.append(thumb_tip_x > thumb_ip_x)

        finger_indices = [(5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20)]
        for mcp_idx, pip_idx, tip_idx in finger_indices:
            mcp = np.array(landmarks[mcp_idx])
            pip = np.array(landmarks[pip_idx])
            tip = np.array(landmarks[tip_idx])
            
            vec1 = pip - mcp
            vec2 = tip - pip
            
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                extended.append(False)
                continue
                
            dot = np.dot(vec1, vec2) / (norm1 * norm2)
            extended.append(bool(dot > 0.75))
            
        return extended

    def _normalize_landmarks(self, landmarks) -> List[Tuple[float, float, float]]:
        wrist = np.array(landmarks[0])
        middle_mcp = np.array(landmarks[9])
        
        palm_width = np.linalg.norm(middle_mcp - wrist)
        if palm_width == 0:
            palm_width = 1.0
            
        normalized = []
        for lm in landmarks:
            norm = (np.array(lm) - wrist) / palm_width
            normalized.append(tuple(float(v) for v in norm))
        return normalized

    def _compute_palm_normal(self, landmarks) -> Tuple[float, float, float]:
        wrist = np.array(landmarks[0])
        index_mcp = np.array(landmarks[5])
        pinky_mcp = np.array(landmarks[17])
        
        v1 = index_mcp - wrist
        v2 = pinky_mcp - wrist
        normal = np.cross(v1, v2)
        norm_mag = np.linalg.norm(normal)
        if norm_mag != 0:
            normal = normal / norm_mag
        return tuple(float(v) for v in normal)

    def release(self):
        if self.detector:
            self.detector.close()
