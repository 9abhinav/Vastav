from typing import Optional, Dict, Any
from ai.tracking.trajectory import VehicleTrack
from ai.violations.deduplicator import ViolationDeduplicator


class OverSpeedDetector:
    """Detects over-speeding violations against a configurable speed limit."""
    
    def __init__(self, speed_limit_kmh: float = 60.0, tolerance_kmh: float = 3.0):
        self.speed_limit = speed_limit_kmh
        self.tolerance = tolerance_kmh
        self.deduplicator = ViolationDeduplicator(cooldown_seconds=10.0)

    def check(self, track: VehicleTrack, timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Checks if vehicle speed exceeds (speed_limit + tolerance).
        Returns violation payload if triggered, None otherwise.
        """
        effective_limit = self.speed_limit + self.tolerance
        
        if track.current_speed > effective_limit:
            if self.deduplicator.should_trigger(track.track_id, "OVER_SPEEDING", timestamp):
                track.active_violations.append("OVER_SPEEDING")
                return {
                    "violation_type": "OVER_SPEEDING",
                    "track_id": track.track_id,
                    "speed": round(track.current_speed, 1),
                    "speed_limit": round(self.speed_limit, 1),
                    "plate_number": track.plate_number or "UNKNOWN",
                    "details": f"Vehicle clocked at {round(track.current_speed, 1)} km/h in a {int(self.speed_limit)} km/h zone."
                }
        return None
