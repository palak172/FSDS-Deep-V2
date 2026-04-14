"""
Geometry utilities for point, polygon, and distance calculations
"""
import math
import numpy as np
from typing import List, Tuple, Optional


def calculate_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: (x, y) coordinates
        point2: (x, y) coordinates
    
    Returns:
        Distance in pixels
    """
    if not point1 or not point2:
        return float('inf')
    
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def point_in_polygon(point: Tuple[int, int], polygon: np.ndarray) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm
    
    Args:
        point: (x, y) coordinates to check
        polygon: Array of polygon points
    
    Returns:
        True if point is inside polygon
    """
    import cv2
    result = cv2.pointPolygonTest(polygon, point, False)
    return result >= 0


def get_polygon_center(polygon: np.ndarray) -> Tuple[int, int]:
    """
    Calculate the center point of a polygon
    
    Args:
        polygon: Array of polygon points
    
    Returns:
        (center_x, center_y) coordinates
    """
    center = np.mean(polygon, axis=0)
    return (int(center[0]), int(center[1]))


def get_rectangle_from_points(points: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    """
    Convert a list of points to a bounding rectangle
    
    Args:
        points: List of (x, y) points
    
    Returns:
        (x, y, width, height) of bounding rectangle
    """
    if not points:
        return (0, 0, 0, 0)
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x = min(x_coords)
    y = min(y_coords)
    w = max(x_coords) - x
    h = max(y_coords) - y
    
    return (x, y, w, h)