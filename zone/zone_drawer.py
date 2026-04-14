"""
Zone visualization - draws zones on the frame
"""
import cv2
import numpy as np
from typing import Dict


class ZoneDrawer:
    """
    Draws safety zones on the camera feed
    """
    
    def __init__(self, zone_manager):
        self.zone_manager = zone_manager
        self.config = zone_manager.config
    
    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw all zones on the frame with transparency
        """
        # Create overlay for transparent fill
        overlay = frame.copy()
        
        for zone_name, zone_data in self.zone_manager.zones.items():
            points = zone_data['points']
            color = zone_data['color']
            label = zone_data['label']
            
            # Draw filled polygon on overlay
            cv2.fillPoly(overlay, [points], color)
            
            # Draw outline on main frame
            cv2.polylines(frame, [points], True, (255, 255, 255), 2)
            
            # Add zone label
            center = np.mean(points, axis=0).astype(int)
            cv2.putText(frame, label, (center[0] - 40, center[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Blend overlay with original frame
        opacity = self.zone_manager.zone_opacity
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        
        return frame