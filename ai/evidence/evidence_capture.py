import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np


class EvidenceCapture:
    """Captures and annotates high-resolution violation evidence images."""

    def __init__(self, evidence_dir: Path):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def capture_evidence(
        self,
        frame: np.ndarray,
        violation: Dict[str, Any],
        vehicle_bbox: list,
        vehicle_type: str = "car",
        location: str = "Main Junction - Camera 01"
    ) -> Optional[str]:
        """
        Creates an annotated evidence snapshot with telemetry banner and bounding box.
        Saves to disk and returns the relative file path.
        """
        if frame is None:
            return None

        try:
            annotated = frame.copy()
            h, w = annotated.shape[:2]

            track_id = violation.get("track_id", 0)
            v_type = violation.get("violation_type", "VIOLATION")
            speed = violation.get("speed", 0.0)
            limit = violation.get("speed_limit", 60.0)
            plate = violation.get("plate_number", "UNKNOWN")
            timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

            # 1. Draw vehicle bounding box with bright red alert styling
            x1, y1, x2, y2 = [int(v) for v in vehicle_bbox]
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))

            # Bounding box & target corners
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 235), 3)

            # Draw tag above vehicle
            tag_text = f"ID #{track_id} | {v_type} | {speed} km/h"
            (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, max(0, y1 - 25)), (x1 + tw + 10, y1), (0, 0, 220), -1)
            cv2.putText(
                annotated,
                tag_text,
                (x1 + 5, max(15, y1 - 7)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            # 2. Draw Top Telemetry Banner (Glassmorphism dark overlay)
            banner_h = 75
            overlay = annotated.copy()
            cv2.rectangle(overlay, (0, 0), (w, banner_h), (15, 15, 25), -1)
            cv2.addWeighted(overlay, 0.85, annotated, 0.15, 0, annotated)

            # Border line under banner
            cv2.line(annotated, (0, banner_h), (w, banner_h), (0, 0, 220), 2)

            # Text inside banner
            cv2.putText(
                annotated,
                f"TRAFFIC ENFORCEMENT EVIDENCE - {v_type.replace('_', ' ')}",
                (20, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 100, 255),
                2
            )
            
            info_line = (
                f"Vehicle: {vehicle_type.upper()} #{track_id}  |  "
                f"Plate: {plate}  |  "
                f"Speed: {speed} km/h (Limit: {int(limit)} km/h)  |  "
                f"Time: {timestamp_str}"
            )
            cv2.putText(
                annotated,
                info_line,
                (20, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (220, 220, 220),
                1
            )

            # 3. Save evidence image
            timestamp_safe = int(time.time() * 1000)
            filename = f"violation_{track_id}_{v_type.lower()}_{timestamp_safe}.jpg"
            save_path = self.evidence_dir / filename
            cv2.imwrite(str(save_path), annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])

            return f"evidence/{filename}"
        except Exception as e:
            print(f"Error capturing evidence: {e}")
            return None
