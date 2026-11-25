import math
from collections import deque
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime


class VehicleTrack:
    """Maintains trajectory history, speed profile, and attributes for a tracked vehicle."""
    
    def __init__(
        self,
        track_id: int,
        class_name: str,
        class_id: int,
        initial_bbox: List[float],
        frame_idx: int,
        timestamp: float,
        max_history: int = 60
    ):
        self.track_id = track_id
        self.class_name = class_name
        self.class_id = class_id
        self.bbox = initial_bbox
        self.max_history = max_history
        
        # History queue: (frame_idx, timestamp, centroid, bottom_center, speed_kmh)
        self.history = deque(maxlen=max_history)
        
        # Key attributes
        self.first_frame_idx = frame_idx
        self.last_frame_idx = frame_idx
        self.first_seen_time = timestamp
        self.last_seen_time = timestamp
        self.created_at = datetime.utcnow()
        
        # Speed attributes
        self.current_speed = 0.0
        self.max_speed = 0.0
        self.speed_samples: List[float] = []
        
        # OCR / Plate
        self.plate_number: Optional[str] = None
        self.plate_confidence: float = 0.0
        self.ocr_attempts: int = 0
        
        # Violations tracked on this vehicle
        self.active_violations: List[str] = []
        
        # Add initial point
        x1, y1, x2, y2 = initial_bbox
        centroid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        bottom_center = ((x1 + x2) / 2.0, y2)
        self.history.append((frame_idx, timestamp, centroid, bottom_center, 0.0))

    def update(
        self,
        bbox: List[float],
        frame_idx: int,
        timestamp: float,
        speed_kmh: Optional[float] = None
    ):
        """Update vehicle position, bbox, and speed."""
        self.bbox = bbox
        self.last_frame_idx = frame_idx
        self.last_seen_time = timestamp
        
        x1, y1, x2, y2 = bbox
        centroid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        bottom_center = ((x1 + x2) / 2.0, y2)
        
        if speed_kmh is not None and speed_kmh > 0:
            self.current_speed = speed_kmh
            if speed_kmh > self.max_speed:
                self.max_speed = speed_kmh
            self.speed_samples.append(speed_kmh)
            
        self.history.append((frame_idx, timestamp, centroid, bottom_center, self.current_speed))

    @property
    def avg_speed(self) -> float:
        if not self.speed_samples:
            return self.current_speed
        return sum(self.speed_samples) / len(self.speed_samples)

    def get_direction_vector(self, window_size: int = 6) -> Optional[Tuple[float, float]]:
        """Calculate movement vector (dx, dy) over the last N history entries."""
        if len(self.history) < 2:
            return None
        
        pts = [entry[3] for entry in list(self.history)[-window_size:]]  # bottom_center
        start_pt = pts[0]
        end_pt = pts[-1]
        
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        return (dx, dy)

    def get_movement_angle_degrees(self, window_size: int = 6) -> Optional[float]:
        """
        Returns movement angle in degrees (0 = right, 90 = down, 180 = left, 270 = up).
        Screen coordinate system: +x is right, +y is down.
        """
        vec = self.get_direction_vector(window_size)
        if not vec:
            return None
        dx, dy = vec
        if math.hypot(dx, dy) < 5.0:  # Negligible movement
            return None
        rad = math.atan2(dy, dx)
        deg = math.degrees(rad)
        return (deg + 360) % 360

    def is_stale(self, current_frame_idx: int, max_missing_frames: int = 30) -> bool:
        """Check if vehicle has not been seen for more than max_missing_frames."""
        return (current_frame_idx - self.last_frame_idx) > max_missing_frames

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "bbox": self.bbox,
            "current_speed": round(self.current_speed, 1),
            "max_speed": round(self.max_speed, 1),
            "avg_speed": round(self.avg_speed, 1),
            "plate_number": self.plate_number or "UNKNOWN",
            "plate_confidence": round(self.plate_confidence, 2),
            "active_violations": list(self.active_violations),
            "history_length": len(self.history),
            "first_frame": self.first_frame_idx,
            "last_frame": self.last_frame_idx
        }
