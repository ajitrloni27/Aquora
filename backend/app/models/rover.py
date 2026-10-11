from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from app.core.database import Base


class RoverStatus(Base):
    __tablename__ = "rover_statuses"

    id = Column(Integer, primary_key=True, index=True)
    battery_level = Column(Float, nullable=False, default=100.0)  # percentage (0-100)
    temperature = Column(Float, nullable=False, default=25.0)    # Celsius
    depth = Column(Float, nullable=False, default=0.0)            # meters
    speed = Column(Float, nullable=False, default=0.0)            # m/s
    status = Column(String(50), nullable=False, default="idle")   # idle, active, returning, error
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
