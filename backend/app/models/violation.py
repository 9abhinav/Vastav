from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)
    tracking_id = Column(Integer, index=True, nullable=False)
    violation_type = Column(String(50), index=True, nullable=False)  # OVER_SPEEDING, RED_LIGHT, WRONG_WAY, LANE_VIOLATION
    speed = Column(Float, nullable=False, default=0.0)
    speed_limit = Column(Float, nullable=False, default=60.0)
    plate_number = Column(String(50), nullable=True, index=True, default="UNKNOWN")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    location = Column(String(150), default="Main Junction - Camera 01")
    evidence_path = Column(String(255), nullable=True)
    confidence = Column(Float, default=0.90)
    status = Column(String(30), default="PENDING", index=True)  # PENDING, CONFIRMED, DISMISSED
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="violations")

    def __repr__(self):
        return f"<Violation(id={self.id}, type={self.violation_type}, vehicle_id={self.vehicle_id}, speed={self.speed})>"
