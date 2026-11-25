from datetime import datetime, timedelta
from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.vehicle import Vehicle
from backend.app.models.violation import Violation
from backend.app.schemas.statistics import (
    DashboardStatistics, ViolationTypeCount, VehicleTypeCount,
    SpeedDistribution, HourlyViolationTrend
)
from backend.app.services.video_service import video_service

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("", response_model=DashboardStatistics)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """Computes aggregated traffic and violation analytics."""
    total_vehicles = db.query(Vehicle).count()
    active_vehicles = len(video_service.pipeline.tracker.tracks) if video_service.pipeline else 0
    total_violations = db.query(Violation).count()

    # Violation counts by type
    overspeeding_count = db.query(Violation).filter(Violation.violation_type == "OVER_SPEEDING").count()
    red_light_count = db.query(Violation).filter(Violation.violation_type == "RED_LIGHT").count()
    wrong_way_count = db.query(Violation).filter(Violation.violation_type == "WRONG_WAY").count()
    lane_violation_count = db.query(Violation).filter(Violation.violation_type == "LANE_VIOLATION").count()

    # Speed metrics
    avg_speed_res = db.query(func.avg(Vehicle.avg_speed)).filter(Vehicle.avg_speed > 0).scalar() or 0.0
    max_speed_res = db.query(func.max(Vehicle.max_speed)).scalar() or 0.0

    # Violations by type distribution
    violations_by_type = []
    if total_violations > 0:
        counts = {
            "OVER_SPEEDING": overspeeding_count,
            "RED_LIGHT": red_light_count,
            "WRONG_WAY": wrong_way_count,
            "LANE_VIOLATION": lane_violation_count
        }
        for vtype, count in counts.items():
            violations_by_type.append(ViolationTypeCount(
                violation_type=vtype,
                count=count,
                percentage=round((count / total_violations) * 100.0, 1)
            ))

    # Vehicles by type distribution
    vehicles_by_type = []
    type_counts = (
        db.query(Vehicle.vehicle_type, func.count(Vehicle.id))
        .group_by(Vehicle.vehicle_type)
        .all()
    )
    for v_type, count in type_counts:
        pct = round((count / max(1, total_vehicles)) * 100.0, 1)
        vehicles_by_type.append(VehicleTypeCount(
            vehicle_type=v_type,
            count=count,
            percentage=pct
        ))

    # Speed distribution bins
    all_speeds = [s[0] for s in db.query(Vehicle.avg_speed).filter(Vehicle.avg_speed > 0).all()]
    speed_bins = {
        "0-30 km/h": 0,
        "30-50 km/h": 0,
        "50-70 km/h": 0,
        "70-90 km/h": 0,
        "90+ km/h": 0
    }
    for s in all_speeds:
        if s < 30:
            speed_bins["0-30 km/h"] += 1
        elif s < 50:
            speed_bins["30-50 km/h"] += 1
        elif s < 70:
            speed_bins["50-70 km/h"] += 1
        elif s < 90:
            speed_bins["70-90 km/h"] += 1
        else:
            speed_bins["90+ km/h"] += 1

    speed_dist = [
        SpeedDistribution(range_label=label, count=cnt)
        for label, cnt in speed_bins.items()
    ]

    # Hourly trend
    hourly_trend = []
    now = datetime.utcnow()
    for h in range(6, -1, -1):
        target_hour = now - timedelta(hours=h)
        h_str = target_hour.strftime("%H:00")
        start_h = target_hour.replace(minute=0, second=0, microsecond=0)
        end_h = start_h + timedelta(hours=1)

        h_violations = db.query(Violation).filter(
            Violation.timestamp >= start_h,
            Violation.timestamp < end_h
        ).all()

        o_cnt = sum(1 for v in h_violations if v.violation_type == "OVER_SPEEDING")
        r_cnt = sum(1 for v in h_violations if v.violation_type == "RED_LIGHT")
        w_cnt = sum(1 for v in h_violations if v.violation_type == "WRONG_WAY")
        l_cnt = sum(1 for v in h_violations if v.violation_type == "LANE_VIOLATION")

        hourly_trend.append(HourlyViolationTrend(
            hour=h_str,
            count=len(h_violations),
            overspeeding=o_cnt,
            red_light=r_cnt,
            wrong_way=w_cnt,
            lane_violation=l_cnt
        ))

    return DashboardStatistics(
        total_vehicles=total_vehicles,
        active_vehicles=active_vehicles,
        total_violations=total_violations,
        overspeeding_count=overspeeding_count,
        red_light_count=red_light_count,
        wrong_way_count=wrong_way_count,
        lane_violation_count=lane_violation_count,
        average_speed=round(avg_speed_res, 1),
        highest_recorded_speed=round(max_speed_res, 1),
        violations_by_type=violations_by_type,
        vehicles_by_type=vehicles_by_type,
        speed_distribution=speed_dist,
        hourly_trend=hourly_trend
    )
