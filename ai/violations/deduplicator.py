import time
from typing import Dict, Tuple


class ViolationDeduplicator:
    """
    Prevents repeated violation events for the same vehicle within a cooldown window.
    Key is (track_id, violation_type).
    """

    def __init__(self, cooldown_seconds: float = 10.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_violation_time: Dict[Tuple[int, str], float] = {}

    def should_trigger(self, track_id: int, violation_type: str, current_time: float) -> bool:
        """Returns True if enough time has elapsed since the last violation of this type."""
        key = (track_id, violation_type)
        last_time = self.last_violation_time.get(key)

        if last_time is None or (current_time - last_time) >= self.cooldown_seconds:
            self.last_violation_time[key] = current_time
            return True
        return False

    def clear(self):
        self.last_violation_time.clear()
