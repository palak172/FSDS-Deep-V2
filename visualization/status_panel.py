"""
Status Panel - Simple version
"""
import cv2
import numpy as np
import time
from typing import Dict


class StatusPanel:
    
    def __init__(self, config: dict):
        self.config = config
        vis_config = config.get('visualization', {})
        self.colors = vis_config.get('colors', {})
        
        self.state_colors = {
            'SAFE': (0, 255, 0),
            'WARNING': (0, 255, 255),
            'CRITICAL': (0, 0, 255),
        }
        
        self.current_state = 'SAFE'
        
        safety_config = config.get('safety', {})
        self.warning_threshold = safety_config.get('warning_threshold', 2.0)
        self.violation_threshold = safety_config.get('violation_threshold', 8.0)
        self.violation_start_time = None
    
    def update_violation_state(self, safety_state: str, is_violation: bool):
        self.current_state = safety_state
        if is_violation:
            if self.violation_start_time is None:
                self.violation_start_time = time.time()
        else:
            self.violation_start_time = None
    
    def draw(self, frame: np.ndarray, safety_state: str, face_orientation: str,
             hand_zones: Dict[str, str], fps: float) -> np.ndarray:
        
        h, w = frame.shape[:2]
        # Add this right before your hand status logic
        #print("=" * 50)
        #print(f"[DEBUG] hand_zones FULL: {hand_zones}")
        #print(f"[DEBUG] hand_zones values list: {list(hand_zones.values())}")
        #print(f"[DEBUG] 'Hand Zone' in values? {'Hand Zone' in list(hand_zones.values())}")
        #print(f"[DEBUG] Any value not 'Not Detected'? {any(zone != 'Not Detected' for zone in hand_zones.values())}")
        #print("=" * 50)
        # Simple hand status logic
        hand_zones_list = list(hand_zones.values())
        hands_detected = any(zone != 'Not Detected' for zone in hand_zones_list)
        hands_in_zone = any(zone == 'Hand Zone' for zone in hand_zones_list)
        
        # Determine hand status and color
        if hands_in_zone:
            hands_text = "OK"
            hands_color = (0, 255, 0)
        elif hands_detected and not hands_in_zone:
            hands_text = "WARNING"
            hands_color = (0, 255, 255)
        else:  # No hands detected
            hands_text = "UNSAFE"
            hands_color = (0, 0, 255)
        
        # Face status
        face_ok = face_orientation == "Forward"
        face_text = "OK" if face_ok else face_orientation
        face_color = (0, 255, 0) if face_ok else (0, 0, 255)
        
        # State color
        state_color = self.state_colors.get(safety_state, (0, 255, 0))
        
        # Draw background panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw all text
        cv2.putText(frame, "Safety Detection System", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Orientation: {face_orientation}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 1)
        
        cv2.putText(frame, f"Face: {face_text}", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 1)
        
        cv2.putText(frame, f"Hands: {hands_text}", (20, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hands_color, 1)
        
        cv2.putText(frame, f"State: {safety_state}", (20, 145),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
        
        # FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame