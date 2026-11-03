from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Rover(Base):
    __tablename__ = "rovers"

    id = Column(Integer, primary_key=True, index=True)
    rover_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="idle")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Time-series relationships
    telemetry_records = relationship("Telemetry", back_populates="rover", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="rover", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="rover", cascade="all, delete-orphan")
