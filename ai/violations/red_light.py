from typing import Optional, Dict, Any, Tuple, List
from ai.tracking.trajectory import VehicleTrack
from ai.violations.deduplicator import ViolationDeduplicator


def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
    """Returns True if points A, B, C are in counter-clockwise order."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def intersect(
    A: Tuple[float, float],
    B: Tuple[float, float],
    C: Tuple[float, float],
    D: Tuple[float, float]
) -> bool:
    """Returns True if line segment AB intersects line segment CD."""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


class RedLightDetector:
    """Detects vehicles crossing a virtual stop line when the virtual traffic light is RED."""

    def __init__(
        self,
        stop_line: Tuple[Tuple[float, float], Tuple[float, float]] = ((100.0, 500.0), (1180.0, 500.0)),
        initial_light_state: str = "GREEN"
    ):
        self.stop_line = stop_line  # ((x1, y1), (x2, y2))
        self.traffic_light_state = initial_light_state.upper()
        self.deduplicator = ViolationDeduplicator(cooldown_seconds=15.0)

    def set_traffic_light_state(self, state: str):
        """Update virtual traffic light state: RED, YELLOW, or GREEN."""
        self.traffic_light_state = state.upper()

    def update_stop_line(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        """Update stop line coordinates."""
        self.stop_line = (p1, p2)

    def check(self, track: VehicleTrack, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Checks if vehicle crossed the stop line while the light is RED.
        Uses bottom-center trajectory over the last 2 frames.
        """
        if self.traffic_light_state != "RED":
            return None

        if len(track.history) < 2:
            return None

        history_list = list(track.history)
        prev_pt = history_list[-2][3]  # previous bottom_center
        curr_pt = history_list[-1][3]  # current bottom_center

        line_start, line_end = self.stop_line

        # Check line segment intersection
        if intersect(prev_pt, curr_pt, line_start, line_end):
            if self.deduplicator.should_trigger(track.track_id, "RED_LIGHT", timestamp):
                track.active_violations.append("RED_LIGHT")
                return {
                    "violation_type": "RED_LIGHT",
                    "track_id": track.track_id,
                    "speed": round(track.current_speed, 1),
                    "speed_limit": 60.0,
                    "plate_number": track.plate_number or "UNKNOWN",
                    "details": f"Vehicle breached virtual stop line while traffic signal was RED."
                }
        return None
