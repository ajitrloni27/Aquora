from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from app.core.database import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), nullable=False, index=True)       # e.g., "plastic_bottle", "debris", "oil_slick"
    confidence = Column(Float, nullable=False)                    # 0.0 - 1.0
    depth = Column(Float, nullable=True, default=0.0)             # water depth in meters
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
