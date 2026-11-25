import logging
from typing import List, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraCalibration:
    """
    Handles perspective homography transformation between camera pixel coordinates
    and real-world metric coordinates (meters).
    """

    def __init__(
        self,
        source_points: Optional[List[List[float]]] = None,
        real_world_width_meters: float = 8.0,
        real_world_height_meters: float = 30.0
    ):
        # Default source points: roughly trapezoid on a standard 1280x720 frame
        self.source_points = source_points or [
            [200.0, 300.0],   # Top-left
            [1080.0, 300.0],  # Top-right
            [1200.0, 700.0],  # Bottom-right
            [80.0, 700.0]     # Bottom-left
        ]
        self.real_world_width = real_world_width_meters
        self.real_world_height = real_world_height_meters
        
        self.homography_matrix: Optional[np.ndarray] = None
        self.inverse_homography_matrix: Optional[np.ndarray] = None
        self._compute_homography()

    def update_calibration(
        self,
        source_points: List[List[float]],
        real_world_width_meters: float,
        real_world_height_meters: float
    ):
        """Update calibration points and recompute transformation matrix."""
        self.source_points = source_points
        self.real_world_width = real_world_width_meters
        self.real_world_height = real_world_height_meters
        self._compute_homography()

    def _compute_homography(self):
        """Compute the 3x3 homography matrix."""
        try:
            if len(self.source_points) != 4:
                raise ValueError("Calibration requires exactly 4 source points.")

            src = np.array(self.source_points, dtype=np.float32)
            
            # Destination rectangle in real-world metric coordinates (meters)
            # Top-left (0,0), Top-right (W, 0), Bottom-right (W, H), Bottom-left (0, H)
            dst = np.array([
                [0.0, 0.0],
                [self.real_world_width, 0.0],
                [self.real_world_width, self.real_world_height],
                [0.0, self.real_world_height]
            ], dtype=np.float32)

            self.homography_matrix = cv2.getPerspectiveTransform(src, dst)
            self.inverse_homography_matrix = cv2.getPerspectiveTransform(dst, src)
            logger.info("Camera calibration homography matrix computed successfully.")
        except Exception as e:
            logger.error(f"Failed to compute homography matrix: {e}")
            self.homography_matrix = None
            self.inverse_homography_matrix = None

    def transform_point_to_meters(self, point: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """Transform a pixel coordinate (x, y) to real-world coordinate (x_m, y_m)."""
        if self.homography_matrix is None:
            return None

        try:
            pts = np.array([[[point[0], point[1]]]], dtype=np.float32)
            transformed = cv2.perspectiveTransform(pts, self.homography_matrix)
            x_m = float(transformed[0][0][0])
            y_m = float(transformed[0][0][1])
            return (x_m, y_m)
        except Exception as e:
            logger.error(f"Error transforming point {point}: {e}")
            return None

    def calculate_distance_meters(
        self,
        pt1: Tuple[float, float],
        pt2: Tuple[float, float]
    ) -> Optional[float]:
        """Calculate real-world Euclidean distance between two pixel points in meters."""
        m1 = self.transform_point_to_meters(pt1)
        m2 = self.transform_point_to_meters(pt2)
        if m1 is None or m2 is None:
            return None
        
        dx = m2[0] - m1[0]
        dy = m2[1] - m1[1]
        return float(np.hypot(dx, dy))
