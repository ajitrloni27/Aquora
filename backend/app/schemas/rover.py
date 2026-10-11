from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoverStatusBase(BaseModel):
    battery_level: float = Field(..., ge=0.0, le=100.0, description="Battery percentage (0-100)")
    temperature: float = Field(..., description="Operating temperature in Celsius")
    depth: float = Field(default=0.0, ge=0.0, description="Current depth in meters")
    speed: float = Field(default=0.0, ge=0.0, description="Speed in m/s")
    status: str = Field(default="idle", description="Rover state: idle, active, returning, error")
    latitude: Optional[float] = Field(default=None, description="GPS Latitude")
    longitude: Optional[float] = Field(default=None, description="GPS Longitude")


class RoverStatusCreate(RoverStatusBase):
    pass


class RoverStatusResponse(RoverStatusBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
