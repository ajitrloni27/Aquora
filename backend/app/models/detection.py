from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    rover_id = Column(String(50), ForeignKey("rovers.rover_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    class_name = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 .. 1.0
    bbox = Column(JSON, nullable=False)         # [x1, y1, x2, y2]
    image_ref = Column(String(500), nullable=True)  # Future S3 object key or URL

    rover = relationship("Rover", back_populates="detections")

    __table_args__ = (
        Index("ix_detections_rover_id_timestamp", "rover_id", "timestamp"),
    )
