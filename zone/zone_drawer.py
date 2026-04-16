"""
Zone Drawer - Draws ONLY the Hand Zone (safe zone) on the camera feed
All other zones (danger, warning) are hidden
"""
import cv2
import numpy as np
from typing import Dict


class ZoneDrawer:
    """
    Draws only the Hand Zone (safe zone) on the frame
    No other zones are displayed
    """
    
    def __init__(self, zone_manager):
        """
        Initialize zone drawer with zone manager
        
        Args:
            zone_manager: ZoneManager instance
        """
        self.zone_manager = zone_manager
        print("✅ ZoneDrawer initialized (ONLY Hand Zone will be drawn)")
    
    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw ONLY the Hand Zone (safe zone) on the frame
        
        Args:
            frame: The image frame to draw on
        
        Returns:
            Frame with Hand Zone drawn (if exists)
        """
        # Get ONLY the hand zone (safe zone)
        hand_zone_info = self.zone_manager.get_only_hand_zone_info()
        
        if hand_zone_info is None:
            # No hand zone defined in config
            return frame
        
        points = hand_zone_info['points']
        color = hand_zone_info['color']
        label = hand_zone_info['label']
        
        # Reshape points for drawing
        pts = points.reshape((-1, 1, 2))
        
        # Draw semi-transparent filled polygon
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], color)
        cv2.addWeighted(overlay, self.zone_manager.zone_opacity, frame, 0.7, 0, frame)
        
        # Draw polygon outline
        cv2.polylines(frame, [pts], True, color, 2)
        
        # Draw zone label
        # Calculate center of polygon for label placement
        center_x = int(sum(p[0] for p in points) / len(points))
        center_y = int(sum(p[1] for p in points) / len(points))
        
        # Put label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        label_x = center_x - label_size[0] // 2
        label_y = center_y - 10
        
        cv2.rectangle(frame, 
                     (label_x - 5, label_y - label_size[1] - 5),
                     (label_x + label_size[0] + 5, label_y + 5),
                     (0, 0, 0), -1)
        cv2.putText(frame, label, (label_x, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
    
    def draw_all_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Legacy method - now just calls draw_zones() to show only Hand Zone
        """
        return self.draw_zones(frame)