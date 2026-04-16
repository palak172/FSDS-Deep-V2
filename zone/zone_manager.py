"""
Zone management for safety monitoring - SHOWS ONLY HAND ZONE
"""
import cv2
import numpy as np
from typing import Dict, Tuple, List, Optional


class ZoneManager:
    """
    Manages safety zones - MODIFIED to only show Hand Zone (safe zone)
    All danger/warning zones are ignored from display
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Load zones from config
        self.zones = {}
        self.safe_zone_name = None
        self.danger_zone_name = None
        
        zones_config = config.get('zones', {})
        
        for zone_name, zone_data in zones_config.items():
            points = np.array(zone_data['points'], np.int32)
            zone_type = zone_data.get('type', 'unknown')
            
            self.zones[zone_name] = {
                'points': points,
                'color': tuple(zone_data['color']),
                'label': zone_data['label'],
                'type': zone_type
            }
            
            # Track which zone is which
            if zone_type == 'safe':
                self.safe_zone_name = zone_name
            elif zone_type == 'danger':
                self.danger_zone_name = zone_name
        
        # Load safety rules
        self.safety_rules = config.get('safety_rules', {})
        
        # Visualization settings
        vis_config = config.get('visualization', {})
        self.zone_opacity = vis_config.get('zone_opacity', 0.3)
        self.hand_radius = vis_config.get('hand_radius', 12)
        self.colors = vis_config.get('colors', {})
        
        print(f"✅ Zone Manager initialized")
        print(f"   Safe zone: {self.safe_zone_name} (ONLY THIS ZONE WILL BE DISPLAYED)")
        if self.danger_zone_name:
            print(f"   Danger zone: {self.danger_zone_name} (HIDDEN - not displayed)")
    
    def get_only_hand_zone_points(self) -> Optional[np.ndarray]:
        """
        Get the points of the Hand Zone (safe zone) only
        
        Returns:
            Points array of the hand zone, or None if not found
        """
        if self.safe_zone_name and self.safe_zone_name in self.zones:
            return self.zones[self.safe_zone_name]['points']
        return None
    
    def get_only_hand_zone_info(self) -> Optional[Dict]:
        """
        Get the full Hand Zone info (label, color, points)
        
        Returns:
            Dictionary with hand zone info, or None if not found
        """
        if self.safe_zone_name and self.safe_zone_name in self.zones:
            return self.zones[self.safe_zone_name]
        return None
    
    def check_hand_zone(self, hand_positions: Dict[str, Optional[Tuple[int, int]]]) -> Dict[str, str]:
        """
        Check which zone each hand is in - ONLY checks Hand Zone
        
        Returns:
            Dictionary with zone names:
            - 'Hand Zone' if inside safe zone
            - 'Outside Safe Zone' if hand detected but outside
            - 'Not Detected' if no hand
        """
        hand_status = {}
        
        for hand_name, position in hand_positions.items():
            if position is None:
                hand_status[hand_name] = 'Not Detected'
                continue
            
            # ONLY check if in SAFE zone (Hand Zone)
            if self.safe_zone_name:
                safe_points = self.zones[self.safe_zone_name]['points']
                result = cv2.pointPolygonTest(safe_points, position, False)
                if result >= 0:
                    hand_status[hand_name] = self.zones[self.safe_zone_name]['label']
                    continue
            
            # If not in safe zone
            hand_status[hand_name] = 'Outside Safe Zone'
        
        return hand_status
    
    def get_hands_in_safe_zone(self, hand_status: Dict[str, str]) -> int:
        """Count how many hands are in the safe zone"""
        count = 0
        for hand, zone in hand_status.items():
            if zone == self.zones.get(self.safe_zone_name, {}).get('label', 'Hand Zone'):
                count += 1
        return count
    
    def get_hands_in_danger_zone(self, hand_status: Dict[str, str]) -> int:
        """DANGER ZONE DISABLED - always returns 0"""
        return 0
    
    def get_total_hands_detected(self, hand_status: Dict[str, str]) -> int:
        """Count total number of hands detected"""
        count = 0
        for hand, zone in hand_status.items():
            if zone != 'Not Detected':
                count += 1
        return count
    
    def is_hand_safety_violated(self, hand_status: Dict[str, str]) -> bool:
        """
        Check if there's a hand safety violation
        Returns True if hands are detected but NOT in safe zone
        """
        total_hands = self.get_total_hands_detected(hand_status)
        hands_in_safe = self.get_hands_in_safe_zone(hand_status)
        
        # If hands are detected but not in safe zone, that's a violation
        if total_hands > 0 and hands_in_safe == 0:
            return True
        
        return False
    
    def get_all_zones(self) -> Dict:
        """
        Returns ONLY the Hand Zone (safe zone) for drawing
        All other zones are filtered out
        """
        if self.safe_zone_name:
            return {self.safe_zone_name: self.zones[self.safe_zone_name]}
        return {}