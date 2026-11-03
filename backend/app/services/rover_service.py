from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.rover import Rover
from app.schemas.rover import RoverCreate


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
