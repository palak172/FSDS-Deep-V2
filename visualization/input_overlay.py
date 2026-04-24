"""
Input Overlay - For typing Employee ID, Batch ID, and Product Name
"""
import cv2

class InputOverlay:
    def __init__(self):
        self.employee_id = ""
        self.batch_id = ""
        self.product_name = ""
        self.current_input = "employee"  # 'employee', 'batch', or 'product'
        self.input_active = True
        self.confirmed = False
        self.needs_product_name = False
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.input_active:
            return
        
        # ========== NUMBERS (0-9) ==========
        if 48 <= key <= 57:
            char = chr(key)
            if self.current_input == "employee":
                self.employee_id += char
            elif self.current_input == "batch":
                self.batch_id += char
            elif self.current_input == "product":
                self.product_name += char
        
        # ========== LETTERS (A-Z, a-z) - ONLY FOR PRODUCT NAME ==========
        elif 65 <= key <= 90:  # Uppercase A-Z
            char = chr(key)
            if self.current_input == "product":
                self.product_name += char
        
        elif 97 <= key <= 122:  # Lowercase a-z
            char = chr(key)
            if self.current_input == "product":
                self.product_name += char
        
        # ========== SYMBOLS FOR PRODUCT NAME ==========
        elif key == 32:  # Space
            if self.current_input == "product":
                self.product_name += ' '
        elif key == 45:  # Hyphen (-)
            if self.current_input == "product":
                self.product_name += '-'
        elif key == 95:  # Underscore (_)
            if self.current_input == "product":
                self.product_name += '_'
        elif key == 46:  # Period (.)
            if self.current_input == "product":
                self.product_name += '.'
        
        # ========== BACKSPACE ==========
        elif key == 8:
            if self.current_input == "employee" and self.employee_id:
                self.employee_id = self.employee_id[:-1]
            elif self.current_input == "batch" and self.batch_id:
                self.batch_id = self.batch_id[:-1]
            elif self.current_input == "product" and self.product_name:
                self.product_name = self.product_name[:-1]
        
        # ========== ENTER ==========
        elif key == 13:
            if self.current_input == "employee":
                if self.employee_id:
                    self.current_input = "batch"
            elif self.current_input == "batch":
                if self.batch_id:
                    self.current_input = "product"
                    self.needs_product_name = True
            elif self.current_input == "product":
                if self.product_name:
                    self.confirmed = True
                    self.input_active = False
                else:
                    # Default product name if user presses ENTER without typing
                    self.product_name = f"Product_{self.batch_id}"
                    self.confirmed = True
                    self.input_active = False
        
        # ========== ESC ==========
        elif key == 27:
            self.reset()
    
    def set_batch_exists(self, exists: bool):
        """Called when batch already exists - skip product name"""
        if exists:
            self.confirmed = True
            self.input_active = False
            self.needs_product_name = False
    
    def reset(self):
        self.employee_id = ""
        self.batch_id = ""
        self.product_name = ""
        self.current_input = "employee"
        self.input_active = True
        self.confirmed = False
        self.needs_product_name = False
    
    def is_confirmed(self):
        return self.confirmed
    
    def needs_product(self):
        return self.needs_product_name
    
    def get_session_info(self):
        return {
            'employee_id': self.employee_id,
            'batch_id': self.batch_id,
            'product_name': self.product_name
        }
    
    def draw(self, frame):
        if not self.input_active:
            return frame
        
        h, w = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//4, h//3), (3*w//4, 2*h//3), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        cv2.rectangle(frame, (w//4, h//3), (3*w//4, 2*h//3), (100, 100, 100), 2)
        
        # Title
        cv2.putText(frame, "START WORK SESSION", (w//2 - 100, h//3 + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Employee ID
        color = (0, 255, 0) if self.current_input == "employee" else (200, 200, 200)
        cv2.putText(frame, f"Employee ID: {self.employee_id}", 
                   (w//2 - 120, h//3 + 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Batch ID
        color = (0, 255, 0) if self.current_input == "batch" else (200, 200, 200)
        cv2.putText(frame, f"Batch ID: {self.batch_id}", 
                   (w//2 - 120, h//3 + 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Product Name (only shown when creating new batch)
        if self.current_input == "product" or self.needs_product_name:
            color = (0, 255, 0) if self.current_input == "product" else (200, 200, 200)
            cv2.putText(frame, f"Product Name: {self.product_name}", 
                       (w//2 - 130, h//3 + 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            
            if self.current_input == "product":
                cv2.putText(frame, "Use letters, numbers, space, hyphen (-), underscore (_), or period (.)", 
                           (w//2 - 250, h//3 + 215),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Instructions
        if self.current_input == "product":
            cv2.putText(frame, "Press ENTER to confirm, ESC to cancel", 
                       (w//2 - 160, h//3 + 245),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        else:
            cv2.putText(frame, "Use numbers only, Press ENTER to confirm, ESC to cancel", 
                       (w//2 - 220, h//3 + 210),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        return frame