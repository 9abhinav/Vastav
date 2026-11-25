from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    tracking_id: int
    vehicle_type: str = "car"
    plate_number: Optional[str] = "UNKNOWN"
    max_speed: Optional[float] = 0.0
    avg_speed: Optional[float] = 0.0
    total_detections: Optional[int] = 1


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate_number: Optional[str] = None
    max_speed: Optional[float] = None
    avg_speed: Optional[float] = None
    last_seen: Optional[datetime] = None
    total_detections: Optional[int] = None


class VehicleViolationSummary(BaseModel):
    id: int
    violation_type: str
    speed: float
    timestamp: datetime
    evidence_path: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class VehicleRead(VehicleBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    violations: List[VehicleViolationSummary] = []

    model_config = ConfigDict(from_attributes=True)


class VehicleListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[VehicleRead]
