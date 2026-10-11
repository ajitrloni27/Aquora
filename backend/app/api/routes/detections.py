from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.detection import Detection
from app.schemas.detection import DetectionCreate, DetectionResponse

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.get("", response_model=List[DetectionResponse])
def get_detections(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Limit records returned"),
    label: Optional[str] = Query(None, description="Filter by detection label"),
    db: Session = Depends(get_db),
):
    """
    Retrieve logged detections, with optional filtering by label and pagination.
    """
    query = db.query(Detection)
    if label:
        query = query.filter(Detection.label.ilike(f"%{label}%"))
    return query.order_by(Detection.id.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
def create_detection(payload: DetectionCreate, db: Session = Depends(get_db)):
    """
    Record a new object/debris detection event from the rover camera/sensors.
    """
    detection = Detection(**payload.model_dump())
    db.add(detection)
    db.commit()
    db.refresh(detection)
    return detection


@router.get("/{detection_id}", response_model=DetectionResponse)
def get_detection_by_id(detection_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific detection event by its unique ID.
    """
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection with ID {detection_id} not found",
        )
    return detection
