from typing import List, Optional, Any
from pydantic import BaseModel, Field


class CalibrationPoint(BaseModel):
    x: float
    y: float


class LineCoordinates(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class LanePolygon(BaseModel):
    id: int
    name: str
    points: List[List[float]]  # [[x1, y1], [x2, y2], ...]


class CalibrationConfigSchema(BaseModel):
    source_points: List[List[float]] = Field(
        default=[[200, 300], [1080, 300], [1200, 700], [80, 700]],
        description="4 points defining the road perspective quadrilateral"
    )
    real_world_width_meters: float = Field(default=8.0, description="Real world road width in meters")
    real_world_height_meters: float = Field(default=30.0, description="Real world road length in meters")


class TrafficLightStateSchema(BaseModel):
    state: str = Field(default="GREEN", description="RED, YELLOW, or GREEN")
    manual_override: bool = Field(default=True, description="Whether state is manual or automated")
    cycle_seconds: int = Field(default=20, description="Auto cycle time in seconds if automated")


class SystemSettingsSchema(BaseModel):
    speed_limit: float = Field(default=60.0, description="Speed limit in km/h")
    speed_unit: str = Field(default="km/h")
    allowed_direction: str = Field(default="down", description="down, up, left, right")
    traffic_light: TrafficLightStateSchema = Field(default_factory=TrafficLightStateSchema)
    stop_line: LineCoordinates = Field(
        default=LineCoordinates(x1=100, y1=500, x2=1180, y2=500),
        description="Virtual stop line coordinates"
    )
    lanes: List[LanePolygon] = Field(
        default=[
            LanePolygon(id=1, name="Lane 1 (Left)", points=[[100, 300], [640, 300], [600, 720], [50, 720]]),
            LanePolygon(id=2, name="Lane 2 (Right)", points=[[640, 300], [1180, 300], [1230, 720], [600, 720]])
        ]
    )
    calibration: CalibrationConfigSchema = Field(default_factory=CalibrationConfigSchema)
    enable_ocr: bool = Field(default=True)
    detection_confidence: float = Field(default=0.40)
    ocr_confidence: float = Field(default=0.35)
    video_source: str = Field(default="videos/sample_traffic.mp4")
