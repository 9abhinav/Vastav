import os
import time
import json
import asyncio
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import cv2
import numpy as np

from backend.app.config import settings
from backend.app.database import SessionLocal
from backend.app.models.vehicle import Vehicle
from backend.app.models.violation import Violation
from backend.app.models.settings import SystemSetting
from backend.app.schemas.video import VideoProcessingStatus
from backend.app.services.websocket_manager import ws_manager
from ai.pipeline import TrafficAIPipeline

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """
    Manages background AI video processing thread, MJPEG frame buffer,
    database persistence of violations, and WebSocket broadcasts.
    """

    def __init__(self):
        self.status = "IDLE"  # IDLE, PROCESSING, PAUSED, COMPLETED, ERROR
        self.source: str = ""
        self.source_type: str = "demo"
        self.current_frame_idx: int = 0
        self.total_frames: int = 0
        self.fps: float = 0.0
        self.error_message: Optional[str] = None
        self.traffic_light_state: str = "GREEN"

        # Frame buffer for MJPEG streaming
        self._latest_jpeg_frame: Optional[bytes] = None
        self._frame_lock = threading.Lock()

        # Worker control
        self._is_running: bool = False
        self._is_paused: bool = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # AI Pipeline instance
        self.pipeline: Optional[TrafficAIPipeline] = None
        self._init_pipeline()

    def _init_pipeline(self):
        """Initializes the AI pipeline with current settings."""
        try:
            self.pipeline = TrafficAIPipeline(
                evidence_dir=settings.DIR_EVIDENCE,
                yolo_model_path=settings.YOLO_MODEL,
                speed_limit_kmh=settings.DEFAULT_SPEED_LIMIT,
                allowed_direction=settings.ALLOWED_DIRECTION,
                traffic_light_state=self.traffic_light_state,
                enable_ocr=settings.ENABLE_OCR,
                confidence_threshold=settings.DETECTION_CONFIDENCE
            )
            # Load stored settings from DB if available
            self.reload_settings_from_db()
        except Exception as e:
            logger.error(f"Error initializing TrafficAIPipeline: {e}")

    def reload_settings_from_db(self):
        """Loads system settings and calibration from database into the AI pipeline."""
        if not self.pipeline:
            return
        db = SessionLocal()
        try:
            setting_record = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
            if setting_record and setting_record.value:
                cfg = json.loads(setting_record.value)
                self.pipeline.update_settings(cfg)
                if "traffic_light" in cfg and "state" in cfg["traffic_light"]:
                    self.traffic_light_state = cfg["traffic_light"]["state"]
                logger.info("Pipeline settings reloaded successfully from database.")
        except Exception as e:
            logger.error(f"Error loading settings from DB: {e}")
        finally:
            db.close()

    def set_traffic_light(self, state: str):
        """Sets the virtual traffic light state (RED, YELLOW, GREEN)."""
        self.traffic_light_state = state.upper()
        if self.pipeline:
            self.pipeline.set_traffic_light(self.traffic_light_state)

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def get_status(self) -> VideoProcessingStatus:
        """Returns current processing status."""
        active_count = len(self.pipeline.tracker.tracks) if self.pipeline else 0
        total_violations = self.pipeline.total_violations_count if self.pipeline else 0
        progress = 0.0
        if self.total_frames > 0:
            progress = min(100.0, round((self.current_frame_idx / self.total_frames) * 100.0, 1))

        return VideoProcessingStatus(
            status=self.status,
            source=str(self.source),
            current_frame=self.current_frame_idx,
            total_frames=self.total_frames,
            progress_percent=progress,
            fps=round(self.fps, 1),
            active_vehicles_count=active_count,
            total_violations_detected=total_violations,
            error_message=self.error_message,
            traffic_light_state=self.traffic_light_state
        )

    def get_latest_jpeg(self) -> Optional[bytes]:
        """Returns the latest processed JPEG frame for MJPEG streaming."""
        with self._frame_lock:
            return self._latest_jpeg_frame

    def start_processing(
        self,
        source_type: str = "demo",
        video_path: Optional[str] = None,
        webcam_index: int = 0,
        rtsp_url: Optional[str] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """Starts video processing in a background worker thread."""
        if self._is_running:
            self.stop_processing()

        if loop:
            self._loop = loop

        self.source_type = source_type
        if source_type == "demo":
            self.source = str(settings.DIR_VIDEOS / "sample_traffic.mp4")
            # Generate demo video if not present
            if not os.path.exists(self.source):
                from scripts.generate_demo_video import generate_sample_traffic_video
                generate_sample_traffic_video(self.source)
        elif source_type == "upload" or source_type == "file":
            self.source = video_path or str(settings.DEFAULT_VIDEO_SOURCE)
        elif source_type == "webcam":
            self.source = webcam_index
        elif source_type == "rtsp":
            self.source = rtsp_url or ""
        else:
            self.source = video_path or str(settings.DEFAULT_VIDEO_SOURCE)

        self._is_running = True
        self._is_paused = False
        self.status = "PROCESSING"
        self.error_message = None
        self.current_frame_idx = 0

        # Reload settings
        self.reload_settings_from_db()

        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        logger.info(f"Video processing started on source: {self.source}")

    def pause_processing(self):
        self._is_paused = True
        self.status = "PAUSED"

    def resume_processing(self):
        self._is_paused = False
        self.status = "PROCESSING"

    def stop_processing(self):
        self._is_running = False
        self._is_paused = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.status = "IDLE"
        logger.info("Video processing stopped.")

    def _worker_loop(self):
        """Background worker thread that reads frames and runs the AI pipeline."""
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            self.status = "ERROR"
            self.error_message = f"Could not open video source: {self.source}"
            logger.error(self.error_message)
            self._is_running = False
            return

        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.total_frames < 0:
            self.total_frames = 0
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        frame_idx = 0
        start_wall_time = time.time()

        try:
            while self._is_running:
                if self._is_paused:
                    time.sleep(0.1)
                    continue

                ret, frame = cap.read()
                if not ret:
                    # If looping video (demo mode), rewind to start
                    if self.source_type in ["demo", "file", "upload"]:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        frame_idx = 0
                        continue
                    else:
                        break

                frame_idx += 1
                self.current_frame_idx = frame_idx
                timestamp = frame_idx / max(1.0, src_fps)

                # Process frame through AI pipeline
                result = self.pipeline.process_frame(frame, frame_idx, timestamp)
                self.fps = result.fps

                # Encode annotated frame to JPEG for MJPEG stream
                _, buffer = cv2.imencode(".jpg", result.annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                with self._frame_lock:
                    self._latest_jpeg_frame = buffer.tobytes()

                # Persist violations & vehicles to DB
                if result.new_violations:
                    self._persist_violations(result.new_violations, result.active_tracks)

                # Update vehicles in DB occasionally
                if frame_idx % 15 == 0:
                    self._persist_active_vehicles(result.active_tracks)

                # Broadcast telemetry via WebSocket
                if self._loop and self._loop.is_running():
                    telemetry = result.to_telemetry()
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast_json(telemetry),
                        self._loop
                    )

                # Throttle to match target FPS
                target_frame_time = 1.0 / max(10, settings.FPS_TARGET)
                time.sleep(max(0.001, target_frame_time * 0.4))

            self.status = "COMPLETED"
        except Exception as e:
            self.status = "ERROR"
            self.error_message = f"Processing error: {str(e)}"
            logger.exception("Error in video processing worker")
        finally:
            cap.release()
            self._is_running = False

    def _persist_violations(self, new_violations: list, active_tracks: dict):
        """Persist newly detected violations to database."""
        db = SessionLocal()
        try:
            for v in new_violations:
                track_id = v.get("track_id")
                track = active_tracks.get(track_id)

                # Find or create vehicle record
                vehicle_rec = db.query(Vehicle).filter(Vehicle.tracking_id == track_id).first()
                if not vehicle_rec and track:
                    vehicle_rec = Vehicle(
                        tracking_id=track_id,
                        vehicle_type=track.class_name,
                        plate_number=track.plate_number or "UNKNOWN",
                        max_speed=track.max_speed,
                        avg_speed=track.avg_speed
                    )
                    db.add(vehicle_rec)
                    db.flush()

                violation_rec = Violation(
                    vehicle_id=vehicle_rec.id if vehicle_rec else None,
                    tracking_id=track_id,
                    violation_type=v.get("violation_type"),
                    speed=v.get("speed", 0.0),
                    speed_limit=v.get("speed_limit", 60.0),
                    plate_number=v.get("plate_number") or (vehicle_rec.plate_number if vehicle_rec else "UNKNOWN"),
                    location="Northbound Expressway - KM 14",
                    evidence_path=v.get("evidence_path"),
                    confidence=0.92,
                    status="PENDING",
                    details=v.get("details")
                )
                db.add(violation_rec)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist violations to database: {e}")
        finally:
            db.close()

    def _persist_active_vehicles(self, active_tracks: dict):
        """Sync active vehicle tracks into the database."""
        db = SessionLocal()
        try:
            for tid, track in active_tracks.items():
                v_rec = db.query(Vehicle).filter(Vehicle.tracking_id == tid).first()
                if v_rec:
                    v_rec.last_seen = track.created_at
                    if track.max_speed > v_rec.max_speed:
                        v_rec.max_speed = track.max_speed
                    v_rec.avg_speed = track.avg_speed
                    if track.plate_number and track.plate_number != "UNKNOWN":
                        v_rec.plate_number = track.plate_number
                    v_rec.total_detections += 1
                else:
                    new_v = Vehicle(
                        tracking_id=tid,
                        vehicle_type=track.class_name,
                        plate_number=track.plate_number or "UNKNOWN",
                        max_speed=track.max_speed,
                        avg_speed=track.avg_speed,
                        total_detections=1
                    )
                    db.add(new_v)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to sync active vehicles: {e}")
        finally:
            db.close()


video_service = VideoProcessingService()
