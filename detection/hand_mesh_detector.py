"""
Hand Mesh Detector - Draws only hand skeleton (optimized for speed)
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class HandMeshDetector:
    """
    Detects hands and draws ONLY hand skeleton (optimized for performance)
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get hand detection settings
        hand_config = config.get('hand_detection', {})
        self.min_detection_confidence = hand_config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = hand_config.get('min_tracking_confidence', 0.5)
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        # self.mp_drawing_styles removed - not needed for optimized version
        
        print("✅ Hand Mesh Detector initialized (OPTIMIZED - simple green skeleton)")
    
    def detect_hands(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect hands and draw simplified skeleton (faster)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hands_info = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                   results.multi_handedness):
                # Simplified drawing - just green lines, no complex styling
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
                
                # Extract hand info (still needed for zone checking)
                hand_info = self._extract_hand_info(hand_landmarks, handedness, frame.shape)
                hands_info.append(hand_info)
        
        return frame, hands_info
    
    def _extract_hand_info(self, hand_landmarks, handedness, frame_shape: Tuple[int, int]) -> Dict:
        """Extract hand information for zone checking"""
        h, w = frame_shape[:2]
        
        # Get wrist position (landmark 0) - needed for zone checking
        wrist = hand_landmarks.landmark[0]
        wrist_pos = (int(wrist.x * w), int(wrist.y * h))
        
        # Get handedness
        hand_label = handedness.classification[0].label.lower()
        
        return {
            'handedness': hand_label,
            'wrist_position': wrist_pos,
            'confidence': handedness.classification[0].score,
            'landmarks': hand_landmarks
        }
    
    def get_hand_positions(self, hands_info: List[Dict]) -> Dict[str, Optional[Tuple[int, int]]]:
        """Get wrist positions for left and right hands"""
        positions = {'left': None, 'right': None}
        
        for hand in hands_info:
            handedness = hand['handedness']
            if handedness in positions:
                positions[handedness] = hand['wrist_position']
        
        return positions