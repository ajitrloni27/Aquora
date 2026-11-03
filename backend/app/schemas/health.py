from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service status (healthy or degraded)")
    project: str = Field(..., description="Project name")
    environment: str = Field(..., description="Current environment (e.g. development, production)")
    timestamp: datetime = Field(..., description="Current server time in UTC")
    database: str = Field(..., description="Database reachability status (connected or disconnected)")
