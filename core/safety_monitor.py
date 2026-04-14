"""
Safety Monitor - Core logic that combines all modules with mesh detection
"""
import cv2
import time
from typing import Dict, Optional


class SafetyMonitor:
    """
    Main safety monitoring system with mesh detection
    """
    
    def __init__(self, camera, face_detector, face_mesh_detector, 
                 hand_detector, hand_mesh_detector, zone_manager,
                 hand_drawer, zone_drawer, status_panel, safety_overlay, logger):
        
        self.camera = camera
        self.face_detector = face_detector
        self.face_mesh_detector = face_mesh_detector
        self.hand_detector = hand_detector
        self.hand_mesh_detector = hand_mesh_detector
        self.zone_manager = zone_manager
        self.hand_drawer = hand_drawer
        self.zone_drawer = zone_drawer
        self.status_panel = status_panel
        self.safety_overlay = safety_overlay
        self.logger = logger
        
        # Safety state tracking
        self.safety_state = 'SAFE'
        self.violation_start_time = None
        self.last_log_time = 0
        
        # Current frame data
        self.current_face_orientation = 'No Face'
        self.current_hand_positions = {'left': None, 'right': None}
        self.current_hand_zones = {'left': 'Not Detected', 'right': 'Not Detected'}
    
    def process_frame(self, frame):
        """
        Process a single frame through all detectors with mesh drawing
        """
        # 1. Draw FACE MESH (full face with eyes)
        frame = self.face_mesh_detector.detect_face_mesh(frame)
        
        # 2. Detect face orientation
        self.current_face_orientation = self.face_mesh_detector.get_face_orientation(frame)
        
        # 3. Detect HANDS with mesh
        frame, hands_info = self.hand_mesh_detector.detect_hands(frame)
        
        # 4. Get hand positions for zone checking
        self.current_hand_positions = self.hand_mesh_detector.get_hand_positions(hands_info)
        
        # 5. Check hand zones
        self.current_hand_zones = self.zone_manager.check_hand_zone(self.current_hand_positions)
        
        # 6. Determine safety state
        self.safety_state = self._determine_safety_state()
        
        # 7. Update safety overlay with violation tracking
        is_violation = self.safety_state != 'SAFE'
        self.safety_overlay.update_state(self.safety_state, is_violation)
        self.status_panel.update_violation_state(self.safety_state, is_violation)
        
        # 8. Draw zones
        frame = self.zone_drawer.draw_zones(frame)
        
        # 9. Draw safety overlay (red border + time bar)
        frame = self.safety_overlay.draw(frame)
        
        # 10. Draw status panel
        fps = self.camera.get_actual_fps() if hasattr(self.camera, 'get_actual_fps') else 0
        frame = self.status_panel.draw(frame, self.safety_state, self.current_face_orientation,
                                       self.current_hand_zones, fps)
        
        # 11. Log violations
        self._log_if_needed()
        
        return frame
    
    def _determine_safety_state(self) -> str:
        """
        Determine safety state based on face orientation and hand positions
        """
        # CRITICAL: Face tilted down
        if self.current_face_orientation == 'Tilted Down':
            return 'CRITICAL'
        
        # WARNING: No face detected
        if self.current_face_orientation == 'No Face':
            return 'WARNING'
        
        # WARNING: Hands in danger zone
        for hand, zone in self.current_hand_zones.items():
            if zone == 'DANGER ZONE':
                return 'WARNING'
        
        # SAFE: All conditions normal
        return 'SAFE'
    
    def _log_if_needed(self):
        """Log violations periodically"""
        current_time = time.time()
        
        if self.safety_state != 'SAFE' and current_time - self.last_log_time > 5:
            hands_in_safe = sum(1 for z in self.current_hand_zones.values() 
                               if z in ['Hand Zone', 'Work Area'])
            total_hands = sum(1 for z in self.current_hand_zones.values() 
                            if z != 'Not Detected')
            
            self.logger.log_violation(
                self.safety_state,
                self.current_face_orientation,
                self.current_hand_zones,
                hands_in_safe,
                total_hands
            )
            self.last_log_time = current_time