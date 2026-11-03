from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    rover_id = Column(String(50), ForeignKey("rovers.rover_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    battery = Column(Float, nullable=False)  # percentage 0.0 - 100.0
    speed = Column(Float, nullable=False)    # speed >= 0.0 (m/s)
    status = Column(String(50), nullable=False)

    # Optional sensor additions (nullable)
    temperature = Column(Float, nullable=True)  # operating temperature in Celsius
    signal = Column(Float, nullable=True)       # signal quality percentage or dBm

    rover = relationship("Rover", back_populates="telemetry_records")

    __table_args__ = (
        Index("ix_telemetry_rover_id_timestamp", "rover_id", "timestamp"),
    )
