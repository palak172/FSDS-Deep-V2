"""
Factory Safety Detection System - Main Entry Point with Mesh Detection
"""
import sys
import cv2
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.camera_manager import CameraManager
from detection.face_mesh_detector import FaceMeshDetector
from detection.hand_mesh_detector import HandMeshDetector
from zone.zone_manager import ZoneManager
from zone.zone_drawer import ZoneDrawer
from visualization.hand_drawer import HandDrawer
from visualization.status_panel import StatusPanel
from visualization.safety_overlay import SafetyOverlay
from utils.logger import SafetyLogger
from core.safety_monitor import SafetyMonitor


class SafetySystem:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = None
        self.camera = None
        self.face_mesh_detector = None
        self.hand_mesh_detector = None
        self.zone_manager = None
        self.zone_drawer = None
        self.hand_drawer = None
        self.status_panel = None
        self.safety_overlay = None
        self.logger = None
        self.monitor = None
        
        self.is_running = False
        self.window_name = 'Safety Detection System'
    
    def initialize(self):
        """Initialize all components"""
        print("=" * 60)
        print("FACTORY SAFETY DETECTION SYSTEM")
        print("with Face & Hand Mesh Detection")
        print("=" * 60)
        
        # Load configuration
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            print("✅ Configuration loaded")
        except FileNotFoundError:
            print(f"❌ config.json not found")
            return False
        
        # Initialize camera
        camera_config = self.config.get('camera', {})
        self.camera = CameraManager(camera_config)
        if not self.camera.start():
            print("❌ Failed to start camera")
            return False
        print("✅ Camera initialized")
        
        # Initialize mesh detectors
        self.face_mesh_detector = FaceMeshDetector(self.config)
        self.hand_mesh_detector = HandMeshDetector(self.config)
        print("✅ Face & Hand Mesh detectors initialized")
        
        # Initialize zone management
        self.zone_manager = ZoneManager(self.config)
        self.zone_drawer = ZoneDrawer(self.zone_manager)
        print("✅ Zone manager initialized")
        
        # Initialize visualization
        self.hand_drawer = HandDrawer(self.config)
        self.status_panel = StatusPanel(self.config)
        self.safety_overlay = SafetyOverlay(self.config)
        print("✅ Visualization initialized")
        
        # Initialize logger
        self.logger = SafetyLogger()
        self.logger.log_info("System started")
        print("✅ Logger initialized")
        
        # Initialize safety monitor
        self.monitor = SafetyMonitor(
            self.camera, None, self.face_mesh_detector,
            None, self.hand_mesh_detector, self.zone_manager,
            self.hand_drawer, self.zone_drawer, self.status_panel,
            self.safety_overlay, self.logger
        )
        print("✅ Safety monitor initialized")
        
        return True
    
    def run(self):
        """Main loop"""
        if not self.initialize():
            return
        
        self.is_running = True
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)
        
        print("\n🎥 SYSTEM IS LIVE!")
        print("Press 'q' to quit, 's' for screenshot\n")
        
        try:
            while self.is_running:
                success, frame = self.camera.read_frame()
                
                if not success:
                    continue
                
                processed_frame = self.monitor.process_frame(frame)
                cv2.imshow(self.window_name, processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('s'):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"screenshot_{timestamp}.png", processed_frame)
                    print(f"📸 Screenshot saved")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("System shutdown complete")


if __name__ == "__main__":
    system = SafetySystem('config.json')
    system.run()