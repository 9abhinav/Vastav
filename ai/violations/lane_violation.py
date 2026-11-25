from typing import Optional, Dict, Any, List, Tuple
import cv2
import numpy as np
from ai.tracking.trajectory import VehicleTrack
from ai.violations.deduplicator import ViolationDeduplicator


class LaneViolationDetector:
    """Detects vehicles straying outside defined lane boundaries or crossing prohibited dividers."""

    def __init__(
        self,
        lane_polygons: Optional[List[Dict[str, Any]]] = None
    ):
        self.lanes = lane_polygons or []
        self.deduplicator = ViolationDeduplicator(cooldown_seconds=12.0)
        self._parsed_polygons: List[Tuple[int, str, np.ndarray]] = []
        self._parse_lanes()

    def set_lanes(self, lane_polygons: List[Dict[str, Any]]):
        self.lanes = lane_polygons
        self._parse_lanes()

    def _parse_lanes(self):
        self._parsed_polygons = []
        for lane in self.lanes:
            points = lane.get("points", [])
            if len(points) >= 3:
                pts_np = np.array(points, dtype=np.int32)
                self._parsed_polygons.append((
                    lane.get("id", 1),
                    lane.get("name", "Lane"),
                    pts_np
                ))

    def check(self, track: VehicleTrack, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Check if vehicle is outside all legitimate driving lanes (e.g. driving on shoulder/median).
        """
        if not self._parsed_polygons:
            return None

        if len(track.history) < 3:
            return None

        curr_pt = track.history[-1][3]  # bottom-center point
        pt = (float(curr_pt[0]), float(curr_pt[1]))

        # Check if point is inside ANY valid lane
        inside_any_lane = False
        for lane_id, name, poly in self._parsed_polygons:
            dist = cv2.pointPolygonTest(poly, pt, False)
            if dist >= 0:  # inside or on contour
                inside_any_lane = True
                break

        # If vehicle is outside all configured legal road lanes
        if not inside_any_lane:
            if self.deduplicator.should_trigger(track.track_id, "LANE_VIOLATION", timestamp):
                track.active_violations.append("LANE_VIOLATION")
                return {
                    "violation_type": "LANE_VIOLATION",
                    "track_id": track.track_id,
                    "speed": round(track.current_speed, 1),
                    "speed_limit": 60.0,
                    "plate_number": track.plate_number or "UNKNOWN",
                    "details": f"Vehicle operating outside designated lane boundaries / road corridor."
                }
        return None
