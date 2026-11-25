import numpy as np
from typing import List


class SpeedSmoother:
    """Exponential Moving Average (EMA) and outlier rejection filter for vehicle speed."""
    
    def __init__(self, alpha: float = 0.35, max_reasonable_speed: float = 240.0):
        self.alpha = alpha
        self.max_reasonable_speed = max_reasonable_speed

    def smooth(self, raw_speed: float, previous_smoothed_speed: float) -> float:
        """Apply EMA smoothing with outlier clamping."""
        if raw_speed < 0 or raw_speed > self.max_reasonable_speed:
            return previous_smoothed_speed

        if previous_smoothed_speed <= 0.0:
            return raw_speed

        # EMA formula: S_t = alpha * Y_t + (1 - alpha) * S_{t-1}
        smoothed = (self.alpha * raw_speed) + ((1.0 - self.alpha) * previous_smoothed_speed)
        return float(round(smoothed, 1))

    @staticmethod
    def median_filter(speed_samples: List[float], window_size: int = 5) -> float:
        """Compute median speed across recent samples to reject momentary spikes."""
        if not speed_samples:
            return 0.0
        window = speed_samples[-window_size:]
        return float(np.median(window))
