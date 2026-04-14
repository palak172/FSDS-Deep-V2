"""
Hand detection module - tracks wrist positions for zone monitoring
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class HandDetector:
    """
    Detects hands and tracks wrist positions
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get hand detection settings
        hand_config = config.get('hand_detection', {})
        self.min_detection_confidence = hand_config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = hand_config.get('min_tracking_confidence', 0.5)
        self.wrist_threshold = hand_config.get('wrist_threshold', 50)
        
        # Initialize MediaPipe hands
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            print("✅ Hand detector initialized with mp.solutions")
        except AttributeError:
            try:
                from mediapipe import solutions
                self.hands = solutions.hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                print("✅ Hand detector initialized with mediapipe.solutions")
            except ImportError:
                raise ImportError("Could not initialize MediaPipe hands. Please install mediapipe==0.10.7")
        
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_hands(self, frame: np.ndarray) -> List[Dict]:
        """Detect hands and return wrist positions"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hands = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                   results.multi_handedness):
                hand_info = self._extract_hand_info(hand_landmarks, handedness, frame.shape)
                hands.append(hand_info)
        
        return hands
    
    def _extract_hand_info(self, hand_landmarks, handedness, frame_shape: Tuple[int, int]) -> Dict:
        """Extract hand information"""
        h, w = frame_shape[:2]
        
        # Get wrist landmark (landmark 0)
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
    
    def get_hand_positions(self, hands: List[Dict]) -> Dict[str, Optional[Tuple[int, int]]]:
        """Get wrist positions for left and right hands"""
        positions = {'left': None, 'right': None}
        
        for hand in hands:
            handedness = hand['handedness']
            if handedness in positions:
                positions[handedness] = hand['wrist_position']
        
        return positions