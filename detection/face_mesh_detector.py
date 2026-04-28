"""
Face Mesh Detector - Ultra-minimal with Calibration Support
"""
import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple


class FaceMeshDetector:
    """
    Ultra-minimal face detector with calibration support
    - Draws only 4 key points
    - Calibrates neutral face position at startup
    - Detects tilt based on calibrated baseline
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get face detection settings
        face_config = config.get('face_mesh', {})
        self.min_detection_confidence = face_config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = face_config.get('min_tracking_confidence', 0.5)
        
        # Tilt threshold (pixels from neutral position)
        self.tilt_threshold = face_config.get('tilt_threshold', 35)
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        self.current_face_orientation = 'No Face'
        self.current_nose_position = None
        
        # ========== CALIBRATION DATA ==========
        self.calibrated = False
        self.neutral_nose_offset = None  # pixels from eyes to nose at neutral
        self.calibration_samples = []    # Store multiple samples for accuracy
        
        print("✅ Face Mesh Detector initialized (with calibration support)")
    
    # ========== CALIBRATION METHODS ==========
    
    def start_calibration(self):
        """Start the calibration process"""
        self.calibrated = False
        self.neutral_nose_offset = None
        self.calibration_samples = []
        print("📏 Face calibration started")
    
    def is_calibrated(self) -> bool:
        """Check if calibration is complete"""
        return self.calibrated
    
    def get_calibration_progress(self) -> int:
        """Get calibration progress (0-100)"""
        return len(self.calibration_samples) * 20  # 5 samples = 100%
    
    def add_calibration_sample(self, frame):
        """
        Take a calibration sample from current frame
        Returns: (success, message)
        """
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return False, "No face detected"
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Get eye and nose positions
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        nose_tip = face_landmarks.landmark[1]
        
        eye_y_avg = (left_eye.y + right_eye.y) / 2 * h
        nose_y = nose_tip.y * h
        
        # Calculate offset (nose position relative to eyes)
        offset = nose_y - eye_y_avg
        
        self.calibration_samples.append(offset)
        
        if len(self.calibration_samples) >= 5:
            # Average all samples for accuracy
            self.neutral_nose_offset = sum(self.calibration_samples) / len(self.calibration_samples)
            self.calibrated = True
            print(f"✅ Calibration complete! Neutral offset: {self.neutral_nose_offset:.1f}px")
            return True, "Calibration complete!"
        
        return False, f"Sample {len(self.calibration_samples)}/5 taken"
    
    def reset_calibration(self):
        """Reset calibration (for re-calibration)"""
        self.calibrated = False
        self.neutral_nose_offset = None
        self.calibration_samples = []
        print("🔄 Calibration reset")
    
    # ========== ORIENTATION DETECTION ==========
    
    def _detect_face_orientation(self, face_landmarks, w, h):
        """
        Detect face orientation based on calibrated neutral position
        """
        # Get positions
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        nose_tip = face_landmarks.landmark[1]
        
        eye_y_avg = (left_eye.y + right_eye.y) / 2 * h
        nose_y = nose_tip.y * h
        
        # Store current nose position
        self.current_nose_position = (int(nose_tip.x * w), int(nose_y))
        
        # If not calibrated, return unknown
        if not self.calibrated:
            self.current_face_orientation = 'Unknown'
            return
        
        # Calculate current offset from eyes
        current_offset = nose_y - eye_y_avg
        
        # Calculate difference from neutral (calibrated) position
        # Positive = nose lower (looking down)
        # Negative = nose higher (looking up)
        difference = current_offset - self.neutral_nose_offset
        
        # Determine orientation based on threshold
        if difference > self.tilt_threshold:
            self.current_face_orientation = 'Tilted Down'
        elif difference < -self.tilt_threshold:
            self.current_face_orientation = 'Tilted Up'
        else:
            self.current_face_orientation = 'Forward'
    
    # ========== DRAWING METHODS ==========
    
    def detect_face_mesh(self, frame: np.ndarray) -> np.ndarray:
        """Detect face and draw only 4 key points"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        h, w = frame.shape[:2]
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw minimal face points
                self._draw_minimal_face(frame, face_landmarks, w, h)
                
                # Detect orientation (uses calibration if available)
                self._detect_face_orientation(face_landmarks, w, h)
        else:
            if self.calibrated:
                self.current_face_orientation = 'No Face'
            self.current_nose_position = None
        
        return frame
    
    def _draw_minimal_face(self, frame, face_landmarks, w, h):
        """Draw only 4 essential facial points"""
        
        # Left Eye (Green)
        left_eye = face_landmarks.landmark[33]
        lx, ly = int(left_eye.x * w), int(left_eye.y * h)
        cv2.circle(frame, (lx, ly), 4, (0, 255, 0), -1)
        
        # Right Eye (Green)
        right_eye = face_landmarks.landmark[263]
        rx, ry = int(right_eye.x * w), int(right_eye.y * h)
        cv2.circle(frame, (rx, ry), 4, (0, 255, 0), -1)
        
        # Nose Tip (Blue)
        nose_tip = face_landmarks.landmark[1]
        nx, ny = int(nose_tip.x * w), int(nose_tip.y * h)
        
        # Color nose based on calibration status
        if self.calibrated:
            nose_color = (0, 255, 255)  # Yellow when calibrated
        else:
            nose_color = (255, 0, 0)    # Blue when not calibrated
        
        cv2.circle(frame, (nx, ny), 4, nose_color, -1)
        
        # Lips Center (Red) - Average of upper and lower lip
        upper_lip = face_landmarks.landmark[13]
        lower_lip = face_landmarks.landmark[14]
        lip_x = int((upper_lip.x + lower_lip.x) / 2 * w)
        lip_y = int((upper_lip.y + lower_lip.y) / 2 * h)
        cv2.circle(frame, (lip_x, lip_y), 4, (0, 0, 255), -1)
    
    # ========== GETTER METHODS ==========
    
    def get_face_orientation(self, frame=None) -> str:
        """Return current face orientation"""
        if not self.calibrated:
            return 'Needs Calibration'
        return self.current_face_orientation
    
    def get_nose_position(self, frame=None):
        """Return current nose position"""
        return self.current_nose_position
    
    def get_neutral_offset(self) -> Optional[float]:
        """Return the calibrated neutral offset"""
        return self.neutral_nose_offset