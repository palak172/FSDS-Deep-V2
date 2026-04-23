"""
Input Overlay - Simple version (only numbers)
"""
import cv2

class InputOverlay:
    def __init__(self):
        self.employee_id = ""
        self.batch_id = ""
        self.current_input = "employee"
        self.input_active = True
        self.confirmed = False
        
    def handle_key(self, key):
        """Handle keyboard input - numbers only"""
        if not self.input_active:
            return
        
        # Number keys only
        if 48 <= key <= 57:  # '0' to '9'
            char = chr(key)
            if self.current_input == "employee":
                self.employee_id += char
            else:
                self.batch_id += char
        
        # Backspace
        elif key == 8:
            if self.current_input == "employee" and self.employee_id:
                self.employee_id = self.employee_id[:-1]
            elif self.current_input == "batch" and self.batch_id:
                self.batch_id = self.batch_id[:-1]
        
        # Enter
        elif key == 13:
            if self.current_input == "employee":
                if self.employee_id:
                    self.current_input = "batch"
            else:
                if self.batch_id:
                    self.confirmed = True
                    self.input_active = False
        
        # ESC
        elif key == 27:
            self.reset()
    
    def reset(self):
        self.employee_id = ""
        self.batch_id = ""
        self.current_input = "employee"
        self.input_active = True
        self.confirmed = False
    
    def is_confirmed(self):
        return self.confirmed
    
    def get_session_info(self):
        return {'employee_id': self.employee_id, 'batch_id': self.batch_id}
    
    def draw(self, frame):
        if not self.input_active:
            return frame
        
        h, w = frame.shape[:2]
        
        # Dark background
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//4, h//3), (3*w//4, 2*h//3), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Border
        cv2.rectangle(frame, (w//4, h//3), (3*w//4, 2*h//3), (100, 100, 100), 2)
        
        # Title
        cv2.putText(frame, "START WORK SESSION", (w//2 - 100, h//3 + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Employee ID (green when active)
        color = (0, 255, 0) if self.current_input == "employee" else (200, 200, 200)
        cv2.putText(frame, f"Employee ID: {self.employee_id}", 
                   (w//2 - 120, h//3 + 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Batch ID (green when active)
        color = (0, 255, 0) if self.current_input == "batch" else (200, 200, 200)
        cv2.putText(frame, f"Batch ID: {self.batch_id}", 
                   (w//2 - 120, h//3 + 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Instructions
        cv2.putText(frame, "Use number keys to type", (w//2 - 120, h//3 + 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "Press ENTER to confirm, ESC to cancel", 
                   (w//2 - 160, h//3 + 190),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame