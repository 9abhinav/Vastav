from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.app.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False, default="Northbound Expressway - KM 14")
    source = Column(String(255), nullable=False, default="videos/sample_traffic.mp4")
    camera_type = Column(String(50), default="FILE")  # FILE, WEBCAM, RTSP
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="ONLINE")  # ONLINE, OFFLINE, STREAMING
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Camera(id={self.id}, name={self.name}, source={self.source})>"
