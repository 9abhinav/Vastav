import math
from typing import Optional, Dict, Any
from ai.tracking.trajectory import VehicleTrack
from ai.violations.deduplicator import ViolationDeduplicator

# Target angles in screen coordinates (+x right, +y down):
# right = 0 deg, down = 90 deg, left = 180 deg, up = 270 deg
DIRECTION_ANGLES = {
    "right": 0.0,
    "down": 90.0,
    "left": 180.0,
    "up": 270.0
}


def angle_difference_degrees(angle1: float, angle2: float) -> float:
    """Computes the smallest positive angle difference between two angles in degrees [0, 180]."""
    diff = abs(angle1 - angle2) % 360
    return 360 - diff if diff > 180 else diff


class WrongWayDetector:
    """Detects vehicles travelling opposite to the configured traffic flow direction."""

    def __init__(
        self,
        allowed_direction: str = "down",
        angle_threshold_degrees: float = 110.0,
        min_consecutive_frames: int = 6
    ):
        self.allowed_direction = allowed_direction.lower()
        self.angle_threshold = angle_threshold_degrees
        self.min_consecutive_frames = min_consecutive_frames
        self.deduplicator = ViolationDeduplicator(cooldown_seconds=12.0)
        self._wrong_way_counts: Dict[int, int] = {}

    def set_allowed_direction(self, direction: str):
        self.allowed_direction = direction.lower()

    def check(self, track: VehicleTrack, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Calculates vehicle movement angle over trajectory and compares with allowed direction.
        Requires consecutive frames of wrong-way movement to reject transient jitter.
        """
        allowed_angle = DIRECTION_ANGLES.get(self.allowed_direction, 90.0)
        track_angle = track.get_movement_angle_degrees(window_size=self.min_consecutive_frames)

        if track_angle is None:
            return None

        diff = angle_difference_degrees(track_angle, allowed_angle)

        if diff > self.angle_threshold:
            self._wrong_way_counts[track.track_id] = self._wrong_way_counts.get(track.track_id, 0) + 1
        else:
            self._wrong_way_counts[track.track_id] = max(0, self._wrong_way_counts.get(track.track_id, 0) - 1)

        if self._wrong_way_counts.get(track.track_id, 0) >= self.min_consecutive_frames:
            if self.deduplicator.should_trigger(track.track_id, "WRONG_WAY", timestamp):
                track.active_violations.append("WRONG_WAY")
                return {
                    "violation_type": "WRONG_WAY",
                    "track_id": track.track_id,
                    "speed": round(track.current_speed, 1),
                    "speed_limit": 60.0,
                    "plate_number": track.plate_number or "UNKNOWN",
                    "details": f"Vehicle moving at heading {round(track_angle, 1)} deg, opposite to allowed '{self.allowed_direction}' flow."
                }
        return None
