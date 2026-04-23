"""
Safety Monitor - SIMPLE VERSION (No database, just safety)
"""
import cv2
import time
from typing import Dict, Optional


class SafetyMonitor:
    """
    Simple safety monitoring - no database, just hands and face detection
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
        
        # Simple session flag (no database)
        self.session_active = False
        self.employee_id = None
        self.batch_id = None
        
        print("✅ Safety Monitor initialized (SIMPLE MODE - no database)")
    
    def start_work_session(self, employee_id: str, batch_id: str = None):
        """Simple session start - no database"""
        self.session_active = True
        self.employee_id = employee_id
        self.batch_id = batch_id
        print(f"\n✅ WORK SESSION STARTED")
        print(f"   Employee ID: {employee_id}")
        print(f"   Batch ID: {batch_id}")
        print(f"   Now monitoring hands and face...\n")
        return True
    
    def end_work_session(self):
        """Simple session end"""
        if self.session_active:
            print(f"\n🏁 WORK SESSION ENDED")
            print(f"   Employee: {self.employee_id}")
            print(f"   Batch: {self.batch_id}\n")
            self.session_active = False
            self.employee_id = None
            self.batch_id = None
    
    def process_frame(self, frame):
        """Process frame with all detectors"""
        # 1. Face mesh and orientation
        frame = self.face_mesh_detector.detect_face_mesh(frame)
        self.current_face_orientation = self.face_mesh_detector.get_face_orientation(frame)
        
        # 2. Hand detection
        frame, hands_info = self.hand_mesh_detector.detect_hands(frame)
        self.current_hand_positions = self.hand_mesh_detector.get_hand_positions(hands_info)
        self.current_hand_zones = self.zone_manager.check_hand_zone(self.current_hand_positions)
        
        # 3. Determine safety state
        self.safety_state = self._determine_safety_state()
        
        # 4. Update visual elements
        is_violation = self.safety_state != 'SAFE'
        self.safety_overlay.update_state(self.safety_state, is_violation)
        self.status_panel.update_violation_state(self.safety_state, is_violation)
        
        # 5. Draw zones and overlays
        frame = self.zone_drawer.draw_zones(frame)
        frame = self.safety_overlay.draw(frame)
        
        # 6. Draw status panel
        fps = self.camera.get_actual_fps() if hasattr(self.camera, 'get_actual_fps') else 0
        frame = self.status_panel.draw(frame, self.safety_state, self.current_face_orientation,
                                       self.current_hand_zones, fps)
        
        return frame
    
    def _determine_safety_state(self) -> str:
        """Determine safety state based on face and hands"""
        # Critical: Face tilted down
        if self.current_face_orientation == 'Tilted Down':
            return 'CRITICAL'
        
        # Check hand status
        hands_detected = any(zone != 'Not Detected' for zone in self.current_hand_zones.values())
        hands_in_zone = any(zone == 'Hand Zone' for zone in self.current_hand_zones.values())
        
        # No hands detected
        if not hands_detected:
            return 'WARNING'
        
        # Hands outside zone
        if hands_detected and not hands_in_zone:
            return 'WARNING'
        
        # No face
        if self.current_face_orientation == 'No Face':
            return 'WARNING'
        
        # All good
        return 'SAFE'