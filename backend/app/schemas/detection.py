from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DetectionBase(BaseModel):
    label: str = Field(..., max_length=100, description="Detected object class (e.g. plastic_bottle, debris)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score between 0.0 and 1.0")
    depth: Optional[float] = Field(default=0.0, ge=0.0, description="Water depth when detected")
    latitude: Optional[float] = Field(default=None, description="Detection GPS Latitude")
    longitude: Optional[float] = Field(default=None, description="Detection GPS Longitude")
    image_url: Optional[str] = Field(default=None, max_length=255, description="Associated snapshot URL or file path")


class DetectionCreate(DetectionBase):
    pass


class DetectionResponse(DetectionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
