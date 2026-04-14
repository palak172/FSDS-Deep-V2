"""
Hand Drawer - Draws hand positions on the camera feed
This module specifically handles visual representation of hands
"""
import cv2
import numpy as np
from typing import Dict, Tuple, Optional


class HandDrawer:
    """
    Draws hand positions with colors based on which zone they're in
    
    Zone colors:
    - Work Area / Hand Zone: Green (Safe)
    - Danger Zone: Red (Danger)
    - Outside Zones: Yellow (Warning)
    - Not Detected: Gray
    """
    
    def __init__(self, config: dict):
        """
        Initialize hand drawer with configuration
        
        Args:
            config: Configuration dictionary from config.json
        """
        self.config = config
        
        # Get visualization settings from config
        vis_config = config.get('visualization', {})
        self.hand_radius = vis_config.get('hand_radius', 12)
        self.colors = vis_config.get('colors', {})
        
        # Define colors for different zones (BGR format for OpenCV)
        # These match your screenshot expectations
        self.zone_colors = {
            'Work Area': (0, 255, 0),      # Green - Safe zone
            'Hand Zone': (0, 255, 0),       # Green - Safe zone
            'Danger Zone': (0, 0, 255),     # Red - Danger zone
            'Outside Zones': (0, 255, 255), # Yellow - Warning
            'Unsafe Area': (0, 255, 255),   # Yellow - Warning
            'Not Detected': (128, 128, 128) # Gray - Not found
        }
        
        print(f"✅ HandDrawer initialized (radius: {self.hand_radius}px)")
    
    def draw_hands(self, frame: np.ndarray, 
                   hand_positions: Dict[str, Optional[Tuple[int, int]]],
                   hand_zones: Dict[str, str]) -> np.ndarray:
        """
        Draw hand positions on the frame with zone-based colors
        
        Args:
            frame: The image frame to draw on
            hand_positions: Dictionary with 'left' and 'right' wrist positions
            hand_zones: Dictionary with zone names for each hand
        
        Returns:
            Frame with hand drawings (modified in-place)
        
        Example:
            >>> hand_positions = {'left': (300, 400), 'right': (500, 400)}
            >>> hand_zones = {'left': 'Work Area', 'right': 'Danger Zone'}
            >>> frame = hand_drawer.draw_hands(frame, hand_positions, hand_zones)
        """
        for hand_name, position in hand_positions.items():
            if position is None:
                continue
            
            # Get zone for this hand
            zone = hand_zones.get(hand_name, 'Not Detected')
            
            # Get color based on zone
            color = self.zone_colors.get(zone, (0, 255, 255))  # Default yellow
            
            # Draw outer circle (white border)
            cv2.circle(frame, position, self.hand_radius + 2, (255, 255, 255), 2)
            
            # Draw inner circle (zone color)
            cv2.circle(frame, position, self.hand_radius, color, -1)
            
            # Draw center dot (for precision)
            cv2.circle(frame, position, 3, (255, 255, 255), -1)
            
            # Add hand label above the circle
            label = f"{hand_name.capitalize()} Hand"
            label_position = (position[0] - 30, position[1] - self.hand_radius - 5)
            cv2.putText(frame, label, label_position,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Add zone label below the circle (if not "Not Detected")
            if zone != 'Not Detected':
                zone_label = zone
                zone_position = (position[0] - 35, position[1] + self.hand_radius + 15)
                cv2.putText(frame, zone_label, zone_position,
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
    
    def draw_hand_skeleton(self, frame: np.ndarray, hand_landmarks, 
                           handedness: str) -> np.ndarray:
        """
        Optional: Draw full hand skeleton (if you need finger tracking later)
        
        This is for future expansion - not needed for basic wrist tracking
        """
        import mediapipe as mp
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        
        # Draw hand landmarks
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
        )
        
        return frame
    
    def get_hand_color_by_zone(self, zone: str) -> Tuple[int, int, int]:
        """
        Get the color for a hand based on its zone
        
        Args:
            zone: Zone name (e.g., 'Work Area', 'Danger Zone')
        
        Returns:
            RGB color tuple (B, G, R for OpenCV)
        """
        return self.zone_colors.get(zone, (0, 255, 255))