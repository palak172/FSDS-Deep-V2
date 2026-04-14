"""
Status Panel - Displays safety information with time bar
"""
import cv2
import numpy as np
import time
from typing import Dict


class StatusPanel:
    """
    Draws the safety status panel with time bar
    """
    
    def __init__(self, config: dict):
        self.config = config
        vis_config = config.get('visualization', {})
        self.colors = vis_config.get('colors', {})
        
        # State colors
        self.state_colors = {
            'SAFE': (0, 255, 0),
            'WARNING': (0, 255, 255),
            'CRITICAL': (0, 0, 255),
            'STOPPED': (0, 0, 255)
        }
        
        # Violation tracking
        self.violation_start_time = None
        self.current_state = 'SAFE'
        
        # Thresholds
        safety_config = config.get('safety', {})
        self.warning_threshold = safety_config.get('warning_threshold', 2.0)
        self.violation_threshold = safety_config.get('violation_threshold', 8.0)
    
    def update_violation_state(self, safety_state: str, is_violation: bool):
        """
        Update violation tracking
        """
        self.current_state = safety_state
        
        if is_violation:
            if self.violation_start_time is None:
                self.violation_start_time = time.time()
        else:
            self.violation_start_time = None
    
    def draw(self, frame: np.ndarray, safety_state: str, face_orientation: str,
             hand_zones: Dict[str, str], fps: float) -> np.ndarray:
        """
        Draw the complete status panel
        """
        h, w = frame.shape[:2]
        
        # Get violation duration
        violation_duration = 0
        if self.violation_start_time is not None:
            violation_duration = time.time() - self.violation_start_time
        
        # Get state color
        state_color = self.state_colors.get(safety_state, (0, 255, 0))
        
        # Create semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Title
        cv2.putText(frame, "Safety Detection System", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Orientation
        orientation_text = "Facing Forward" if face_orientation == "Forward" else face_orientation
        orientation_color = (0, 255, 0) if face_orientation == "Forward" else (0, 0, 255)
        cv2.putText(frame, f"Orientation: {orientation_text}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, orientation_color, 1)
        
        # Face status
        face_ok = face_orientation == "Forward"
        face_text = "OK" if face_ok else face_orientation
        face_color = (0, 255, 0) if face_ok else (0, 0, 255)
        cv2.putText(frame, f"Face: {face_text}", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 1)
        # DEBUG: Print what hand_zones contains
        print("hand_zones:", hand_zones)
        print("hand_zones values:", list(hand_zones.values()))
        # Hands status
        all_hands_safe = all(zone in ['Hand Zone'] #'Work Area', 'Not Detected'] 
                            for zone in hand_zones.values())
        hands_text = "OK" if all_hands_safe else "NOT FOUND"
        hands_color = (0, 255, 0) if all_hands_safe else (0, 0, 255)
        cv2.putText(frame, f"Hands: {hands_text}", (20, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hands_color, 1)
        
        # Safety state
        cv2.putText(frame, f"State: {safety_state}", (20, 145),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
        
        # Hand zone info
        left_zone = hand_zones.get('left', 'Not Detected')
        right_zone = hand_zones.get('right', 'Not Detected')
        primary_zone = left_zone if left_zone != 'Not Detected' else right_zone
        cv2.putText(frame, f"Hand Zone: {primary_zone}", (20, 175),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw TIME BAR at bottom of status panel
        if self.violation_start_time is not None:
            bar_y = 190
            bar_height = 6
            
            if safety_state == 'WARNING':
                max_duration = self.warning_threshold
                bar_color = (0, 255, 255)
            else:
                max_duration = self.violation_threshold
                bar_color = (0, 0, 255)
            
            progress = min(violation_duration / max_duration, 1.0)
            bar_width = int(360 * progress)
            
            # Background
            cv2.rectangle(frame, (20, bar_y), (380, bar_y + bar_height), (50, 50, 50), -1)
            # Progress
            cv2.rectangle(frame, (20, bar_y), (20 + bar_width, bar_y + bar_height), bar_color, -1)
        
        # FPS counter (top right)
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame