from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.camera import Camera
from backend.app.schemas.camera import CameraCreate, CameraRead, CameraUpdate

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("", response_model=List[CameraRead])
def list_cameras(db: Session = Depends(get_db)):
    """List all configured camera sources."""
    return db.query(Camera).all()


@router.post("", response_model=CameraRead, status_code=201)
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    """Register a new camera source (file, webcam, or RTSP)."""
    camera = Camera(**camera_in.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=CameraRead)
def update_camera(camera_id: int, cam_update: CameraUpdate, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = cam_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(camera, k, v)

    db.commit()
    db.refresh(camera)
    return camera
