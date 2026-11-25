import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np

from ai.detection.yolo_detector import YOLODetector
from ai.tracking.bytetrack_tracker import ByteTrackTracker
from ai.tracking.trajectory import VehicleTrack
from ai.calibration.camera_calibration import CameraCalibration
from ai.speed.speed_estimator import SpeedEstimator
from ai.violations.overspeed import OverSpeedDetector
from ai.violations.red_light import RedLightDetector
from ai.violations.wrong_way import WrongWayDetector
from ai.violations.lane_violation import LaneViolationDetector
from ai.ocr.plate_ocr import LicensePlateOCR
from ai.evidence.evidence_capture import EvidenceCapture

logger = logging.getLogger(__name__)


class PipelineFrameResult:
    """Encapsulates the complete result of processing a single video frame."""

    def __init__(
        self,
        frame_idx: int,
        timestamp: float,
        annotated_frame: np.ndarray,
        active_tracks: Dict[int, VehicleTrack],
        new_violations: List[Dict[str, Any]],
        traffic_light_state: str,
        fps: float
    ):
        self.frame_idx = frame_idx
        self.timestamp = timestamp
        self.annotated_frame = annotated_frame
        self.active_tracks = active_tracks
        self.new_violations = new_violations
        self.traffic_light_state = traffic_light_state
        self.fps = fps

    def to_telemetry(self) -> Dict[str, Any]:
        """Convert result to lightweight JSON-serializable telemetry for WebSockets."""
        vehicles_data = []
        for tid, track in self.active_tracks.items():
            vehicles_data.append(track.to_dict())

        return {
            "frame_idx": self.frame_idx,
            "timestamp": round(self.timestamp, 2),
            "fps": round(self.fps, 1),
            "active_vehicles_count": len(self.active_tracks),
            "traffic_light_state": self.traffic_light_state,
            "vehicles": vehicles_data,
            "new_violations": self.new_violations
        }


