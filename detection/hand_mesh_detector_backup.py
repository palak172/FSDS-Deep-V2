"""
Hand Mesh Detector - Draws full hand skeleton with landmarks
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class HandMeshDetector:
    """
    Detects hands and draws full hand mesh/skeleton
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
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        print("✅ Hand Mesh Detector initialized")
    
    def detect_hands(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect hands and draw full mesh/skeleton
        """
        # Debug: Check frame validity
        if frame is None or frame.size == 0:
            print("❌ Invalid frame received in hand detector")
            return frame, []
        
        # Debug: Print frame info once
        if not hasattr(self, '_debug_printed'):
            print(f"📷 Frame shape: {frame.shape}")
            print(f"📷 Frame dtype: {frame.dtype}")
            self._debug_printed = True
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # CRITICAL DEBUG: Check if hands are found
        if results.multi_hand_landmarks:
            print(f"✅ HANDS DETECTED! Found {len(results.multi_hand_landmarks)} hands")
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                wrist = hand_landmarks.landmark[0]
                h, w = frame.shape[:2]
                wrist_pos = (int(wrist.x * w), int(wrist.y * h))
                print(f"   Hand {i} wrist at: {wrist_pos}")
        else:
            # Print occasionally to avoid spam
            import random
            if random.random() < 0.01:  # 1% of frames
                print("🔍 No hands detected in frame")
        
        hands_info = []
    
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                results.multi_handedness):
                # Draw full hand skeleton
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Extract hand info
                hand_info = self._extract_hand_info(hand_landmarks, handedness, frame.shape)
                hands_info.append(hand_info)
        
        return frame, hands_info
    
    def _extract_hand_info(self, hand_landmarks, handedness, frame_shape: Tuple[int, int]) -> Dict:
        """Extract hand information"""
        h, w = frame_shape[:2]
        
        # Get wrist position (landmark 0)
        wrist = hand_landmarks.landmark[0]
        wrist_pos = (int(wrist.x * w), int(wrist.y * h))
        
        # Get handedness
        hand_label = handedness.classification[0].label.lower()
        
        # Get all finger tip positions (for zone checking)
        finger_tips = {
            'thumb': (int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)),
            'index': (int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)),
            'middle': (int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)),
            'ring': (int(hand_landmarks.landmark[16].x * w), int(hand_landmarks.landmark[16].y * h)),
            'pinky': (int(hand_landmarks.landmark[20].x * w), int(hand_landmarks.landmark[20].y * h))
        }
        
        return {
            'handedness': hand_label,
            'wrist_position': wrist_pos,
            'finger_tips': finger_tips,
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