"""
Hand Drawer - Minimal version (no visual drawing)
Hand skeleton is already drawn by HandMeshDetector
"""
import cv2
import numpy as np
from typing import Dict, Tuple, Optional


class HandDrawer:
    """
    Minimal hand drawer - does NOT draw any circles or labels
    Hand skeleton is handled by HandMeshDetector
    """
    
    def __init__(self, config: dict):
        """
        Initialize hand drawer (minimal mode - no drawing)
        """
        self.config = config
        print("✅ HandDrawer initialized (MINIMAL MODE - no circles/labels)")
    
    def draw_hands(self, frame: np.ndarray, 
                   hand_positions: Dict[str, Optional[Tuple[int, int]]],
                   hand_zones: Dict[str, str]) -> np.ndarray:
        """
        NO DRAWING - returns frame unchanged
        
        Hand skeleton is already drawn by HandMeshDetector
        """
        # Do nothing - return frame as is
        return frame
    
    def draw_hand_skeleton(self, frame: np.ndarray, hand_landmarks, 
                           handedness: str) -> np.ndarray:
        """
        NO DRAWING - returns frame unchanged
        """
        return frame
    
    def get_hand_color_by_zone(self, zone: str) -> Tuple[int, int, int]:
        """
        Returns color (not used since no drawing)
        """
        return (0, 255, 0)  # Green default