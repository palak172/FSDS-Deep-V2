"""
Camera Manager - Handles all camera operations with 16:9 aspect ratio
"""
import cv2
import time
from typing import Optional, Tuple
import numpy as np


class CameraManager:
    """
    Manages camera with proper 16:9 aspect ratio
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Get camera settings
        self.camera_type = config.get('type', 'usb_camera')
        self.source = config.get('source', 0)
        
        # Force 16:9 resolution
        self.width = config.get('width', 1280)
        self.height = config.get('height', 720)
        self.target_fps = config.get('fps', 30)
        
        # Verify 16:9 ratio
        expected_ratio = self.width / self.height
        if abs(expected_ratio - 16/9) > 0.01:
            #print(f"⚠️ Warning: {self.width}x{self.height} is not 16:9 ratio")
            #print(f"   Adjusting to 1280x720 (16:9)")
            self.width = 1280
            self.height = 720
        
        self.cap = None
        self.is_running = False
        self.is_streaming = False
        self.frame_count = 0
        
        # For FPS calculation
        self.last_frame_time = time.time()
        self.actual_fps = 0
    
    def start(self) -> bool:
        """Start the camera with 16:9 settings"""
        try:
            if self.camera_type == 'usb_camera':
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)  # Use DirectShow for better compatibility
            else:
                self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                print(f"Failed to open camera: {self.source}")
                return False
            
            # Set to 16:9 resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            # Verify actual resolution
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Camera started: {actual_width}x{actual_height} (16:9 ratio)")
            
            if actual_width != self.width or actual_height != self.height:
                print(f"   Note: Camera using {actual_width}x{actual_height} instead of requested {self.width}x{self.height}")
            
            self.is_running = True
            self.is_streaming = True
            return True
            
        except Exception as e:
            print(f"Camera error: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame and ensure it's 16:9"""
        if not self.is_running or self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            # Check if frame needs resizing to 16:9
            h, w = frame.shape[:2]
            expected_ratio = 16/9
            current_ratio = w / h
            
            if abs(current_ratio - expected_ratio) > 0.05:
                # Resize to 16:9 if needed
                new_width = int(h * expected_ratio)
                frame = cv2.resize(frame, (new_width, h))
            
            self.frame_count += 1
            self._update_fps()
            return True, frame
        else:
            return False, None
    
    def _update_fps(self):
        """Calculate actual FPS"""
        current_time = time.time()
        time_diff = current_time - self.last_frame_time
        
        if time_diff > 0:
            self.actual_fps = 1.0 / time_diff
        
        self.last_frame_time = current_time
    
    def stop(self):
        """Stop camera streaming"""
        self.is_streaming = False
    
    def resume(self):
        """Resume camera streaming"""
        self.is_streaming = True
    
    def release(self):
        """Fully release camera resources"""
        self.is_running = False
        self.is_streaming = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        print("📷 Camera released")
    
    def get_frame_shape(self) -> Tuple[int, int]:
        """Get frame dimensions (height, width)"""
        return (self.height, self.width)
    
    def get_actual_fps(self) -> float:
        """Get current actual FPS"""
        return self.actual_fps
    
    def is_camera_ready(self) -> bool:
        """Check if camera is ready"""
        return self.is_running and self.cap is not None and self.cap.isOpened()