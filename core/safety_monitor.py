"""
Safety Monitor - Supabase Database Version
"""
import cv2
import time
from datetime import datetime
from typing import Dict, Optional
from supabase import create_client

# ========== SUPABASE CONFIGURATION ==========
# Replace these with your actual values from Supabase dashboard
SUPABASE_URL = "https://ohzxcmigfhhgvkzlaviw.supabase.co"  # ← YOUR URL
SUPABASE_KEY = "sb_publishable_dnBykYQQjBgwXuzkhoI7YQ_ohPS395c"  # ← YOUR KEY

class SafetyMonitor:
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
        
        # Session tracking
        self.session_active = False
        self.current_session_id = None
        self.current_employee = None
        self.current_batch = None
        
        # Connect to Supabase
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase connected!")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            self.supabase = None 
    
    
    def start_work_session(self, employee_id: str, batch_id: str = None, product_name: str = None):
            """Start a new work session - auto-creates batch if needed"""
            if not self.supabase:
                print("❌ No database connection")
                return False
            
            try:
                # 1. Find employee
                employee = self.supabase.table('employees')\
                    .select('employee_id, full_name')\
                    .eq('employee_id', employee_id)\
                    .eq('is_active', True)\
                    .execute()
                
                if not employee.data:
                    print(f"❌ Employee {employee_id} not found")
                    return False
                
                self.current_employee = employee.data[0]
                self.status_panel.update_employee(self.current_employee['full_name'])
                
                # 2. Check if batch exists
                existing_batch = self.supabase.table('production_batches')\
                    .select('batch_id')\
                    .eq('batch_id', batch_id)\
                    .execute()
                
                if not existing_batch.data:
                    # Batch doesn't exist - create it
                    if product_name is None:
                        product_name = f"Product_{batch_id}"
                    
                    print(f"📦 Creating new batch: {batch_id} - {product_name}")
                    
                    self.supabase.table('production_batches')\
                        .insert({
                            'batch_id': batch_id,
                            'product_name': product_name,
                            'status': 'active',
                            'start_time': datetime.now().isoformat()
                        })\
                        .execute()
                    
                    print(f"✅ New batch created!")
                
                # 3. Create work session
                result = self.supabase.table('work_sessions')\
                    .insert({
                        'employee_id': employee_id,
                        'batch_id': batch_id,
                        'session_start': datetime.now().isoformat()
                    })\
                    .execute()
                self.status_panel.start_session_timer()
                self.current_session_id = result.data[0]['session_id']
                self.session_active = True
                
                print(f"\n✅ SESSION STARTED")
                print(f"   Employee: {self.current_employee['full_name']}")
                print(f"   Batch: {batch_id}")
                print(f"   Session ID: {self.current_session_id}")
                
                return True
        
            except Exception as e:
                print(f"❌ Session error: {e}")
                return False
    


    def check_batch_exists(self, batch_id: str) -> bool:
        """Check if a batch already exists in the database"""
        if not self.supabase:
            return False
        
        try:
            result = self.supabase.table('production_batches')\
                .select('batch_id')\
                .eq('batch_id', batch_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking batch: {e}")
            return False

    def create_batch_and_start_session(self, employee_id: str, batch_id: str, product_name: str = None):
        """Create a new batch and start work session"""
        if not self.supabase:
            print("❌ No database connection")
            return False
        
        try:
            # 1. Find employee
            employee = self.supabase.table('employees')\
                .select('employee_id, full_name')\
                .eq('employee_id', employee_id)\
                .eq('is_active', True)\
                .execute()
            
            if not employee.data:
                print(f"❌ Employee {employee_id} not found")
                return False
            
            self.current_employee = employee.data[0]
            self.status_panel.update_employee(self.current_employee['full_name'])
            
            # 2. Create new batch
            if not product_name:
                product_name = f"Product_{batch_id}"
            
            print(f"📦 Creating new batch: {batch_id} - {product_name}")
            
            self.supabase.table('production_batches')\
                .insert({
                    'batch_id': batch_id,
                    'product_name': product_name,
                    'status': 'active',
                    'start_time': datetime.now().isoformat()
                })\
                .execute()
            
            print(f"✅ New batch created!")
            
            # 3. Create work session
            result = self.supabase.table('work_sessions')\
                .insert({
                    'employee_id': employee_id,
                    'batch_id': batch_id,
                    'session_start': datetime.now().isoformat()
                })\
                .execute()
            
            self.current_session_id = result.data[0]['session_id']
            self.session_active = True
            
            print(f"\n✅ SESSION STARTED")
            print(f"   Employee: {self.current_employee['full_name']}")
            print(f"   Batch: {batch_id} (NEW)")
            print(f"   Session ID: {self.current_session_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Session error: {e}")
            return False

    def end_work_session(self):
        """End current session"""
        if not self.session_active or not self.supabase:
            return
        self.status_panel.end_session_timer()
        
        try:
            self.supabase.table('work_sessions')\
                .update({
                    'session_end': datetime.now().isoformat(),
                    'safety_status_at_end': self.safety_state
                })\
                .eq('session_id', self.current_session_id)\
                .execute()
            
            print(f"\n🏁 SESSION ENDED")
            print(f"   Final Status: {self.safety_state}")
            
            self.session_active = False
            

        except Exception as e:
            print(f"Error ending session: {e}")
    
    def log_violation(self, violation_type: str, severity: str):
        """Log violation to Supabase (no counter)"""
        if not self.session_active or not self.supabase:
            return
        
        try:
            self.supabase.table('safety_violations')\
                .insert({
                    'session_id': self.current_session_id,
                    'violation_type': violation_type,
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                })\
                .execute()
            
            print(f"📝 Violation: {violation_type}")
            
        except Exception as e:
            print(f"Log error: {e}")

    def get_violation_count(self, session_id):
        result = self.supabase.table('safety_violations')\
            .select('*', count='exact')\
            .eq('session_id', session_id)\
            .execute()
        return result.count
    
    def process_frame(self, frame):
        """Process frame with detection"""
        # Face mesh and orientation
        frame = self.face_mesh_detector.detect_face_mesh(frame)
        self.current_face_orientation = self.face_mesh_detector.get_face_orientation(frame)
        
        # Hand detection
        frame, hands_info = self.hand_mesh_detector.detect_hands(frame)
        self.current_hand_positions = self.hand_mesh_detector.get_hand_positions(hands_info)
        self.current_hand_zones = self.zone_manager.check_hand_zone(self.current_hand_positions)
        
        # Safety state
        self.safety_state = self._determine_safety_state()
        
        # Visuals
        is_violation = self.safety_state != 'SAFE'
        self.safety_overlay.update_state(self.safety_state, is_violation)
        self.status_panel.update_violation_state(self.safety_state, is_violation)
        
        frame = self.zone_drawer.draw_zones(frame)
        frame = self.safety_overlay.draw(frame)
        
        fps = self.camera.get_actual_fps() if hasattr(self.camera, 'get_actual_fps') else 0
        frame = self.status_panel.draw(frame, self.safety_state, self.current_face_orientation,
                                       self.current_hand_zones, fps)
        
        # Log violations
        self._log_if_needed()
        
        return frame
    
    def _determine_safety_state(self) -> str:
        if self.current_face_orientation == 'Tilted Down':
            return 'CRITICAL'
        
        hands_detected = any(zone != 'Not Detected' for zone in self.current_hand_zones.values())
        hands_in_zone = any(zone == 'Hand Zone' for zone in self.current_hand_zones.values())
        
        if not hands_detected:
            return 'WARNING'
        if hands_detected and not hands_in_zone:
            return 'WARNING'
        if self.current_face_orientation == 'No Face':
            return 'WARNING'
        
        return 'SAFE'
    
    def _log_if_needed(self):
        current_time = time.time()
        
        if self.safety_state != 'SAFE' and current_time - self.last_log_time > 5:
            if self.current_face_orientation == 'Tilted Down':
                self.log_violation('face_tilted_down', 'CRITICAL')
            elif self.current_face_orientation == 'No Face':
                self.log_violation('face_not_detected', 'WARNING')
            elif any(zone == 'Outside Safe Zone' for zone in self.current_hand_zones.values()):
                self.log_violation('hands_outside_zone', 'WARNING')
            
            self.last_log_time = current_time