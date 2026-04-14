"""
Test script to verify everything is working
"""
import sys
import cv2
import mediapipe as mp
import numpy as np

print("=" * 50)
print("Testing Factory Safety System Setup")
print("=" * 50)

# Test 1: Python version
print(f"\n✅ Python version: {sys.version}")

# Test 2: OpenCV
print(f"✅ OpenCV version: {cv2.__version__}")

# Test 3: MediaPipe
print(f"✅ MediaPipe version: {mp.__version__}")

# Test 4: NumPy
print(f"✅ NumPy version: {np.__version__}")

# Test 5: Camera
print("\n📷 Testing camera...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print(f"✅ Camera working! Frame size: {frame.shape}")
    else:
        print("❌ Camera opened but couldn't read frame")
    cap.release()
else:
    print("❌ Could not open camera")

print("\n" + "=" * 50)
print("Setup test complete!")