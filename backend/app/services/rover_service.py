from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.rover import Rover
from app.models.telemetry import Telemetry
from app.models.location import Location
from app.schemas.rover import RoverCreate
from app.schemas.telemetry import TelemetryCreate


def create_rover(db: Session, rover_in: RoverCreate) -> Rover:
    """
    Registers a new rover. Raises 409 Conflict if rover_id already exists.
    """
    existing = db.query(Rover).filter(Rover.rover_id == rover_in.rover_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rover with ID '{rover_in.rover_id}' already exists",
        )

    rover = Rover(
        rover_id=rover_in.rover_id,
        name=rover_in.name,
        status=rover_in.status or "idle",
    )
    db.add(rover)
    db.commit()
    db.refresh(rover)
    return rover


def list_rovers(db: Session) -> List[Rover]:
    """
    Retrieves all registered rovers.
    """
    return db.query(Rover).order_by(Rover.id.asc()).all()


def get_rover_by_id(db: Session, rover_id: str) -> Rover:
    """
    Retrieves a rover by its unique string rover_id (e.g. AR-001).
    Raises 404 Not Found if missing.
    """
    rover = db.query(Rover).filter(Rover.rover_id == rover_id).first()
    if not rover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rover with ID '{rover_id}' not found",
        )
    return rover


def ingest_telemetry(db: Session, telemetry_in: TelemetryCreate) -> Telemetry:
    """
    Validates rover existence and stores telemetry and location records in one atomic transaction.
    Raises 404 Not Found if rover_id does not exist.
    """
    get_rover_by_id(db, telemetry_in.rover_id)

    telemetry = Telemetry(
        rover_id=telemetry_in.rover_id,
        timestamp=telemetry_in.timestamp,
        battery=telemetry_in.battery,
        speed=telemetry_in.speed,
        status=telemetry_in.status,
        temperature=telemetry_in.temperature,
        signal=telemetry_in.signal,
    )
    location = Location(
        rover_id=telemetry_in.rover_id,
        timestamp=telemetry_in.timestamp,
        latitude=telemetry_in.latitude,
        longitude=telemetry_in.longitude,
    )
    db.add(telemetry)
    db.add(location)
    db.commit()
    db.refresh(telemetry)
    return telemetry


def get_latest_status(db: Session, rover_id: str) -> Telemetry:
    """
    Retrieves the most recent telemetry record for the specified rover.
    Raises 404 Not Found if rover does not exist or has no telemetry recorded.
    """
    get_rover_by_id(db, rover_id)

    latest = (
        db.query(Telemetry)
        .filter(Telemetry.rover_id == rover_id)
        .order_by(Telemetry.timestamp.desc(), Telemetry.id.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for rover '{rover_id}'",
        )
    return latest


def get_latest_location(db: Session, rover_id: str) -> Location:
    """
    Retrieves the most recent location record for the specified rover.
    Raises 404 Not Found if rover does not exist or has no location recorded.
    """
    get_rover_by_id(db, rover_id)

    latest = (
        db.query(Location)
        .filter(Location.rover_id == rover_id)
        .order_by(Location.timestamp.desc(), Location.id.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No location found for rover '{rover_id}'",
        )
    return latest

