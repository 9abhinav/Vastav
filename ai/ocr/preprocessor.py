import cv2
import numpy as np
from typing import Optional, Tuple


class ImagePreprocessor:
    """Preprocesses cropped vehicle/plate images for OCR clarity."""

    @staticmethod
    def enhance_plate_region(image: np.ndarray) -> np.ndarray:
        """
        Enhance license plate image for EasyOCR:
        - Grayscale conversion
        - Bilateral filter (preserves edges while removing noise)
        - Contrast Limited Adaptive Histogram Equalization (CLAHE)
        - Upscaling for small plates
        """
        if image is None or image.size == 0:
            return image

        h, w = image.shape[:2]
        if h < 10 or w < 20:
            return image

        # 1. Convert to grayscale if 3-channel
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 2. Resize / upscale if plate is small
        if w < 200 or h < 60:
            scale = max(2.0, 200.0 / max(1, w))
            gray = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # 3. Noise reduction with edge preservation
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # 4. CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    @staticmethod
    def extract_lower_vehicle_crop(frame: np.ndarray, bbox: list) -> Optional[np.ndarray]:
        """
        Extracts the lower portion of the vehicle bounding box where license plates are located.
        """
        if frame is None:
            return None

        h_img, w_img = frame.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox]

        x1 = max(0, min(x1, w_img - 1))
        y1 = max(0, min(y1, h_img - 1))
        x2 = max(0, min(x2, w_img - 1))
        y2 = max(0, min(y2, h_img - 1))

        if (x2 - x1) < 10 or (y2 - y1) < 10:
            return None

        box_h = y2 - y1
        # Lower 50% of vehicle bounding box contains the license plate
        plate_y1 = y1 + int(box_h * 0.50)
        plate_crop = frame[plate_y1:y2, x1:x2]

        return plate_crop
