from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CameraBase(BaseModel):
    name: str
    location: str = "Main Junction"
    source: str = "videos/sample_traffic.mp4"
    camera_type: str = "FILE"  # FILE, WEBCAM, RTSP
    is_active: bool = True
    status: str = "ONLINE"


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    camera_type: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class CameraRead(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
