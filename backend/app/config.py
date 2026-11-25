import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = BASE_DIR / "evidence"
VIDEOS_DIR = BASE_DIR / "videos"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Real-Time Vehicle Speed & Traffic Violation Tracking System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'traffic_system.db'}")
    
    # AI Models
    YOLO_MODEL: str = "yolov8n.pt"
    DETECTION_CONFIDENCE: float = 0.40
    TRACKER_TYPE: str = "bytetrack"
    ENABLE_OCR: bool = True
    OCR_CONFIDENCE: float = 0.35
    OCR_LANGUAGE: str = "en"
    
    # Traffic Rules Defaults
    DEFAULT_SPEED_LIMIT: float = 60.0  # km/h
    SPEED_UNIT: str = "km/h"
    ALLOWED_DIRECTION: str = "down"  # 'down', 'up', 'left', 'right'
    WRONG_WAY_ANGLE_THRESHOLD: float = 120.0  # degrees deviation
    
    # Virtual Traffic Signal Defaults
    DEFAULT_TRAFFIC_LIGHT_STATE: str = "GREEN"  # RED, YELLOW, GREEN
    RED_LIGHT_AUTOMATION: bool = False
    SIGNAL_CYCLE_SECONDS: int = 20
    
    # Video Processing
    DEFAULT_VIDEO_SOURCE: str = str(VIDEOS_DIR / "sample_traffic.mp4")
    FPS_TARGET: int = 30
    FRAME_SKIP: int = 1
    
    # Directories
    DIR_BASE: Path = BASE_DIR
    DIR_EVIDENCE: Path = EVIDENCE_DIR
    DIR_VIDEOS: Path = VIDEOS_DIR
    DIR_MODELS: Path = MODELS_DIR

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
