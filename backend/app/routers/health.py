from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def check_health(db: Session = Depends(get_db)):
    """Health check endpoint for application, database, and AI service status."""
    db_status = "ONLINE"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "database": db_status,
        "yolo_model": settings.YOLO_MODEL,
        "speed_limit_default": settings.DEFAULT_SPEED_LIMIT
    }
