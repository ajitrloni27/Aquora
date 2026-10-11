from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.rover import RoverStatus
from app.schemas.rover import RoverStatusCreate, RoverStatusResponse

router = APIRouter(prefix="/rover", tags=["Rover"])


@router.get("/status", response_model=RoverStatusResponse)
def get_current_rover_status(db: Session = Depends(get_db)):
    """
    Get the latest operational status and telemetry of the rover.
    If no telemetry has been logged yet, initializes a default record.
    """
    latest = db.query(RoverStatus).order_by(RoverStatus.id.desc()).first()
    if not latest:
        # Create an initial default status entry if table is empty
        latest = RoverStatus(
            battery_level=100.0,
            temperature=24.5,
            depth=0.0,
            speed=0.0,
            status="idle",
            latitude=15.2993,
            longitude=74.1240,
        )
        db.add(latest)
        db.commit()
        db.refresh(latest)
    return latest


@router.post("/status", response_model=RoverStatusResponse, status_code=status.HTTP_201_CREATED)
def record_rover_status(payload: RoverStatusCreate, db: Session = Depends(get_db)):
    """
    Post a new telemetry/status report from the rover.
    """
    new_status = RoverStatus(**payload.model_dump())
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return new_status


@router.get("/status/history", response_model=List[RoverStatusResponse])
def get_rover_status_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve historical telemetry records.
    """
    return db.query(RoverStatus).order_by(RoverStatus.id.desc()).limit(limit).all()
