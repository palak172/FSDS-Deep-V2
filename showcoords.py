"""
Coordinate Mapper - Shows real-time cursor coordinates
Run this separately to find polygon points for config.json
"""
import cv2
import numpy as np

# Mouse callback function
coordinates = []

def mouse_callback(event, x, y, flags, param):
    global coordinates
    
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinates.append((x, y))
        print(f"📍 Point {len(coordinates)}: ({x}, {y})")
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        if coordinates:
            removed = coordinates.pop()
            print(f"❌ Removed: ({removed[0]}, {removed[1]})")
            print(f"   Remaining points: {len(coordinates)}")
    
    elif event == cv2.EVENT_MOUSEMOVE:
        # Show current position on frame
        param['current_pos'] = (x, y)

# Start camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create window and set mouse callback
window_name = "Coordinate Mapper - Left Click: Add Point | Right Click: Remove Last | 's': Save | 'c': Clear | 'q': Quit"
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, mouse_callback, {'current_pos': (0, 0)})

print("=" * 60)
print("COORDINATE MAPPING TOOL")
print("=" * 60)
print("📌 Left Click  - Add point at cursor")
print("🗑️  Right Click - Remove last point")
print("💾 Press 's'   - Save points to console")
print("🗑️  Press 'c'   - Clear all points")
print("❌ Press 'q'   - Quit")
print("=" * 60)
print("\n🎯 Click on the corners of your HAND ZONE")
print("   (where hands SHOULD be for safety)")
print("")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Draw existing points
    for i, point in enumerate(coordinates):
        cv2.circle(frame, point, 8, (0, 255, 0), -1)
        cv2.putText(frame, str(i+1), (point[0]+10, point[1]+5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Draw lines between points (if more than 1)
    if len(coordinates) >= 2:
        for i in range(len(coordinates)-1):
            cv2.line(frame, coordinates[i], coordinates[i+1], (0, 255, 0), 2)
    
    # Draw polygon if 3+ points
    if len(coordinates) >= 3:
        pts = np.array(coordinates, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
        
        # Fill with semi-transparent
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 255, 0))
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    # Show current mouse position
    current_pos = cv2.getMouseCallback(window_name)[1] if hasattr(mouse_callback, '__globals__') else (0, 0)
    # Alternative: use global variable
    if 'current_pos' in locals():
        cv2.putText(frame, f"Mouse: ({current_pos[0]}, {current_pos[1]})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Show instruction
    cv2.putText(frame, f"Points: {len(coordinates)}", (10, 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    cv2.imshow(window_name, frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        print("\n" + "=" * 60)
        print("📋 COPY THESE POINTS TO YOUR config.json:")
        print("=" * 60)
        print("points: [")
        for i, point in enumerate(coordinates):
            print(f"    [{point[0]}, {point[1]}],")
        print("]")
        print("=" * 60)
    elif key == ord('c'):
        coordinates = []
        print("🗑️  All points cleared")

cap.release()
cv2.destroyAllWindows()