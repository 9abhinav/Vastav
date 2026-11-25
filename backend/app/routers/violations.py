import io
import csv
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.violation import Violation
from backend.app.schemas.violation import (
    ViolationCreate, ViolationRead, ViolationUpdate, ViolationListResponse
)

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("", response_model=ViolationListResponse)
def list_violations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    violation_type: Optional[str] = None,
    plate_number: Optional[str] = None,
    status: Optional[str] = None,
    min_speed: Optional[float] = None,
    max_speed: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """List traffic violations with comprehensive multi-criteria filtering."""
    query = db.query(Violation)

    if violation_type:
        query = query.filter(Violation.violation_type == violation_type.upper())
    if plate_number:
        query = query.filter(Violation.plate_number.ilike(f"%{plate_number}%"))
    if status:
        query = query.filter(Violation.status == status.upper())
    if min_speed is not None:
        query = query.filter(Violation.speed >= min_speed)
    if max_speed is not None:
        query = query.filter(Violation.speed <= max_speed)
    if start_date:
        query = query.filter(Violation.timestamp >= start_date)
    if end_date:
        query = query.filter(Violation.timestamp <= end_date)

    total = query.count()
    items = (
        query.order_by(desc(Violation.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ViolationListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/export/csv")
def export_violations_csv(db: Session = Depends(get_db)):
    """Export all violations as a CSV file for download."""
    violations = db.query(Violation).order_by(desc(Violation.timestamp)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Violation ID", "Tracking ID", "Violation Type", "Recorded Speed (km/h)",
        "Speed Limit (km/h)", "Plate Number", "Timestamp (UTC)", "Status", "Location", "Evidence Path"
    ])

    for v in violations:
        writer.writerow([
            v.id, v.tracking_id, v.violation_type, v.speed, v.speed_limit,
            v.plate_number, v.timestamp.isoformat() if v.timestamp else "",
            v.status, v.location, v.evidence_path or ""
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=traffic_violations_export.csv"
    return response


@router.get("/{violation_id}", response_model=ViolationRead)
def get_violation(violation_id: int, db: Session = Depends(get_db)):
    """Get single violation record by ID."""
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation


@router.post("", response_model=ViolationRead, status_code=201)
def create_violation(violation_in: ViolationCreate, db: Session = Depends(get_db)):
    """Manually create or inject a traffic violation record."""
    violation = Violation(
        vehicle_id=violation_in.vehicle_id,
        tracking_id=violation_in.tracking_id,
        violation_type=violation_in.violation_type.upper(),
        speed=violation_in.speed,
        speed_limit=violation_in.speed_limit,
        plate_number=violation_in.plate_number or "UNKNOWN",
        location=violation_in.location or "Main Junction - Camera 01",
        evidence_path=violation_in.evidence_path,
        confidence=violation_in.confidence or 0.95,
        status=violation_in.status or "PENDING",
        details=violation_in.details,
        timestamp=violation_in.timestamp or datetime.utcnow()
    )
    db.add(violation)
    db.commit()
    db.refresh(violation)
    return violation


@router.put("/{violation_id}", response_model=ViolationRead)
def update_violation(
    violation_id: int,
    violation_update: ViolationUpdate,
    db: Session = Depends(get_db)
):
    """Update violation status (e.g. PENDING -> CONFIRMED / DISMISSED) or plate number."""
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    if violation_update.status:
        violation.status = violation_update.status.upper()
    if violation_update.plate_number:
        violation.plate_number = violation_update.plate_number
    if violation_update.details:
        violation.details = violation_update.details

    db.commit()
    db.refresh(violation)
    return violation


@router.delete("/{violation_id}", status_code=204)
def delete_violation(violation_id: int, db: Session = Depends(get_db)):
    """Delete a violation record."""
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    db.delete(violation)
    db.commit()
    return None
