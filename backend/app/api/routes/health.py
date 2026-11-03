from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health_service import check_db_health

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health(response: Response, db: Session = Depends(get_db)):
    """
    Health check endpoint returning API service status, project metadata,
    UTC timestamp, and verified database reachability.
    """
    is_db_connected = check_db_health(db)
    if not is_db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "degraded"
        db_status = "disconnected"
    else:
        overall_status = "healthy"
        db_status = "connected"

    return HealthResponse(
        status=overall_status,
        project=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        database=db_status,
    )
