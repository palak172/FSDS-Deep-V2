"""
Test script with proper controls and release button
This will keep the camera window open until you press 'q'
"""
import sys
import cv2
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.camera_manager import CameraManager
from detection.face_detector import FaceDetector


class CameraTestController:
    """
    Controller that properly manages camera lifecycle
    """
    
    def __init__(self):
        self.camera = None
        self.face_detector = None
        self.is_running = False
        self.window_name = 'Safety System - Camera Test'
        
    def initialize(self):
        """Initialize all components"""
        print("\n" + "=" * 60)
        print("SAFETY SYSTEM - CAMERA TEST")
        print("=" * 60)
        
        # Load config
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            print("✅ Configuration loaded")
        except FileNotFoundError:
            print("❌ config.json not found!")
            return False
        
        # Initialize camera
        camera_config = self.config.get('camera', {})
        self.camera = CameraManager(camera_config)
        
        if not self.camera.start():
            print("❌ Failed to start camera!")
            return False
        
        print("✅ Camera initialized")
        
        # Initialize face detector
        self.face_detector = FaceDetector(self.config)
        print("✅ Face detector ready")
        
        return True
    
    def run(self):
        """Main loop - keeps camera open until user quits"""
        if not self.initialize():
            return
        
        self.is_running = True
        
        print("\n" + "-" * 60)
        print("🎥 CAMERA IS LIVE!")
        print("-" * 60)
        print("\nCONTROLS:")
        print("  'q' or 'ESC' - Quit and release camera")
        print("  's'          - Save screenshot")
        print("  'r'          - Reset camera (if frozen)")
        print("  'h'          - Show this help")
        print("\n" + "-" * 60)
        
        try:
            while self.is_running:
                # Read frame
                success, frame = self.camera.read_frame()
                
                if not success:
                    print("⚠️ Failed to read frame, retrying...")
                    cv2.waitKey(100)
                    continue
                
                # Process with face detector
                faces = self.face_detector.detect_faces(frame)
                status = self.face_detector.get_orientation_status(faces)
                
                # Draw face boxes
                for face in faces:
                    frame = self.face_detector.draw_face(frame, face)
                
                # Draw control panel
                self._draw_controls(frame, status)
                
                # Draw FPS
                fps = self.camera.get_actual_fps()
                cv2.putText(frame, f"FPS: {fps:.1f}", 
                           (frame.shape[1] - 100, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Show the frame
                cv2.imshow(self.window_name, frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("\n🛑 User requested quit")
                    break
                elif key == ord('s'):
                    self._save_screenshot(frame)
                elif key == ord('r'):
                    self._reset_camera()
                elif key == ord('h'):
                    self._show_help()
                    
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.cleanup()
    
    def _draw_controls(self, frame, status):
        """Draw control panel on frame"""
        h, w = frame.shape[:2]
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Title
        cv2.putText(frame, "SAFETY DETECTION SYSTEM", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Camera status
        status_text = "● LIVE" if self.camera.is_streaming else "○ PAUSED"
        status_color = (0, 255, 0) if self.camera.is_streaming else (0, 0, 255)
        cv2.putText(frame, status_text, (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Face status
        if status['has_face']:
            orientation = status['orientation']
            color = (0, 255, 0) if orientation == 'Forward' else (0, 0, 255)
            cv2.putText(frame, f"Face: {orientation}", (20, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, f"Confidence: {status['primary_confidence']:.2f}", 
                       (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        else:
            cv2.putText(frame, "Face: NOT DETECTED", (20, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Controls hint
        cv2.putText(frame, "Press 'q' to quit | 's' save | 'h' help", 
                   (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _save_screenshot(self, frame):
        """Save screenshot with timestamp"""
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot saved: {filename}")
    
    def _reset_camera(self):
        """Reset camera if frozen"""
        print("🔄 Resetting camera...")
        self.camera.release()
        time.sleep(1)
        if self.camera.start():
            print("✅ Camera reset successful")
        else:
            print("❌ Camera reset failed")
    
    def _show_help(self):
        """Show help overlay"""
        print("\n" + "=" * 40)
        print("CONTROLS SUMMARY")
        print("=" * 40)
        print("q / ESC - Quit and release camera")
        print("s       - Save screenshot")
        print("r       - Reset camera (if frozen)")
        print("h       - Show this help")
        print("=" * 40 + "\n")
    
    def cleanup(self):
        """Proper cleanup of all resources"""
        print("\n🧹 Cleaning up...")
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        print("✅ Camera released")
        print("✅ Windows closed")
        print("\nTest completed successfully!")


def main():
    """Main entry point"""
    controller = CameraTestController()
    controller.run()


if __name__ == "__main__":
    main()