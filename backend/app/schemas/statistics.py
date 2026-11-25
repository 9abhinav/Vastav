from typing import List, Dict
from pydantic import BaseModel


class ViolationTypeCount(BaseModel):
    violation_type: str
    count: int
    percentage: float


class VehicleTypeCount(BaseModel):
    vehicle_type: str
    count: int
    percentage: float


class SpeedDistribution(BaseModel):
    range_label: str  # e.g., "0-30", "30-50", "50-70", "70-90", "90+"
    count: int


class HourlyViolationTrend(BaseModel):
    hour: str  # "00:00", "01:00", etc.
    count: int
    overspeeding: int
    red_light: int
    wrong_way: int
    lane_violation: int


class DashboardStatistics(BaseModel):
    total_vehicles: int = 0
    active_vehicles: int = 0
    total_violations: int = 0
    overspeeding_count: int = 0
    red_light_count: int = 0
    wrong_way_count: int = 0
    lane_violation_count: int = 0
    average_speed: float = 0.0
    highest_recorded_speed: float = 0.0
    violations_by_type: List[ViolationTypeCount] = []
    vehicles_by_type: List[VehicleTypeCount] = []
    speed_distribution: List[SpeedDistribution] = []
    hourly_trend: List[HourlyViolationTrend] = []
