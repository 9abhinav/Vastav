from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from backend.app.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False)  # JSON-encoded string or plain text
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting(key={self.key}, value={self.value})>"
