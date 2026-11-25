from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tracking_id = Column(Integer, index=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False, default="car")
    plate_number = Column(String(50), nullable=True, index=True, default="UNKNOWN")
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    max_speed = Column(Float, default=0.0)
    avg_speed = Column(Float, default=0.0)
    total_detections = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    violations = relationship("Violation", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, tracking_id={self.tracking_id}, type={self.vehicle_type}, plate={self.plate_number})>"
