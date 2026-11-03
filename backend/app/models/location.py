from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    rover_id = Column(String(50), ForeignKey("rovers.rover_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    latitude = Column(Float, nullable=False)   # -90.0 .. 90.0
    longitude = Column(Float, nullable=False)  # -180.0 .. 180.0

    rover = relationship("Rover", back_populates="locations")

    __table_args__ = (
        Index("ix_locations_rover_id_timestamp", "rover_id", "timestamp"),
    )
