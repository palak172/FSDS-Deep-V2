"""
Face Mesh Detector - Ultra-minimal (only 4 key points)
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple


class FaceMeshDetector:
    """
    Ultra-minimal face detector - draws only 4 key points (eyes, nose, lip)
    Maximum performance, minimal visual feedback
    """
    
    # Just 4 key landmarks for minimal face representation
    KEY_LANDMARKS = {
        'left_eye': [33],      # 1 point - left eye center
        'right_eye': [263],    # 1 point - right eye center
        'nose_tip': [1],       # 1 point - nose tip
        'lips': [61],          # 1 point - center of lips
    }
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get face detection settings
        face_config = config.get('face_mesh', {})
        self.min_detection_confidence = face_config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = face_config.get('min_tracking_confidence', 0.5)
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,  # False = faster
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        self.current_face_orientation = 'No Face'
        self.current_nose_position = None
        
        print("✅ Face Mesh Detector initialized (ULTRA-MINIMAL - 4 points only)")
    
    def detect_face_mesh(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect face and draw only 4 key points
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        h, w = frame.shape[:2]
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw minimal face points (4 dots)
                self._draw_minimal_face(frame, face_landmarks, w, h)
                
                # Detect orientation (for safety logic)
                self._detect_face_orientation(face_landmarks, w, h)
        else:
            self.current_face_orientation = 'No Face'
            self.current_nose_position = None
        
        return frame
    
    def _draw_minimal_face(self, frame, face_landmarks, w, h):
        """Draw only 4 essential facial points"""
        
        # Left Eye (Green)
        idx = self.KEY_LANDMARKS['left_eye'][0]
        landmark = face_landmarks.landmark[idx]
        x, y = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)  # Green filled circle
        
        # Right Eye (Green)
        idx = self.KEY_LANDMARKS['right_eye'][0]
        landmark = face_landmarks.landmark[idx]
        x, y = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)  # Green filled circle
        
        # Nose Tip (Blue)
        idx = self.KEY_LANDMARKS['nose_tip'][0]
        landmark = face_landmarks.landmark[idx]
        x, y = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(frame, (x, y), 4, (255, 0, 0), -1)  # Blue filled circle
        
        upper_lip = face_landmarks.landmark[13]
        lower_lip = face_landmarks.landmark[14]
        
        lip_x = int((upper_lip.x + lower_lip.x) / 2 * w)
        lip_y = int((upper_lip.y + lower_lip.y) / 2 * h)
        
        cv2.circle(frame, (lip_x, lip_y), 4, (0, 0, 255), -1)
    
    def _detect_face_orientation(self, face_landmarks, w, h):
        """
        Detect face orientation based on nose and eye positions
        """
        nose_tip = face_landmarks.landmark[1]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        
        nose_y = nose_tip.y * h
        eye_y_avg = (left_eye.y + right_eye.y) / 2 * h
        
        # Store nose position (for dynamic zone if needed)
        self.current_nose_position = (int(nose_tip.x * w), int(nose_y))
        
        # Determine orientation
        if nose_y > eye_y_avg + 30:
            self.current_face_orientation = 'Tilted Down'
        elif nose_y < eye_y_avg - 30:
            self.current_face_orientation = 'Tilted Up'
        else:
            self.current_face_orientation = 'Forward'
    
    def get_face_orientation(self, frame=None) -> str:
        """Return current face orientation"""
        return self.current_face_orientation
    
    def get_nose_position(self, frame=None):
        """Return current nose position"""
        return self.current_nose_position