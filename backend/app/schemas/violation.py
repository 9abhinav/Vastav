from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ViolationBase(BaseModel):
    tracking_id: int
    violation_type: str  # OVER_SPEEDING, RED_LIGHT, WRONG_WAY, LANE_VIOLATION
    speed: float = 0.0
    speed_limit: float = 60.0
    plate_number: Optional[str] = "UNKNOWN"
    location: Optional[str] = "Main Junction - Camera 01"
    evidence_path: Optional[str] = None
    confidence: Optional[float] = 0.90
    status: Optional[str] = "PENDING"  # PENDING, CONFIRMED, DISMISSED
    details: Optional[str] = None


class ViolationCreate(ViolationBase):
    vehicle_id: Optional[int] = None
    timestamp: Optional[datetime] = None


class ViolationUpdate(BaseModel):
    status: Optional[str] = None
    plate_number: Optional[str] = None
    details: Optional[str] = None


class ViolationVehicleInfo(BaseModel):
    id: int
    vehicle_type: str
    plate_number: Optional[str] = None
    first_seen: datetime

    model_config = ConfigDict(from_attributes=True)


class ViolationRead(ViolationBase):
    id: int
    vehicle_id: Optional[int] = None
    timestamp: datetime
    created_at: datetime
    vehicle: Optional[ViolationVehicleInfo] = None

    model_config = ConfigDict(from_attributes=True)


class ViolationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ViolationRead]


class ViolationFilter(BaseModel):
    violation_type: Optional[str] = None
    vehicle_type: Optional[str] = None
    plate_number: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_speed: Optional[float] = None
    max_speed: Optional[float] = None
