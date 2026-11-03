from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoverBase(BaseModel):
    rover_id: str = Field(..., max_length=50, description="Unique rover identifier (e.g. AR-001)")
    name: str = Field(..., max_length=100, description="Rover friendly name")
    status: Optional[str] = Field(default="idle", max_length=50, description="Rover operational status")


class RoverCreate(RoverBase):
    pass


class RoverResponse(RoverBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
