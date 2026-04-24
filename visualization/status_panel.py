"""
Status Panel - With Session Timer (Fixed Spacing)
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
        
        # Session tracking
        self.current_employee_name = None
        self.session_start_time = None
    
    def update_violation_state(self, safety_state: str, is_violation: bool):
        self.current_state = safety_state
        if is_violation:
            if self.violation_start_time is None:
                self.violation_start_time = time.time()
        else:
            self.violation_start_time = None
    
    def update_employee(self, employee_name: str):
        self.current_employee_name = employee_name
    
    def start_session_timer(self):
        """Called when a work session starts"""
        self.session_start_time = time.time()
    
    def end_session_timer(self):
        """Called when a work session ends"""
        self.session_start_time = None
    
    def get_session_duration(self) -> str:
        """Get formatted session duration (HH:MM:SS)"""
        if self.session_start_time is None:
            return "00:00:00"
        
        elapsed = time.time() - self.session_start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def draw(self, frame: np.ndarray, safety_state: str, face_orientation: str,
             hand_zones: Dict[str, str], fps: float) -> np.ndarray:
        
        h, w = frame.shape[:2]
        
        # Hand status logic
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
        else:
            hands_text = "UNSAFE"
            hands_color = (0, 0, 255)
        
        # Face status
        face_ok = face_orientation == "Forward"
        face_text = "OK" if face_ok else face_orientation
        face_color = (0, 255, 0) if face_ok else (0, 0, 255)
        
        # State color
        state_color = self.state_colors.get(safety_state, (0, 255, 0))
        
        # Get session duration
        session_duration = self.get_session_duration()
        
        # Draw background panel (INCREASED HEIGHT for all rows)
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 230), (0, 0, 0), -1)  # Height 230
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Y-position tracker (starts at 35, increases by 25 each line)
        y = 35
        
        # Title
        cv2.putText(frame, "Safety Detection System", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 28
        
        # Employee name
        if self.current_employee_name:
            cv2.putText(frame, f"Operator: {self.current_employee_name}", (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y += 25
        
        # Session Timer
        cv2.putText(frame, f"Session Time: {session_duration}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        y += 25
        
        # Orientation
        cv2.putText(frame, f"Orientation: {face_orientation}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 1)
        y += 25
        
        # Face
        cv2.putText(frame, f"Face: {face_text}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 1)
        y += 25
        
        # Hands
        cv2.putText(frame, f"Hands: {hands_text}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hands_color, 1)
        y += 25
        
        # State
        cv2.putText(frame, f"State: {safety_state}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
        
        # FPS (top right, independent of Y tracker)
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame