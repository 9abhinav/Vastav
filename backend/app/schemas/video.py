from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class VideoStartRequest(BaseModel):
    source_type: str = "demo"  # demo, upload, webcam, rtsp
    video_path: Optional[str] = None
    webcam_index: Optional[int] = 0
    rtsp_url: Optional[str] = None
    fps_target: Optional[int] = 30


class VideoProcessingStatus(BaseModel):
    status: str = "IDLE"  # IDLE, PROCESSING, PAUSED, COMPLETED, ERROR
    source: str = ""
    current_frame: int = 0
    total_frames: int = 0
    progress_percent: float = 0.0
    fps: float = 0.0
    active_vehicles_count: int = 0
    total_vehicles_detected: int = 0
    total_violations_detected: int = 0
    error_message: Optional[str] = None
    traffic_light_state: str = "GREEN"
