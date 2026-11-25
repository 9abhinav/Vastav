import pytest
import numpy as np
from ai.calibration.camera_calibration import CameraCalibration
from ai.speed.smoothing import SpeedSmoother
from ai.speed.speed_estimator import SpeedEstimator
from ai.tracking.trajectory import VehicleTrack


def test_camera_calibration_homography():
    """Verify that homography computes valid metric transformations."""
    calib = CameraCalibration(
        source_points=[[200.0, 300.0], [1080.0, 300.0], [1200.0, 700.0], [80.0, 700.0]],
        real_world_width_meters=8.0,
        real_world_height_meters=30.0
    )
    assert calib.homography_matrix is not None
    assert calib.homography_matrix.shape == (3, 3)

    # Top-left corner should map near (0, 0)
    tl_m = calib.transform_point_to_meters((200.0, 300.0))
    assert tl_m is not None
    assert abs(tl_m[0] - 0.0) < 0.1
    assert abs(tl_m[1] - 0.0) < 0.1

    # Bottom-right corner should map near (8.0, 30.0)
    br_m = calib.transform_point_to_meters((1200.0, 700.0))
    assert br_m is not None
    assert abs(br_m[0] - 8.0) < 0.1
    assert abs(br_m[1] - 30.0) < 0.1


def test_speed_smoother():
    """Verify EMA smoothing and outlier clamping."""
    smoother = SpeedSmoother(alpha=0.4, max_reasonable_speed=200.0)
    
    # First measurement
    s1 = smoother.smooth(60.0, 0.0)
    assert s1 == 60.0

    # Slight change
    s2 = smoother.smooth(70.0, s1)
    assert 60.0 < s2 < 70.0

    # Unreasonable outlier (e.g. 350 km/h) should be rejected
    s_outlier = smoother.smooth(350.0, s2)
    assert s_outlier == s2


def test_speed_estimator():
    """Verify speed estimation across synthetic trajectory entries."""
    calib = CameraCalibration()
    estimator = SpeedEstimator(calibration=calib, min_history_frames=3, window_frames=5)

    track = VehicleTrack(
        track_id=1,
        class_name="car",
        class_id=2,
        initial_bbox=[500, 350, 600, 450],
        frame_idx=1,
        timestamp=0.0
    )

    # Simulate vehicle moving down the road over 10 frames (1/3 second)
    for i in range(1, 10):
        t = i * 0.033
        y_pos = 350 + i * 15
        track.update(
            bbox=[500, y_pos, 600, y_pos + 100],
            frame_idx=i + 1,
            timestamp=t
        )
        speed = estimator.estimate_speed(track, t)
        track.current_speed = speed

    assert track.current_speed > 10.0  # Vehicle is moving at positive speed
