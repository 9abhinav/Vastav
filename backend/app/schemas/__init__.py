from backend.app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate, VehicleListResponse
from backend.app.schemas.violation import ViolationCreate, ViolationRead, ViolationUpdate, ViolationListResponse, ViolationFilter
from backend.app.schemas.camera import CameraCreate, CameraRead, CameraUpdate
from backend.app.schemas.settings import SystemSettingsSchema, CalibrationConfigSchema, TrafficLightStateSchema
from backend.app.schemas.video import VideoProcessingStatus, VideoStartRequest
from backend.app.schemas.statistics import DashboardStatistics, SpeedDistribution, HourlyViolationTrend

__all__ = [
    "VehicleCreate", "VehicleRead", "VehicleUpdate", "VehicleListResponse",
    "ViolationCreate", "ViolationRead", "ViolationUpdate", "ViolationListResponse", "ViolationFilter",
    "CameraCreate", "CameraRead", "CameraUpdate",
    "SystemSettingsSchema", "CalibrationConfigSchema", "TrafficLightStateSchema",
    "VideoProcessingStatus", "VideoStartRequest",
    "DashboardStatistics", "SpeedDistribution", "HourlyViolationTrend"
]
