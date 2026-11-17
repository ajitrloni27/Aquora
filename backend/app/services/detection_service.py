from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.detection import Detection
from app.models.rover import Rover
from app.schemas.detection import DetectionsBatchCreate


def create_detections_batch(
    db: Session, batch_in: DetectionsBatchCreate
) -> List[Detection]:
    """
    Validates rover existence and saves a batch of detections in one database transaction.
    Raises 404 Not Found if rover_id does not exist.
    """
    rover = db.query(Rover).filter(Rover.rover_id == batch_in.rover_id).first()
    if not rover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rover with ID '{batch_in.rover_id}' not found",
        )

    records: List[Detection] = []
    for item in batch_in.detections:
        detection = Detection(
            rover_id=batch_in.rover_id,
            timestamp=batch_in.timestamp,
            class_name=item.class_name,
            confidence=item.confidence,
            bbox=item.bbox,
            image_ref=item.image_ref,
        )
        db.add(detection)
        records.append(detection)

    db.commit()
    for detection in records:
        db.refresh(detection)

    return records


def list_detections(
    db: Session,
    rover_id: Optional[str] = None,
    class_name: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Detection]:
    """
    Retrieves detections ordered by newest first (timestamp DESC, id DESC),
    with optional filtering by rover_id, class_name, min_confidence, and pagination.
    """
    query = db.query(Detection)

    if rover_id:
        query = query.filter(Detection.rover_id == rover_id)
    if class_name:
        query = query.filter(Detection.class_name.ilike(class_name))
    if min_confidence is not None:
        query = query.filter(Detection.confidence >= min_confidence)

    return (
        query.order_by(Detection.timestamp.desc(), Detection.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
