"""
Logging module for safety events
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from datetime import datetime 

class SafetyLogger:
    """
    Handles all logging for the safety system
    """
    
    def __init__(self, log_file: str = 'safety_log.csv'):
        self.log_file = log_file
        self.system_log = 'system_log.txt'
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize log file with headers if it doesn't exist"""
        if not Path(self.log_file).exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp',
                    'Safety State',
                    'Face Orientation',
                    'Left Hand Zone',
                    'Right Hand Zone',
                    'Hands in Zone',
                    'Total Hands'
                ])
    
    def log_violation(self, safety_state: str, face_orientation: str,
                      hand_status: Dict[str, str], hands_in_zone: int, total_hands: int):
        """
        Log a safety violation or state change
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                safety_state,
                face_orientation,
                hand_status.get('left', 'Unknown'),
                hand_status.get('right', 'Unknown'),
                hands_in_zone,
                total_hands
            ])
        
        # Console output for immediate feedback
        if safety_state != 'SAFE':
            print(f"⚠️ [{timestamp}] {safety_state} - Face: {face_orientation} - "
                  f"Left: {hand_status.get('left', 'N/A')} - "
                  f"Right: {hand_status.get('right', 'N/A')}")
    
    def log_info(self, message: str):
        """Log general information"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.system_log, 'a') as f:
            f.write(f"{timestamp} - INFO: {message}\n")