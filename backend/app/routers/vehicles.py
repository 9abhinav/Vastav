from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.vehicle import VehicleRead, VehicleListResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("", response_model=VehicleListResponse)
def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve paginated list of tracked vehicles with optional filtering."""
    query = db.query(Vehicle)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Vehicle.plate_number.ilike(search_pattern)) |
            (Vehicle.tracking_id.ilike(search_pattern))
        )

    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type.lower())

    total = query.count()
    items = (
        query.order_by(desc(Vehicle.last_seen))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return VehicleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle_details(vehicle_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed vehicle profile including violation history."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
