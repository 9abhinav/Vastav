import logging
from typing import Optional
from ai.tracking.trajectory import VehicleTrack
from ai.calibration.camera_calibration import CameraCalibration
from ai.speed.smoothing import SpeedSmoother

logger = logging.getLogger(__name__)


class SpeedEstimator:
    """Estimates real-time vehicle speed (km/h) using perspective homography and time delta."""
    
    def __init__(
        self,
        calibration: CameraCalibration,
        speed_limit_kmh: float = 60.0,
        min_history_frames: int = 5,
        window_frames: int = 8,
        fps_assumed: float = 30.0
    ):
        self.calibration = calibration
        self.speed_limit = speed_limit_kmh
        self.min_history_frames = min_history_frames
        self.window_frames = window_frames
        self.fps_assumed = fps_assumed
        self.smoother = SpeedSmoother(alpha=0.30)

    def estimate_speed(self, track: VehicleTrack, current_timestamp: float) -> float:
        """
        Calculates smoothed speed in km/h from trajectory history.
        Uses bottom-center contact points for perspective accuracy.
        """
        if len(track.history) < self.min_history_frames:
            return track.current_speed

        history_list = list(track.history)
        window = min(self.window_frames, len(history_list))
        
        start_entry = history_list[-window]
        end_entry = history_list[-1]
        
        # entry format: (frame_idx, timestamp, centroid, bottom_center, speed)
        f_start, t_start, _, pt_start, _ = start_entry
        f_end, t_end, _, pt_end, _ = end_entry

        dt = t_end - t_start
        if dt <= 0.0:
            # Fallback to frame-based delta
            df = f_end - f_start
            if df <= 0:
                return track.current_speed
            dt = df / max(1.0, self.fps_assumed)

        # Minimum dt check to avoid division by zero or extreme noise
        if dt < 0.05:
            return track.current_speed

        # Calculate distance in real-world meters via homography
        dist_m = self.calibration.calculate_distance_meters(pt_start, pt_end)
        if dist_m is None:
            return track.current_speed

        # Speed in m/s converted to km/h
        raw_speed_kmh = (dist_m / dt) * 3.6

        # Apply smoothing
        smoothed_speed = self.smoother.smooth(raw_speed_kmh, track.current_speed)
        
        return smoothed_speed
