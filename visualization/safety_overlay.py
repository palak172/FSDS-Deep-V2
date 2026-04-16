"""
Safety Overlay - Draws visual indicators for safety state
"""
import cv2
import numpy as np
import time


class SafetyOverlay:
    """
    Draws visual overlays based on safety state:
    - Green border when SAFE
    - Yellow border when WARNING
    - Red border when CRITICAL
    - Time bar for violation duration
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get safety thresholds
        safety_config = config.get('safety', {})
        self.warning_threshold = safety_config.get('warning_threshold', 2.0)
        self.violation_threshold = safety_config.get('violation_threshold', 8.0)
        
        # State tracking
        self.current_state = 'SAFE'
        self.violation_start_time = None
        
        # Border colors (BGR format)
        self.border_colors = {
            'SAFE': (0, 255, 0),      # Green
            'WARNING': (0, 255, 255), # Yellow
            'CRITICAL': (0, 0, 255),  # Red
            'STOPPED': (0, 0, 255)    # Red
        }
        
        # Border thickness
        self.border_thickness = 8
        
        print("✅ Safety Overlay initialized - Border will show GREEN when SAFE")
    
    def update_state(self, safety_state: str, is_violation: bool):
        """
        Update safety state and violation tracking
        
        Args:
            safety_state: Current safety state ('SAFE', 'WARNING', 'CRITICAL')
            is_violation: True if there's an active violation
        """
        self.current_state = safety_state
        
        if is_violation:
            if self.violation_start_time is None:
                self.violation_start_time = time.time()
        else:
            self.violation_start_time = None
    
    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw safety overlays on the frame
        
        - Draws colored border based on safety state
        - Draws time bar at the top for violations
        
        Args:
            frame: The image frame to draw on
        
        Returns:
            Frame with overlays applied
        """
        h, w = frame.shape[:2]
        
        # Get border color for current state
        border_color = self.border_colors.get(self.current_state, (0, 255, 0))
        
        # Draw colored border
        # Top border
        cv2.rectangle(frame, (0, 0), (w, self.border_thickness), border_color, -1)
        # Bottom border
        cv2.rectangle(frame, (0, h - self.border_thickness), (w, h), border_color, -1)
        # Left border
        cv2.rectangle(frame, (0, 0), (self.border_thickness, h), border_color, -1)
        # Right border
        cv2.rectangle(frame, (w - self.border_thickness, 0), (w, h), border_color, -1)
        
        # Draw time bar at the top (under the border) for violations
        if self.violation_start_time is not None:
            violation_duration = time.time() - self.violation_start_time
            
            if self.current_state == 'WARNING':
                max_duration = self.warning_threshold
                bar_color = (0, 255, 255)  # Yellow
            else:
                max_duration = self.violation_threshold
                bar_color = (0, 0, 255)  # Red
            
            progress = min(violation_duration / max_duration, 1.0)
            bar_width = int(w * progress)
            
            # Draw time bar just below the top border
            bar_y = self.border_thickness + 2
            bar_height = 6
            
            # Background
            cv2.rectangle(frame, (0, bar_y), (w, bar_y + bar_height), (50, 50, 50), -1)
            # Progress bar
            cv2.rectangle(frame, (0, bar_y), (bar_width, bar_y + bar_height), bar_color, -1)
        
        return frame
    
    def get_border_color(self, state: str) -> tuple:
        """Get border color for a given safety state"""
        return self.border_colors.get(state, (0, 255, 0))