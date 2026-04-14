"""
Face detection and orientation module
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class FaceDetector:
    """
    Detects faces and determines orientation (Forward/Tilted Down/No Face)
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get face detection settings
        face_config = config.get('face_detection', {})
        self.min_detection_confidence = face_config.get('min_detection_confidence', 0.5)
        self.tilt_threshold = face_config.get('tilt_threshold', 15)
        
        # Initialize MediaPipe face detection
        # Note: Some versions need 'mp.solutions.face_detection', others need 'mp.solutions.face_detection.FaceDetection'
        try:
            # Try the standard way
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=self.min_detection_confidence
            )
            print("✅ Face detector initialized with mp.solutions")
        except AttributeError:
            # Fallback for different MediaPipe versions
            try:
                from mediapipe import solutions
                self.face_detection = solutions.face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=self.min_detection_confidence
                )
                print("✅ Face detector initialized with mediapipe.solutions")
            except ImportError:
                raise ImportError("Could not initialize MediaPipe face detection. Please install mediapipe==0.10.7")
        
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect all faces in the frame
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        faces = []
        
        if results.detections:
            for detection in results.detections:
                face_info = self._extract_face_info(detection, frame.shape)
                face_info['orientation'] = self._detect_orientation(face_info, frame.shape)
                faces.append(face_info)
        
        return faces
    
    def _extract_face_info(self, detection, frame_shape: Tuple[int, int]) -> Dict:
        """Extract face information from detection"""
        h, w = frame_shape[:2]
        bbox = detection.location_data.relative_bounding_box
        
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        box_w = int(bbox.width * w)
        box_h = int(bbox.height * h)
        
        return {
            'bbox': (x, y, box_w, box_h),
            'center': (x + box_w // 2, y + box_h // 2),
            'confidence': detection.score[0]
        }
    
    def _detect_orientation(self, face_info: Dict, frame_shape: Tuple[int, int]) -> str:
        """
        Detect if face is looking down or forward
        """
        h, w = frame_shape[:2]
        x, y, box_w, box_h = face_info['bbox']
        
        # Cue 1: Face position in frame
        face_center_y = face_info['center'][1]
        lower_threshold = h * 0.65
        
        if face_center_y > lower_threshold:
            return 'Tilted Down'
        
        # Cue 2: Aspect ratio
        aspect_ratio = box_w / box_h if box_h > 0 else 1
        
        if aspect_ratio > 0.95:
            return 'Tilted Down'
        
        return 'Forward'
    
    def get_primary_face(self, faces: List[Dict]) -> Optional[Dict]:
        """Get the most prominent face"""
        if not faces:
            return None
        return max(faces, key=lambda f: f['confidence'] * (f['bbox'][2] * f['bbox'][3]))
    
    def get_orientation_status(self, faces: List[Dict]) -> Dict:
        """Get summary of face orientation status"""
        if not faces:
            return {
                'has_face': False,
                'orientation': 'No Face',
                'is_safe': False
            }
        
        primary = self.get_primary_face(faces)
        
        return {
            'has_face': True,
            'orientation': primary['orientation'],
            'is_safe': primary['orientation'] == 'Forward',
            'face_count': len(faces)
        }