class TrafficAIPipeline:
    """
    Unified Computer Vision & AI Pipeline for Vehicle Detection, Tracking,
    Speed Estimation, Multi-Violation Detection, OCR, and Evidence Capture.
    """

    def __init__(
        self,
        evidence_dir: Path,
        yolo_model_path: str = "yolov8n.pt",
        speed_limit_kmh: float = 60.0,
        allowed_direction: str = "down",
        traffic_light_state: str = "GREEN",
        enable_ocr: bool = True,
        confidence_threshold: float = 0.40
    ):
        self.evidence_dir = Path(evidence_dir)
        self.speed_limit = speed_limit_kmh
        self.allowed_direction = allowed_direction
        self.traffic_light_state = traffic_light_state
        self.enable_ocr = enable_ocr

        # Initialize sub-modules
        logger.info("Initializing AI Pipeline modules...")
        self.detector = YOLODetector(
            model_name=yolo_model_path,
            confidence_threshold=confidence_threshold
        )
        self.tracker = ByteTrackTracker(max_missing_frames=25, history_length=60)
        self.calibration = CameraCalibration()
        self.speed_estimator = SpeedEstimator(
            calibration=self.calibration,
            speed_limit_kmh=speed_limit_kmh
        )
        self.overspeed_detector = OverSpeedDetector(speed_limit_kmh=speed_limit_kmh)
        self.red_light_detector = RedLightDetector(initial_light_state=traffic_light_state)
        self.wrong_way_detector = WrongWayDetector(allowed_direction=allowed_direction)
        self.lane_detector = LaneViolationDetector()
        self.ocr = LicensePlateOCR()
        self.evidence_capture = EvidenceCapture(self.evidence_dir)

        # Performance counters
        self.fps_counter = 0.0
        self.last_time = time.time()
        self.total_violations_count = 0

    def update_settings(self, settings_data: Dict[str, Any]):
        """Dynamically update settings during runtime."""
        if "speed_limit" in settings_data:
            self.speed_limit = float(settings_data["speed_limit"])
            self.speed_estimator.speed_limit = self.speed_limit
            self.overspeed_detector.speed_limit = self.speed_limit

        if "traffic_light" in settings_data:
            tl = settings_data["traffic_light"]
            if isinstance(tl, dict) and "state" in tl:
                self.set_traffic_light(tl["state"])
            elif isinstance(tl, str):
                self.set_traffic_light(tl)

        if "allowed_direction" in settings_data:
            self.allowed_direction = settings_data["allowed_direction"]
            self.wrong_way_detector.set_allowed_direction(self.allowed_direction)

        if "stop_line" in settings_data:
            sl = settings_data["stop_line"]
            if isinstance(sl, dict):
                p1 = (float(sl.get("x1", 100)), float(sl.get("y1", 500)))
                p2 = (float(sl.get("x2", 1180)), float(sl.get("y2", 500)))
                self.red_light_detector.update_stop_line(p1, p2)

        if "lanes" in settings_data:
            self.lane_detector.set_lanes(settings_data["lanes"])

        if "calibration" in settings_data:
            cal = settings_data["calibration"]
            if isinstance(cal, dict):
                pts = cal.get("source_points", self.calibration.source_points)
                w = float(cal.get("real_world_width_meters", self.calibration.real_world_width))
                h = float(cal.get("real_world_height_meters", self.calibration.real_world_height))
                self.calibration.update_calibration(pts, w, h)

    def set_traffic_light(self, state: str):
        """Update traffic light state."""
        self.traffic_light_state = state.upper()
        self.red_light_detector.set_traffic_light_state(self.traffic_light_state)

    def process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int,
        timestamp: float
    ) -> PipelineFrameResult:
        """
        Processes a single video frame through the complete AI violation pipeline.
        """
        start_t = time.time()
        new_violations: List[Dict[str, Any]] = []

        if frame is None:
            return PipelineFrameResult(
                frame_idx, timestamp, np.zeros((720, 1280, 3), dtype=np.uint8),
                {}, [], self.traffic_light_state, 0.0
            )

        # 1. Detection
        detections = self.detector.detect(frame)

        # 2. Tracking
        active_tracks = self.tracker.update_tracks(detections, frame_idx, timestamp)

        # 3. Speed Estimation & Violations per Track
        for tid, track in list(active_tracks.items()):
            # Speed estimation
            speed_kmh = self.speed_estimator.estimate_speed(track, timestamp)
            track.current_speed = speed_kmh
            if speed_kmh > track.max_speed:
                track.max_speed = speed_kmh

            # Perform OCR on newly detected vehicles or vehicles without a plate (at reasonable intervals)
            if self.enable_ocr and (track.plate_number is None or track.plate_number == "UNKNOWN"):
                if track.ocr_attempts < 3 and len(track.history) >= 2:
                    plate_text, plate_conf = self.ocr.recognize_plate(frame, track.bbox)
                    track.ocr_attempts += 1
                    if plate_text != "UNKNOWN":
                        track.plate_number = plate_text
                        track.plate_confidence = plate_conf

            # Check Violations:
            # A. Over-speeding
            v_overspeed = self.overspeed_detector.check(track, timestamp)
            if v_overspeed:
                self._handle_violation(frame, track, v_overspeed, new_violations)

            # B. Red Light
            v_redlight = self.red_light_detector.check(track, timestamp)
            if v_redlight:
                self._handle_violation(frame, track, v_redlight, new_violations)

            # C. Wrong Way
            v_wrongway = self.wrong_way_detector.check(track, timestamp)
            if v_wrongway:
                self._handle_violation(frame, track, v_wrongway, new_violations)

            # D. Lane Violation
            v_lane = self.lane_detector.check(track, timestamp)
            if v_lane:
                self._handle_violation(frame, track, v_lane, new_violations)

        # 4. Compute FPS
        elapsed = time.time() - start_t
        fps = 1.0 / max(0.001, elapsed)
        self.fps_counter = 0.9 * self.fps_counter + 0.1 * fps

        # 5. Render HUD Overlay
        annotated = self._render_hud(frame, active_tracks, self.fps_counter, frame_idx)

        return PipelineFrameResult(
            frame_idx=frame_idx,
            timestamp=timestamp,
            annotated_frame=annotated,
            active_tracks=active_tracks,
            new_violations=new_violations,
            traffic_light_state=self.traffic_light_state,
            fps=self.fps_counter
        )

    def _handle_violation(
        self,
        frame: np.ndarray,
        track: VehicleTrack,
        violation: Dict[str, Any],
        new_violations_list: List[Dict[str, Any]]
    ):
        """Captures evidence image and records violation event."""
        evidence_rel_path = self.evidence_capture.capture_evidence(
            frame=frame,
            violation=violation,
            vehicle_bbox=track.bbox,
            vehicle_type=track.class_name
        )
        violation["evidence_path"] = evidence_rel_path
        violation["vehicle_type"] = track.class_name
        violation["timestamp"] = time.time()
        self.total_violations_count += 1
        new_violations_list.append(violation)
        logger.info(f"Violation triggered: {violation['violation_type']} for vehicle #{track.track_id} (Speed: {violation.get('speed')} km/h)")

    def _render_hud(
        self,
        frame: np.ndarray,
        tracks: Dict[int, VehicleTrack],
        fps: float,
        frame_idx: int
    ) -> np.ndarray:
        """Render cyberpunk command-center HUD overlay on the output video frame."""
        vis = frame.copy()
        h, w = vis.shape[:2]

        # 1. Draw Stop Line
        p1, p2 = self.red_light_detector.stop_line
        pt1 = (int(p1[0]), int(p1[1]))
        pt2 = (int(p2[0]), int(p2[1]))
        line_color = (0, 0, 240) if self.traffic_light_state == "RED" else (0, 220, 0)
        cv2.line(vis, pt1, pt2, line_color, 3)
        cv2.putText(
            vis,
            f"VIRTUAL STOP LINE ({self.traffic_light_state})",
            (pt1[0] + 10, pt1[1] - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            line_color,
            2
        )

        # 2. Draw Lane Boundaries
        if self.lane_detector._parsed_polygons:
            for lane_id, name, poly in self.lane_detector._parsed_polygons:
                cv2.polylines(vis, [poly], isClosed=True, color=(180, 180, 50), thickness=2)

        # 3. Draw Tracked Vehicles
        for tid, track in tracks.items():
            x1, y1, x2, y2 = [int(v) for v in track.bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            # Determine color based on violations / speeding
            has_violation = len(track.active_violations) > 0
            is_speeding = track.current_speed > self.speed_limit

            if has_violation or is_speeding:
                box_color = (0, 0, 235)  # Red Alert
            elif track.current_speed > (self.speed_limit - 10):
                box_color = (0, 165, 255)  # Amber Warning
            else:
                box_color = (0, 230, 70)  # Neon Emerald Normal

            # Draw rounded/styled bounding box
            cv2.rectangle(vis, (x1, y1), (x2, y2), box_color, 2)

            # Draw Trajectory trail
            if len(track.history) > 1:
                trail_pts = [np.array(entry[3], dtype=np.int32) for entry in list(track.history)[-15:]]
                for i in range(1, len(trail_pts)):
                    cv2.line(vis, tuple(trail_pts[i - 1]), tuple(trail_pts[i]), box_color, 2)

            # Header badge above vehicle
            speed_text = f"{int(track.current_speed)} km/h" if track.current_speed > 0 else "Est..."
            plate_display = f" | {track.plate_number}" if track.plate_number and track.plate_number != "UNKNOWN" else ""
            badge_text = f"#{tid} {track.class_name.upper()} | {speed_text}{plate_display}"
            
            (bw, bh), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
            badge_y = max(bh + 5, y1 - 6)
            cv2.rectangle(vis, (x1, badge_y - bh - 4), (x1 + bw + 8, badge_y + 4), (20, 20, 25), -1)
            cv2.rectangle(vis, (x1, badge_y - bh - 4), (x1 + bw + 8, badge_y + 4), box_color, 1)
            cv2.putText(vis, badge_text, (x1 + 4, badge_y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        # 4. Top Telemetry HUD Header
        hud_h = 50
        overlay = vis.copy()
        cv2.rectangle(overlay, (0, 0), (w, hud_h), (15, 18, 28), -1)
        cv2.addWeighted(overlay, 0.85, vis, 0.15, 0, vis)
        cv2.line(vis, (0, hud_h), (w, hud_h), (50, 60, 80), 1)

        # Traffic Signal Pill
        signal_color = (0, 0, 255) if self.traffic_light_state == "RED" else (0, 220, 220) if self.traffic_light_state == "YELLOW" else (0, 220, 0)
        cv2.circle(vis, (25, 25), 10, signal_color, -1)
        cv2.circle(vis, (25, 25), 11, (255, 255, 255), 1)
        cv2.putText(vis, f"SIGNAL: {self.traffic_light_state}", (45, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Stats widgets
        stats_text = (
            f"ACTIVE: {len(tracks)}  |  "
            f"SPEED LIMIT: {int(self.speed_limit)} km/h  |  "
            f"FLOW: {self.allowed_direction.upper()}  |  "
            f"VIOLATIONS: {self.total_violations_count}  |  "
            f"FPS: {round(fps, 1)}"
        )
        cv2.putText(vis, stats_text, (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 220, 240), 1)

        return vis
