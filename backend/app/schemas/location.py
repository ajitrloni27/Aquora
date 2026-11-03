from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class LocationResponse(BaseModel):
    id: int
    rover_id: str
    timestamp: datetime
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    model_config = ConfigDict(from_attributes=True)
