"""
Safety Overlay - Draws time bar, border, and status indicators
"""
import cv2
import numpy as np
import time
from typing import Dict, Optional


class SafetyOverlay:
    """
    Draws safety overlays:
    - Colored border based on safety state
    - Time bar showing violation duration
    - Status indicators
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.violation_start_time = None
        self.safety_state = 'SAFE'
        
        # Color mapping for different states
        self.state_colors = {
            'SAFE': (0, 255, 0),        # Green
            'WARNING': (0, 255, 255),   # Yellow
            'CRITICAL': (0, 0, 255)     # Red
        }
        
        # Thresholds from config
        safety_config = config.get('safety', {})
        self.warning_threshold = safety_config.get('warning_threshold', 2.0)
        self.violation_threshold = safety_config.get('violation_threshold', 8.0)
        
        # Border thickness
        self.border_thickness = 5
        
        print("✅ Safety Overlay initialized")
    
    def update_state(self, safety_state: str, violation_active: bool):
        """
        Update safety state and track violation duration
        """
        self.safety_state = safety_state
        
        if violation_active:
            if self.violation_start_time is None:
                self.violation_start_time = time.time()
        else:
            self.violation_start_time = None
    
    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw all overlays on frame
        
        Returns:
            Frame with overlays drawn
        """
        h, w = frame.shape[:2]
        
        # Get current violation duration
        violation_duration = 0
        if self.violation_start_time is not None:
            violation_duration = time.time() - self.violation_start_time
        
        # Get color for current state
        border_color = self.state_colors.get(self.safety_state, (0, 255, 0))
        
        # 1. Draw RED BORDER around entire screen
        # This is the most prominent visual alert
        cv2.rectangle(frame, (0, 0), (w, h), border_color, self.border_thickness)
        
        # Add inner border for better visibility
        cv2.rectangle(frame, (self.border_thickness, self.border_thickness),
                     (w - self.border_thickness, h - self.border_thickness),
                     border_color, 1)
        
        # 2. Draw TIME BAR (progress bar showing violation duration)
        if self.violation_start_time is not None:
            # Calculate progress (0 to 1)
            if self.safety_state == 'WARNING':
                max_duration = self.warning_threshold
                bar_color = (0, 255, 255)  # Yellow
            else:  # CRITICAL
                max_duration = self.violation_threshold
                bar_color = (0, 0, 255)  # Red
            
            progress = min(violation_duration / max_duration, 1.0)
            
            # Draw time bar at bottom of screen
            bar_height = 8
            bar_width = int(w * progress)
            bar_y = h - bar_height - 10
            
            # Background bar (dark)
            cv2.rectangle(frame, (10, bar_y), (w - 10, bar_y + bar_height), (50, 50, 50), -1)
            
            # Progress bar (colored)
            cv2.rectangle(frame, (10, bar_y), (10 + bar_width, bar_y + bar_height), bar_color, -1)
            
            # Add time text
            time_text = f"Violation: {violation_duration:.1f}s / {max_duration}s"
            cv2.putText(frame, time_text, (20, bar_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, bar_color, 1)
        
        return frame
    
    def draw_time_bar(self, frame: np.ndarray, duration: float, 
                      max_duration: float, color: tuple) -> np.ndarray:
        """
        Draw a time/progress bar
        """
        h, w = frame.shape[:2]
        bar_height = 8
        bar_width = int(w * (duration / max_duration))
        bar_y = h - bar_height - 10
        
        # Background
        cv2.rectangle(frame, (10, bar_y), (w - 10, bar_y + bar_height), (50, 50, 50), -1)
        
        # Progress
        cv2.rectangle(frame, (10, bar_y), (10 + bar_width, bar_y + bar_height), color, -1)
        
        return frame