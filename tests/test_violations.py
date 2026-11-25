import pytest
from ai.tracking.trajectory import VehicleTrack
from ai.violations.overspeed import OverSpeedDetector
from ai.violations.red_light import RedLightDetector
from ai.violations.wrong_way import WrongWayDetector
from ai.violations.lane_violation import LaneViolationDetector
from ai.violations.deduplicator import ViolationDeduplicator


def test_violation_deduplicator():
    dedup = ViolationDeduplicator(cooldown_seconds=5.0)
    # First trigger should pass
    assert dedup.should_trigger(1, "OVER_SPEEDING", 0.0) is True
    # Immediate repeat should be blocked
    assert dedup.should_trigger(1, "OVER_SPEEDING", 1.0) is False
    # Different violation type should pass
    assert dedup.should_trigger(1, "RED_LIGHT", 1.0) is True
    # After cooldown expires, should pass
    assert dedup.should_trigger(1, "OVER_SPEEDING", 6.0) is True


def test_overspeed_detector():
    detector = OverSpeedDetector(speed_limit_kmh=60.0, tolerance_kmh=2.0)
    track = VehicleTrack(1, "car", 2, [100, 100, 200, 200], 1, 0.0)

    # Normal speed
    track.current_speed = 55.0
    assert detector.check(track, 0.0) is None

    # Overspeeding
    track.current_speed = 85.0
    res = detector.check(track, 1.0)
    assert res is not None
    assert res["violation_type"] == "OVER_SPEEDING"
    assert res["speed"] == 85.0


def test_red_light_detector():
    stop_line = ((100.0, 400.0), (800.0, 400.0))
    detector = RedLightDetector(stop_line=stop_line, initial_light_state="GREEN")
    track = VehicleTrack(2, "car", 2, [200, 300, 300, 390], 1, 0.0)

    # Move across line while light is GREEN -> No violation
    track.update([200, 350, 300, 420], 2, 0.1)
    assert detector.check(track, 0.1) is None

    # Switch light to RED
    detector.set_traffic_light_state("RED")
    track2 = VehicleTrack(3, "car", 2, [400, 300, 500, 390], 1, 1.0)
    track2.update([400, 350, 500, 420], 2, 1.1)

    res = detector.check(track2, 1.1)
    assert res is not None
    assert res["violation_type"] == "RED_LIGHT"


def test_wrong_way_detector():
    detector = WrongWayDetector(allowed_direction="down", min_consecutive_frames=3)
    track = VehicleTrack(4, "car", 2, [500, 500, 600, 600], 1, 0.0)

    # Move upward (wrong way for 'down' flow) over consecutive frames
    res = None
    for i in range(1, 6):
        y = 500 - i * 20
        t = i * 0.1
        track.update([500, y, 600, y + 100], i + 1, t)
        v_res = detector.check(track, t)
        if v_res is not None:
            res = v_res

    assert res is not None
    assert res["violation_type"] == "WRONG_WAY"
