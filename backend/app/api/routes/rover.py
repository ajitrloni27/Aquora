from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.location import LocationResponse
from app.schemas.rover import RoverCreate, RoverResponse
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse
from app.services import rover_service

router = APIRouter(tags=["Rover"])


# ---------------------------------------------------------
# Telemetry & Location Endpoints (/rover/...)
# ---------------------------------------------------------

@router.post("/rover/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
def post_rover_telemetry(payload: TelemetryCreate, db: Session = Depends(get_db)):
    """
    Validate and store telemetry; ALSO write a Location row from its latitude/longitude,
    in ONE transaction.
    """
    return rover_service.ingest_telemetry(db, payload)


@router.get("/rover/status", response_model=TelemetryResponse)
def get_rover_status(
    rover_id: str = Query("AR-001", description="Rover identifier"),
    db: Session = Depends(get_db),
):
    """
    Latest telemetry for a rover. Optional query rover_id (default AR-001).
    404 if the rover is unknown or has no telemetry.
    """
    return rover_service.get_latest_status(db, rover_id=rover_id)


@router.get("/rover/location", response_model=LocationResponse)
def get_rover_location(
    rover_id: str = Query("AR-001", description="Rover identifier"),
    db: Session = Depends(get_db),
):
    """
    Latest location for a rover. Optional query rover_id (default AR-001).
    404 if the rover is unknown or has no location.
    """
    return rover_service.get_latest_location(db, rover_id=rover_id)


# ---------------------------------------------------------
# Rover CRUD Endpoints (/rovers)
# ---------------------------------------------------------

@router.post("/rovers", response_model=RoverResponse, status_code=status.HTTP_201_CREATED)
def register_rover(payload: RoverCreate, db: Session = Depends(get_db)):
    """
    Register a new rover. Returns 409 Conflict if rover_id already exists.
    """
    return rover_service.create_rover(db, payload)


@router.get("/rovers", response_model=List[RoverResponse])
def get_all_rovers(db: Session = Depends(get_db)):
    """
    List all registered rovers.
    """
    return rover_service.list_rovers(db)


@router.get("/rovers/{rover_id}", response_model=RoverResponse)
def get_rover_details(rover_id: str, db: Session = Depends(get_db)):
    """
    Get registered rover details by unique rover_id (e.g. AR-001). Returns 404 if not found.
    """
    return rover_service.get_rover_by_id(db, rover_id)
