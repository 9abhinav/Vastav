import os
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

# COCO vehicle class mappings
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


class Detection:
    def __init__(
        self,
        bbox: List[float],
        confidence: float,
        class_id: int,
        class_name: str,
        track_id: Optional[int] = None
    ):
        self.bbox = [float(x) for x in bbox]  # [x1, y1, x2, y2]
        self.confidence = float(confidence)
        self.class_id = int(class_id)
        self.class_name = class_name
        self.track_id = int(track_id) if track_id is not None else None
        
        # Calculate key reference points
        x1, y1, x2, y2 = self.bbox
        self.width = x2 - x1
        self.height = y2 - y1
        self.centroid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        self.bottom_center = ((x1 + x2) / 2.0, y2)  # Ground contact point for homography

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bbox": self.bbox,
            "confidence": round(self.confidence, 3),
            "class_id": self.class_id,
            "class_name": self.class_name,
            "track_id": self.track_id,
            "centroid": [round(c, 2) for c in self.centroid],
            "bottom_center": [round(c, 2) for c in self.bottom_center]
        }


class YOLODetector:
    """YOLO vehicle detector supporting car, motorcycle, bus, and truck classes."""
    
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence_threshold: float = 0.40,
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            logger.info(f"Loading YOLO model: {self.model_name}...")
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect vehicle objects in a single frame."""
        if self.model is None or frame is None:
            return []

        try:
            # Filter classes: car(2), motorcycle(3), bus(5), truck(7)
            target_classes = list(VEHICLE_CLASSES.keys())
            results = self.model.predict(
                source=frame,
                conf=self.confidence_threshold,
                classes=target_classes,
                verbose=False,
                device=self.device
            )

            detections: List[Detection] = []
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    class_name = VEHICLE_CLASSES.get(cls_id, "vehicle")
                    
                    detections.append(Detection(
                        bbox=xyxy,
                        confidence=conf,
                        class_id=cls_id,
                        class_name=class_name
                    ))
            return detections
        except Exception as e:
            logger.error(f"Error during vehicle detection: {e}")
            return []

    def track(self, frame: np.ndarray, persist: bool = True) -> List[Detection]:
        """Run YOLO with built-in ByteTrack tracker."""
        if self.model is None or frame is None:
            return []

        try:
            target_classes = list(VEHICLE_CLASSES.keys())
            results = self.model.track(
                source=frame,
                conf=self.confidence_threshold,
                classes=target_classes,
                tracker="bytetrack.yaml",
                persist=persist,
                verbose=False,
                device=self.device
            )

            detections: List[Detection] = []
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    class_name = VEHICLE_CLASSES.get(cls_id, "vehicle")
                    track_id = int(box.id[0].item()) if box.id is not None else None
                    
                    detections.append(Detection(
                        bbox=xyxy,
                        confidence=conf,
                        class_id=cls_id,
                        class_name=class_name,
                        track_id=track_id
                    ))
            return detections
        except Exception as e:
            logger.error(f"Error during vehicle tracking: {e}")
            return []
