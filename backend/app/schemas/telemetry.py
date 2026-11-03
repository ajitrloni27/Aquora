from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TelemetryBase(BaseModel):
    rover_id: str = Field(..., max_length=50, description="Rover identifier (e.g. AR-001)")
    timestamp: datetime = Field(..., description="UTC timestamp of the telemetry reading")
    battery: float = Field(..., ge=0.0, le=100.0, description="Battery percentage (0.0 - 100.0)")
    speed: float = Field(..., ge=0.0, description="Speed in m/s (>= 0.0)")
    status: str = Field(..., max_length=50, description="Current operational status")
    temperature: Optional[float] = Field(default=None, description="Operating temperature in Celsius")
    signal: Optional[float] = Field(default=None, description="Signal strength")


class TelemetryCreate(TelemetryBase):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="GPS Latitude (-90.0 to 90.0)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="GPS Longitude (-180.0 to 180.0)")


class TelemetryResponse(TelemetryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
