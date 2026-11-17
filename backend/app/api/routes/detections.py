from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.detection import DetectionsBatchCreate, DetectionResponse
from app.services import detection_service

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.post("", response_model=List[DetectionResponse], status_code=status.HTTP_201_CREATED)
def create_detections(payload: DetectionsBatchCreate, db: Session = Depends(get_db)):
    """
    Validate and store the AI detections payload.
    Creates one Detection row per item in detections[], committed in one atomic transaction.
    """
    return detection_service.create_detections_batch(db, payload)


@router.get("", response_model=List[DetectionResponse])
def get_detections(
    rover_id: Optional[str] = Query(None, description="Filter detections by rover ID"),
    class_name: Optional[str] = Query(None, description="Filter detections by class name (e.g. plastic)"),
    min_confidence: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="Minimum confidence score threshold (0.0 - 1.0)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of detections to return (1-100)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    Retrieve logged detections, ordered newest first (timestamp DESC).
    Supports filtering by rover_id, class_name, min_confidence, and offset/limit pagination.
    """
    return detection_service.list_detections(
        db,
        rover_id=rover_id,
        class_name=class_name,
        min_confidence=min_confidence,
        limit=limit,
        offset=offset,
    )
