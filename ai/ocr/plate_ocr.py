import re
import logging
from typing import Optional, Tuple, List
import numpy as np
from ai.ocr.preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class LicensePlateOCR:
    """Performs optical character recognition on vehicle crops using EasyOCR with normalization."""

    def __init__(
        self,
        confidence_threshold: float = 0.35,
        languages: Optional[List[str]] = None,
        gpu: bool = False
    ):
        self.confidence_threshold = confidence_threshold
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.reader = None
        self.preprocessor = ImagePreprocessor()

    def _init_reader(self):
        """Lazy loader for EasyOCR reader."""
        if self.reader is None:
            try:
                import easyocr
                logger.info("Initializing EasyOCR reader...")
                self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
                logger.info("EasyOCR reader initialized.")
            except Exception as e:
                logger.warning(f"EasyOCR initialization deferred or failed: {e}")
                self.reader = None

    def clean_plate_text(self, text: str) -> str:
        """
        Normalize plate string:
        - Convert to uppercase
        - Remove spaces, dashes, dots, and special characters
        - Keep alphanumeric characters only
        """
        if not text:
            return ""
        cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
        return cleaned

    def recognize_plate(self, frame: np.ndarray, bbox: list) -> Tuple[str, float]:
        """
        Extracts vehicle lower region, preprocesses it, runs OCR,
        and returns (normalized_plate_text, confidence).
        """
        if self.reader is None:
            self._init_reader()

        if self.reader is None or frame is None:
            return "UNKNOWN", 0.0

        try:
            crop = self.preprocessor.extract_lower_vehicle_crop(frame, bbox)
            if crop is None or crop.size == 0:
                return "UNKNOWN", 0.0

            enhanced = self.preprocessor.enhance_plate_region(crop)
            if enhanced is None or enhanced.size == 0:
                return "UNKNOWN", 0.0

            results = self.reader.readtext(enhanced)
            if not results:
                return "UNKNOWN", 0.0

            best_text = "UNKNOWN"
            best_conf = 0.0

            for bbox_res, text, conf in results:
                cleaned = self.clean_plate_text(text)
                # Plate number should typically be 4-12 characters
                if 4 <= len(cleaned) <= 12 and conf > self.confidence_threshold:
                    if conf > best_conf:
                        best_conf = float(conf)
                        best_text = cleaned

            return best_text, best_conf
        except Exception as e:
            logger.error(f"Error during license plate OCR: {e}")
            return "UNKNOWN", 0.0
