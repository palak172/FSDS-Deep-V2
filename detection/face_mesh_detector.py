"""
Face Mesh Detector - Draws full face mesh with landmarks
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class FaceMeshDetector:
    """
    Detects face and draws full mesh (eyes, nose, mouth, etc.)
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,  # This gives iris/eye landmarks
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Face mesh drawing specs
        self.face_connections = self.mp_face_mesh.FACEMESH_TESSELATION
        self.iris_connections = self.mp_face_mesh.FACEMESH_IRISES
        
        print("✅ Face Mesh Detector initialized")
    
    def detect_face_mesh(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect face and draw full mesh on frame
        
        Returns:
            Frame with face mesh drawn
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw the full face mesh
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.face_connections,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_tesselation_style()
                )
                
                # Draw iris/eyes specifically
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.iris_connections,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style()
                )
        
        return frame
    
    def get_face_orientation(self, frame: np.ndarray) -> str:
        """
        Detect face orientation using mesh landmarks
        More accurate than bbox method
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return 'No Face'
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Get key landmarks
        # Nose tip (landmark 1)
        nose_tip = face_landmarks.landmark[1]
        # Chin (landmark 152)
        chin = face_landmarks.landmark[152]
        # Left eye (landmark 33)
        left_eye = face_landmarks.landmark[33]
        # Right eye (landmark 263)
        right_eye = face_landmarks.landmark[263]
        
        # Calculate vertical ratio (looking down vs forward)
        nose_y = nose_tip.y
        chin_y = chin.y
        eye_center_y = (left_eye.y + right_eye.y) / 2
        
        # If nose is closer to chin, person is looking down
        if (chin_y - nose_y) < 0.05:
            return 'Tilted Down'
        
        # If eyes are high in frame, person is looking down
        if eye_center_y > 0.7:
            return 'Tilted Down'
        
        return 'Forward'