from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DetectionItem(BaseModel):
    class_name: str = Field(..., max_length=100, description="Detected object class (e.g. plastic)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    image_ref: Optional[str] = Field(default=None, max_length=500, description="Snapshot reference/URL")

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: List[float]) -> List[float]:
        if len(v) != 4:
            raise ValueError("Bounding box must contain exactly 4 coordinates [x1, y1, x2, y2]")
        x1, y1, x2, y2 = v
        if x2 <= x1:
            raise ValueError(f"Invalid bbox: x2 ({x2}) must be strictly greater than x1 ({x1})")
        if y2 <= y1:
            raise ValueError(f"Invalid bbox: y2 ({y2}) must be strictly greater than y1 ({y1})")
        return v


class DetectionsBatchCreate(BaseModel):
    rover_id: str = Field(..., max_length=50, description="Rover identifier (e.g. AR-001)")
    timestamp: datetime = Field(..., description="UTC timestamp of the detection event")
    detections: List[DetectionItem] = Field(..., description="List of detected objects")

    @field_validator("detections")
    @classmethod
    def validate_non_empty(cls, v: List[DetectionItem]) -> List[DetectionItem]:
        if not v:
            raise ValueError("Detections list cannot be empty")
        return v


class DetectionResponse(BaseModel):
    id: int
    rover_id: str
    timestamp: datetime
    class_name: str
    confidence: float
    bbox: List[float]
    image_ref: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Aliases for transition
DetectionCreate = DetectionItem

