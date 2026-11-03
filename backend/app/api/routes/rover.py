from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.rover import RoverCreate, RoverResponse
from app.services import rover_service

router = APIRouter(tags=["Rover"])


# ---------------------------------------------------------
# Sprint 1 Rover CRUD Endpoints (/rovers)
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
